import pymcprotocol

def main():
    # PLC 연결 정보
    HOST = '192.168.0.10'  # PLC IP 주소
    PORT = 5000           # MC 프로토콜 포트

    # pyMCProtocol 객체 생성 (타입 3E)
    plc = pymcprotocol.Type3E()
    
    try:
        # PLC 연결
        plc.connect(HOST, PORT)
        print(f"PLC 연결 성공: {HOST}:{PORT}")

        # 1. D5000에서 1워드 읽기
        value = plc.read_word('D5000', 1)
        print(f"D5000 1워드 읽기 결과: {value[0]} (0x{value[0]:04X})")

        # 2. D5000에서 2워드 읽기
        values = plc.read_word('D5000', 2)
        print(f"D5000-D5001 2워드 읽기 결과: {values} (0x{values[0]:04X}, 0x{values[1]:04X})")

        # 3. 단일 워드 쓰기 예제
        write_value = 12345
        plc.write_word('D5000', [write_value])
        print(f"D5000에 값 {write_value} 쓰기 완료")

        # 4. 여러 워드 쓰기 예제
        write_values = [11111, 22222]
        plc.write_word('D5000', write_values)
        print(f"D5000부터 {len(write_values)}개 워드 쓰기 완료")

    except Exception as e:
        print(f"에러 발생: {str(e)}")
    
    finally:
        # PLC 연결 종료
        plc.close()
        print("PLC 연결 종료")

if __name__ == "__main__":
    main() 


# python mc/pymcprotocol_example.py