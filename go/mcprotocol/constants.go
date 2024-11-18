package mcprotocol

// Frame types
const (
	FrameType3E = 0x03
	FrameType4E = 0x04
)

// Command types
const (
	BatchRead  = 0x0401
	BatchWrite = 0x1401
)

// Sub command types
const (
	SubCmdWord   = 0x0000
	SubCmdBit    = 0x0001
	SubCmdDword  = 0x0000
	SubCmdBitDev = 0x0001
)

// Device codes
const (
	DeviceCodeD   = 0xA8 // Data Register
	DeviceCodeW   = 0xB4 // Link Register
	DeviceCodeR   = 0xAF // File Register
	DeviceCodeZR  = 0xB0 // File Register
	DeviceCodeM   = 0x90 // Internal Relay
	DeviceCodeSM  = 0x91 // Special Relay
	DeviceCodeL   = 0x92 // Latch Relay
	DeviceCodeF   = 0x93 // Annunciator
	DeviceCodeV   = 0x94 // Edge Relay
	DeviceCodeB   = 0xA0 // Link Relay
	DeviceCodeSB  = 0xA1 // Special Link Relay
	DeviceCodeX   = 0x9C // Input
	DeviceCodeY   = 0x9D // Output
	DeviceCodeSD  = 0xA9 // Special Register
	DeviceCodeTS  = 0xC1 // Timer Contact
	DeviceCodeTC  = 0xC0 // Timer Coil
	DeviceCodeTN  = 0xC2 // Timer Current Value
	DeviceCodeCS  = 0xC4 // Counter Contact
	DeviceCodeCC  = 0xC3 // Counter Coil
	DeviceCodeCN  = 0xC5 // Counter Current Value
	DeviceCodeSTS = 0xC7 // Retentive Timer Contact
	DeviceCodeSTC = 0xC6 // Retentive Timer Coil
	DeviceCodeSTN = 0xC8 // Retentive Timer Current Value
) 