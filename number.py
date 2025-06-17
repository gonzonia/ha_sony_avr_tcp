import logging
import json
import socket

from homeassistant.components.number import NumberEntity
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

def send_json(host, port, obj):
    try:
        with socket.create_connection((host, port), timeout=2) as sock:
            sock.sendall(json.dumps(obj).encode("utf-8"))
        return True
    except Exception as e:
        _LOGGER.error("Failed to send JSON for number: %s", e)
        return False

def get_json(host, port, feature):
    try:
        with socket.create_connection((host, port), timeout=2) as sock:
            sock.sendall(json.dumps({"type": "get", "feature": feature}).encode("utf-8"))
            resp = sock.recv(4096).decode("utf-8")
            data = json.loads(resp)
            value = data.get("value")
            if value is None or not str(value).isdigit():
                _LOGGER.warning("Unexpected response for %s: %s", feature, value)
                return None
            return int(value)
    except Exception as e:
        _LOGGER.error("Get failed: %s", e)
        return None

class SonyVolumeNumber(NumberEntity):
    def __init__(self, host, port):
        self._host = host
        self._port = port
        self._attr_name = "Sony AVR Volume Level"
        self._attr_native_min_value = 0
        self._attr_native_max_value = 74
        self._attr_native_step = 1
        self._value = 30

    def set_native_value(self, value):
        send_json(self._host, self._port, {
            "type": "set",
            "feature": "main.volume",
            "value": str(int(value))
        })
        self._value = value

    @property
    def native_value(self):
        return self._value

    def update(self):
        val = get_json(self._host, self._port, "main.volumestep")
        if val is not None:
            self._value = val

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    host = config.get("host")
    port = config.get("port")
    async_add_entities([SonyVolumeNumber(host, port)])
