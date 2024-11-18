package main

import (
	"fmt"
	"log"
	"mcprotocol/mcprotocol"
	"time"
)

func main() {
	// PLC 연결 객체 생성
	plc := mcprotocol.NewType3E()

	// 타임아웃 설정
	plc.SetTimeout(5 * time.Second)

	fmt.Println("PLC 연결 시도 중...")
	err := plc.Connect("192.168.0.10", 5000)
	if err != nil {
		log.Fatalf("PLC 연결 실패: %v", err)
	}
	fmt.Println("PLC 연결 성공")
	defer plc.Close()

	// 읽기 테스트
	fmt.Println("\nD5000 레지스터 읽기 시도 중...")
	data, err := plc.BatchRead(mcprotocol.DeviceCodeD, 5000, 1)
	if err != nil {
		log.Fatalf("데이터 읽기 실패: %v", err)
	}
	fmt.Printf("D5000 레지스터 값: %d (0x%X)\n", data[0], data[0])

	// // 쓰기 테스트
	// fmt.Println("\nD5000 레지스터에 값 쓰기 시도 중...")
	// err = plc.BatchWrite(mcprotocol.DeviceCodeD, 5000, []uint16{123})
	// if err != nil {
	// 	log.Fatalf("데이터 쓰기 실패: %v", err)
	// }
	// fmt.Println("쓰기 성공")

	// // 쓴 값 다시 읽어보기
	// data, err = plc.BatchRead(mcprotocol.DeviceCodeD, 5000, 1)
	// if err != nil {
	// 	log.Fatalf("데이터 읽기 실패: %v", err)
	// }
	fmt.Printf("D5000 레지스터 새로운 값: %d (0x%X)\n", data[0], data[0])
}
