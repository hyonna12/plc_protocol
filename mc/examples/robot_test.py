from ..controllers.robot import RobotController

def main():
    # FRONT와 REAR 로봇 컨트롤러 생성
    front_robot = RobotController(is_front=True)
    rear_robot = RobotController(is_front=False)
    
    # PLC 연결
    if not front_robot.connect() or not rear_robot.connect():
        return
        
    try:
        print("=== 동작 테스트 시작 ===")
        
        # FRONT 로봇 X축 이동 테스트
        # 위치: 100mm = 100.000 = 100000
        # 속도: 5mm/s = 5.000 = 5000
        front_robot.x_axis_move(10000, 20000)  # 30mm, 20mm/s
        if front_robot.wait_for_completion(RobotController.CMD_X_AXIS_MOVE):
            print("[FRONT] X축 이동 완료")
        else:
            print("[FRONT] X축 이동 시간 초과")
        
        # REAR 로봇 Z축 이동 테스트
        # 위치: 45mm = 45.000 = 45000
        # 속도: 5mm/s = 5.000 = 5000
        # rear_robot.z_axis_move(45000, 5000)  # 45mm, 5mm/s
        # if rear_robot.wait_for_completion(RobotController.CMD_Z_AXIS_MOVE):
        #     print("[REAR] Z축 이동 완료")
        # else:
        #     print("[REAR] Z축 이동 시간 초과")
            
    finally:
        front_robot.disconnect()
        rear_robot.disconnect()

if __name__ == "__main__":
    main() 


# python3 robot_test.py
