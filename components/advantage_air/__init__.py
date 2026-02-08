import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import uart, sensor, text_sensor

AUTO_LOAD = []
MULTI_CONF = True

CONF_ID = "advantage_air_id"

advantage_air_ns = cg.esphome_ns.namespace("advantage_air")

AdvantageAir = advantage_air_ns.class_("AdvantageAir", cg.Component)

CONFIG_SCHEMA = cv.Schema(
    {
        cv.GenerateID(): cv.declare_id(AdvantageAir),
        cv.Optional("uart_id"): cv.use_id(uart.UARTComponent),
        cv.Optional("update_interval", default="30s"): cv.update_interval,
    }
)


async def to_code(config):
    var = cg.new_Pvariable(config[cv.GenerateID()])
    await cg.register_component(var, config)

    if "uart_id" in config:
        uart_comp = await cg.get_variable(config["uart_id"])
        cg.add(var.set_uart(uart_comp))
