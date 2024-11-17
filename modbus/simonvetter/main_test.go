package main

import (
    "fmt"
    "github.com/simonvetter/modbus"
    "testing"
    "time"
)

func setupTestClient(t *testing.T) *modbus.ModbusClient {
    client, err := modbus.NewClient(&modbus.ClientConfiguration{
        URL:     "tcp://192.168.0.10:502",
        Timeout: 10 * time.Second,
    })
    if err != nil {
        t.Fatal("클라이언트 생성 실패:", err)
    }

    err = client.Open()
    if err != nil {
        t.Fatal("연결 실패:", err)
    }

    return client
}

// convertDToModbus 함수 추가
func convertDToModbus(dAddr uint16) uint16 {
    return dAddr + 4096
}

func TestModbusOperations(t *testing.T) {
    client := setupTestClient(t)
    defer client.Close()

    dAddress := uint16(5000)
    modbusAddress := convertDToModbus(dAddress)

    // 1. 단일 워드 읽기 테스트
    t.Run("Read Single Word", func(t *testing.T) {
        value, err := client.ReadRegister(modbusAddress, modbus.HOLDING_REGISTER)
        if err != nil {
            t.Fatal("단일 워드 읽기 실패:", err)
        }
        fmt.Printf("D%d (Modbus 주소: %d) 값: %d (0x%04X)\n", 
            dAddress, modbusAddress, value, value)
    })

    // 2. 여러 워드 읽기 테스트
    t.Run("Read Multiple Words", func(t *testing.T) {
        values, err := client.ReadRegisters(modbusAddress, 2, modbus.HOLDING_REGISTER)
        if err != nil {
            t.Fatal("다중 워드 읽기 실패:", err)
        }
        for i, val := range values {
            fmt.Printf("D%d (Modbus 주소: %d) 값: %d (0x%04X)\n", 
                dAddress+uint16(i), modbusAddress+uint16(i), val, val)
        }
    })

    // 3. Int16 타입 읽기 테스트
    t.Run("Read Int16", func(t *testing.T) {
        value, err := client.ReadInt16(modbusAddress, modbus.HOLDING_REGISTER)
        if err != nil {
            t.Fatal("Int16 읽기 실패:", err)
        }
        fmt.Printf("D%d (Modbus 주소: %d) Int16 값: %d\n", 
            dAddress, modbusAddress, value)
    })

    // 4. Uint32 타입 읽기 테스트 (2개 레지스터)
    t.Run("Read Uint32", func(t *testing.T) {
        value, err := client.ReadUint32(modbusAddress, modbus.HOLDING_REGISTER)
        if err != nil {
            t.Fatal("Uint32 읽기 실패:", err)
        }
        fmt.Printf("D%d (Modbus 주소: %d) Uint32 값: %d\n", 
            dAddress, modbusAddress, value)
    })

    // 5. Float32 타입 읽기 테스트 (2개 레지스터)
    t.Run("Read Float32", func(t *testing.T) {
        value, err := client.ReadFloat32(modbusAddress, modbus.HOLDING_REGISTER)
        if err != nil {
            t.Fatal("Float32 읽기 실패:", err)
        }
        fmt.Printf("D%d (Modbus 주소: %d) Float32 값: %f\n", 
            dAddress, modbusAddress, value)
    })

    // 6. 단일 워드 쓰기 테스트
    t.Run("Write Single Word", func(t *testing.T) {
        writeValue := uint16(12345)
        err := client.WriteRegister(modbusAddress, writeValue)
        if err != nil {
            t.Fatal("단일 워드 쓰기 실패:", err)
        }
        
        // 쓰기 확인
        readValue, err := client.ReadRegister(modbusAddress, modbus.HOLDING_REGISTER)
        if err != nil {
            t.Fatal("확인 읽기 실패:", err)
        }
        if readValue != writeValue {
            t.Errorf("쓰기 실패: 예상값 %d, 실제값 %d", writeValue, readValue)
        }
        fmt.Printf("D%d (Modbus 주소: %d)에 값 %d (0x%04X) 쓰기 완료\n", 
            dAddress, modbusAddress, writeValue, writeValue)
    })

    // 7. 여러 워드 쓰기 테스트
    t.Run("Write Multiple Words", func(t *testing.T) {
        writeValues := []uint16{11111, 22222}
        err := client.WriteRegisters(modbusAddress, writeValues)
        if err != nil {
            t.Fatal("다중 워드 쓰기 실패:", err)
        }
        
        // 쓰기 확인
        readValues, err := client.ReadRegisters(modbusAddress, uint16(len(writeValues)), modbus.HOLDING_REGISTER)
        if err != nil {
            t.Fatal("확인 읽기 실패:", err)
        }
        for i, expected := range writeValues {
            if readValues[i] != expected {
                t.Errorf("쓰기 실패: 인덱스 %d, 예상값 %d, 실제값 %d", i, expected, readValues[i])
            }
        }
        fmt.Printf("D%d (Modbus 주소: %d)부터 %d개 워드 쓰기 완료\n", 
            dAddress, modbusAddress, len(writeValues))
    })
}

// 테스트 실행 방법:
// 모든 테스트 실행
// go test -v

// 개별 테스트 실행
// go test -v -run TestModbusOperations/Read_Single_Word
// go test -v -run TestModbusOperations/Read_Multiple_Words
// go test -v -run TestModbusOperations/Read_Int16
// go test -v -run TestModbusOperations/Read_Uint32
// go test -v -run TestModbusOperations/Read_Float32
// go test -v -run TestModbusOperations/Write_Single_Word
// go test -v -run TestModbusOperations/Write_Multiple_Words 