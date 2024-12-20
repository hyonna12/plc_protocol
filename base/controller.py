from conn.connection import PLCConnection
import time
from config.config import load_config

class BaseController:
    """모든 컨트롤러의 기본 클래스"""
    
    def __init__(self):
        """
        Args:
            host: PLC IP 주소
            port: PLC 포트 번호
        """
        
        plc_config = load_config()
        self.host = plc_config['host']
        self.port = plc_config['port']
        
    def connect(self):
        """PLC 연결"""
        return PLCConnection.initialize(self.host, self.port)
    
    def disconnect(self):
        """PLC 연결 해제"""
        PLCConnection.disconnect()

    def reset_command(self, command_addr, bit_position=None):
        """명령 비트 리셋
        Args:
            command_addr: 명령 레지스터 주소
            bit_position: 리셋할 비트 위치. None이면 전체 워드 리셋
        """
        print(f"명령 레지스터(D{command_addr}) 비트 {bit_position} 리셋 시도...")
        
        if bit_position is not None:
            # 특정 비트만 리셋
            result = self._set_bit(command_addr, bit_position, False)
            if result:
                print(f"명령 비트 {bit_position} 리셋 성공")
            else:
                print(f"명령 비트 {bit_position} 리셋 실패")
            return result
        else:
            # 워드 전체 리셋
            self.command_register = 0
            result = PLCConnection.write_word(command_addr, [0])
            if result:
                print(f"명령 레지스터 전체 리셋 성공")
            else:
                print(f"명령 레지스터 전체 리셋 실패")
            return result

    def _set_bit(self, addr, bit_position, value):
        """워드의 특정 비트 설정"""
        return PLCConnection.write_bits(addr, [bit_position], [value])

    def _check_bit(self, addr, bit_position):
        """워드의 특정 비트 확인"""
        result = PLCConnection.read_bits(addr, [bit_position])
        print(f"비트 확인 - 주소: D{addr}, 비트: {bit_position}, 값: {result[0] if result else False}")
        return result[0] if result else False

    def wait_for_bit(self, addr, bit_position, timeout=30):
        """특정 비트가 ON될 때까지 대기"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self._check_bit(addr, bit_position):
                return True
            time.sleep(0.1)
        return False 