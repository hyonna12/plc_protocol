package mcprotocol

import (
	"fmt"
	"net"
	"strconv"
	"time"
)

// Type3E represents MC protocol type 3E communication
type Type3E struct {
	Host                  string
	Port                  int
	NetworkNumber         byte
	PCNumber              byte
	DestUnitIONumber      uint16
	DestUnitStationNumber byte
	conn                  net.Conn
	timeout               time.Duration
	commType              string // "binary" or "ascii"
	timer                 uint16 // MC protocol timeout (250msec * 4 = 1sec)
}

// NewType3E creates a new Type3E instance
func NewType3E() *Type3E {
	return &Type3E{
		NetworkNumber:         0x00,
		PCNumber:              0xFF,
		DestUnitIONumber:      0x03FF,
		DestUnitStationNumber: 0x00,
		timeout:               10 * time.Second,
		commType:              "ascii", // 기본값을 ASCII로 설정
		timer:                 4,       // 기본값 4 (1초)
	}
}

// SetTimeout sets communication timeout
func (t *Type3E) SetTimeout(timeout time.Duration) {
	t.timeout = timeout
}

// SetTimer sets MC protocol timer value (unit: 250msec)
func (t *Type3E) SetTimer(timer uint16) {
	t.timer = timer
}

// Connect establishes connection to PLC
func (t *Type3E) Connect(host string, port int) error {
	t.Host = host
	t.Port = port

	addr := fmt.Sprintf("%s:%d", host, port)
	conn, err := net.DialTimeout("tcp", addr, t.timeout)
	if err != nil {
		return err
	}

	t.conn = conn
	return nil
}

// Close closes the connection
func (t *Type3E) Close() error {
	if t.conn != nil {
		return t.conn.Close()
	}
	return nil
}

// makeCommandData creates command and subcommand data
func (t *Type3E) makeCommandData(command uint16, subcommand uint16) []byte {
	cmdData := fmt.Sprintf("%04X%04X", command, subcommand)
	return []byte(cmdData)
}

// makeDeviceData creates device code and device number data
func (t *Type3E) makeDeviceData(deviceCode string, headDevice uint32) []byte {
	// Python style: D* + device number
	deviceData := fmt.Sprintf("%s%04d", deviceCode, headDevice)
	return []byte(deviceData)
}

// encodeValue encodes a value to ASCII format
func (t *Type3E) encodeValue(value int, mode string, isSigned bool) []byte {
	var result string
	switch mode {
	case "byte":
		result = fmt.Sprintf("%02X", value&0xff)
	case "short":
		result = fmt.Sprintf("%04X", value&0xffff)
	case "long":
		result = fmt.Sprintf("%08X", value&0xffffffff)
	}
	return []byte(result)
}

// makeSendData creates the complete frame
func (t *Type3E) makeSendData(requestData []byte) []byte {
	// Calculate data length
	dataLength := len(requestData) + 6 // Python style

	// Create frame header
	frame := []byte(fmt.Sprintf("%04X", 0x5000))                          // Subheader
	frame = append(frame, t.encodeValue(int(t.NetworkNumber), "byte", false)...)
	frame = append(frame, t.encodeValue(int(t.PCNumber), "byte", false)...)
	frame = append(frame, []byte("03FF")...)                              // DestUnitIONumber
	frame = append(frame, []byte("0000")...)                              // DestUnitStationNumber
	frame = append(frame, t.encodeValue(dataLength, "short", false)...)   // Data length
	frame = append(frame, requestData...)                                 // Request data

	return frame
}

func (t *Type3E) BatchRead(deviceCode byte, headDevice uint32, readSize uint16) ([]uint16, error) {
	// Create command data
	cmdData := t.makeCommandData(BatchRead, SubCmdWord)
	
	// Create device data
	devData := t.makeDeviceData("D*", headDevice)
	
	// Create size data
	sizeData := t.encodeValue(int(readSize), "short", false)
	
	// Combine request data
	requestData := append(cmdData, devData...)
	requestData = append(requestData, sizeData...)
	
	// Create complete frame
	frame := t.makeSendData(requestData)

	fmt.Printf("Send frame: %s\n", string(frame))
	fmt.Printf("Send frame hex: %X\n", frame)

	// Send command and receive response
	resp, err := t.sendCommand(frame)
	if err != nil {
		return nil, fmt.Errorf("send command failed: %v", err)
	}

	// Parse response
	result := make([]uint16, readSize)
	respStr := string(resp)
	
	for i := 0; i < int(readSize); i++ {
		startIdx := i * 4
		endIdx := startIdx + 4
		
		if len(respStr) < endIdx {
			return nil, fmt.Errorf("response data too short: need %d bytes, got %d", endIdx, len(respStr))
		}
		
		value, err := strconv.ParseInt(respStr[startIdx:endIdx], 16, 16)
		if err != nil {
			return nil, fmt.Errorf("failed to parse word value: %v", err)
		}
		result[i] = uint16(value)
		fmt.Printf("Parsed value[%d]: %d (0x%04X)\n", i, value, value)
	}

	return result, nil
}

func (t *Type3E) sendCommand(commandData []byte) ([]byte, error) {
	if t.conn == nil {
		return nil, NewMCProtocolError(ErrCodeCannotCreatePack, "not connected")
	}

	// Add termination characters for ASCII mode
	sendData := append(commandData, []byte("\r\n")...)
	fmt.Printf("Sending: %s\n", string(sendData))

	// Send data
	n, err := t.conn.Write(sendData)
	if err != nil {
		return nil, fmt.Errorf("failed to send data: %v", err)
	}
	fmt.Printf("Sent %d bytes\n", n)

	// Receive response with timeout
	t.conn.SetReadDeadline(time.Now().Add(t.timeout))
	resp := make([]byte, 4096)
	n, err = t.conn.Read(resp)
	if err != nil {
		return nil, fmt.Errorf("failed to read response: %v", err)
	}

	// Reset read deadline
	t.conn.SetReadDeadline(time.Time{})

	fmt.Printf("Received raw data: % X\n", resp[:n])
	respStr := string(resp[:n])
	fmt.Printf("Response string: %s\n", respStr)

	// Check response format
	if len(respStr) < 4 {
		return nil, NewMCProtocolError(ErrCodeWrongLength,
			fmt.Sprintf("response too short: got %d bytes", n))
	}

	// Check response header (D0 means success)
	if respStr[:2] != "D0" {
		return nil, fmt.Errorf("PLC returned error code: %s", respStr[:4])
	}

	// Extract data portion (skip header)
	dataStart := 22 // ASCII 모드에서 데이터 시작 위치
	if len(respStr) < dataStart {
		return nil, fmt.Errorf("response too short for data extraction")
	}

	return []byte(respStr[dataStart:]), nil
}

// BatchWrite writes data to consecutive devices
func (t *Type3E) BatchWrite(deviceCode byte, headDevice uint32, writeData []uint16) error {
	writeSize := uint16(len(writeData))

	// Create ASCII command
	command := fmt.Sprintf("5000%02X%02XFF03FF0000%04X0000%02X%08X%04X",
		t.NetworkNumber,
		t.PCNumber,
		BatchWrite, // 0x1401
		deviceCode, // Device code
		headDevice, // Device number
		writeSize)  // Number of points to write

	// Add write data in ASCII format
	for _, data := range writeData {
		command += fmt.Sprintf("%04X", data)
	}

	fmt.Printf("Write Command: %s\n", command)

	// Send command
	_, err := t.sendCommand([]byte(command))
	return err
}
