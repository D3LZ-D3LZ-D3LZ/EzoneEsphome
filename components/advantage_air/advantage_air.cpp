#include "advantage_air.h"
#include "esphome/core/log.h"
#include "esphome/core/helpers.h"

namespace esphome {
namespace advantage_air {

static const char *const TAG = "advantage_air";

void AdvantageAir::setup() {
  ESP_LOGI(TAG, "Advantage Air Controller starting...");
  delay(500);
  this->request_update();
}

void AdvantageAir::loop() {
  uint32_t now = millis();

  if (now - last_update_ > this->update_interval_) {
    this->request_update();
    last_update_ = now;
  }
}

void AdvantageAir::send_command(const std::string &command) {
  uint8_t crc = 0;
  for (char c : command) {
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

  std::string formatted = "<U>" + command + "</U=";
  char crc_str[8];
  snprintf(crc_str, sizeof(crc_str), "%02x", crc);
  formatted += crc_str + std::string(">");

  ESP_LOGI(TAG, "TX: %s", formatted.c_str());
  this->uart_->write_str(formatted.c_str());
}

void AdvantageAir::request_update() {
  this->send_command("Ping");
  delay(10);
  this->send_command("getSystemData");
  delay(30);
  this->send_command("getZoneData?zone=1");
  delay(20);
  this->send_command("getZoneData?zone=2");
  delay(20);
  this->send_command("getZoneData?zone=3");
  delay(20);
  this->send_command("getZoneData?zone=7");
}

std::string AdvantageAir::extract_tag(const std::string &xml, const std::string &tag) {
  std::string start_tag = "<" + tag + ">";
  std::string end_tag = "</" + tag + ">";

  size_t start = xml.find(start_tag);
  if (start == std::string::npos) return "";

  size_t end = xml.find(end_tag, start);
  if (end == std::string::npos) return "";

  return xml.substr(start + start_tag.length(), end - start - start_tag.length());
}

void AdvantageAir::parse_response(const std::string &response) {
  ESP_LOGI(TAG, "Parsing: %s", response.c_str());

  if (response.find("<authenticated>1</authenticated>") != std::string::npos) {
    ESP_LOGI(TAG, "Authentication successful");
  }

  if (response.find("<request>getSystemData</request>") != std::string::npos) {
    std::string power = this->extract_tag(response, "airconOnOff");
    std::string mode = this->extract_tag(response, "mode");
    std::string fan = this->extract_tag(response, "fanSpeed");
    std::string desired = this->extract_tag(response, "centralDesiredTemp");
    std::string zones = this->extract_tag(response, "numberOfZones");
    std::string filter = this->extract_tag(response, "filterCleanWarning");

    if (!power.empty()) this->data_.power = (power == "1");
    if (!mode.empty()) this->data_.mode = atoi(mode.c_str());
    if (!fan.empty()) this->data_.fan_speed = atoi(fan.c_str());
    if (!desired.empty()) this->data_.desired_temp = atof(desired.c_str());
    if (!zones.empty()) this->data_.number_of_zones = atoi(zones.c_str());
    if (!filter.empty()) this->data_.filter_warning = (filter == "1");

    ESP_LOGI(TAG, "System: power=%s, mode=%d, fan=%d, desired=%.1f, zones=%d",
             this->data_.power ? "ON" : "OFF",
             this->data_.mode,
             this->data_.fan_speed,
             this->data_.desired_temp,
             this->data_.number_of_zones);
  }
  else if (response.find("<request>getZoneData</request>") != std::string::npos) {
    size_t zone_pos = response.find("zone");
    if (zone_pos != std::string::npos) {
      int zone_id = response[zone_pos + 4] - '0';

      std::string name = this->extract_tag(response, "name");
      std::string setting = this->extract_tag(response, "setting");
      std::string actual = this->extract_tag(response, "actualTemp");
      std::string desired = this->extract_tag(response, "desiredTemp");
      std::string rf = this->extract_tag(response, "RFstrength");

      if (zone_id >= 1 && zone_id <= 7) {
        ZoneData &zone = this->data_.zones[zone_id - 1];
        zone.id = zone_id;
        zone.name = name;
        if (!setting.empty()) zone.open = (setting == "1");
        if (!actual.empty()) zone.measured_temp = atof(actual.c_str());
        if (!desired.empty()) zone.desired_temp = atof(desired.c_str());
        if (!rf.empty()) zone.rf_strength = atoi(rf.c_str());

        ESP_LOGI(TAG, "Zone %d: %s, temp=%.1f, desired=%.1f, rf=%d, open=%s",
                 zone_id,
                 name.c_str(),
                 zone.measured_temp,
                 zone.desired_temp,
                 zone.rf_strength,
                 zone.open ? "YES" : "NO");
      }
    }
  }
}

}  // namespace advantage_air
}  // namespace esphome
