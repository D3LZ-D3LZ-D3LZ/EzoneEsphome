#pragma once

#include "esphome/core/component.h"
#include "esphome/components/uart/uart.h"
#include "esphome/core/helpers.h"

namespace esphome {
namespace advantage_air {

static const char *const TAG = "advantage_air";

struct AdvantageAirData {
  bool power{false};
  int mode{1};
  int fan_speed{1};
  float set_temp{22.0f};
  float current_temp{0.0f};

  struct Zone {
    int id{0};
    bool open{false};
    float measured_temp{0.0f};
    float set_temp{22.0f};
    int value{0};
    std::string name{""};
  };
  std::vector<Zone> zones;
};

class AdvantageAirController : public Component {
 public:
  void set_uart(uart::UARTComponent *uart) { this->uart_ = uart; }

  void setup() override;
  void loop() override;

  void ping();
  void request_status();
  void set_zone_temperature(int zone, float temperature);
  void set_zone_state(int zone, bool open);
  void set_system(bool power, int mode, int fan_speed, float temperature);

  AdvantageAirData &get_data() { return this->data_; }

 protected:
  uart::UARTComponent *uart_{nullptr};
  AdvantageAirData data_;
  uint32_t last_ping_{0};
  uint32_t last_status_{0};

  uint8_t calculate_crc(const std::string &data);
  void send_command(const std::string &command);
  void parse_response(const std::string &response);
};

class Climate : public Component {
 public:
  void set_controller(AdvantageAirController *controller) { this->controller_ = controller; }

  void setup() override;
  void loop() override;

  float current_temperature() { return this->controller_->get_data().current_temp; }
  float target_temperature() { return this->controller_->get_data().set_temp; }

 protected:
  AdvantageAirController *controller_{nullptr};
};

}  // namespace advantage_air
}  // namespace esphome
