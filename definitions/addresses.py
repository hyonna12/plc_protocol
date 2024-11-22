class RobotAddresses:
    """로봇 메모리 주소 정의"""
    
    FRONT = {
        'command': 5500,       # 명령 레지스터
        'done': 5000,          # 완료 레지스터
        
        'x_position': 5520,    # X축 위치 이동값 (D5520-D5021)
        'x_speed': 5522,       # X축 속도값 (D5522-D5023)
        'z_position': 5524,    # Z축 위치 이동값 (D5524-D5025)
        'z_speed': 5526,       # Z축 속도값 (D5526-D5027)
        
        'x_current': 5020,     # X축 현재 위치 (D5020-D5021)
        'z_current': 5022,     # Z축 현재 위치 (D5022-D5023)
    }
    
    REAR = {
        'command': 5501,       # 명령 레지스터
        'done': 5001,          # 완료 레지스터
        
        'x_position': 5530,    # X축 위치 이동값 (D5530-D5031)
        'x_speed': 5532,       # X축 속도값 (D5532-D5033)   
        'z_position': 5534,    # Z축 위치 이동값 (D5534-D5035)
        'z_speed': 5536,       # Z축 속도값 (D5536-D5037)
        
        'x_current': 5030,     # X축 현재 위치 (D5030-D5031)
        'z_current': 5032,     # Z축 현재 위치 (D5032-D5033)
    }

class DoorAddresses:
    """도어 메모리 주소 정의"""
    COMMAND = 5502  # 도어 명령 레지스터
    DONE = 5002     # 도어 완료 레지스터

class SystemAddresses:
    """시스템 제어 메모리 주소 정의"""
    COMMAND = 5503  # 시스템 명령 레지스터
    STATUS = 5003   # 시스템 상태 레지스터