#pragma once

#include "esphome/core/component.h"
#include "esphome/components/uart/uart.h"
#include "esphome/core/automation.h"
#include <string>
#include <vector>

namespace esphome {
namespace advantage_air {

static const char *const TAG = "advantage_air";

struct ZoneData {
  int id{0};
  std::string name{""};
  bool open{false};
  float measured_temp{0.0f};
  float desired_temp{0.0f};
  int rf_strength{0};
};

struct SystemData {
  bool power{false};
  int mode{1};
  int fan_speed{1};
  float central_temp{0.0f};
  float desired_temp{21.0f};
  int number_of_zones{7};
  bool filter_warning{false};
  std::vector<ZoneData> zones;
};

class AdvantageAir : public Component {
 public:
  void set_uart(uart::UARTComponent *uart) { this->uart_ = uart; }

  void setup() override;
  void loop() override;

  SystemData &get_data() { return this->data_; }

 protected:
  uart::UARTComponent *uart_{nullptr};
  SystemData data_;
  std::string response_buffer_;
  uint32_t last_update_{0};
  uint32_t update_interval_{30000};

  void send_command(const std::string &command);
  void parse_response(const std::string &response);
  void request_update();
  std::string extract_tag(const std::string &xml, const std::string &tag);
};

}  // namespace advantage_air
}  // namespace esphome
