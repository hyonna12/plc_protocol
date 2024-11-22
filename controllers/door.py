from base.controller import BaseController
from definitions.commands import DoorCommands
from definitions.addresses import DoorAddresses

class DoorController(BaseController):
    """도어 제어 클래스"""
    
    def __init__(self):
        super().__init__()
        self.command_register = 0

    def _send_door_command(self, command_bit):
        """도어 명령 전송 및 완료 대기"""
        if self._set_bit(DoorAddresses.COMMAND, command_bit, True):
            result = self.wait_for_bit(DoorAddresses.DONE, command_bit)
            self._set_bit(DoorAddresses.COMMAND, command_bit, False)  # 명령 비트 리셋
            return result
        return False

    # 도어 제어 명령들
    def in_door_open(self):
        """In Door Open"""
        print("In Door Open 명령 전송")
        return self._send_door_command(DoorCommands.IN_DOOR_OPEN)

    def in_door_close(self):
        """In Door Close"""
        print("In Door Close 명령 전송")
        return self._send_door_command(DoorCommands.IN_DOOR_CLOSE)

    def out_door_open(self):
        """Out Door Open"""
        print("Out Door Open 명령 전송")
        return self._send_door_command(DoorCommands.OUT_DOOR_OPEN)

    def out_door_close(self):
        """Out Door Close"""
        print("Out Door Close 명령 전송")
        return self._send_door_command(DoorCommands.OUT_DOOR_CLOSE)

    def robot_door1_open(self):
        """Robot Door#1 Open"""
        print("Robot Door#1 Open 명령 전송")
        return self._send_door_command(DoorCommands.ROBOT_DOOR1_OPEN)

    def robot_door1_close(self):
        """Robot Door#1 Close"""
        print("Robot Door#1 Close 명령 전송")
        return self._send_door_command(DoorCommands.ROBOT_DOOR1_CLOSE)

    def robot_door2_open(self):
        """Robot Door#2 Open"""
        print("Robot Door#2 Open 명령 전송")
        return self._send_door_command(DoorCommands.ROBOT_DOOR2_OPEN)

    def robot_door2_close(self):
        """Robot Door#2 Close"""
        print("Robot Door#2 Close 명령 전송")
        return self._send_door_command(DoorCommands.ROBOT_DOOR2_CLOSE)

    def handler_trigger_f(self):
        """핸들러 바코드 Trigger F"""
        print("핸들러 바코드 Trigger F 명령 전송")
        return self._send_door_command(DoorCommands.HANDLER_TRIGGER_F)

    def handler_trigger_r(self):
        """핸들러 바코드 Trigger R"""
        print("핸들러 바코드 Trigger R 명령 전송")
        return self._send_door_command(DoorCommands.HANDLER_TRIGGER_R) 