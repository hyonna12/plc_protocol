from ..base.controller import BaseController
from ..definitions.commands import SystemCommands
from ..definitions.addresses import SystemAddresses

class SystemController(BaseController):
    """시스템 제어 클래스"""
    
    def __init__(self, host="192.168.0.10", port=5000):
        super().__init__(host, port)
        
    def _send_system_command(self, command_bit):
        """시스템 명령 전송 및 완료 대기"""
        if self._set_bit(SystemAddresses.COMMAND, command_bit, True):
            result = self.wait_for_bit(SystemAddresses.STATUS, command_bit)
            self._set_bit(SystemAddresses.COMMAND, command_bit, False)
            return result
        return False
        
    def ready(self):
        """운전 준비"""
        print("운전 준비 요청...")
        return self._send_system_command(SystemCommands.READY)
        
    def start(self):
        """운전 시작"""
        print("운전 시작 요청...")
        return self._send_system_command(SystemCommands.START)
        
    def stop(self):
        """운전 정지"""
        print("운전 정지 요청...")
        return self._send_system_command(SystemCommands.STOP)
        
    def emergency_stop(self):
        """비상 정지"""
        print("비상 정지 요청...")
        # 비상정지는 즉시 실행되어야 하므로 응답 대기 없이 신호만 전송
        if self._set_bit(SystemAddresses.COMMAND, SystemCommands.EMERGENCY, True):
            print("비상 정지 신호 전송 완료")
            return True
        print("비상 정지 신호 전송 실패")
        return False