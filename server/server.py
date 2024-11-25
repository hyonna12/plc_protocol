# plc_protocol/server.py
import socket
import threading
import json
import time

from typing import Dict, Any
from definitions.slots import SlotLayout

class PLCServer:
    def __init__(self, robot_system):
        self.robot_system = robot_system
        self.slot_layout = SlotLayout()
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.running = True
        self.client = None  # 연결된 클라이언트 저장

    def start(self, host="0.0.0.0", port=5000):
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        self.server.bind((host, port))
        self.server.listen(1)
        print(f"PLC Server listening on {host}:{port}")

        while self.running:
            try:
                client, addr = self.server.accept()
                print(f"Connected by {addr}")
                self.client = client  # 클라이언트 저장
                print("[PLC Server] 새로운 클라이언트 연결")
                self.handle_client(client)
            except Exception as e:
                print(f"Error accepting connection: {e}")

    def send_message(self, message):
        """APCS로 메시지 전송"""
        if self.client is None:
            print("No client connected")
            return False
            
        try:
            data = json.dumps(message).encode()
            self.client.send(data)
            print(f"Message sent: {message}")
            return True
        except Exception as e:
            print(f"Error sending message: {e}")
            return False

    def handle_client(self, client):
        """클라이언트 요청 처리"""
        client.settimeout(None)

        # TCP keepalive 설정 최적화
        client.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        client.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 1)    
        client.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 1)   
        client.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 10)    

        # 버퍼 크기 설정
        client.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 8192)
        client.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 8192)

        while self.running:
            try:
                data = client.recv(4096)
                if not data:
                    print("[PLC Server] 클라이언트 연결 종료 감지")
                    break
                
                try:
                    command = json.loads(data.decode())
                    print(f"[PLC Server] 수신된 명령: {command}")

                    response = self.execute_command(command)
                    client.send(json.dumps(response).encode())

                except json.JSONDecodeError:
                    print("[PLC Server] JSON 디코딩 에러, 무시하고 계속")
                    continue

            except Exception as e:
                print(f"[PLC Server] 예외 발생: {e}")
                break

        print("[PLC Server] 클라이언트 연결 종료")
        if self.client == client:
            self.client = None
        try:
            client.close()
        except:
            pass

        # 새로운 연결을 즉시 받을 준비
        print("[PLC Server] 새로운 연결 대기 중...")

    def execute_command(self, command: Dict[str, Any]) -> Dict[str, Any]:
        cmd_type = command.get("type")
        params = command.get("params", {})
        command_id = params.get("command_id")
        
        try:
            if cmd_type == "robot_move":
                robot_id = params["robot_id"]
                is_front = (robot_id == 1)  # robot_id 1은 전면, 2는 후면
                robot = self.robot_system.front_robot if is_front else self.robot_system.rear_robot
                
                # 슬롯 ID를 좌표로 변환
                slot_id = params["position"]
                target_pos = self.slot_layout.get_position(slot_id, is_front)
                if not target_pos:
                    return {
                        "success": False, 
                        "message": f"Invalid slot ID: {slot_id}",
                        "command_id": command_id,
                        "details": {
                            "step": "position_validation",
                            "slot_id": slot_id,
                            "robot_id": robot_id
                        }
                    }
                
                speed = params["speed"]
                
                # X축 이동
                success = robot.x_axis_move(target_pos["x"], speed)
                if not success:
                    return {
                        "success": False, 
                        "message": "X axis move failed",
                        "command_id": command_id,
                        "details": {
                            "step": "x_axis",
                            "position": target_pos["x"],
                            "robot_id": robot_id
                        }
                    }
                
                # Z축 이동
                success = robot.z_axis_move(target_pos["z"], speed)
                if not success:
                    return {
                        "success": False, 
                        "message": "Z axis move failed",
                        "command_id": command_id,
                        "details": {
                            "step": "z_axis",
                            "position": target_pos["z"],
                            "robot_id": robot_id
                        }
                    }
                
                return {
                    "success": True,
                    "message": "Robot move completed",
                    "command_id": command_id,
                    "details": {
                        "position": {"x": target_pos["x"], "z": target_pos["z"]},
                        "robot_id": robot_id
                    }
                }
                
            elif cmd_type == "robot_rotate":
                robot = self.robot_system.front_robot if params["robot_id"] == 1 else self.robot_system.rear_robot
                direction = params["direction"]
                
                if direction == "home":
                    success = robot.z_handler_rotate_home()
                elif direction == "front":
                    success = robot.z_handler_rotate_front()
                elif direction == "rear":
                    success = robot.z_handler_rotate_rear()
                else:
                    return {
                        "success": False,
                        "message": f"Invalid rotation direction: {direction}",
                        "command_id": command_id,
                        "details": {
                            "step": "validation",
                            "direction": direction
                        }
                    }
                    
                return {
                    "success": success,
                    "message": "Rotation completed" if success else "Rotation failed",
                    "command_id": command_id,
                    "details": {
                        "direction": direction,
                        "robot_id": params["robot_id"]
                    }
                }
                
            elif cmd_type == "robot_handler":
                robot = self.robot_system.front_robot if params["robot_id"] == 1 else self.robot_system.rear_robot
                operation = params["operation"]
                
                if operation == "pull":
                    success = robot.z_handler_get()
                elif operation == "push":
                    success = robot.z_handler_put()
                else:
                    return {
                        "success": False,
                        "message": f"Invalid handler operation: {operation}",
                        "command_id": command_id,
                        "details": {
                            "step": "validation",
                            "operation": operation
                        }
                    }
                    
                return {
                    "success": success,
                    "message": f"Handler {operation} completed" if success else f"Handler {operation} failed",
                    "command_id": command_id,
                    "details": {
                        "operation": operation,
                        "robot_id": params["robot_id"]
                    }
                }
                
            elif cmd_type == "door_operation":
                door_type = params["door_type"]
                operation = params["operation"] 
                
                if door_type not in ["DoorTypeFront", "DoorTypeBack"]:
                    return {
                        "success": False,
                        "message": f"Invalid door type: {door_type}",
                        "command_id": command_id,
                        "details": {
                            "step": "validation",
                            "door_type": door_type
                        }
                    }
                    
                if operation not in ["DoorOperationOpen", "DoorOperationClose"]:
                    return {
                        "success": False,
                        "message": f"Invalid door operation: {operation}",
                        "command_id": command_id,
                        "details": {
                            "step": "validation",
                            "operation": operation
                        }
                    }

                # 도어 조작 실행
                if door_type == "DoorTypeFront":
                    success = (self.robot_system.door.in_door_open() if operation == "DoorOperationOpen" 
                              else self.robot_system.door.in_door_close())
                else:  # DoorTypeBack
                    success = (self.robot_system.door.out_door_open() if operation == "DoorOperationOpen"
                              else self.robot_system.door.out_door_close())

                return {
                    "success": success,
                    "message": f"Door {operation.lower()} {'completed' if success else 'failed'}",
                    "command_id": command_id,
                    "details": {
                        "door_type": door_type,
                        "operation": operation
                    }
                }

            elif cmd_type == "tray_buffer":
                operation = params.get("operation")
                
                if operation not in ["BufferOperationUp", "BufferOperationDown"]:
                    return {
                        "success": False,
                        "message": f"Invalid buffer operation: {operation}",
                        "command_id": command_id,
                        "details": {
                            "step": "validation",
                            "operation": operation
                        }
                    }

                # 트레이 버퍼 조작 실행
                success = (self.robot_system.tray_buffer.buffer_up() if operation == "BufferOperationUp"
                          else self.robot_system.tray_buffer.buffer_down())

                # # 완료 신호 대기
                # if success:
                #     success = self.wait_for_complete(self.robot_system.tray_buffer)

                return {
                    "success": success,
                    "message": f"Tray buffer {operation.lower()} {'completed' if success else 'failed'}",
                    "command_id": command_id,
                    "details": {
                        "operation": operation
                    }
                }

            else:
                return {
                    "success": False,
                    "message": "Unknown command type",
                    "command_id": command_id,
                    "details": {
                        "type": cmd_type
                    }
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": str(e),
                "command_id": command_id,
                "details": {
                    "error_type": type(e).__name__
                }
            }

    def stop(self):
        self.running = False
        self.server.close()