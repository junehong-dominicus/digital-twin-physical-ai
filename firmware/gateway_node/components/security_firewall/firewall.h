#ifndef SECURITY_FIREWALL_H
#define SECURITY_FIREWALL_H

#include <stdint.h>
#include <stdbool.h>
#include "esp_one.h"

/**
 * @brief Security Policy for the Protocol-Aware Firewall.
 */
typedef struct {
    bool allow_writes;       // Allow/Block Modbus Write commands
    bool allow_config_sync;  // Allow remote configuration updates
    uint16_t allowed_nodes;  // Bitmask of allowed Slave IDs
} security_policy_t;

/**
 * @brief Initialize the Security Firewall and Secure Boot verification.
 */
void firewall_init(void);

/**
 * @brief Inspect an incoming message from the Cloud/Control layer.
 * 
 * @param packet The ESP-ONE packet to inspect
 * @return true if the packet is allowed, false if blocked
 */
bool firewall_inspect_command(const esp_one_packet_t *packet);

/**
 * @brief Log a security violation event.
 */
void firewall_log_violation(const char *reason, const esp_one_packet_t *packet);

#endif // SECURITY_FIREWALL_H
