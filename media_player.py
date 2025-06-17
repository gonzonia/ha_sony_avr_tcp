import socket
import logging
import json

from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
)
from homeassistant.components.media_player.const import MediaPlayerState
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

def send_json(host, port, json_obj, expect_response=False):
    try:
        json_str = json.dumps(json_obj)
        with socket.create_connection((host, port), timeout=2) as sock:
            sock.sendall(json_str.encode("utf-8"))
            if expect_response:
                return sock.recv(4096).decode("utf-8")
        return True
    except Exception as e:
        _LOGGER.error("Failed to send JSON to %s:%s - %s", host, port, e)
        return None if expect_response else False

class SonyAVR(MediaPlayerEntity):
    def __init__(self, host, port):
        self._host = host
        self._port = port
        self._attr_name = "Sony AVR"
        self._state = MediaPlayerState.OFF
        self._volume_level = 0.5
        self._muted = False
        self._source = None
        self._source_list = [
            "cd", "tuner", "am", "fm", "sat", "video", "stb", "aux", "game", "bd", "tv"
        ]

    def turn_on(self):
        send_json(self._host, self._port, {"type": "set", "feature": "main.power", "value": "on"})
        self._state = MediaPlayerState.ON
        self.schedule_update_ha_state()

    def turn_off(self):
        send_json(self._host, self._port, {"type": "set", "feature": "main.power", "value": "off"})
        self._state = MediaPlayerState.OFF
        self.schedule_update_ha_state()

    def set_volume_level(self, volume):
        level = int(volume * 74)
        send_json(self._host, self._port, {"type": "set", "feature": "main.volume", "value": str(level)})
        self._volume_level = volume

    def mute_volume(self, mute):
        send_json(self._host, self._port, {"type": "set", "feature": "main.mute", "value": "on" if mute else "off"})
        self._muted = mute

    def select_source(self, source):
        if source in self._source_list:
            send_json(self._host, self._port, {"type": "set", "feature": "main.input", "value": source})
            self._source = source

    def update(self):
        def get_val(feature):
            try:
                resp = send_json(self._host, self._port, {"type": "get", "feature": feature}, expect_response=True)
                return json.loads(resp)["value"]
            except:
                return None

        if (power := get_val("main.power")):
            self._state = MediaPlayerState.ON if power == "on" else MediaPlayerState.OFF

        if (mute := get_val("main.mute")):
            self._muted = mute == "on"

        if (vol := get_val("main.volume")):
            try:
                self._volume_level = min(1.0, int(vol) / 74)
            except:
                pass

        if (src := get_val("main.input")):
            self._source = src

    @property
    def state(self): return self._state
    @property
    def volume_level(self): return self._volume_level
    @property
    def is_volume_muted(self): return self._muted
    @property
    def source(self): return self._source
    @property
    def source_list(self): return self._source_list
    @property
    def supported_features(self):
        return (
            MediaPlayerEntityFeature.TURN_ON
            | MediaPlayerEntityFeature.TURN_OFF
            | MediaPlayerEntityFeature.VOLUME_SET
            | MediaPlayerEntityFeature.VOLUME_MUTE
            | MediaPlayerEntityFeature.SELECT_SOURCE
        )

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    host = config.get("host")
    port = config.get("port")
    async_add_entities([SonyAVR(host, port)])
