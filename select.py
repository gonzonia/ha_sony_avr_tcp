import logging
import json
import socket

from homeassistant.components.select import SelectEntity
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

def send_json(host, port, json_obj):
    try:
        json_str = json.dumps(json_obj)
        with socket.create_connection((host, port), timeout=2) as sock:
            sock.sendall(json_str.encode("utf-8"))
        return True
    except Exception as e:
        _LOGGER.error("Failed to send JSON for select: %s", e)
        return False

class SonyHDMIOutSelect(SelectEntity):
    def __init__(self, host, port):
        self._host = host
        self._port = port
        self._attr_name = "Sony AVR HDMI Output"
        self._options = ["A", "B", "AB", "OFF"]
        self._current = None

    @property
    def options(self):
        return self._options

    @property
    def current_option(self):
        return self._current

    def select_option(self, option: str) -> None:
        if option in self._options:
            send_json(self._host, self._port, {"type": "set", "feature": "hdmi.out", "value": option})
            self._current = option

    def update(self):
        # Poll current HDMI output
        try:
            with socket.create_connection((self._host, self._port), timeout=2) as sock:
                sock.sendall(json.dumps({"type": "get", "feature": "hdmi.out"}).encode("utf-8"))
                resp = sock.recv(4096).decode("utf-8")
                data = json.loads(resp)
                self._current = data.get("value")
        except Exception as e:
            _LOGGER.error("Failed to poll HDMI output: %s", e)

async def async_setup_platform(hass, config: ConfigType, async_add_entities, discovery_info: DiscoveryInfoType = None):
    host = config.get("host")
    port = config.get("port")
    async_add_entities([SonyHDMIOutSelect(host, port)])
