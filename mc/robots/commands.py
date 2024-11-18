class RobotCommands:
    """로봇 명령 비트 정의"""
    CMD_X_AXIS_MOVE = 0        # X축 이동 지령
    CMD_Z_AXIS_MOVE = 1        # Z축 이동 지령
    CMD_Z_HANDLER_GET = 2      # Z축 핸들러 GET 지령
    CMD_Z_HANDLER_PUT = 3      # Z축 핸들러 PUT 지령
    CMD_Z_HANDLER_ROT_HOME = 4 # Z축 핸들러 회전 원위치 지령
    CMD_Z_HANDLER_ROT = 5      # Z축 핸들러 회전 지령

class DoorCommands:
    """도어 명령 비트 정의"""
    CMD_IN_DOOR_OPEN = 0       # In Door Open 지령
    CMD_IN_DOOR_CLOSE = 1      # In Door Close 지령
    CMD_OUT_DOOR_OPEN = 2      # Out Door Open 지령
    CMD_OUT_DOOR_CLOSE = 3     # Out Door Close 지령
    CMD_ROBOT_DOOR1_OPEN = 4   # Robot Door#1 Open 지령
    CMD_ROBOT_DOOR1_CLOSE = 5  # Robot Door#1 Close 지령
    CMD_ROBOT_DOOR2_OPEN = 6   # Robot Door#2 Open 지령
    CMD_ROBOT_DOOR2_CLOSE = 7  # Robot Door#2 Close 지령
    CMD_HANDLER_TRIGGER_F = 8  # 핸들러 바코드 Trigger F
    CMD_HANDLER_TRIGGER_R = 9  # 핸들러 바코드 Trigger R