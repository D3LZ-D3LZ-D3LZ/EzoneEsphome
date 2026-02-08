import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import uart
from esphome.const import CONF_ID, CONF_TEMPERATURE, CONF_FAN_MODE

from . import AdvantageAirController, advantage_air_ns, CONF_ID

Climate = advantage_air_ns.class_("Climate", cg.Component)

CONFIG_SCHEMA = cv.Schema({})


async def to_code(config):
    pass
