from mcprotocol import MCProtocol
import time

class RobotController:
    # 명령 비트 정의 (공통)
    CMD_X_AXIS_MOVE = 0        # X축 이동 지령
    CMD_Z_AXIS_MOVE = 1        # Z축 이동 지령
    CMD_Z_HANDLER_GET = 2      # Z축 핸들러 GET 지령
    CMD_Z_HANDLER_PUT = 3      # Z축 핸들러 PUT 지령
    CMD_Z_HANDLER_ROT_HOME = 4 # Z축 핸들러 회전 원위치 지령
    CMD_Z_HANDLER_ROT = 5      # Z축 핸들러 회전 지령

    # 메모리 주소 정의
    FRONT_ADDRESSES = {
        'x_position': 5520,    # X축 위치 이동값
        'x_speed': 5522,       # X축 속도값
        'z_position': 5524,    # Z축 위치 이동값
        'z_speed': 5526,       # Z축 속도값
        'command': 5500,       # 명령 레지스터
        'done': 5000,          # 완료 레지스터
    }
    
    REAR_ADDRESSES = {
        'x_position': 5530,    # X축 위치 이동값
        'x_speed': 5532,       # X축 속도값
        'z_position': 5534,    # Z축 위치 이동값
        'z_speed': 5536,       # Z축 속도값
        'command': 5501,       # 명령 레지스터
        'done': 5001,          # 완료 레지스터
    }

    def __init__(self, host="192.168.0.10", port=5000, is_front=True):
        self.mc = MCProtocol(host, port)
        self.command_register = 0
        self.is_front = is_front
        self.addresses = self.FRONT_ADDRESSES if is_front else self.REAR_ADDRESSES
        self.robot_name = "FRONT" if is_front else "REAR"
        
    def connect(self):
        """PLC 연결"""
        return self.mc.connect()
    
    def disconnect(self):
        """PLC 연결 해제"""
        self.mc.disconnect()

    def _write_position_speed(self, position_addr, speed_addr, position, speed):
        """위치와 속도 값 쓰기 (32비트)"""
        try:
            # 32비트 값을 상위/하위 워드로 분할
            position_low = position & 0xFFFF
            position_high = (position >> 16) & 0xFFFF
            speed_low = speed & 0xFFFF
            speed_high = (speed >> 16) & 0xFFFF
            
            # 위치 값 쓰기
            self.mc.write_word('D', position_addr, [position_low, position_high])
            # 속도 값 쓰기
            self.mc.write_word('D', speed_addr, [speed_low, speed_high])
            return True
        except Exception as e:
            print(f"[{self.robot_name}] 위치/속도 설정 실패: {str(e)}")
            return False

    def _set_command_bit(self, bit_position, value):
        """명령 레지스터의 특정 비트 설정"""
        try:
            if value:
                self.command_register |= (1 << bit_position)
            else:
                self.command_register &= ~(1 << bit_position)
            
            self.mc.write_word('D', self.addresses['command'], [self.command_register])
            return True
        except Exception as e:
            print(f"[{self.robot_name}] 명령 비트 설정 실패: {str(e)}")
            return False

    def _check_done_bit(self, bit_position):
        """완료 레지스터의 특정 비트 확인"""
        try:
            result = self.mc.read_word('D', self.addresses['done'], 1)
            if result:
                return (result[0] & (1 << bit_position)) != 0
            return False
        except Exception as e:
            print(f"[{self.robot_name}] 완료 비트 확인 실패: {str(e)}")
            return False

    def x_axis_move(self, position, speed):
        """X축 이동 지령
        Args:
            position: 이동할 위치 값 (0.01mm 단위)
            speed: 이동 속도 값
        """
        print(f"[{self.robot_name}] X축 이동 명령 전송 (위치: {position/100.0}mm, 속도: {speed})")
        if self._write_position_speed(
            self.addresses['x_position'],
            self.addresses['x_speed'],
            position,
            speed
        ):
            return self._set_command_bit(self.CMD_X_AXIS_MOVE, True)
        return False
    
    def z_axis_move(self, position, speed):
        """Z축 이동 지령
        Args:
            position: 이동할 위치 값 (0.01mm 단위)
            speed: 이동 속도 값
        """
        print(f"[{self.robot_name}] Z축 이동 명령 전송 (위치: {position/100.0}mm, 속도: {speed})")
        if self._write_position_speed(
            self.addresses['z_position'],
            self.addresses['z_speed'],
            position,
            speed
        ):
            return self._set_command_bit(self.CMD_Z_AXIS_MOVE, True)
        return False

    def z_handler_get(self):
        """Z축 핸들러 GET 지령"""
        print(f"[{self.robot_name}] Z축 핸들러 GET 명령 전송")
        return self._set_command_bit(self.CMD_Z_HANDLER_GET, True)
    
    def z_handler_put(self):
        """Z축 핸들러 PUT 지령"""
        print(f"[{self.robot_name}] Z축 핸들러 PUT 명령 전송")
        return self._set_command_bit(self.CMD_Z_HANDLER_PUT, True)
    
    def z_handler_rotate_home(self):
        """Z축 핸들러 회전 원위치 지령"""
        print(f"[{self.robot_name}] Z축 핸들러 회전 원위치 명령 전송")
        return self._set_command_bit(self.CMD_Z_HANDLER_ROT_HOME, True)
    
    def z_handler_rotate(self):
        """Z축 핸들러 회전 지령"""
        print(f"[{self.robot_name}] Z축 핸들러 회전 명령 전송")
        return self._set_command_bit(self.CMD_Z_HANDLER_ROT, True)
    
    def reset_command(self):
        """모든 명령 비트 리셋"""
        self.command_register = 0
        return self._set_command_bit(0, False)

    def wait_for_completion(self, command_bit, timeout=30):
        """특정 동작의 완료 대기"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self._check_done_bit(command_bit):
                self.reset_command()
                return True
            time.sleep(0.1)
        self.reset_command()
        return False

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
        # 위치: 100mm (10000), 속도: 1000
        front_robot.x_axis_move(10000, 1000)
        if front_robot.wait_for_completion(RobotController.CMD_X_AXIS_MOVE):
            print("[FRONT] X축 이동 완료")
        else:
            print("[FRONT] X축 이동 시간 초과")
        
        # REAR 로봇 Z축 이동 테스트
        # 위치: 50mm (5000), 속도: 800
        rear_robot.z_axis_move(5000, 800)
        if rear_robot.wait_for_completion(RobotController.CMD_Z_AXIS_MOVE):
            print("[REAR] Z축 이동 완료")
        else:
            print("[REAR] Z축 이동 시간 초과")
            
    finally:
        front_robot.disconnect()
        rear_robot.disconnect()

if __name__ == "__main__":
    main() 