from enum import Enum
from typing import Any
import json

from dqt.MAGIC_NUMS import MAGIC_NUMS

class SubDictEnum(Enum):
    """Store custom configurations subdict keys."""
    TRACKER = 'tracker'
    GRAPH = 'graph'
    NONE_SELECTED = 'none_selected'

# static
class json_manager():
    config: dict[str, dict[str, Any]] | None = None

    @staticmethod
    def load_json() -> bool:
        try:
            with open(MAGIC_NUMS.SETTINGS_FILE, 'r') as file:
                setting_config: dict[str, dict[str, Any]] = json.load(file)
            json_manager.config = setting_config
            return True
        except(Exception):
            return False

    @staticmethod
    def save_json() -> bool:
        if (json_manager.config is None):
            return False
        
        with open(MAGIC_NUMS.SETTINGS_FILE, 'w') as file:
            json.dump(json_manager.config, file, indent=2)
        return True


    @staticmethod
    def get_range_with_key(subdict: SubDictEnum, key: str) -> list[Any]:
        range: list[Any] = []

        if json_manager.config is None:
            print("Json is not loaded, no range to retrieve")
            return range

        try:
            range = json_manager.config[subdict.value][key]['ranges']
        except (KeyError):
            print("that subdict key combo does not exist, cannot retrieve")
        finally:
            return range

    @staticmethod
    def get_subdict_ranges(subdict: SubDictEnum) -> list[tuple[str, list[Any]]]:
        if json_manager.config is None:
            return []
        
        return list(json_manager.config[subdict.value].items())

    @staticmethod
    def get_value(subdict: str, key: str) -> Any | None:
        value: Any | None = None

        if json_manager.config is None:
            print("Json is not loaded, no range to retrieve")
            return value
        
        try:
            value = json_manager.config[subdict][key]['ranges']
        except (KeyError):
            print("that subdict key combo does not exist, cannot retrieve")
        finally:
            return value