package main

import (
    "fmt"
    "github.com/goburrow/modbus"
    "log"
    "time"
)

func main() {
    // Modbus TCP 클라이언트 핸들러 생성
    handler := modbus.NewTCPClientHandler("192.168.0.10:502") // PLC의 IP 주소와 포트
    handler.Timeout = 10 * time.Second
    handler.SlaveId = 0xFF // PLC의 슬레이브 ID
    
    // 연결
    err := handler.Connect()
    if err != nil {
        log.Fatal("연결 실패:", err)
    }
    defer handler.Close()

    // 클라이언트 생성
    client := modbus.NewClient(handler)
    
    // D 디바이스에서 1워드(2바이트) 읽기
    // D0 레지스터는 보통 40001 또는 400001부터 시작
	// 4096, 40001, 5000
    address := uint16(5000) // D5000 주소
    length := uint16(1)  // 1워드 읽기
    
    results, err := client.ReadHoldingRegisters(address, length)
    if err != nil {
        log.Fatal("데이터 읽기 실패:", err)
    }

    // 결과 출력 (2바이트를 uint16으로 변환)
    if len(results) >= 2 {
        value := uint16(results[0])<<8 | uint16(results[1])
        fmt.Printf("D%d의 값: %d (0x%04X)\n", address, value, value)
    }
}
