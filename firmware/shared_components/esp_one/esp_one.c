#include "esp_one.h"
#include "esp_log.h"
#include "driver/uart.h"
#include "string.h"

static const char *TAG = "ESP_ONE";
static const int UART_NUM = UART_NUM_1;

void esp_one_init(int tx_io, int rx_io, int baud_rate) {
    const uart_config_t uart_config = {
        .baud_rate = baud_rate,
        .data_bits = UART_DATA_8_BITS,
        .parity = UART_PARITY_DISABLE,
        .stop_bits = UART_STOP_BITS_1,
        .flow_ctrl = UART_HW_FLOWCTRL_DISABLE,
        .source_clk = UART_SCLK_DEFAULT,
    };
    uart_driver_install(UART_NUM, 1024 * 2, 0, 0, NULL, 0);
    uart_param_config(UART_NUM, &uart_config);
    uart_set_pin(UART_NUM, tx_io, rx_io, UART_PIN_NO_CHANGE, UART_PIN_NO_CHANGE);
    ESP_LOGI(TAG, "ESP-ONE Initialized on UART %d (TX:%d, RX:%d)", UART_NUM, tx_io, rx_io);
}

int esp_one_send(esp_one_msg_type_t type, const uint8_t *data, size_t len) {
    if (len > 256) return -1;

    esp_one_packet_t packet;
    packet.sync_byte = 0xAA;
    packet.msg_type = (uint8_t)type;
    packet.payload_len = (uint16_t)len;
    memcpy(packet.payload, data, len);
    packet.checksum = 0; // Simple placeholder

    return uart_write_bytes(UART_NUM, (const char*)&packet, sizeof(esp_one_packet_t));
}

int esp_one_receive(esp_one_packet_t *packet, uint32_t timeout_ms) {
    return uart_read_bytes(UART_NUM, (uint8_t*)packet, sizeof(esp_one_packet_t), pdMS_TO_TICKS(timeout_ms));
}
