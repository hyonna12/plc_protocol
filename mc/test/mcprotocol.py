import pymcprotocol # type: ignore

def words(pymc3e):
    # 워드 읽기 
    print("\n=== D5520-D5521 영역 읽기 결과 ===")
    values = pymc3e.batchread_wordunits(headdevice="D5520", readsize=2)
    for i, value in enumerate(values):
        print(f"D{5520+i}: {value} (DEC) (0x{value:04X})")
    
    # 2워드(32비트) 값 설정
    value32 = 100000  # 목표 값
    
    # 32비트 값을 16비트씩 분할
    low_word = value32 & 0xFFFF          # 하위 16비트
    high_word = (value32 >> 16) & 0xFFFF # 상위 16비트
    # 16비트 형식으로 강제 변환
    low_word = int(low_word) & 0xFFFF
    high_word = int(high_word) & 0xFFFF

    # if low_word > 32767:
    #     low_word -= 65536  # signed 변환 (음수 처리)
    # if high_word > 32767:
    #     high_word -= 65536  # signed 변환 (음수 처리)

    print(f"\n=== D5520-D5521에 2워드 값 쓰기 시도 ===")
    print(f"32비트 값: {value32} (DEC) (0x{value32:08X})")
    print(f"D5520 (하위 워드): {low_word} (DEC) (0x{low_word:04X})")
    print(f"D5521 (상위 워드): {high_word} (DEC) (0x{high_word:04X})")
    
    # D5520-D5521에 2워드 값 쓰기
    pymc3e.batchwrite_wordunits(headdevice="D5520", values=[low_word, high_word])
    
    print(f"\n=== D5520-D5521에 2워드 값 쓰기 완료 ===")
    print(f"32비트 값: {value32} (DEC)")
    print(f"D5520 (하위 워드): {low_word} (DEC)")
    print(f"D5521 (상위 워드): {high_word} (DEC)")
    
    # 쓴 값 확인
    values = pymc3e.batchread_wordunits(headdevice="D5520", readsize=2)
    print("\n=== 쓰기 후 확인 ===")
    for i, value in enumerate(values):
        print(f"D{5520+i}: {value} (DEC) (0x{value:04X})")
    
    # D5510에 1워드 값 쓰기 (16비트)
    # value16 = 5678  # 16비트 값
    # pymc3e.batchwrite_wordunits(headdevice="D5510", values=[value16])
    
    # print(f"\n=== D5510에 1워드 값 쓰기 완료 ===")
    # print(f"D5510: {value16} (DEC)")
    
    # # 쓴 값 확인
    # value = pymc3e.batchread_wordunits(headdevice="D5510", readsize=1)[0]
    # print(f"D5510 확인: {value} (DEC)")
    

def bits(pymc3e):
    # 비트 읽기
    print("\n=== D5500 비트 상태 읽기 ===")
    # 워드 값을 읽어서 비트 상태 확인
    word_value = pymc3e.batchread_wordunits(headdevice="D5500", readsize=1)[0]
    print("변경 전 워드 값:", word_value)
    
    for bit in range(16):
        bit_value = (word_value >> bit) & 1
        print(f"D5500.{bit}: {bit_value}")
        
    # D5500의 0번 비트를 1로 변경
    print("\n=== D5500.0 비트를 1로 변경 ===")
    
    # 0번 비트를 1로 설정 (OR 연산 사용)
    new_value = word_value | (1 << 0)  # 0번 비트를 1로 설정
    pymc3e.batchwrite_wordunits(headdevice="D5500", values=[new_value])
    print("D5500.0 비트를 1로 설정")
    
    # 변경 후 상태 확인
    print("\n=== 변경 후 D5500 비트 상태 ===")
    word_value = pymc3e.batchread_wordunits(headdevice="D5500", readsize=1)[0]
    print("변경 후 워드 값:", word_value)
    
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
        
        words(pymc3e)  # 워드 테스트 실행
        # bits(pymc3e)  # 비트 테스트 실행
        
    except Exception as e:
        print(f"에러 발생: {e}")
    
    finally:
        # 연결 종료
        pymc3e.close()
        print("\n연결 종료")

if __name__ == "__main__":
    main()


# python3 mcprotocol.py