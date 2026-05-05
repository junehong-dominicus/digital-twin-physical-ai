#ifndef ESP_ONE_H
#define ESP_ONE_H

#include <stdint.h>
#include <stddef.h>

/**
 * @brief ESP-ONE Packet structure for inter-node communication.
 * Designed for high-speed transfer of normalized industrial data.
 */
typedef enum {
    ESP_ONE_MSG_TELEMETRY = 0x01,
    ESP_ONE_MSG_ALERT     = 0x02,
    ESP_ONE_MSG_COMMAND   = 0x03,
    ESP_ONE_MSG_HEARTBEAT = 0x04
} esp_one_msg_type_t;

typedef struct {
    uint8_t  sync_byte;      // 0xAA
    uint8_t  msg_type;       // esp_one_msg_type_t
    uint16_t payload_len;
    uint8_t  payload[256];
    uint16_t checksum;       // Simple CRC or XOR
} __attribute__((packed)) esp_one_packet_t;

/**
 * @brief Initialize the ESP-ONE interface (UART-based for simplicity).
 */
void esp_one_init(int tx_io, int rx_io, int baud_rate);

/**
 * @brief Send a packet over ESP-ONE.
 */
int esp_one_send(esp_one_msg_type_t type, const uint8_t *data, size_t len);

/**
 * @brief Receive a packet from ESP-ONE (blocking or async).
 */
int esp_one_receive(esp_one_packet_t *packet, uint32_t timeout_ms);

#endif // ESP_ONE_H
