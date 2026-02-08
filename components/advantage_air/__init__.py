import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import uart

AUTO_LOAD = ["sensor", "text_sensor", "binary_sensor", "climate"]
MULTI_CONF = True

CONF_ID = "advantage_air_id"

advantage_air_ns = cg.esphome_ns.namespace("advantage_air")

AdvantageAirController = advantage_air_ns.class_("AdvantageAirController", cg.Component)

CONFIG_SCHEMA = cv.Schema(
    {
        cv.GenerateID(): cv.declare_id(AdvantageAirController),
        cv.Optional("uart_id"): cv.use_id(uart.UARTComponent),
    }
)


async def to_code(config):
    var = cg.new_Pvariable(config[cv.GenerateID()])
    await cg.register_component(var, config)

    if "uart_id" in config:
        uart_comp = await cg.get_variable(config["uart_id"])
        cg.add(var.set_uart(uart_comp))
