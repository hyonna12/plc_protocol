from ..controllers.door import DoorController
import time

def main():
    # 도어 컨트롤러 생성
    door = DoorController()
    
    if not door.connect():
        return
        
    try:
        print("=== 도어 제어 테스트 시작 ===")
        
        # In Door 테스트
        print("\n--- In Door 테스트 ---")
        if door.in_door_open():
            print("In Door Open 완료")
        else:
            print("In Door Open 실패")
        
        time.sleep(2)  # 2초 대기
        
        if door.in_door_close():
            print("In Door Close 완료")
        else:
            print("In Door Close 실패")
            
        # Robot Door#1 테스트
        print("\n--- Robot Door#1 테스트 ---")
        if door.robot_door1_open():
            print("Robot Door#1 Open 완료")
        else:
            print("Robot Door#1 Open 실패")
            
        time.sleep(2)  # 2초 대기
        
        if door.robot_door1_close():
            print("Robot Door#1 Close 완료")
        else:
            print("Robot Door#1 Close 실패")
            
        # Robot Door#2 테스트
        print("\n--- Robot Door#2 테스트 ---")
        if door.robot_door2_open():
            print("Robot Door#2 Open 완료")
        else:
            print("Robot Door#2 Open 실패")
            
        time.sleep(2)  # 2초 대기
        
        if door.robot_door2_close():
            print("Robot Door#2 Close 완료")
        else:
            print("Robot Door#2 Close 실패")
            
        # 핸들러 바코드 트리거 테스트
        print("\n--- 핸들러 바코드 트리거 테스트 ---")
        if door.handler_trigger_f():
            print("핸들러 바코드 Trigger F 완료")
        else:
            print("핸들러 바코드 Trigger F 실패")
            
    finally:
        door.disconnect()

if __name__ == "__main__":
    main() 

# python3 door_test.py
