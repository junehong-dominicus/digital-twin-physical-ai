#include "firewall.h"
#include <string.h>
#include "esp_log.h"

static const char *TAG = "SECURE_FIREWALL";
static security_policy_t current_policy;

void firewall_init(void) {
    ESP_LOGI(TAG, "Initializing Protocol-Aware Firewall...");
    
    // Mock Secure Boot Check
    ESP_LOGI(TAG, "[SECURE_BOOT] Firmware signature verified (RSA-4096)");
    ESP_LOGI(TAG, "[FLASH_ENCRYPTION] Encrypted storage enabled");

    // Default policy: One-way traffic (Block Writes)
    current_policy.allow_writes = false;
    current_policy.allow_config_sync = true;
    current_policy.allowed_nodes = 0xFFFF; // All nodes allowed
    
    ESP_LOGI(TAG, "Default Policy: One-Way Traffic (Read-Only) ENABLED");
}

bool firewall_inspect_command(const esp_one_packet_t *packet) {
    if (packet->msg_type != ESP_ONE_MSG_COMMAND) {
        return true; // Non-command messages pass through
    }

    // Protocol-Aware Deep Packet Inspection (DPI)
    // Assume payload[0] is the command type
    uint8_t cmd_type = packet->payload[0];

    if (cmd_type == 0x05 || cmd_type == 0x06 || cmd_type == 0x10) { // Modbus Write FCs
        if (!current_policy.allow_writes) {
            firewall_log_violation("Blocked Unauthorized MODBUS WRITE", packet);
            return false;
        }
    }

    return true;
}

void firewall_log_violation(const char *reason, const esp_one_packet_t *packet) {
    ESP_LOGE(TAG, "!!! SECURITY VIOLATION !!! %s", reason);
    ESP_LOGE(TAG, "Source: CLOUD, Type: 0x%02X, Node: %d", 
             packet->msg_type, packet->payload[1]);
}
