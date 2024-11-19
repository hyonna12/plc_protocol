from mc.base.controller import BaseController
from mc.definitions.commands import RobotCommands
from mc.definitions.addresses import RobotAddresses
from mc.conn.connection import PLCConnection
import time

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
        """위치와 속도 값 쓰기 (32비트)"""
        try:
            print(f"\n[{self.robot_name}] === 위치/속도 값 쓰기 시작 ===")
            
            # 32비트 값을 16비트씩 분할
            position_low = position & 0xFFFF          # 하위 16비트
            position_high = (position >> 16) & 0xFFFF # 상위 16비트
            speed_low = speed & 0xFFFF                # 하위 16비트
            speed_high = (speed >> 16) & 0xFFFF       # 상위 16비트
            
            if position_low > 32767:
                position_low -= 65536  # signed 변환 (음수 처리)
            if position_high > 32767:
                position_high -= 65536  # signed 변환 (음수 처리)
            if speed_low > 32767:
                speed_low -= 65536  # signed 변환 (음수 처리)
            if speed_high > 32767:
                speed_high -= 65536  # signed 변환 (음수 처리)

            print(f"[{self.robot_name}] 위치 값 분할:")
            print(f"  - 32비트 값: {position} (0x{position:08X})")
            print(f"  - D{position_addr} (하위 워드): {position_low} (0x{position_low:04X})")
            print(f"  - D{position_addr+1} (상위 워드): {position_high} (0x{position_high:04X})")
            
            # 위치 값 쓰기 (연속된 2개 워드)
            print(f"\n[{self.robot_name}] 위치 값 쓰기 시도 (D{position_addr}-D{position_addr+1})...")
            if not PLCConnection.write_word(position_addr, [position_low, position_high]):
                print(f"[{self.robot_name}] 위치 값 쓰기 실패")
                return False
            print(f"[{self.robot_name}] 위치 값 쓰기 성공")
            
            print(f"\n[{self.robot_name}] 속도 값 분할:")
            print(f"  - 32비트 값: {speed} (0x{speed:08X})")
            print(f"  - D{speed_addr} (하위 워드): {speed_low} (0x{speed_low:04X})")
            print(f"  - D{speed_addr+1} (상위 워드): {speed_high} (0x{speed_high:04X})")
            
            # 속도 값 쓰기 (연속된 2개 워드)
            print(f"\n[{self.robot_name}] 속도 값 쓰기 시도 (D{speed_addr}-D{speed_addr+1})...")
            if not PLCConnection.write_word(speed_addr, [speed_low, speed_high]):
                print(f"[{self.robot_name}] 속도 값 쓰기 실패")
                return False
            print(f"[{self.robot_name}] 속도 값 쓰기 성공")
            
            print(f"\n[{self.robot_name}] === 위치/속도 값 쓰기 완료 ===")
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
        
        # 1. 위치/속도 값 쓰기
        if not self._write_position_speed(
            self.addresses['x_position'],
            self.addresses['x_speed'],
            position,
            speed
        ):
            print(f"[{self.robot_name}] 위치/속도 값 쓰기 실패")
            return False
        
        # print(f"[{self.robot_name}] 위치/속도 값 쓰기 완료, 1초 대기...")
        # time.sleep(1)  # 0.5초 대기
        
        # 2. X축 이동 명령 비트 설정
        print(f"[{self.robot_name}] X축 이동 명령 비트 설정 시도...")
        if not self._set_bit(self.addresses['command'], RobotCommands.X_AXIS_MOVE, True):
            print(f"[{self.robot_name}] X축 이동 명령 비트 설정 실패")
            return False
        
        # 3. 완료 신호 대기
        print(f"[{self.robot_name}] X축 이동 완료 신호 대기...")
        result = self.wait_for_bit(self.addresses['done'], RobotCommands.X_AXIS_MOVE)
        if not result:
            print(f"[{self.robot_name}] X축 이동 완료 신호 대기 시간 초과")
        
        # 4. 명령 비트 리셋
        print(f"\n[{self.robot_name}] 명령 비트 리셋...")
        if not self.reset_command(self.addresses['command']):
            print(f"[{self.robot_name}] 명령 비트 리셋 실패")
        return result
    
    def z_axis_move(self, position, speed):
        """Z축 이동 지령"""
        print(f"\n[{self.robot_name}] === Z축 이동 명령 시작 ===")
        print(f"[{self.robot_name}] 목표: 위치={position/1000.0}mm, 속도={speed/1000.0}mm/s")
        
        # 1. 위치/속도 값 쓰기
        if not self._write_position_speed(
            self.addresses['z_position'],
            self.addresses['z_speed'],
            position,
            speed
        ):
            print(f"[{self.robot_name}] 위치/속도 값 쓰기 실패")
            return False
        
        # print(f"\n[{self.robot_name}] 위치/속도 값 쓰기 완료, 0.5초 대기...")
        # time.sleep(0.5)  # 0.5초 대기
        
        # 2. Z축 이동 명령 비트 설정
        print(f"\n[{self.robot_name}] Z축 이동 명령 비트 설정 시도...")
        if not self._set_bit(self.addresses['command'], RobotCommands.Z_AXIS_MOVE, True):
            print(f"[{self.robot_name}] Z축 이동 명령 비트 설정 실패")
            return False
        print(f"[{self.robot_name}] Z축 이동 명령 비트 설정 성공")
        
        # 3. 완료 신호 대기
        print(f"\n[{self.robot_name}] Z축 이동 완료 신호 대기...")
        result = self.wait_for_bit(self.addresses['done'], RobotCommands.Z_AXIS_MOVE)
        if not result:
            print(f"[{self.robot_name}] Z축 이동 완료 신호 대기 시간 초과")
        else:
            print(f"[{self.robot_name}] Z축 이동 완료 신호 수신")
        
        # 4. 명령 비트 리셋
        print(f"\n[{self.robot_name}] 명령 비트 리셋...")
        if not self.reset_command(self.addresses['command']):
            print(f"[{self.robot_name}] 명령 비트 리셋 실패")
        return result
    
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

    def get_x_position(self):
        """X축 현재 위치 읽기 (단위: 0.001mm)"""
        addr = self.addresses['x_current']
        result = PLCConnection.read_word(addr, 2)  # 32비트 값을 읽기 위해 2워드 읽음
        if result:
            # 하위워드와 상위워드를 32비트 값으로 조합
            position = (result[1] << 16) | result[0]
            return position
        return None

    def get_z_position(self):
        """Z축 현재 위치 읽기 (단위: 0.001mm)"""
        addr = self.addresses['z_current']
        result = PLCConnection.read_word(addr, 2)  # 32비트 값을 읽기 위해 2워드 읽음
        if result:
            # 하위워드와 상위워드를 32비트 값으로 조합
            position = (result[1] << 16) | result[0]
            return position
        return None

