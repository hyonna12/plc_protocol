from controllers.robot import RobotController
from controllers.door import DoorController
from controllers.system import SystemController
from conn.connection import PLCConnection
from definitions.addresses import SystemAddresses
from definitions.commands import SystemCommands
from server.server import PLCServer
from config.config import load_config
import time
import sys

class RobotSystem:
    def __init__(self):
        plc_config = load_config()
        self.host = plc_config['host']
        self.port = plc_config['port']
        
        # 컨트롤러 초기화
        self.system = SystemController()
        self.front_robot = RobotController(is_front=True)
        self.rear_robot = RobotController(is_front=False)
        self.door = DoorController()
        
    def initialize(self):
        """시스템 초기화 및 연결"""
        print("=== 시스템 초기화 시작 ===")
        
        # PLC 연결 초기화 (싱글톤)
        if not PLCConnection.initialize():
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
    robot_system = RobotSystem()
    
    # 시스템 초기화
    if not robot_system.initialize():
            print("Failed to initialize robot system")
            return

    # TCP 서버 시작(apcs와 통신)
    server = PLCServer(robot_system)
    
    try:
        server.start()
    except KeyboardInterrupt:
        print("Shutting down server...")
    finally:
        server.stop()
        robot_system.shutdown()



        # system.start()

        # system.front_robot.z_handler_rotate_home()


        # system.door.in_door_close()


        # 작업 수행
        # Front 로봇 X축 이동
        # 위치: 10mm = 10.000 = 10000
        # 속도: 5mm/s = 5.000 = 5000
        # print("\nFront 로봇 X축 30mm 이동...")
        # if not system.front_robot.x_axis_move(0, 20000): # 100, 20
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
   

if __name__ == "__main__":
    main() 

# python3 main.py