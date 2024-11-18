from ..base.controller import BaseController
from ..definitions.commands import RobotCommands
from ..definitions.addresses import RobotAddresses
from ..communication.connection import PLCConnection

class RobotController(BaseController):
    """로봇 제어 클래스"""
    
    def __init__(self, host="192.168.0.10", port=5000, is_front=True):
        """
        Args:
            host: PLC IP 주소
            port: PLC 포트 번호
            is_front: True=전면 로봇, False=후면 로봇
        """
        super().__init__(host, port)
        self.is_front = is_front
        self.addresses = RobotAddresses.FRONT if is_front else RobotAddresses.REAR
        self.robot_name = "FRONT" if is_front else "REAR"

    def _write_position_speed(self, position_addr, speed_addr, position, speed):
        """위치와 속도 값 쓰기 (32비트)
        Args:
            position_addr: 위치 값 시작 주소
            speed_addr: 속도 값 시작 주소
            position: 위치 값 (32비트)
            speed: 속도 값 (32비트)
        """
        try:
            # 32비트 값을 상위/하위 워드로 분할
            position_low = position & 0xFFFF
            position_high = (position >> 16) & 0xFFFF
            speed_low = speed & 0xFFFF
            speed_high = (speed >> 16) & 0xFFFF
            
            # 위치 값 쓰기 (연속된 2개 워드)
            if not PLCConnection.write_word(position_addr, [position_low, position_high]):
                return False
            
            # 속도 값 쓰기 (연속된 2개 워드)
            if not PLCConnection.write_word(speed_addr, [speed_low, speed_high]):
                return False
            
            return True
        except Exception as e:
            print(f"[{self.robot_name}] 위치/속도 설정 실패: {str(e)}")
            return False

    def x_axis_move(self, position, speed):
        """X축 이동 지령
        Args:
            position: 이동할 위치 값 (0.001mm 단위)
                     예) 10mm = 10000, 100mm = 100000
            speed: 이동 속도 값 (0.001mm/s 단위)
                  예) 10mm/s = 10000
        """
        print(f"[{self.robot_name}] X축 이동 명령 전송 (위치: {position/1000.0}mm, 속도: {speed/1000.0}mm/s)")
        if self._write_position_speed(
            self.addresses['x_position'],
            self.addresses['x_speed'],
            position,
            speed
        ):
            if self._set_bit(self.addresses['command'], RobotCommands.X_AXIS_MOVE, True):
                result = self.wait_for_bit(self.addresses['done'], RobotCommands.X_AXIS_MOVE)
                self.reset_command(self.addresses['command'])
                return result
        return False
    
    def z_axis_move(self, position, speed):
        """Z축 이동 지령
        Args:
            position: 이동할 위치 값 (0.001mm 단위)
                     예) 10mm = 10000, 100mm = 100000
            speed: 이동 속도 값 (0.001mm/s 단위)
                  예) 10mm/s = 10000
        """
        print(f"[{self.robot_name}] Z축 이동 명령 전송 (위치: {position/1000.0}mm, 속도: {speed/1000.0}mm/s)")
        if self._write_position_speed(
            self.addresses['z_position'],
            self.addresses['z_speed'],
            position,
            speed
        ):
            if self._set_bit(self.addresses['command'], RobotCommands.Z_AXIS_MOVE, True):
                result = self.wait_for_bit(self.addresses['done'], RobotCommands.Z_AXIS_MOVE)
                self.reset_command(self.addresses['command'])
                return result
        return False

    def z_handler_get(self):
        """Z축 핸들러 GET 지령"""
        print(f"[{self.robot_name}] Z축 핸들러 GET 명령 전송")
        if self._set_bit(self.addresses['command'], RobotCommands.Z_HANDLER_GET, True):
            result = self.wait_for_bit(self.addresses['done'], RobotCommands.Z_HANDLER_GET)
            self.reset_command(self.addresses['command'])
            return result
        return False
    
    def z_handler_put(self):
        """Z축 핸들러 PUT 지령"""
        print(f"[{self.robot_name}] Z축 핸들러 PUT 명령 전송")
        if self._set_bit(self.addresses['command'], RobotCommands.Z_HANDLER_PUT, True):
            result = self.wait_for_bit(self.addresses['done'], RobotCommands.Z_HANDLER_PUT)
            self.reset_command(self.addresses['command'])
            return result
        return False
    
    def z_handler_rotate_home(self):
        """Z축 핸들러 회전 원위치 지령"""
        print(f"[{self.robot_name}] Z축 핸들러 회전 원위치 명령 전송")
        if self._set_bit(self.addresses['command'], RobotCommands.Z_HANDLER_ROT_HOME, True):
            result = self.wait_for_bit(self.addresses['done'], RobotCommands.Z_HANDLER_ROT_HOME)
            self.reset_command(self.addresses['command'])
            return result
        return False
    
    def z_handler_rotate(self):
        """Z축 핸들러 회전 지령"""
        print(f"[{self.robot_name}] Z축 핸들러 회전 명령 전송")
        if self._set_bit(self.addresses['command'], RobotCommands.Z_HANDLER_ROT, True):
            result = self.wait_for_bit(self.addresses['done'], RobotCommands.Z_HANDLER_ROT)
            self.reset_command(self.addresses['command'])
            return result
        return False

