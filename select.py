import logging
import json
import socket
from homeassistant.components.select import SelectEntity
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

def send_json(host, port, obj):
    try:
        with socket.create_connection((host, port), timeout=2) as sock:
            sock.sendall(json.dumps(obj).encode("utf-8"))
        return True
    except Exception as e:
        _LOGGER.error("Failed to send JSON for select: %s", e)
        return False

def get_json(host, port, feature):
    try:
        with socket.create_connection((host, port), timeout=2) as sock:
            sock.sendall(json.dumps({"type": "get", "feature": feature}).encode("utf-8"))
            return json.loads(sock.recv(4096).decode("utf-8")).get("value")
    except Exception as e:
        _LOGGER.error("Failed to get JSON: %s", e)
        return None

class SonyHDMIOutSelect(SelectEntity):
    def __init__(self, host, port):
        self._host = host
        self._port = port
        self._attr_name = "Sony AVR HDMI Out"
        self._options = ["A", "B", "AB", "OFF"]
        self._current = None

    @property
    def options(self): return self._options
    @property
    def current_option(self): return self._current

    def select_option(self, option):
        send_json(self._host, self._port, {"type": "set", "feature": "hdmi.out", "value": option})
        self._current = option

    def update(self):
        self._current = get_json(self._host, self._port, "hdmi.out")

class SonySoundFieldSelect(SelectEntity):
    def __init__(self, host, port):
        self._host = host
        self._port = port
        self._attr_name = "Sony AVR Sound Field"
        self._options = [
            "2ch", "direct", "afd", "multi", "hddcs", "dolby", "pl2", "pl2x", "pl2_music",
            "pl2x_music", "neo6", "neo6_movie", "neo6_music", "jazz", "concert", "stadium",
            "sports", "hall_a", "hall_b", "hall_c"
        ]
        self._current = None

    @property
    def options(self): return self._options
    @property
    def current_option(self): return self._current

    def select_option(self, option):
        send_json(self._host, self._port, {"type": "set", "feature": "audio.soundfield", "value": option})
        self._current = option

    def update(self):
        self._current = get_json(self._host, self._port, "audio.soundfield")

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    host = config.get("host")
    port = config.get("port")
    async_add_entities([
        SonyHDMIOutSelect(host, port),
        SonySoundFieldSelect(host, port)
    ])
