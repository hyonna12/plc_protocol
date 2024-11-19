from ..conn.connection import PLCConnection
import time

class BaseController:
    """모든 컨트롤러의 기본 클래스"""
    
    def __init__(self, host="192.168.0.10", port=5000):
        """
        Args:
            host: PLC IP 주소
            port: PLC 포트 번호
        """
        self.command_register = 0
        self.host = host
        self.port = port
        
    def connect(self):
        """PLC 연결"""
        return PLCConnection.initialize(self.host, self.port)
    
    def disconnect(self):
        """PLC 연결 해제"""
        PLCConnection.disconnect()

    def reset_command(self, command_addr):
        """모든 명령 비트 리셋"""
        self.command_register = 0
        return PLCConnection.write_bits(command_addr, [0], [False])

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