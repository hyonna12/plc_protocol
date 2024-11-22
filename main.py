from controllers.robot import RobotController
from controllers.door import DoorController
from controllers.system import SystemController
from conn.connection import PLCConnection
from definitions.addresses import SystemAddresses
from definitions.commands import SystemCommands
from server.server import PLCServer
from config.config import load_config
from datetime import datetime
import time
import sys
import random
import threading

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
        
    def test_input_operation(self):
        """물품 입고 테스트"""
        print("\n=== 물품 입고 테스트 시작 ===")
        
        try:
            # 1. 로봇 테이블(slot_id=0) 위치로 이동 (X, Z축 동시 이동)
            print("\n1. 로봇 테이블 위치로 이동")
            if not self.front_robot.x_axis_move(0, 20000):  # 20mm/s 속도
                print("테이블 X축 이동 실패")
                return False
            if not self.front_robot.z_axis_move(0, 20000):  # 20mm/s 속도
                print("테이블 Z축 이동 실패")
                return False
                
            # 2. 전면 도어 열기
            print("\n2. 전면 도어 열기")
            if not self.door.in_door_open():  # in_door가 전면
                print("전면 도어 열기 실패")
                return False
                
            # 5초 대기
            print("\n 물품 입고 대기 (5초)")
            time.sleep(5)
            

            # 3. 물품 크기, 높이 랜덤 생성 및 로그
            print("\n3. 물품 정보 감지")
            item_height = random.randint(100, 250)  # 100~250mm
            item_weight = round(random.uniform(0.5, 5.0), 1)  # 0.5~5.0kg
            print(f"감지된 물품 정보:")
            print(f"- 높이: {item_height}mm")
            print(f"- 무게: {item_weight}kg")
            
            # 4. 전면 도어 닫기
            print("\n4. 전면 도어 닫기")
            if not self.door.in_door_close():  # in_door가 전면
                print("전면 도어 닫기 실패")
                return False
                
            # 5. 후면 도어 열기
            print("\n5. 후면 도어 열기")
            if not self.door.out_door_open():  # out_door가 후면
                print("후면 도어 열기 실패")
                return False
                
            # 6. 트레이 GET
            print("\n6. 트레이 GET")
            if not self.front_robot.z_handler_get():
                print("트레이 GET 실패")
                return False
                
            # 7. 후면 도어 닫기
            print("\n7. 후면 도어 닫기")
            if not self.door.out_door_close():  # out_door가 후면
                print("후면 도어 닫기 실패")
                return False
                
            # 8. 목표 슬롯으로 이동 (X, Z축 동시 이동)
            print("\n8. 목표 슬롯으로 이동")
            target_slot = 1
            if not self.front_robot.x_axis_move(target_slot * 100000, 20000):  # 100mm 간격, 20mm/s 속도
                print("슬롯 X축 이동 실패")
                return False
            if not self.front_robot.z_axis_move(target_slot * 45000, 20000):  # 45mm 간격, 20mm/s 속도
                print("슬롯 Z축 이동 실패")
                return False
                
            # 9. 슬롯 방향으로 회전
            print("\n9. 슬롯 방향으로 회전")
            if not self.front_robot.z_handler_rotate_rear():
                print("핸들러 회전 실패")
                return False
                
            # 10. 트레이 PUT
            print("\n10. 트레이 PUT")
            if not self.front_robot.z_handler_put():
                print("트레이 PUT 실패")
                return False
                
            # 11. 원위치로 회전
            print("\n11. 원위치로 회전")
            if not self.front_robot.z_handler_rotate_home():
                print("원위치 회전 실패")
                return False
                
            print("\n=== 물품 입고 테스트 완료 ===")
            return True
            
        except Exception as e:
            print(f"물품 입고 테스트 중 오류 발생: {e}")
            return False

    def test_output_operation(self):
        """물품 불출 테스트"""
        print("\n=== 물품 불출 테스트 시작 ===")
        
        try:
            # 1. 로봇 슬롯 위치로 이동 (X, Z축 동시 이동)
            print("\n1. 로봇 슬롯 위치로 이동")
            target_slot = 1  # 테스트용 슬롯 번호
            if not self.front_robot.x_axis_move(target_slot * 100000, 20000):  # 100mm 간격, 20mm/s 속도
                print("슬롯 X축 이동 실패")
                return False
            if not self.front_robot.z_axis_move(target_slot * 45000, 20000):  # 45mm 간격, 20mm/s 속도
                print("슬롯 Z축 이동 실패")
                return False
                
            # 2. 슬롯 방향으로 회전
            print("\n2. 슬롯 방향으로 회전")
            if not self.front_robot.z_handler_rotate_front():
                print("핸들러 회전 실패")
                return False
                
            # 3. 트레이 GET
            print("\n3. 트레이 GET")
            if not self.front_robot.z_handler_get():
                print("트레이 GET 실패")
                return False
                
            # 4. 원위치로 회전
            print("\n4. 원위치로 회전")
            if not self.front_robot.z_handler_rotate_home():
                print("원위치 회전 실패")
                return False
                
            # 5. 테이블로 이동 (X, Z축 동시 이동)
            print("\n5. 테이블로 이동")
            if not self.front_robot.x_axis_move(0, 20000):  # 20mm/s 속도
                print("테이블 X축 이동 실패")
                return False
            if not self.front_robot.z_axis_move(0, 20000):  # 20mm/s 속도
                print("테이블 Z축 이동 실패")
                return False
                
            # 6. 후면 도어 열기
            print("\n6. 후면 도어 열기")
            if not self.door.out_door_open():
                print("후면 도어 열기 실패")
                return False
                
            # 7. 트레이 PUT
            print("\n7. 트레이 PUT")
            if not self.front_robot.z_handler_put():
                print("트레이 PUT 실패")
                return False
                
            # 8. 후면 도어 닫기
            print("\n8. 후면 도어 닫기")
            if not self.door.out_door_close():
                print("후면 도어 닫기 실패")
                return False
                
            # 9. 전면 도어 열기
            print("\n9. 전면 도어 열기")
            if not self.door.in_door_open():
                print("전면 도어 열기 실패")
                return False
                
            # 10. 5초 대기
            print("\n10. 물품 수령 대기 (5초)")
            time.sleep(5)
                
            # 11. 전면 도어 닫기
            print("\n11. 전면 도어 닫기")
            if not self.door.in_door_close():
                print("전면 도어 닫기 실패")
                return False
                
            print("\n=== 물품 불출 테스트 완료 ===")
            return True
            
        except Exception as e:
            print(f"물품 불출 테스트 중 오류 발생: {e}")
            return False

    def test_sort_operation(self):
        """물품 정리 테스트"""
        print("\n=== 물품 정리 테스트 시작 ===")
        
        try:
            # 1. 출발 슬롯으로 이동 (X, Z축 동시 이동)
            print("\n1. 출발 슬롯으로 이동")
            source_slot = 1  # 출발 슬롯 번호
            if not self.front_robot.x_axis_move(source_slot * 100000, 20000):  # 100mm 간격, 20mm/s 속도
                print("출발 슬롯 X축 이동 실패")
                return False
            if not self.front_robot.z_axis_move(source_slot * 45000, 20000):  # 45mm 간격, 20mm/s 속도
                print("출발 슬롯 Z축 이동 실패")
                return False
                
            # 2. 슬롯 방향으로 회전
            print("\n2. 슬롯 방향으로 회전")
            if not self.front_robot.z_handler_rotate_front():
                print("핸들러 회전 실패")
                return False
                
            # 3. 트레이 GET
            print("\n3. 트레이 GET")
            if not self.front_robot.z_handler_get():
                print("트레이 GET 실패")
                return False
                
            # 4. 목적지 슬롯으로 이동 (X, Z축 동시 이동)
            print("\n4. 목적지 슬롯으로 이동")
            target_slot = 2  # 목적지 슬롯 번호
            if not self.front_robot.x_axis_move(target_slot * 100000, 20000):  # 100mm 간격, 20mm/s 속도
                print("목적지 슬롯 X축 이동 실패")
                return False
            if not self.front_robot.z_axis_move(target_slot * 45000, 20000):  # 45mm 간격, 20mm/s 속도
                print("목적지 슬롯 Z축 이동 실패")
                return False
                
            # 5. 트레이 PUT
            print("\n5. 트레이 PUT")
            if not self.front_robot.z_handler_put():
                print("트레이 PUT 실패")
                return False
                
            # 6. 원위치로 회전
            print("\n6. 원위치로 회전")
            if not self.front_robot.z_handler_rotate_home():
                print("원위치 회전 실패")
                return False
                
            print("\n=== 물품 정리 테스트 완료 ===")
            return True
            
        except Exception as e:
            print(f"물품 정리 테스트 중 오류 발생: {e}")
            return False

    def test_dual_sort_operation(self):
        """두 로봇 동시 물품 정리 테스트"""
        print("\n=== 두 로봇 동시 정리 테스트 시작 ===")
        
        try:
            # 전면 로봇 작업
            print("\n=== 전면 로봇 작업 시작 ===")
            # 1. 출발 슬롯으로 이동 (X, Z축 동시 이동)
            print("\n1. 전면 로봇 출발 슬롯으로 이동")
            front_source_slot = 289  # 전면 출발 슬롯 번호
            if not self.front_robot.x_axis_move(front_source_slot * 100000, 20000):
                print("전면 로봇 출발 슬롯 X축 이동 실패")
                return False
            if not self.front_robot.z_axis_move(front_source_slot * 45000, 20000):
                print("전면 로봇 출발 슬롯 Z축 이동 실패")
                return False
            
            # 후면 로봇 작업
            print("\n=== 후면 로봇 작업 시작 ===")
            # 1. 출발 슬롯으로 이동 (X, Z축 동시 이동)
            print("\n1. 후면 로봇 출발 슬롯으로 이동")
            rear_source_slot = 1  # 후면 출발 슬롯 번호
            if not self.rear_robot.x_axis_move(rear_source_slot * 100000, 20000):
                print("후면 로봇 출발 슬롯 X축 이동 실패")
                return False
            if not self.rear_robot.z_axis_move(rear_source_slot * 45000, 20000):
                print("후면 로봇 출발 슬롯 Z축 이동 실패")
                return False
            
            # 2. 두 로봇 동시에 슬롯 방향으로 회전
            print("\n2. 두 로봇 슬롯 방향으로 회전")
            front_rotate = self.front_robot.z_handler_rotate_front()
            rear_rotate = self.rear_robot.z_handler_rotate_rear()
            if not (front_rotate and rear_rotate):
                print("로봇 회전 실패")
                return False
            
            # 3. 두 로봇 동시에 트레이 GET
            print("\n3. 두 로봇 트레이 GET")
            front_get = self.front_robot.z_handler_get()
            rear_get = self.rear_robot.z_handler_get()
            if not (front_get and rear_get):
                print("트레이 GET 실패")
                return False
            
            # 4. 두 로봇 목적지 슬롯으로 이동
            print("\n4. 두 로봇 목적지 슬롯으로 이동")
            front_target_slot = 290  # 전면 목적지 슬롯 번호
            rear_target_slot = 2    # 후면 목적지 슬롯 번호
            
            # 전면 로봇 이동
            if not self.front_robot.x_axis_move(front_target_slot * 100000, 20000):
                print("전면 로봇 목적지 슬롯 X축 이동 실패")
                return False
            if not self.front_robot.z_axis_move(front_target_slot * 45000, 20000):
                print("전면 로봇 목적지 슬롯 Z축 이동 실패")
                return False
            
            # 후면 로봇 이동
            if not self.rear_robot.x_axis_move(rear_target_slot * 100000, 20000):
                print("후면 로봇 목적지 슬롯 X축 이동 실패")
                return False
            if not self.rear_robot.z_axis_move(rear_target_slot * 45000, 20000):
                print("후면 로봇 목적지 슬롯 Z축 이동 실패")
                return False
            
            # 5. 두 로봇 동시에 트레이 PUT
            print("\n5. 두 로봇 트레이 PUT")
            front_put = self.front_robot.z_handler_put()
            rear_put = self.rear_robot.z_handler_put()
            if not (front_put and rear_put):
                print("트레이 PUT 실패")
                return False
            
            # 6. 두 로봇 동시에 원위치로 회전
            print("\n6. 두 로봇 원위치로 회전")
            front_home = self.front_robot.z_handler_rotate_home()
            rear_home = self.rear_robot.z_handler_rotate_home()
            if not (front_home and rear_home):
                print("원위치 회전 실패")
                return False
            
            print("\n=== 두 로봇 동시 정리 테스트 완료 ===")
            return True
        
        except Exception as e:
            print(f"두 로봇 동시 정리 테스트 중 오류 발생: {e}")
            return False

