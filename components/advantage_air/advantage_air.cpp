#include "advantage_air.h"
#include "esphome/core/log.h"
#include "esphome/core/hal.h"

namespace esphome {
namespace advantage_air {

static const char *const TAG = "advantage_air";

void AdvantageAirController::setup() {
  ESP_LOGI(TAG, "Advantage Air Controller starting...");
  delay(500);
  this->ping();
  delay(100);
  this->request_status();
}

void AdvantageAirController::loop() {
  uint32_t now = millis();

  if (now - last_ping_ > 10000) {
    this->ping();
    last_ping_ = now;
  }

  if (now - last_status_ > 30000) {
    this->request_status();
    last_status_ = now;
  }
}

uint8_t AdvantageAirController::calculate_crc(const std::string &data) {
  uint8_t crc = 0;
  for (char c : data) {
    crc ^= static_cast<uint8_t>(c);
    for (int i = 0; i < 8; i++) {
      if (crc & 0x80) {
        crc = (crc << 1) ^ 0x07;
      } else {
        crc <<= 1;
      }
      crc &= 0xFF;
    }
  }
  return crc;
}

void AdvantageAirController::send_command(const std::string &command) {
  uint8_t crc = this->calculate_crc(command);
  std::string formatted = "<U>" + command + "</U=";
  char crc_str[8];
  snprintf(crc_str, sizeof(crc_str), "%02x", crc);
  formatted += crc_str + std::string(">");

  ESP_LOGI(TAG, "Sending: %s", formatted.c_str());
  this->uart_->write_str(formatted.c_str());
}

void AdvantageAirController::ping() {
  this->send_command("Ping");
  delay(20);
  this->send_command("ackCAN 1");
}

void AdvantageAirController::request_status() {
  this->send_command("getSystemData");
  delay(50);

  for (int zone = 1; zone <= 7; zone++) {
    std::string cmd = "getZoneData?zone=" + std::to_string(zone);
    this->send_command(cmd);
    delay(30);
  }
}

void AdvantageAirController::set_zone_temperature(int zone, float temperature) {
  std::string cmd = "setZoneData?zone=" + std::to_string(zone) +
                     "&desiredTemp=" + std::to_string(temperature);
  this->send_command(cmd);
}

void AdvantageAirController::set_zone_state(int zone, bool open) {
  std::string cmd = "setZoneData?zone=" + std::to_string(zone) +
                     "&setting=" + std::string(open ? "1" : "0");
  this->send_command(cmd);
}

void AdvantageAirController::set_system(bool power, int mode, int fan_speed, float temperature) {
  std::string cmd = "setSystemData?airconOnOff=" + std::string(power ? "1" : "0");
  cmd += "&mode=" + std::to_string(mode);
  cmd += "&fanSpeed=" + std::to_string(fan_speed);
  cmd += "&centralDesiredTemp=" + std::to_string(temperature);
  this->send_command(cmd);
}

void AdvantageAirController::parse_response(const std::string &response) {
  ESP_LOGI(TAG, "Response: %s", response.c_str());

  if (response.find("<system>") != std::string::npos) {
    size_t power_start = response.find("<airconOnOff>");
    if (power_start != std::string::npos) {
      size_t power_end = response.find("</airconOnOff>", power_start);
      if (power_end != std::string::npos) {
        std::string power_str = response.substr(power_start + 13, power_end - power_start - 13);
        this->data_.power = (power_str == "1");
      }
    }

    size_t mode_start = response.find("<mode>");
    if (mode_start != std::string::npos) {
      size_t mode_end = response.find("</mode>", mode_start);
      if (mode_end != std::string::npos) {
        std::string mode_str = response.substr(mode_start + 6, mode_end - mode_start - 6);
        try {
          this->data_.mode = std::stoi(mode_str);
        } catch (...) {
          this->data_.mode = 1;
        }
      }
    }

    size_t fan_start = response.find("<fanSpeed>");
    if (fan_start != std::string::npos) {
      size_t fan_end = response.find("</fanSpeed>", fan_start);
      if (fan_end != std::string::npos) {
        std::string fan_str = response.substr(fan_start + 10, fan_end - fan_start - 10);
        try {
          this->data_.fan_speed = std::stoi(fan_str);
        } catch (...) {
          this->data_.fan_speed = 1;
        }
      }
    }

    size_t temp_start = response.find("<centralDesiredTemp>");
    if (temp_start != std::string::npos) {
      size_t temp_end = response.find("</centralDesiredTemp>", temp_start);
      if (temp_end != std::string::npos) {
        std::string temp_str = response.substr(temp_start + 20, temp_end - temp_start - 20);
        try {
          this->data_.set_temp = std::stof(temp_str);
        } catch (...) {
          this->data_.set_temp = 22.0f;
        }
      }
    }

    ESP_LOGI(TAG, "Parsed AC: power=%s, mode=%d, fan=%d, temp=%.1f",
             this->data_.power ? "ON" : "OFF",
             this->data_.mode,
             this->data_.fan_speed,
             this->data_.set_temp);
  }
  else if (response.find("<zone") != std::string::npos) {
    size_t zone_start = response.find("zone=");
    if (zone_start != std::string::npos) {
      int zone_id = response[zone_start + 5] - '0';

      size_t temp_start = response.find("<measuredTemp>");
      if (temp_start != std::string::npos) {
        size_t temp_end = response.find("</measuredTemp>", temp_start);
        if (temp_end != std::string::npos) {
          std::string temp_str = response.substr(temp_start + 14, temp_end - temp_start - 14);
          try {
            float temp = std::stof(temp_str);
            if (zone_id >= 1 && zone_id <= (int) this->data_.zones.size()) {
              this->data_.zones[zone_id - 1].measured_temp = temp;
            } else if (zone_id == 1 && this->data_.zones.empty()) {
              this->data_.current_temp = temp;
            }
            ESP_LOGI(TAG, "Zone %d temp: %.1f", zone_id, temp);
          } catch (...) {}
        }
      }

      size_t setting_start = response.find("<setting>");
      if (setting_start != std::string::npos) {
        size_t setting_end = response.find("</setting>", setting_start);
        if (setting_end != std::string::npos) {
          std::string setting_str = response.substr(setting_start + 9, setting_end - setting_start - 9);
          bool is_open = (setting_str == "1");
          if (zone_id >= 1 && zone_id <= (int) this->data_.zones.size()) {
            this->data_.zones[zone_id - 1].open = is_open;
          }
          ESP_LOGI(TAG, "Zone %d: %s", zone_id, is_open ? "OPEN" : "CLOSED");
        }
      }
    }
  }
  else if (response.find("<authenticated>") != std::string::npos) {
    ESP_LOGI(TAG, "Authentication successful!");
  }
}

void Climate::setup() {
  ESP_LOGI(TAG, "Climate entity starting...");
}

void Climate::loop() {
}

}  // namespace advantage_air
}  // namespace esphome
