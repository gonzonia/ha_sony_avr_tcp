import logging, json, socket
from homeassistant.components.switch import SwitchEntity
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

def send_json(host, port, obj):
    try:
        with socket.create_connection((host, port), timeout=2) as sock:
            sock.sendall(json.dumps(obj).encode("utf-8"))
        return True
    except Exception as e:
        _LOGGER.error("Switch JSON error: %s", e)
        return False

def get_json(host, port, feature):
    try:
        with socket.create_connection((host, port), timeout=2) as sock:
            sock.sendall(json.dumps({"type": "get", "feature": feature}).encode("utf-8"))
            return json.loads(sock.recv(4096).decode("utf-8")).get("value")
    except Exception as e:
        _LOGGER.error("Failed to get feature %s: %s", feature, e)
        return None

class SonyMuteSwitch(SwitchEntity):
    def __init__(self, host, port):
        self._host = host
        self._port = port
        self._attr_name = "Sony AVR Mute"
        self._state = False

    def turn_on(self): send_json(self._host, self._port, {"type": "set", "feature": "main.mute", "value": "on"}); self._state = True
    def turn_off(self): send_json(self._host, self._port, {"type": "set", "feature": "main.mute", "value": "off"}); self._state = False
    @property
    def is_on(self): return self._state
    def update(self): self._state = get_json(self._host, self._port, "main.mute") == "on"

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    async_add_entities([SonyMuteSwitch(config.get("host"), config.get("port"))])
