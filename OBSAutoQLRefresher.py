import inspect
import re
import threading
import time

import obspython as obs
import psutil
import requests
import valve.source
import valve.source.a2s
from bs4 import BeautifulSoup

QUAKELIVE_PROCESS = "quakelive_steam.exe"
MIN_INTERVAL = 5000
MAX_INTERVAL = 9999999
DEFAULT_INTERVAL = 10000
MIN_BLINK_SPEED = 100
MAX_BLINK_SPEED = 5000
DEFAULT_BLINK_SPEED = 1000
INVALID_IP = ['', -1]

mainscript = None


class MainScript():
    def __init__(self, settings):
        self.steamurl = ''
        self.blink_speed = 1.0
        self.debug = False
        self.source_name = None
        self.onlyruninql = True
        self.personaname = ''
        self.prevmap = ''
        self.curip = INVALID_IP
        self.previp = INVALID_IP
        self.update(settings)

    def update(self, settings):
        self.steamurl = obs.obs_data_get_string(settings, "steamurl")
        self.blink_speed = obs.obs_data_get_int(settings, "blink_speed") * 0.001
        self.debug = obs.obs_data_get_bool(settings, "debug")
        self.source_name = obs.obs_data_get_string(settings, "source_name")
        self.onlyruninql = obs.obs_data_get_bool(settings, "onlyruninql")

    def reset(self):
        self.personaname = ''
        self.prevmap = ''
        self.curip = INVALID_IP
        self.previp = INVALID_IP

    def refresh_screen(self):
        source = obs.obs_frontend_get_current_scene()
        scene = obs.obs_scene_from_source(source)
        sceneitem = obs.obs_scene_find_source_recursive(scene, self.source_name)
        if sceneitem is not None:
            obs.obs_sceneitem_set_visible(sceneitem, False)
            if self.debug:
                print("off")
            time.sleep(self.blink_speed)
            obs.obs_sceneitem_set_visible(sceneitem, True)
            if self.debug:
                print("on")
        obs.obs_sceneitem_release(sceneitem)
        obs.obs_scene_release(scene)
        obs.obs_source_release(source)

    def is_ql_running(self):
        return QUAKELIVE_PROCESS in (p.name() for p in psutil.process_iter())

    def is_ql_source(self):
        source = obs.obs_get_source_by_name(self.source_name)
        setting = obs.obs_source_get_settings(source)
        name = obs.obs_data_get_string(setting, "window")
        if QUAKELIVE_PROCESS in name and (not self.onlyruninql or self.is_ql_running()):
            return True
        else:
            return False

    def get_personaname(self, soup):
        n = None
        soup_persona = soup.find('div', class_='persona_name')
        if soup_persona:
            soup_actual_persona = soup_persona.find('span', class_='actual_persona_name')
            if soup_actual_persona:
                n = soup_actual_persona.string
        if self.debug:
            if not n:
                print('couldnt get personaname')
            else:
                print(f'personaname: {n}')
        return n

    def get_current_status(self):
        p_ip = self.curip
        soup = BeautifulSoup(requests.get(self.steamurl).text, 'html.parser')
        stats = soup.find('div', class_='profile_in_game')
        if not stats or not stats.has_attr('class'):
            return INVALID_IP, p_ip, None
        elif not 'in-game' in stats['class']:
            return INVALID_IP, p_ip, None
        game = soup.find('div', class_='profile_in_game_name')
        if not game:
            return INVALID_IP, p_ip, None
        elif not game.string == 'Quake Live':
            return INVALID_IP, p_ip, None
        srv = soup.find('div', class_='profile_in_game_joingame').find('a')
        if not 'connect' in srv['href']:
            return INVALID_IP, p_ip, None
        address = srv['href'].split('/')[-1]
        address = address.split(':')
        port = int(address[1])
        c_ip = (address[0], port)
        p_name = self.get_personaname(soup)
        if not p_name:
            return INVALID_IP, p_ip, None
        return c_ip, p_ip, p_name

    def is_in_server(self, server):
        for player in server['players']:
            if player['name'] == self.personaname:
                return True
        return False

    def query_server(self, address):
        try:
            with valve.source.a2s.ServerQuerier(address) as server:
                info = server.info()
                players = server.players()['players']
                return {'info': info, 'players': players}
        except valve.source.NoResponseError:
            if self.debug:
                print("[{}]Server {}:{} timed out!".format(inspect.stack()[1].function, *address))
            return None

    def check_status(self):
        if self.curip == INVALID_IP:
            return None
        server = self.query_server(self.curip)
        if not server:
            return None
        elif not self.is_in_server(server):
            return None
        return server

    def run(self):
        if not self.is_ql_source():
            return
        server = self.check_status()
        if server is None:
            self.curip, self.previp, self.personaname = self.get_current_status()
            if self.curip != self.previp and self.curip != INVALID_IP:
                thread = threading.Thread(target=self.refresh_screen)
                thread.start()
                server = self.check_status()
                if server:
                    self.prevmap = server['info']['map']
        elif server:
            if 'info' in server:
                if server['info']['map'] != self.prevmap:
                    thread = threading.Thread(target=self.refresh_screen)
                    thread.start()
                    self.prevmap = server['info']['map']
        if self.debug:
            print(f"current ip: {self.curip}  previous ip: {self.previp} previous map: {self.prevmap}")


