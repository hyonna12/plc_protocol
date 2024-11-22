import pymcprotocol
from typing import List, Optional
from config.config import load_config

class PLCConnection:
    """PLC 연결 관리 클래스 (싱글톤)"""
    _instance: Optional['PLCConnection'] = None
    _plc = None
    _connected = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PLCConnection, cls).__new__(cls)
        return cls._instance
    
    @classmethod
    def initialize(cls) -> bool:
        """PLC 연결 초기화"""
        plc_config = load_config()
        host = plc_config['host']
        port = plc_config['port']
        
        if cls._plc is None:
            cls._plc = pymcprotocol.Type3E()
            cls._plc.setaccessopt(commtype="ascii")
            
        if not cls._connected:
            try:
                cls._plc.connect(host, port)
                cls._connected = True
                print(f"PLC 연결 성공: {host}:{port}")
                return True
            except Exception as e:
                print(f"PLC 연결 실패: {str(e)}")
                cls._connected = False
                return False
        return True
    
    @classmethod
    def disconnect(cls):
        """PLC 연결 해제"""
        if cls._plc and cls._connected:
            try:
                cls._plc.close()
                print("PLC 연결 종료")
            except Exception as e:
                print(f"PLC 연결 해제 실패: {str(e)}")
            finally:
                cls._connected = False
                cls._plc = None

    @classmethod
    def read_word(cls, addr: int, size: int = 1) -> Optional[List[int]]:
        """워드 단위 읽기
        Args:
            addr: 시작 주소
            size: 읽을 워드 수
        Returns:
            Optional[List[int]]: 읽은 값 리스트, 실패시 None
        """
        if not cls._connected or not cls._plc:
            print("PLC가 연결되지 않음")
            return None
            
        try:
            values = cls._plc.batchread_wordunits(f"D{addr}", size)
            return values
        except Exception as e:
            print(f"워드 읽기 실패 (D{addr}, {size}개): {str(e)}")
            return None

    @classmethod
    def write_word(cls, addr: int, values: List[int]) -> bool:
        """워드 단위 쓰기
        Args:
            addr: 시작 주소
            values: 쓸 값 리스트
        Returns:
            bool: 성공 여부
        """
        if not cls._connected or not cls._plc:
            print("PLC가 연결되지 않음")
            return False
        
        try:
            # 2워드를 한 번에 쓰기
            cls._plc.batchwrite_wordunits(f"D{addr}", values)
            return True
        except Exception as e:
            print(f"워드 쓰기 실패 (D{addr}): {str(e)}")
            return False

    @classmethod
    def write_bits(cls, addr: int, bit_positions: List[int], values: List[bool]) -> bool:
        """특정 워드의 여러 비트 설정
        Args:
            addr: 워드 주소
            bit_positions: 비트 위치 리스트 (0-15)
            values: 비트 값 리스트 (True/False)
        Returns:
            bool: 성공 여부
        """
        if len(bit_positions) != len(values):
            print("비트 위치와 값의 개수가 일치하지 않음")
            return False
            
        # 현재 워드 값 읽기
        current = cls.read_word(addr)
        if current is None:
            return False
            
        word_value = current[0]
        
        # 비트 설정
        for pos, val in zip(bit_positions, values):
            if val:
                word_value |= (1 << pos)
            else:
                word_value &= ~(1 << pos)
                
        # 수정된 워드 값 쓰기
        return cls.write_word(addr, [word_value])

    @classmethod
    def read_bits(cls, addr: int, bit_positions: List[int]) -> Optional[List[bool]]:
        """특정 워드의 여러 비트 읽기
        Args:
            addr: 워드 주소
            bit_positions: 비트 위치 리스트 (0-15)
        Returns:
            Optional[List[bool]]: 비트 값 리스트, 실패시 None
        """
        # 워드 값 읽기
        result = cls.read_word(addr)
        if result is None:
            return None
            
        word_value = result[0]
        
        # 비트 값 추출
        return [(word_value & (1 << pos)) != 0 for pos in bit_positions]

    @classmethod
    def is_connected(cls) -> bool:
        """연결 상태 확인"""
        return cls._connected