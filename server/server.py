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


    def start(self, host="0.0.0.0", port=5000):
        self.server.bind((host, port))
        self.server.listen(1)
        print(f"PLC Server listening on {host}:{port}")

        while self.running:
            try:
                client, addr = self.server.accept()
                print(f"Connected by {addr}")
                client_thread = threading.Thread(target=self.handle_client, args=(client,))
                client_thread.start()
            except Exception as e:
                print(f"Error accepting connection: {e}")

    def handle_client(self, client: socket.socket):
        print("[PLC Server] 새로운 클라이언트 연결")

        while self.running:
            try:
                # 소켓 타임아웃 설정
                client.settimeout(30.0)  # 30초로 설정
                
                data = client.recv(1024)
                if not data:
                    break
                
                command = json.loads(data.decode())
                print(f"[PLC Server] 수신된 명령: {command}")

                response = self.execute_command(command)
                
                client.send(json.dumps(response).encode())
                print(f"[PLC Server] 응답 전송: {response}")

            except socket.timeout:
                print("Socket timeout - waiting for next command")
                continue
            except Exception as e:
                print(f"Error handling client: {e}")
                break
        client.close()

    def execute_command(self, command: Dict[str, Any]) -> Dict[str, Any]:
        cmd_type = command.get("type")
        params = command.get("params", {})
        command_id = params.get("command_id")
        
        try:
            if cmd_type == "robot_move":
                robot = self.robot_system.front_robot if params["robot_id"] == 1 else self.robot_system.rear_robot
                
                # 슬롯 ID를 좌표로 변환
                slot_id = params["position"]
                target_pos = self.slot_layout.get_position(slot_id)
                if not target_pos:
                    return {
                        "success": False, 
                        "message": f"Invalid slot ID: {slot_id}",
                        "command_id": command_id,
                        "details": {
                            "step": "position_validation",
                            "slot_id": slot_id
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
                            "position": target_pos["x"]
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
                            "position": target_pos["z"]
                        }
                    }
                
                return {
                    "success": True,
                    "message": "Robot move completed",
                    "command_id": command_id,
                    "details": {
                        "position": {"x": target_pos["x"], "z": target_pos["z"]},
                        "robot_id": params["robot_id"]
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


    # def wait_for_complete(self, controller) -> bool:
    #     """PLC로부터 완료 신호 대기"""
    #     try:
    #         # 완료 신호 대기 (최대 10초)
    #         for _ in range(100):  # 100 * 0.1초 = 10초
    #             if controller.check_done():  # 실제 구현 필요
    #                 return True
    #             time.sleep(0.1)
    #         return False
    #     except Exception as e:
    #         print(f"Error waiting for complete: {e}")
    #         return False
        
    def stop(self):
        self.running = False
        self.server.close()