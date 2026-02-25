from enum import Enum
from typing import Any, Final
import json

from dqt.MAGIC_NUMS import MagicNums


class SubDictEnum(Enum):
    """Store custom configurations subdict keys."""
    TRACKER = 'tracker'
    GRAPH = 'graph'
    NONE_SELECTED = 'none_selected'


class JsonManager:
    """
    Static manager for handling JSON configuration with custom list formatting.
    """
    config: dict[str, dict[str, Any]] | None = None
    json_indent: Final[int] = 4

    @staticmethod
    def __serialize_config(data: Any, indent: int = 2, level: int = 0) -> str:
        """
        Recursively formats dicts vertically and lists horizontally.

        Args:
            data: The data to serialize.
            indent: Spaces per indent level.
            level: Current recursion depth.

        Returns:
            str: The custom formatted JSON string.
        """
        close_indent: str = " " * (level * indent)
        indent_amount: str = " " * ((level + 1) * indent)

        if isinstance(data, dict):
            items: list[str] = []
            for key, value in data.items():  # type: ignore
                formatted_key = json.dumps(key)
                formatted_value = JsonManager.__serialize_config(value, indent, level + 1)
                items.append(f"{indent_amount}{formatted_key}: {formatted_value}")

            return "{\n" + ",\n".join(items) + f"\n{close_indent}" + "}"

        # If it's a list json.dumps will put it on one line.
        return json.dumps(data)

    @staticmethod
    def save_json() -> bool:
        """
        Saves the config to the settings file using custom serialization.

        Returns:
            bool: True if successful, False if config is None.
        """
        if JsonManager.config is None:
            return False

        with open(MagicNums.SETTINGS_FILE, 'w') as file:
            file.write(JsonManager.__serialize_config(JsonManager.config))
        return True

    @staticmethod
    def load_json() -> bool:
        """
        Loads the configuration from the settings file.

        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            with open(MagicNums.SETTINGS_FILE, 'r') as file:
                setting_config: dict[str, dict[str, Any]] = json.load(file)
            JsonManager.config = setting_config
            return True
        except Exception:
            return False

    @staticmethod
    def get_range_with_key(subdict: SubDictEnum, key: str) -> list[Any]:
        """
        Retrieves the ranges list for a specific subdict and key.

        Args:
            subdict: The SubDictEnum category.
            key: The setting key.

        Returns:
            list[Any]: The requested ranges.
        """
        range: list[Any] = []

        if JsonManager.config is None:
            print("Json is not loaded, no range to retrieve")
            return range

        try:
            range = JsonManager.config[subdict.value][key]['ranges']
        except KeyError:
            print("that subdict key combo does not exist, cannot retrieve")

        return range

    @staticmethod
    def get_subdict_ranges(subdict: SubDictEnum) -> list[tuple[str, list[Any]]]:
        """
        Returns all range values for a given sub-dictionary.

        Args:
            subdict: The SubDictEnum category.

        Returns:
            list[tuple[str, list[Any]]]: List of key-range pairs.
        """
        if JsonManager.config is None:
            print("Json is not loaded, no range to retrieve")
            return []

        return [
            (key, data['ranges'])
            for key, data in JsonManager.config[subdict.value].items()
        ]

    @staticmethod
    def get_value(subdict: SubDictEnum, key: str) -> Any | None:
        """
        Retrieves a specific value from the configuration.

        Args:
            subdict: The SubDictEnum category.
            key: The setting key.

        Returns:
            Any | None: The stored value or None if not found.
        """
        value: Any | None = None

        if JsonManager.config is None:
            print("Json is not loaded, no range to retrieve")
            return value

        try:
            value = JsonManager.config[subdict.value][key]['value']
        except KeyError:
            print("that subdict key combo does not exist, cannot retrieve")

        return value

    @staticmethod
    def set_value(subdict: SubDictEnum, key: str, value: Any) -> None:
        """
        Sets a specific value in the configuration.

        Args:
            subdict: The SubDictEnum category.
            key: The setting key.
            value: The value to store.
        """
        if JsonManager.config is None:
            print("Json is not loaded, no range to retrieve")
            return

        try:
            JsonManager.config[subdict.value][key]['value'] = value
        except KeyError:
            print("that subdict key combo does not exist, cannot retrieve")

        return