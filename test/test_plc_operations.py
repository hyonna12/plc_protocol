import unittest
from datetime import datetime
import pymcprotocol  # type: ignore
import time

class PLCOperation:
    def __init__(self):
        self.plc = pymcprotocol.Type3E()
        self.tray_buffer_count = 0  # 트레이 버퍼 카운트
        self.current_tray_id = 0    # 현재 테이블의 트레이 ID
        
    def connect_plc(self, ip: str = "192.168.0.10", port: int = 5000):
        """PLC 연결"""
        try:
            self.plc.setaccessopt(commtype="ascii")
            self.plc.connect(ip, port)
            return True
        except Exception as e:
            print(f"PLC 연결 실패: {e}")
            return False

    def check_door_status(self, door_type: str) -> bool:
        """도어 상태 확인 (front/back)"""
        try:
            # D5100: 전면 도어 상태, D5101: 후면 도어 상태
            addr = "D5100" if door_type == "front" else "D5101"
            status = self.plc.batchread_wordunits(headdevice=addr, readsize=1)[0]
            return status == 1  # 1: 열림, 0: 닫힘
        except Exception as e:
            print(f"도어 상태 확인 실패: {e}")
            return False

    def operate_door(self, door_type: str, operation: str) -> bool:
        """도어 작동 (open/close)"""
        try:
            # D5200: 전면 도어 제어, D5201: 후면 도어 제어
            addr = "D5200" if door_type == "front" else "D5201"
            value = 1 if operation == "open" else 0
            self.plc.batchwrite_wordunits(headdevice=addr, values=[value])
            time.sleep(1)  # 도어 동작 대기
            return True
        except Exception as e:
            print(f"도어 작동 실패: {e}")
            return False

    def check_item_sensor(self) -> bool:
        """물품 감지 센서 확인"""
        try:
            # D5300: 물품 감지 센서
            return self.plc.batchread_wordunits(headdevice="D5300", readsize=1)[0] == 1
        except Exception as e:
            print(f"센서 확인 실패: {e}")
            return False

    def get_item_info(self) -> dict:
        """물품 정보 읽기 (높이, 무게)"""
        try:
            # D5400: 높이, D5401: 무게
            height = self.plc.batchread_wordunits(headdevice="D5400", readsize=1)[0]
            weight = self.plc.batchread_wordunits(headdevice="D5401", readsize=1)[0]
            return {"height": height, "weight": weight}
        except Exception as e:
            print(f"물품 정보 읽기 실패: {e}")
            return {"height": 0, "weight": 0}

    def move_robot(self, x: int, z: int) -> bool:
        """로봇 이동"""
        try:
            # D5500: X축 위치, D5501: Z축 위치
            self.plc.batchwrite_wordunits(headdevice="D5500", values=[x])
            self.plc.batchwrite_wordunits(headdevice="D5501", values=[z])
            time.sleep(2)  # 로봇 이동 대기
            return True
        except Exception as e:
            print(f"로봇 이동 실패: {e}")
            return False

class TestPLCOperations(unittest.TestCase):
    def setUp(self):
        self.plc_op = PLCOperation()
        self.plc_connected = self.plc_op.connect_plc()
        
    def test_input_operation(self):
        """입고 작업 테스트"""
        if not self.plc_connected:
            self.skipTest("PLC가 연결되지 않아 테스트를 건너뜁니다.")
            
        # 1. 후면 도어 열기
        self.assertTrue(self.plc_op.operate_door("back", "open"))
        self.assertTrue(self.plc_op.check_door_status("back"))
        
        # 2. 빈 트레이 감지
        time.sleep(1)
        self.assertFalse(self.plc_op.check_item_sensor())
        
        # 3. 전면 도어 열기
        self.assertTrue(self.plc_op.operate_door("front", "open"))
        
        # 4. 물품 감지 대기
        time.sleep(1)
        self.assertTrue(self.plc_op.check_item_sensor())
        
        # 5. 물품 정보 읽기
        item_info = self.plc_op.get_item_info()
        self.assertGreater(item_info["height"], 0)
        self.assertGreater(item_info["weight"], 0)
        
        # 6. 전면 도어 닫기
        self.assertTrue(self.plc_op.operate_door("front", "close"))

    def test_output_operation(self):
        """불출 작업 테스트"""
        if not self.plc_connected:
            self.skipTest("PLC가 연결되지 않아 테스트를 건너뜁니다.")
            
        # 1. 로봇 이동하여 물품 가져오기
        self.assertTrue(self.plc_op.move_robot(10, 20))
        
        # 2. 전면 도어 열기
        self.assertTrue(self.plc_op.operate_door("front", "open"))
        
        # 3. 물품 감지 확인
        self.assertTrue(self.plc_op.check_item_sensor())
        
        # 4. 물품 제거 대기
        time.sleep(5)
        self.assertFalse(self.plc_op.check_item_sensor())
        
        # 5. 전면 도어 닫기
        self.assertTrue(self.plc_op.operate_door("front", "close"))

    def test_sort_operation(self):
        """정리 작업 테스트"""
        if not self.plc_connected:
            self.skipTest("PLC가 연결되지 않아 테스트를 건너뜁니다.")
            
        # 1. 현재 위치에서 목표 위치로 로봇 이동
        self.assertTrue(self.plc_op.move_robot(30, 40))
        
        # 2. 물품 이동 후 센서 확인
        self.assertTrue(self.plc_op.check_item_sensor())
        
        # 3. 새로운 위치로 이동
        self.assertTrue(self.plc_op.move_robot(50, 60))
        
        # 4. 최종 위치 도달 확인
        time.sleep(1)
        current_pos = self.plc_op.plc.batchread_wordunits(headdevice="D5500", readsize=2)
        self.assertEqual(current_pos[0], 50)  # X축
        self.assertEqual(current_pos[1], 60)  # Z축

    def tearDown(self):
        """테스트 종료 시 PLC 연결 해제"""
        if self.plc_connected:
            try:
                # 모든 도어 닫기
                self.plc_op.operate_door("front", "close")
                self.plc_op.operate_door("back", "close")
                # PLC 연결 종료
                self.plc_op.plc.close()
            except:
                pass

if __name__ == '__main__':
    unittest.main() 