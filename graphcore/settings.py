# -*- coding: utf-8 -*-

import json


# json formatted settings manipulation class
class GraphCoreSettings(object):
    # static variables
    settings = {
        "enable_node_shapes": ["circle", "doublecircle", "box", "doublebox"],
        "enable_node_types": ["domain", "process", "storage"],
        "default_node_attrs": {
            "x": 100,
            "y": 100,
            "w": 50,
            "h": 50,
            "shape": "circle",
            "label": "Node",
            "font-height": 10,
            "complexity": 0,
            "type": "process"
        },
        "enable_edge_types": ["dataflow", "controlflow"],
        "default_edge_attrs": {
            "arrow_angle": 0.3,
            "arrow_length": 20,
            "label": "Edge",
            "font-height": 10,
            "distance": 1.0,
            "type": "dataflow"
        }
    }

    # initializer
    def __init__(self, settings_file: str = "graphcore.cfg"):
        self._settings = None
        self._settings_file = None
        try:
            with open(settings_file, 'r') as f:
                self._settings = json.load(f)
                self._settings_file = settings_file
                self.tune_bool_initial_values()
        except Exception as ex:
            print("load settings failed. default values are used.")
            raise ex

    def save(self):
        try:
            with open(self._settings_file, 'w') as f:
                json.dump(self._settings, f, indent=4)
        except Exception as ex:
            print("save settings failed.")
            raise ex

    # default value
    def default_value(self, elems_sig, field_sig):
        value = self.setting(elems_sig)[field_sig]
        # type_name = self.setting(types_sig)[field_sig]
        return value

    # boolean value tuning
    def tune_bool_initial_values(self):
        pass
        # default_node_values = self._settings['default-node-attrs']
        # node_attr_types = self._settings['node-attr-types']
        # for k in node_attr_types:
        #     if node_attr_types[k] == 'bool':
        #         default_node_values[k] = bool(default_node_values[k])

    # save settings
    def save_settings(self):
        try:
            with open(self._settings_file, 'w') as f:
                json.dump(self._settings, f, indent=4)
        except Exception as ex:
            raise ex

    # get setting keys
    def setting_keys(self):
        return self._settings.keys()

    # get setting
    def setting(self, key):
        return self._settings[key]

    # set setting
    def set_setting(self, key, value):
        self._settings[key] = value

    # get setting value
    def setting_value(self, keys):
        settings = self._settings
        for k in keys:
            settings = settings[k]
        return settings

    # set setting value
    def set_setting_value(self, keys, value):
        settings = self._settings
        for k in keys[0:len(keys)-1]:
            settings = settings[k]
        settings[keys[len(keys)-1]] = value


class GraphCoreSettingsUser:
    def __init__(self):
        self._settings = None

    @property
    def settings(self):
        return self._settings

    @settings.setter
    def settings(self, settings: GraphCoreSettings):
        self._settings = settings


_settings = None


def gcore_settings() -> GraphCoreSettings:
    global _settings
    if _settings is None:
        _settings = GraphCoreSettings()
    return _settings
