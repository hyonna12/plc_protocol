class RobotAddresses:
    """로봇 메모리 주소 정의"""
    
    FRONT_ADDRESSES = {
        'x_position': 5520,    # X축 위치 이동값
        'x_speed': 5522,       # X축 속도값
        'z_position': 5524,    # Z축 위치 이동값
        'z_speed': 5526,       # Z축 속도값
        'command': 5500,       # 명령 레지스터
        'done': 5000,          # 완료 레지스터
    }
    
    REAR_ADDRESSES = {
        'x_position': 5530,    # X축 위치 이동값
        'x_speed': 5532,       # X축 속도값
        'z_position': 5534,    # Z축 위치 이동값
        'z_speed': 5536,       # Z축 속도값
        'command': 5501,       # 명령 레지스터
        'done': 5001,          # 완료 레지스터
    }

class DoorAddresses:
    """도어 메모리 주소 정의"""
    COMMAND = 5502  # 도어 명령 레지스터
    DONE = 5002     # 도어 완료 레지스터