//go:build picoxpander

package machine

// GPIO pins
const (
	GP0  Pin = GPIO0
	GP1  Pin = GPIO1
	GP2  Pin = GPIO2
	GP3  Pin = GPIO3
	GP4  Pin = GPIO4
	GP5  Pin = GPIO5
	GP6  Pin = GPIO6
	GP7  Pin = GPIO7
	GP8  Pin = GPIO8
	GP9  Pin = GPIO9
	GP10 Pin = GPIO10
	GP11 Pin = GPIO11
	GP12 Pin = GPIO12
	GP13 Pin = GPIO13
	GP14 Pin = GPIO14
	GP15 Pin = GPIO15
	GP16 Pin = GPIO16
	GP17 Pin = GPIO17
	GP18 Pin = GPIO18
	GP19 Pin = GPIO19
	GP20 Pin = GPIO20
	GP21 Pin = GPIO21
	GP22 Pin = GPIO22
	GP26 Pin = GPIO26
	GP27 Pin = GPIO27
	GP28 Pin = GPIO28

	// Onboard LED
	LED Pin = GPIO25

	// Onboard crystal oscillator frequency, in MHz.
	xoscFreq = 12 // MHz
)

// Analog pins
const (
	A0 = GPIO26
	A1 = GPIO27
	A2 = GPIO28
	A3 = GPIO29
)

// I2C Default pins on Raspberry Pico.
const (
	I2C0_SDA_PIN = GP0
	I2C0_SCL_PIN = GP1

	I2C1_SDA_PIN = GP2
	I2C1_SCL_PIN = GP3

/*
	I2C1_SDA_PIN = GP2
	I2C1_SCL_PIN = GP3
*/
)

// SPI default pins
const (
	// Default Serial Clock Bus 0 for SPI communications
	SPI0_SCK_PIN = GPIO2
	// Default Serial Out Bus 0 for SPI communications
	SPI0_SDO_PIN = GPIO3 // Tx
	// Default Serial In Bus 0 for SPI communications
	SPI0_SDI_PIN = GPIO4 // Rx

	// Default Serial Clock Bus 1 for SPI communications
	SPI1_SCK_PIN = GPIO10
	// Default Serial Out Bus 1 for SPI communications
	SPI1_SDO_PIN = GPIO11 // Tx
	// Default Serial In Bus 1 for SPI communications
	SPI1_SDI_PIN = GPIO12 // Rx
)

// UART pins
const (
	UART1_TX_PIN = GPIO4
	UART1_RX_PIN = GPIO5
	/*
		UART0_TX_PIN = GPIO0
		UART0_RX_PIN = GPIO1
		UART1_TX_PIN = GPIO8
		UART1_RX_PIN = GPIO9
	*/
	UART_TX_PIN = UART1_TX_PIN
	UART_RX_PIN = UART1_RX_PIN
)

var DefaultUART = UART1

// USB identifiers
const (
	usb_STRING_PRODUCT      = "Pico"
	usb_STRING_MANUFACTURER = "Raspberry Pi"
)

var (
	usb_VID uint16 = 0x2E8A
	usb_PID uint16 = 0x000A
)
