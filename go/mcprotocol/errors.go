package mcprotocol

import "fmt"

// MCProtocolError represents custom error types for MC Protocol
type MCProtocolError struct {
	ErrorCode int
	Message   string
}

func (e *MCProtocolError) Error() string {
	return fmt.Sprintf("MCProtocolError: %s (Error code: %d)", e.Message, e.ErrorCode)
}

// Error codes
const (
	ErrCodeWrongLength        = 1
	ErrCodeWrongDeviceCode   = 2
	ErrCodeWrongDataType     = 3
	ErrCodeWrongSubCommand   = 4
	ErrCodeWrongDataCount    = 5
	ErrCodeCannotCreatePack  = 6
	ErrCodeCannotGetData     = 7
	ErrCodeResponseWaitError = 8
)

// NewMCProtocolError creates a new MCProtocolError with the given error code and message
func NewMCProtocolError(errorCode int, message string) *MCProtocolError {
	return &MCProtocolError{
		ErrorCode: errorCode,
		Message:   message,
	}
} 