import unittest
import time
from controllers.door import DoorController
from controllers.robot import RobotController
from controllers.system import SystemController

class TestControllers(unittest.TestCase):
    def setUp(self):
        """테스트 셋업"""
        self.door = DoorController()
        self.front_robot = RobotController(is_front=True)
        self.rear_robot = RobotController(is_front=False)
        self.system = SystemController()
        
        # 시스템 초기화
        self.system_ready = self.system.ready()
        if not self.system_ready:
            self.skipTest("시스템이 준비되지 않아 테스트를 건너뜁니다.")
            
    def test_input_operation(self):
        """입고 작업 테스트"""
        print("\n=== 입고 작업 테스트 시작 ===")
        
        # 1. 시스템 시작
        self.assertTrue(self.system.start())
        
        # 2. 후면 도어 열기
        self.assertTrue(self.door.in_door_open())
        time.sleep(1)  # 도어 동작 대기
        
        # 3. 후면 로봇으로 빈 트레이 가져오기
        # 테이블 위치(slot_id=0)로 이동
        self.assertTrue(self.rear_robot.x_axis_move(0, 1000))  # 속도 1000mm/s
        
        # Z축 핸들러 동작
        self.assertTrue(self.rear_robot.z_handler_get())
        self.assertTrue(self.rear_robot.z_handler_rotate_home())
        
        # 4. 전면 도어 열기
        self.assertTrue(self.door.out_door_open())
        time.sleep(1)  # 도어 동작 대기
        
        # 5. 물품 적재 후 전면 도어 닫기
        self.assertTrue(self.door.out_door_close())
        time.sleep(1)  # 도어 동작 대기
        
        # 6. 전면 로봇으로 적재된 트레이 이동
        # 목표 슬롯(예: slot_id=1)으로 이동
        self.assertTrue(self.front_robot.x_axis_move(1, 1000))
        
        # Z축 핸들러 동작
        self.assertTrue(self.front_robot.z_handler_get())
        self.assertTrue(self.front_robot.z_handler_rotate_front())
        self.assertTrue(self.front_robot.z_handler_put())
        
        print("=== 입고 작업 테스트 완료 ===")

    def test_output_operation(self):
        """불출 작업 테스트"""
        print("\n=== 불출 작업 테스트 시작 ===")
        
        # 1. 시스템 시작
        self.assertTrue(self.system.start())
        
        # 2. 전면 로봇으로 물품이 있는 트레이 가져오기
        # 물품이 있는 슬롯(예: slot_id=1)으로 이동
        self.assertTrue(self.front_robot.x_axis_move(1, 1000))
        
        # Z축 핸들러 동작
        self.assertTrue(self.front_robot.z_handler_get())
        self.assertTrue(self.front_robot.z_handler_rotate_front())
        
        # 테이블로 이동
        self.assertTrue(self.front_robot.x_axis_move(0, 1000))
        self.assertTrue(self.front_robot.z_handler_put())
        
        # 3. 전면 도어 열기
        self.assertTrue(self.door.out_door_open())
        time.sleep(1)  # 도어 동작 대기
        
        # 4. 물품 수령 대기 (시뮬레이션)
        time.sleep(5)
        
        # 5. 전면 도어 닫기
        self.assertTrue(self.door.out_door_close())
        
        print("=== 불출 작업 테스트 완료 ===")

    def test_sort_operation(self):
        """정리 작업 테스트"""
        print("\n=== 정리 작업 테스트 시작 ===")
        
        # 1. 시스템 시작
        self.assertTrue(self.system.start())
        
        # 2. 전면 로봇으로 정리할 트레이 가져오기
        # 출발 슬롯(예: slot_id=1)으로 이동
        self.assertTrue(self.front_robot.x_axis_move(1, 1000))
        
        # Z축 핸들러 동작
        self.assertTrue(self.front_robot.z_handler_get())
        self.assertTrue(self.front_robot.z_handler_rotate_front())
        
        # 3. 목표 위치로 이동
        # 목표 슬롯(예: slot_id=2)으로 이동
        self.assertTrue(self.front_robot.x_axis_move(2, 1000))
        self.assertTrue(self.front_robot.z_handler_put())
        
        # 4. 로봇 위치 확인
        x_pos = self.front_robot.get_x_position()
        z_pos = self.front_robot.get_z_position()
        self.assertIsNotNone(x_pos)
        self.assertIsNotNone(z_pos)
        
        print(f"최종 로봇 위치 - X: {x_pos/1000.0}mm, Z: {z_pos/1000.0}mm")
        print("=== 정리 작업 테스트 완료 ===")

    def test_robot_movement(self):
        """로봇 이동 상세 테스트"""
        print("\n=== 로봇 이동 테스트 시작 ===")
        
        # 1. X축 이동 테스트
        print("\nX축 이동 테스트:")
        for slot_id in [0, 1, 2]:  # 여러 슬롯 위치로 이동
            print(f"\n슬롯 {slot_id}로 이동:")
            self.assertTrue(self.front_robot.x_axis_move(slot_id, 1000))
            x_pos = self.front_robot.get_x_position()
            print(f"현재 X축 위치: {x_pos/1000.0}mm")
            
        # 2. Z축 이동 테스트
        print("\nZ축 이동 테스트:")
        test_positions = [0, 100000, 200000]  # 0mm, 100mm, 200mm
        for pos in test_positions:
            print(f"\n높이 {pos/1000.0}mm로 이동:")
            self.assertTrue(self.front_robot.z_axis_move(pos, 1000))
            z_pos = self.front_robot.get_z_position()
            print(f"현재 Z축 위치: {z_pos/1000.0}mm")
            
        # 3. 핸들러 회전 테스트
        print("\n핸들러 회전 테스트:")
        self.assertTrue(self.front_robot.z_handler_rotate_home())
        self.assertTrue(self.front_robot.z_handler_rotate_front())
        self.assertTrue(self.front_robot.z_handler_rotate_rear())
        
        print("=== 로봇 이동 테스트 완료 ===")

    def test_door_operations(self):
        """도어 동작 상세 테스트"""
        print("\n=== 도어 동작 테스트 시작 ===")
        
        # 1. 전면 도어 테스트
        print("\n전면 도어 테스트:")
        self.assertTrue(self.door.out_door_open())
        time.sleep(1)
        self.assertTrue(self.door.out_door_close())
        
        # 2. 후면 도어 테스트
        print("\n후면 도어 테스트:")
        self.assertTrue(self.door.in_door_open())
        time.sleep(1)
        self.assertTrue(self.door.in_door_close())
        
        # 3. 로봇 도어 테스트
        print("\n로봇 도어 테스트:")
        self.assertTrue(self.door.robot_door1_open())
        time.sleep(1)
        self.assertTrue(self.door.robot_door1_close())
        self.assertTrue(self.door.robot_door2_open())
        time.sleep(1)
        self.assertTrue(self.door.robot_door2_close())
        
        print("=== 도어 동작 테스트 완료 ===")

    def test_robot_default_positions(self):
        """로봇별 기본 위치 이동 테스트"""
        print("\n=== 로봇 기본 위치 테스트 시작 ===")
        
        # 1. 시스템 시작
        self.assertTrue(self.system.start())
        
        # 2. 전면 로봇 기본 위치(-1)로 이동
        print("\n전면 로봇 기본 위치 이동:")
        self.assertTrue(self.front_robot.x_axis_move(-1, 1000))
        
        # 전면 로봇 위치 확인
        x_pos = self.front_robot.get_x_position()
        z_pos = self.front_robot.get_z_position()
        
        # 전면 로봇 기본 위치는 x=-100, z=0
        self.assertEqual(x_pos, -100000)  # mm를 0.001mm 단위로 변환
        self.assertEqual(z_pos, 0)
        print(f"전면 로봇 기본 위치 도달 - X: {x_pos/1000.0}mm, Z: {z_pos/1000.0}mm")
        
        # 3. 후면 로봇 기본 위치(-1)로 이동
        print("\n후면 로봇 기본 위치 이동:")
        self.assertTrue(self.rear_robot.x_axis_move(-1, 1000))
        
        # 후면 로봇 위치 확인
        x_pos = self.rear_robot.get_x_position()
        z_pos = self.rear_robot.get_z_position()
        
        # 후면 로봇 기본 위치는 x=-200, z=0
        self.assertEqual(x_pos, -200000)  # mm를 0.001mm 단위로 변환
        self.assertEqual(z_pos, 0)
        print(f"후면 로봇 기본 위치 도달 - X: {x_pos/1000.0}mm, Z: {z_pos/1000.0}mm")
        
        print("=== 로봇 기본 위치 테스트 완료 ===")

    def tearDown(self):
        """테스트 종료"""
        if self.system_ready:
            # 모든 도어 닫기
            self.door.out_door_close()
            self.door.in_door_close()
            self.door.robot_door1_close()
            self.door.robot_door2_close()
            
            # 시스템 정지
            self.system.stop()

if __name__ == '__main__':
    unittest.main() 

# python test/test_controllers.py

# -k 옵션으로 특정 이름을 가진 테스트만 실행
# python -m unittest test/test_controllers.py -k test_input_operation

# -v 옵션으로 자세한 출력
# python -m unittest -v test/test_controllers.py