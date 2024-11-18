import pymcprotocol # type: ignore

def main():
    # MC 프로토콜 클라이언트 생성 (3E 프레임)
    pymc3e = pymcprotocol.Type3E()
    
    # ASCII 모드 설정
    pymc3e.setaccessopt(commtype="ascii")
    
    # PLC 연결
    try:
        pymc3e.connect("192.168.0.10", 5000)
        print("PLC 연결 성공 (ASCII 모드)")
        
        # D5000 영역 읽기 (20개)
        print("\n=== D5000 영역 읽기 결과 ===")
        values = pymc3e.batchread_wordunits(headdevice="D5000", readsize=20)
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
        value16 = 1234  # 16비트 값
        pymc3e.batchwrite_wordunits(headdevice="D5510", values=[value16])
        
        print(f"\n=== D5510에 1워드 값 쓰기 완료 ===")
        print(f"D5510: {value16} (DEC)")
        
        # 쓴 값 확인
        value = pymc3e.batchread_wordunits(headdevice="D5510", readsize=1)[0]
        print(f"D5510 확인: {value} (DEC)")
        
    except Exception as e:
        print(f"에러 발생: {e}")
    
    finally:
        # 연결 종료
        pymc3e.close()
        print("\n연결 종료")

if __name__ == "__main__":
    main()


# python mc/pymcprotocol.py