from controllers.robot import RobotController
from controllers.door import DoorController
import time
import sys

class RobotSystem:
    def __init__(self, host="192.168.0.10", port=5000):
        # 로봇 및 도어 컨트롤러 초기화
        self.front_robot = RobotController(host=host, port=port, is_front=True)
        self.rear_robot = RobotController(host=host, port=port, is_front=False)
        self.door = DoorController(host=host, port=port)
        
    def initialize(self):
        """시스템 초기화 및 연결"""
        print("=== 시스템 초기화 시작 ===")
        
        # PLC 연결
        if not self.front_robot.connect():
            print("FRONT 로봇 연결 실패")
            return False
            
        if not self.rear_robot.connect():
            print("REAR 로봇 연결 실패")
            return False
            
        if not self.door.connect():
            print("도어 컨트롤러 연결 실패")
            return False
            
        print("=== 시스템 초기화 완료 ===")
        return True
        
    def shutdown(self):
        """시스템 종료"""
        print("\n=== 시스템 종료 ===")
        self.front_robot.disconnect()
        self.rear_robot.disconnect()
        self.door.disconnect()

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

def main():
    # 시스템 객체 생성
    system = RobotSystem()
    
    try:
        # 시스템 초기화
        if not system.initialize():
            print("시스템 초기화 실패")
            return
            
       
        system.front_robot_operation()
        system.rear_robot_operation()
        system.door_operation()
   
                
    except KeyboardInterrupt:
        print("\n프로그램 중단")
    except Exception as e:
        print(f"\n에러 발생: {str(e)}")
    finally:
        system.shutdown()

if __name__ == "__main__":
    main() 