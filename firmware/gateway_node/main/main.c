#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_one.h"
#include "firewall.h"

static const char *TAG = "GATEWAY_NODE";

void process_esp_one_message(esp_one_packet_t *packet) {
    // 1. All incoming traffic (especially from Cloud/Control) must be inspected
    if (!firewall_inspect_command(packet)) {
        return; // Silently drop or log security violation
    }

    switch (packet->msg_type) {
        case ESP_ONE_MSG_TELEMETRY: {
            float value;
            memcpy(&value, packet->payload, sizeof(float));
            ESP_LOGI(TAG, "Received telemetry from Protocol Node: %.2f", value);
            
            // 1. Run through Protocol Firewall
            // if (security_firewall_allow(packet)) { ... }
            
            // 2. Publish to MQTT
            // mqtt_bridge_publish("factory/sensor_1", value);
            break;
        }
        case ESP_ONE_MSG_ALERT:
            ESP_LOGW(TAG, "Received EDGE AI ALERT!");
            break;
        default:
            break;
    }
}

void app_main(void) {
    ESP_LOGI(TAG, "Initializing Gateway Node...");

    // 1. Initialize Security & Firewall (Pre-connectivity)
    firewall_init();

    // 2. Initialize ESP-ONE
    esp_one_init(17, 16, 115200);

    // 2. Initialize Wi-Fi / Ethernet
    // network_init();

    // 3. Initialize MQTT
    // mqtt_bridge_init();

    esp_one_packet_t packet;
    while (1) {
        if (esp_one_receive(&packet, 100) == 0) {
            process_esp_one_message(&packet);
        }
        vTaskDelay(pdMS_TO_TICKS(10));
    }
}
