from mc.base.controller import BaseController
from mc.definitions.commands import SystemCommands
from mc.definitions.addresses import SystemAddresses

class SystemController(BaseController):
    """시스템 제어 클래스"""
    
    def __init__(self, host="192.168.0.10", port=5000):
        super().__init__(host, port)
        
    def _send_system_command(self, command_bit):
        """시스템 명령 전송 및 완료 대기"""
        print(f"명령 레지스터 주소: D{SystemAddresses.COMMAND}")
        print(f"상태 레지스터 주소: D{SystemAddresses.STATUS}")
        print(f"명령 비트: {command_bit}")
        
        if self._set_bit(SystemAddresses.COMMAND, command_bit, True):
            print(f"명령 비트 {command_bit} 설정 성공")
            result = self.wait_for_bit(SystemAddresses.STATUS, command_bit)
            if result:
                print(f"명령 완료 신호 수신")
            else:
                print(f"명령 완료 신호 대기 시간 초과")
            self._set_bit(SystemAddresses.COMMAND, command_bit, False)
            return result
        print(f"명령 비트 {command_bit} 설정 실패")
        return False
        
    def ready(self):
        """운전 준비"""
        print("운전 준비 요청...")
        return self._send_system_command(SystemCommands.READY)
        
    def start(self):
        """운전 시작"""
        print("운전 시작 요청...")
        
        # 현재 상태 비트 확인
        current_status = self._check_bit(SystemAddresses.STATUS, SystemCommands.START)
        print(f"현재 상태 비트: {current_status}")
        
        # 명령 비트 설정
        print(f"명령 레지스터(D{SystemAddresses.COMMAND})의 {SystemCommands.START}번 비트 설정 시도...")
        if not self._set_bit(SystemAddresses.COMMAND, SystemCommands.START, True):
            print("운전 시작 명령 비트 설정 실패")
            return False
        print("운전 시작 명령 비트 설정 성공")
        
        # 완료 신호 대기
        print(f"상태 레지스터(D{SystemAddresses.STATUS})의 {SystemCommands.START}번 비트 대기...")
        result = self.wait_for_bit(SystemAddresses.STATUS, SystemCommands.START)
        if not result:
            print("운전 시작 완료 신호 대기 시간 초과")
        else:
            print("운전 시작 완료 신호 수신")
        
        # 완료 후 상태 확인
        current_status = self._check_bit(SystemAddresses.STATUS, SystemCommands.START)
        print(f"완료 후 상태 비트: {current_status}")
        
        # 명령 비트 리셋
        print("명령 비트 리셋...")
        self._set_bit(SystemAddresses.COMMAND, SystemCommands.START, False)
        return result
        
    def stop(self):
        """운전 정지"""
        print("운전 정지 요청...")
        return self._send_system_command(SystemCommands.STOP)
        
    # def emergency_stop(self):
    #     """비상 정지"""
    #     print("비상 정지 요청...")
    #     # 비상정지는 즉시 실행되어야 하므로 응답 대기 없이 신호만 전송
    #     if self._set_bit(SystemAddresses.COMMAND, SystemCommands.EMERGENCY, True):
    #         print("비상 정지 신호 전송 완료")
    #         return True
    #     print("비상 정지 신호 전송 실패")
    #     return False