def main():
    # 시스템 객체 생성
    robot_system = RobotSystem()
    
    # 시스템 초기화
    if not robot_system.initialize():
        print("Failed to initialize robot system")
        return
        
    try:
        # 운전 준비 및 시작
        # robot_system.ready()
        # robot_system.start()

        # 테스트 실행
        print("\n=== 테스트 시작 ===")
        
        ## target slot 의 x, z 값은 하드코딩으로 (특정 슬롯 position 측정해서)
        ## 한번에 시작하지 말고 하나씩 실행해보고 잘 동작하면 전체 입고/불출/정리
        ## 후면도어는 현재 안되니깐 주석처리
        # position, 물품 정보 등 로그 찍어야됨
        #plc 주소 변경하고

        # 1. 물품 입고 테스트
        # if robot_system.test_input_operation():
        #     print("입고 테스트 성공")
        # else:
        #     print("입고 테스트 실패")
            
        # time.sleep(2)  # 테스트 간 간격
        
        # 2. 물품 불출 테스트  
        # if robot_system.test_output_operation():
        #     print("불출 테스트 성공")
        # else:
        #     print("불출 테스트 실패")
            
        # time.sleep(2)  # 테스트 간 간격
        
        # 3. 물품 정리 테스트
        # if robot_system.test_sort_operation():
        #     print("정리 테스트 성공")
        # else:
        #     print("정리 테스트 실패")
            
        # 4. 두 로봇 동시 물품 정리 테스트
        # if robot_system.test_dual_sort_operation():
        #     print("두 로봇 동시 정리 테스트 성공")
        # else:
        #     print("두 로봇 동시 정리 테스트 실패")

     
        print("\n=== 테스트 종료 ===")
        
        # 5. 택배함 상태 모니터링
        server = PLCServer(robot_system)
        server.start()
        print("PLC Server started")

        # APCS로 네트워크 절체 감지 메시지 전송
        test_message = {
            "success": True,
            "message": "네트워크 절체 감지",
            "command_id": "0",
            "details": {
                "type": "network_status",
                "timestamp": datetime.now().isoformat(),
                "status": "disconnected",
                "connection_type": "TCP/IP",
                "last_connected": datetime.now().isoformat()
            }
        }
        
        print("\n=== APCS로 네트워크 절체 감지 메시지 전송 ===")
        server.send_message(test_message)
        print(f"메시지 전송 완료: {test_message}")
            
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    finally:
        robot_system.stop()
        robot_system.shutdown()

if __name__ == "__main__":
    main() 

# python3 main.py