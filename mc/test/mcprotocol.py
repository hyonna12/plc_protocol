import pymcprotocol # type: ignore

def words(pymc3e):
    # 워드 읽기 
    print("\n=== D5000 영역 읽기 결과 ===")
    values = pymc3e.batchread_wordunits(headdevice="D5000", readsize=50)
    for i, value in enumerate(values):
        print(f"D{5000+i}: {value} (DEC)")
    
    # 2워드(32비트) 값 설정
    value32 = 12345678  # 목표 값
    
    # 32비트 값을 상위/하위 워드로 분할
    low_word = value32 & 0xFFFF          # 하위 16비트
    high_word = (value32 >> 16) & 0xFFFF # 상위 16비트
    
    # D5500-D5501에 2워드 값 쓰기 (32비트)
    pymc3e.batchwrite_wordunits(headdevice="D5500", values=[low_word, high_word])
    
    print(f"\n=== D5500-D5501에 2워드 값 쓰기 완료 ===")
    print(f"32비트 값: {value32} (DEC)")
    print(f"D5500 (하위 워드): {low_word} (DEC)")
    print(f"D5501 (상위 워드): {high_word} (DEC)")
    # 쓴 값 확인
    value = pymc3e.batchread_wordunits(headdevice="D5500", readsize=2)[0]
    print(f"D5500-5501 확인: {value} (DEC)")

    # D5510에 1워드 값 쓰기 (16비트)
    value16 = 5678  # 16비트 값
    pymc3e.batchwrite_wordunits(headdevice="D5510", values=[value16])
    
    print(f"\n=== D5510에 1워드 값 쓰기 완료 ===")
    print(f"D5510: {value16} (DEC)")
    
    # 쓴 값 확인
    value = pymc3e.batchread_wordunits(headdevice="D5510", readsize=1)[0]
    print(f"D5510 확인: {value} (DEC)")
    

def bits(pymc3e):
    # 비트 읽기
    print("\n=== D5500 비트 상태 읽기 ===")
    # 워드 값을 읽어서 비트 상태 확인
    word_value = pymc3e.batchread_wordunits(headdevice="D5500", readsize=1)[0]
    for bit in range(16):
        bit_value = (word_value >> bit) & 1
        print(f"D5500.{bit}: {bit_value}")
        
    # D5500의 특정 비트 쓰기 예제
    print("\n=== D5500 비트 쓰기 테스트 ===")
    
    # 현재 워드 값 읽기
    current_value = word_value
    
    # 0번 비트를 ON
    new_value = current_value | (1 << 1)
    pymc3e.batchwrite_wordunits(headdevice="D5500", values=[new_value])
    print("D5500.0 비트를 ON으로 설정")
    
    # 1번 비트를 OFF
    new_value = new_value & ~(1 << 1)
    pymc3e.batchwrite_wordunits(headdevice="D5500", values=[new_value])
    print("D5500.1 비트를 OFF로 설정")
    
    # 변경 후 상태 확인
    print("\n=== 변경 후 D5500 비트 상태 ===")
    word_value = pymc3e.batchread_wordunits(headdevice="D5500", readsize=1)[0]
    for bit in range(16):
        bit_value = (word_value >> bit) & 1
        print(f"D5500.{bit}: {bit_value}")
        
        
def main():
    # MC 프로토콜 클라이언트 생성 (3E 프레임)
    pymc3e = pymcprotocol.Type3E()
    
    # ASCII 모드 설정
    pymc3e.setaccessopt(commtype="ascii")
    
    # PLC 연결
    try:
        pymc3e.connect("192.168.0.10", 5000)
        print("PLC 연결 성공 (ASCII 모드)")
        
        # bits(pymc3e)
        words(pymc3e)
        
    except Exception as e:
        print(f"에러 발생: {e}")
    
    finally:
        # 연결 종료
        pymc3e.close()
        print("\n연결 종료")

if __name__ == "__main__":
    main()


# python3 mcprotocol.py