package main

import (
    "fmt"
    "github.com/simonvetter/modbus"
    "log"
    "time"
)

// D디바이스 주소를 Modbus 주소로 변환
func convertDToModbus(dAddr uint16) uint16 {
    return dAddr
}

func main() {
    client, err := modbus.NewClient(&modbus.ClientConfiguration{
        URL:      "tcp://192.168.0.10:502",
        Timeout:  10 * time.Second,
    })

    if err != nil {
        log.Fatal("클라이언트 생성 실패:", err)
    }

    err = client.Open()
    if err != nil {
        log.Fatal("연결 실패:", err)
    }
    defer client.Close()

    // D5000 읽기
    dAddress := uint16(5000)
    modbusAddress := convertDToModbus(dAddress)
    
    value, err := client.ReadRegister(modbusAddress, modbus.HOLDING_REGISTER)
    if err != nil {
        log.Fatal("D5000 읽기 실패:", err)
    }
    fmt.Printf("D%d (Modbus 주소: %d) 값: %d (0x%04X)\n", 
        dAddress, modbusAddress, value, value)
}
