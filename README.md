# plc_protocol


##modbus
###goburrow
Read Input Registers (FC 04)
읽기 전용 16비트 레지스터 읽기
주로 아날로그 입력값 읽을 때 사용
예: 온도센서, 압력센서 값 읽기
Read Holding Registers (FC 03)
읽기/쓰기 가능한 16비트 레지스터 읽기
가장 일반적으로 사용
예: D 디바이스 메모리 읽기

Write Single Register (FC 06)
단일 16비트 레지스터 쓰기
하나의 워드 값 설정
예: 단일 D 레지스터 값 쓰기
Write Multiple Registers (FC 16)
여러 개의 16비트 레지스터 동시 쓰기
연속된 여러 워드 값 설정
예: 여러 D 레지스터 동시 쓰기

Read/Write Multiple Registers (FC 23)
한 번의 통신으로 읽기와 쓰기 동시 수행
통신 효율성 향상
예: 상태 읽으면서 동시에 명령 보내기
Mask Write Register (FC 22)
레지스터의 특정 비트만 수정
AND와 OR 마스크 사용
예: 16비트 중 특정 비트만 변경할 때
Read FIFO Queue (FC 24)
FIFO(First In First Out) 큐 데이터 읽기
순차적 데이터 처리
예: 로깅 데이터 수집