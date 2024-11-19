from mc.controllers.robot import RobotController
from mc.controllers.door import DoorController
from mc.controllers.system import SystemController
from mc.conn.connection import PLCConnection
from mc.definitions.addresses import SystemAddresses
from mc.definitions.commands import SystemCommands
import time
import sys

class RobotSystem:
    def __init__(self, host="192.168.0.10", port=5000):
        self.host = host
        self.port = port
        # 컨트롤러 초기화
        self.system = SystemController(host=host, port=port)
        self.front_robot = RobotController(host=host, port=port, is_front=True)
        self.rear_robot = RobotController(host=host, port=port, is_front=False)
        self.door = DoorController(host=host, port=port)
        
    def initialize(self):
        """시스템 초기화 및 연결"""
        print("=== 시스템 초기화 시작 ===")
        
        # PLC 연결 초기화 (싱글톤)
        if not PLCConnection.initialize(self.host, self.port):
            print("PLC 연결 실패")
            return False
            
        # 운전 시작 요청 및 완료 대기
        # print("운전 시작 요청...")
        # if not self.system.start():
        #     print("운전 시작 실패")
        #     return False
        
        # print("운전 시작 완료")
        print("=== 시스템 초기화 완료 ===")
        return True
        
    def shutdown(self):
        """시스템 종료"""
        print("\n=== 시스템 종료 ===")
        self.system.stop()  # 정상 정지 시도
        PLCConnection.disconnect()

    def front_robot_operation(self):
        """FRONT 로봇 동작"""
        print("\n=== FRONT 로봇 동작 시작 ===")
        
        # X축 이동 (100mm)
        print("X축 100mm 이동...")
        if self.front_robot.x_axis_move(100000, 10000):
            print("X축 이동 완료")
        else:
            print("X축 이동 실패")
            return False
            
        # Z축 핸들러 동작
        print("핸들러 GET 동작...")
        if self.front_robot.z_handler_get():
            print("핸들러 GET 완료")
        else:
            print("핸들러 GET 실패")
            return False
            
        return True

    def rear_robot_operation(self):
        """REAR 로봇 동작"""
        print("\n=== REAR 로봇 동작 시작 ===")
        
        # Z축 이동 (45mm)
        print("Z축 45mm 이동...")
        if self.rear_robot.z_axis_move(45000, 5000):
            print("Z축 이동 완료")
        else:
            print("Z축 이동 실패")
            return False
            
        # 핸들러 회전
        print("핸들러 회전...")
        if self.rear_robot.z_handler_rotate():
            print("핸들러 회전 완료")
        else:
            print("핸들러 회전 실패")
            return False
            
        return True

    def door_operation(self):
        """도어 동작"""
        print("\n=== 도어 동작 시작 ===")
        
        # In Door 열기
        print("In Door 열기...")
        if self.door.in_door_open():
            print("In Door 열기 완료")
        else:
            print("In Door 열기 실패")
            return False
            
        time.sleep(2)  # 2초 대기
        
        # Robot Door1 열기
        print("Robot Door1 열기...")
        if self.door.robot_door1_open():
            print("Robot Door1 열기 완료")
        else:
            print("Robot Door1 열기 실패")
            return False
            
        return True

    def ready(self):
        """운전 준비"""
        print("\n=== 운전 준비 ===")
        self.system.ready()

    def start(self):
        """운전 시작"""
        print("\n=== 운전 시작 ===")
        self.system.start()

    def stop(self):
        """운전 정지"""
        print("\n=== 운전 정지 ===")
        self.system.stop()

    # def emergency_stop(self):
    #     """비상 정지"""
    #     print("\n=== 비상 정지 ===")
    #     self.system.emergency_stop()
        
def main():
    # 시스템 객체 생성 (컨트롤러 초기화)
    system = RobotSystem()
    
    try:
        # 시스템 초기화
        if not system.initialize():
            print("시스템 초기화 실패")
            return

        system.start()

        system.front_robot.z_handler_rotate()


        # system.door.in_door_open()


        # 작업 수행
        # Front 로봇 X축 이동
        # 위치: 10mm = 10.000 = 10000
        # 속도: 5mm/s = 5.000 = 5000
        # print("\nFront 로봇 X축 30mm 이동...")
        # if not system.rear_robot.x_axis_move(30000, 20000): # 100, 20
        #     print("Front 로봇 X축 이동 실패")
        #     return

        # Front 로봇 Z축 이동
        # print("\nFront 로봇 Z축 45mm 이동...")
        # if not system.rear_robot.z_axis_move(500000, 20000):
        #     print("Front 로봇 Z축 이동 실패")
        #     return
        

        # # Front 로봇 핸들러 GET
        # print("\nFront 로봇 핸들러 GET...")
        # if not system.front_robot.z_handler_get():
        #     print("Front 로봇 핸들러 GET 실패")
        #     return

        # # Rear 로봇 Z축 이동
        # print("\nRear 로봇 Z축 45mm 이동...")
        # if not system.rear_robot.z_axis_move(45000, 5000):
        #     print("Rear 로봇 Z축 이동 실패")
        #     return
        
        # system.front_robot_operation()
        # system.rear_robot_operation()
        # system.door_operation()
   
    except KeyboardInterrupt:
        print("\n키보드 인터럽트 감지")
    except Exception as e:
        print(f"\n에러 발생: {str(e)}")
    # finally:
    #     system.shutdown()

if __name__ == "__main__":
    main() 


# python3 -m mc.main