from mcprotocol import MCProtocol
import time

class RobotBase:
    """로봇 제어를 위한 기본 클래스"""
    
    def __init__(self, host="192.168.0.10", port=5000):
        self.mc = MCProtocol(host, port)
        self.command_register = 0
        
    def connect(self):
        """PLC 연결"""
        return self.mc.connect()
    
    def disconnect(self):
        """PLC 연결 해제"""
        self.mc.disconnect()

    def _write_position_speed(self, position_addr, speed_addr, position, speed):
        """위치와 속도 값 쓰기 (32비트)"""
        try:
            position_low = position & 0xFFFF
            position_high = (position >> 16) & 0xFFFF
            speed_low = speed & 0xFFFF
            speed_high = (speed >> 16) & 0xFFFF
            
            self.mc.write_word('D', position_addr, [position_low, position_high])
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