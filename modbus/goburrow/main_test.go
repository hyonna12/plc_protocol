package main

import (
    "fmt"
    "github.com/goburrow/modbus"
    "log"
    "testing"
    "time"
)

func TestModbusFunctions(t *testing.T) {
    // Modbus TCP 클라이언트 핸들러 생성
    handler := modbus.NewTCPClientHandler("192.168.0.10:502")
    handler.Timeout = 10 * time.Second
    handler.SlaveId = 0xFF

    err := handler.Connect()
    if err != nil {
        t.Fatal("연결 실패:", err)
    }
    defer handler.Close()

    client := modbus.NewClient(handler)

    // 1. ReadInputRegisters (FC 04) - 단일 워드 읽기
    t.Run("Read Single Input Register", func(t *testing.T) {
        address := uint16(5000)
        results, err := client.ReadInputRegisters(address, 1)
        if err != nil {
            t.Fatal("입력 레지스터 읽기 실패:", err)
        }
        value := uint16(results[0])<<8 | uint16(results[1])
        fmt.Printf("D%d 입력 레지스터 값: %d (0x%04X)\n", address, value, value)
    })

    // 2. ReadHoldingRegisters (FC 03) - 2워드 읽기
    t.Run("Read Multiple Holding Registers", func(t *testing.T) {
        address := uint16(5000)
        results, err := client.ReadHoldingRegisters(address, 2) // 2워드 읽기
        if err != nil {
            t.Fatal("보유 레지스터 읽기 실패:", err)
        }
        for i := 0; i < len(results); i += 2 {
            value := uint16(results[i])<<8 | uint16(results[i+1])
            fmt.Printf("D%d 보유 레지스터 값: %d (0x%04X)\n", address+uint16(i/2), value, value)
        }
    })

    // 3. WriteSingleRegister (FC 06) - 단일 워드 쓰기
    t.Run("Write Single Register", func(t *testing.T) {
        address := uint16(5000)
        value := uint16(12345)
        _, err := client.WriteSingleRegister(address, value)
        if err != nil {
            t.Fatal("단일 레지스터 쓰기 실패:", err)
        }
        fmt.Printf("D%d에 값 %d (0x%04X) 기록 완료\n", address, value, value)
    })

    // 4. WriteMultipleRegisters (FC 16) - 2워드 쓰기
    t.Run("Write Multiple Registers", func(t *testing.T) {
        address := uint16(5000)
        values := []uint16{12345, 54321}
        data := make([]byte, len(values)*2)
        for i, v := range values {
            data[i*2] = byte(v >> 8)
            data[i*2+1] = byte(v)
        }
        _, err := client.WriteMultipleRegisters(address, uint16(len(values)), data)
        if err != nil {
            t.Fatal("다중 레지스터 쓰기 실패:", err)
        }
        fmt.Printf("D%d부터 %d개 워드 기록 완료\n", address, len(values))
    })

    // 5. ReadWriteMultipleRegisters (FC 23) - 동시 읽기/쓰기
    t.Run("Read Write Multiple Registers", func(t *testing.T) {
        readAddress := uint16(5000)
        writeAddress := uint16(5002)
        writeValues := []uint16{11111, 22222}
        writeData := make([]byte, len(writeValues)*2)
        for i, v := range writeValues {
            writeData[i*2] = byte(v >> 8)
            writeData[i*2+1] = byte(v)
        }
        
        results, err := client.ReadWriteMultipleRegisters(
            readAddress, 2,  // 2워드 읽기
            writeAddress, uint16(len(writeValues)), // 2워드 쓰기
            writeData,
        )
        if err != nil {
            t.Fatal("읽기/쓰기 실패:", err)
        }
        
        // 읽은 데이터 출력
        for i := 0; i < len(results); i += 2 {
            value := uint16(results[i])<<8 | uint16(results[i+1])
            fmt.Printf("읽은 D%d 값: %d (0x%04X)\n", readAddress+uint16(i/2), value, value)
        }
        fmt.Printf("D%d에 2워드 쓰기 완료\n", writeAddress)
    })

    // 6. MaskWriteRegister (FC 22) - 마스크 쓰기
    t.Run("Mask Write Register", func(t *testing.T) {
        address := uint16(5000)
        // 예: 상위 8비트는 유지(0xFFFF)하고 하위 8비트는 클리어(0x0000)
        andMask := uint16(0xFF00) // 1111 1111 0000 0000
        orMask := uint16(0x00FF)  // 0000 0000 1111 1111
        
        _, err := client.MaskWriteRegister(address, andMask, orMask)
        if err != nil {
            t.Fatal("마스크 쓰기 실패:", err)
        }
        fmt.Printf("D%d에 마스크 쓰기 완료 (AND: 0x%04X, OR: 0x%04X)\n", 
            address, andMask, orMask)
    })
}

// go test -v -run TestModbusFunctions/Read_Single_Input_Register
// go test -v -run TestModbusFunctions/Read_Multiple_Holding_Registers
// go test -v -run TestModbusFunctions/Write_Single_Register
// go test -v -run TestModbusFunctions/Write_Multiple_Registers
// go test -v -run TestModbusFunctions/Read_Write_Multiple_Registers
// go test -v -run TestModbusFunctions/Mask_Write_Register