def script_properties():
    props = obs.obs_properties_create()

    obs.obs_properties_add_bool(props,
                                "enable",
                                "Enable this script")

    obs.obs_properties_add_text(
        props, "steamurl", "Steam Community URL", obs.OBS_TEXT_DEFAULT
    )

    p = obs.obs_properties_add_list(props, "source_name", "Target Source",
                                    obs.OBS_COMBO_TYPE_EDITABLE,
                                    obs.OBS_COMBO_FORMAT_STRING)
    sources = obs.obs_enum_sources()
    if sources is not None:
        for source in sources:
            source_id = obs.obs_source_get_id(source)
            if source_id == "game_capture":
                name = obs.obs_source_get_name(source)
                obs.obs_property_list_add_string(p, name, name)
    obs.source_list_release(sources)

    obs.obs_properties_add_int(props,
                               "interval",
                               "Check Interval (ms)",
                               MIN_INTERVAL,
                               MAX_INTERVAL,
                               1)
    obs.obs_properties_add_int(props,
                               "blink_speed",
                               "Blink Speed (ms)",
                               MIN_BLINK_SPEED,
                               MAX_BLINK_SPEED,
                               1)
    obs.obs_properties_add_bool(props,
                                "onlyruninql",
                                "Disable the script when Quake Live is not running")
    obs.obs_properties_add_bool(props,
                                "debug",
                                "Enable debug logging")
    return props


def script_defaults(settings):
    obs.obs_data_set_default_string(settings, 'steamurl', "")
    obs.obs_data_set_default_string(settings, 'source_name', "")
    obs.obs_data_set_default_int(settings, 'interval', DEFAULT_INTERVAL)
    obs.obs_data_set_default_int(settings, 'blink_speed', DEFAULT_BLINK_SPEED)
    obs.obs_data_set_default_bool(settings, 'debug', False)
    obs.obs_data_set_default_bool(settings, 'enable', True)
    obs.obs_data_set_default_bool(settings, 'onlyruninql', True)


def thread_run():
    thread = threading.Thread(target=mainscript.run())
    thread.run()


def script_load(settings):
    global mainscript
    mainscript = MainScript(settings)


def script_save():
    obs.timer_remove(thread_run)


def script_update(settings):
    obs.timer_remove(thread_run)
    mainscript.update(settings)
    mainscript.reset()
    if mainscript.debug:
        print("updated")
    if not re.match(r'https?://steamcommunity.com/(profiles|id)/.+', mainscript.steamurl):
        if mainscript.debug:
            print("The URL does not seem from Steam Community")
        return
    res = requests.get(mainscript.steamurl)
    if not res.ok:
        print(f"Got wrong http status code: {res.status_code}")
        return
    interval = obs.obs_data_get_int(settings, "interval")
    enable = obs.obs_data_get_bool(settings, "enable")
    if enable:
        obs.timer_add(thread_run, interval)
    else:
        if mainscript.debug:
            print("The script is not enabled. Check the \"Enable this script\" checkbox to get it working.")
        return
