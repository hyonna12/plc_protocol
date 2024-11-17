import socket
import binascii

class MCProtocol:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = None

    def connect(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            print(f"PLC 연결 성공: {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"PLC 연결 실패: {str(e)}")
            return False

    def disconnect(self):
        if self.sock:
            self.sock.close()
            print("PLC 연결 종료")

    def read_word(self, device, address, length=1):
        """
        D디바이스에서 워드 단위로 읽기 (ASCII 모드)
        device: 디바이스 코드 (예: 'D')
        address: 시작 주소
        length: 읽을 워드 수
        """
        # 커맨드 생성
        command = f"5000FF03FF000A00" # 헤더
        command += "0401"              # 읽기 명령
        command += "0000"              # 서브 커맨드
        command += f"{address:06X}"    # 디바이스 주소 (16진수 6자리)
        command += f"{length:04X}"     # 읽을 개수 (16진수 4자리)
        
        try:
            # 요청 전송
            self.sock.send(command.encode())
            
            # 응답 수신
            response = self.sock.recv(2048).decode()
            
            # 응답 처리
            if len(response) > 0:
                # 정상 응답 확인 (에러 코드 "0000")
                if response[18:22] == "0000":
                    # 데이터 부분 추출 (헤더 22바이트 이후)
                    data = response[22:]
                    values = []
                    # 4자리씩 끊어서 처리 (1워드 = 4자리 ASCII)
                    for i in range(0, len(data), 4):
                        value = int(data[i:i+4], 16)
                        values.append(value)
                    return values
                else:
                    print(f"에러 코드: {response[18:22]}")
            return None
        except Exception as e:
            print(f"읽기 실패: {str(e)}")
            return None

def main():
    # PLC 연결 정보
    HOST = '192.168.0.10'  # PLC IP 주소
    PORT = 5000           # MC 프로토콜 포트 (보통 5001)

    # MC 프로토콜 객체 생성 및 연결
    plc = MCProtocol(HOST, PORT)
    if not plc.connect():
        return

    try:
        # 1. D5000에서 1워드 읽기
        result = plc.read_word('D', 5000, 1)
        if result:
            print(f"D5000 1워드 읽기 결과: {result[0]} (0x{result[0]:04X})")

        # 2. D5000에서 2워드 읽기
        result = plc.read_word('D', 5000, 2)
        if result:
            print(f"D5000-D5001 2워드 읽기 결과: {result} (0x{result[0]:04X}, 0x{result[1]:04X})")

    finally:
        plc.disconnect()

if __name__ == "__main__":
    main()


# python mc/main.py