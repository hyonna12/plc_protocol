from .base import RobotBase
from .commands import RobotCommands
from .addresses import RobotAddresses

class RobotController(RobotBase, RobotCommands):
    """로봇 제어 클래스"""
    
    def __init__(self, host="192.168.0.10", port=5000, is_front=True):
        super().__init__(host, port)
        self.is_front = is_front
        self.addresses = RobotAddresses.FRONT_ADDRESSES if is_front else RobotAddresses.REAR_ADDRESSES
        self.robot_name = "FRONT" if is_front else "REAR"

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
            return self._set_command_bit(self.CMD_X_AXIS_MOVE, True)
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