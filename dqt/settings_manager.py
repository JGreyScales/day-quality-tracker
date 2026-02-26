from enum import Enum
from typing import Any, Final
import json

from dqt.MAGIC_NUMS import MagicNums
from dqt.ui_utils import err


class SubDictEnum(Enum):
    """Store custom settings options subdict keys."""
    TRACKER = 'tracker'
    GRAPH = 'graph'
    NONE_SELECTED = 'none_selected'


class SettingsManager:
    """Static manager for handling JSON settings with custom list formatting."""
    settings: dict[str, dict[str, Any]] = {}
    json_indent: Final[int] = 4

    @staticmethod
    def _serialize_config(data: Any, indent: int = 2, level: int = 0) -> str:
        """Recursively format dicts vertically and lists horizontally.

        Args:
            data (Any): The data to serialize.
            indent (int): Spaces per indent level.
            level (int): Current recursion depth.

        Returns:
            str: The custom formatted JSON string.
        """
        close_indent: str = " " * (level * indent)
        indent_amount: str = " " * ((level + 1) * indent)

        if isinstance(data, dict):
            items: list[str] = []
            for key, value in data.items():  # type: ignore
                formatted_key = json.dumps(key)
                formatted_value = SettingsManager._serialize_config(
                    value, indent, level + 1
                )
                items.append(
                    f"{indent_amount}{formatted_key}: {formatted_value}"
                )

            return "{\n" + ",\n".join(items) + f"\n{close_indent}" + "}"

        # If it's a list json.dumps will put it on one line.
        return json.dumps(data)

    @staticmethod
    def save_json() -> bool:
        """Save settings to the settings file using custom serialization.

        Returns:
            bool: True if successful, False if settings is None.
        """
        if not SettingsManager.settings:
            return False

        with open(MagicNums.SETTINGS_FILE, 'w') as file:
            file.write(
                SettingsManager._serialize_config(
                    SettingsManager.settings
                )
            )
        return True

    @staticmethod
    def load_json() -> bool:
        """Load the settings option from the settings file.

        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            with open(MagicNums.SETTINGS_FILE, 'r') as file:
                setting_config: dict[str, dict[str, Any]] = json.load(file)
            SettingsManager.settings = setting_config
            return True
        except Exception as e:
            err(str(e))
            return False

    @staticmethod
    def get_range_with_key(subdict: SubDictEnum,
                           setting_name: str) -> list[Any]:
        """Retrieve the ranges list for a specific subdict and key.

        Args:
            subdict (SubDictEnum): The SubDictEnum category.
            setting_name: The setting key.

        Returns ():
            list[Any]: The requested ranges.
        """
        settings_range: list[Any] = []

        if not SettingsManager.settings:
            err("JSON is not loaded, no range to retrieve")
            return settings_range

        try:
            settings_range = (
                SettingsManager.settings[subdict.value][setting_name]['ranges']
            )
        except KeyError:
            err(
                "The subdict key combo does not exist, cannot retrieve range."
            )

        return settings_range

    @staticmethod
    def get_subdict_ranges(subdict: SubDictEnum) -> list[tuple[str, list[Any]]]:
        """Return all range values for a given sub-dictionary.

        Args:
            subdict: The SubDictEnum category.

        Returns:
            list[tuple[str, list[Any]]]: List of key-range pairs.
        """
        if not SettingsManager.settings:
            err("JSON is not loaded, no range to retrieve.")
            return []

        return [
            (setting_name, data['ranges'])
            for setting_name, data in (
                SettingsManager.settings[subdict.value].items()
            )
        ]

    @staticmethod
    def get_value(subdict: SubDictEnum, setting_name: str) -> Any | None:
        """Retrieve a specific value from the settings option.

        Args:
            subdict: The SubDictEnum category.
            setting_name: The setting key.

        Returns:
            Any | None: The stored value or None if not found.
        """
        value: Any | None = None

        if not SettingsManager.settings:
            err("JSON is not loaded, no range to retrieve.")
            return value

        try:
            value = (
                SettingsManager.settings
            )[subdict.value][setting_name]['value']
        except KeyError:
            err(
                "The given subdict key combo does not exist, cannot retrieve "
                "value."
            )

        return value

    @staticmethod
    def set_value(subdict: SubDictEnum, setting_name: str, new_value: Any) -> None:
        """Set a specific value in the settings option.

        Args:
            subdict (SubDictEnum): The SubDictEnum category.
            setting_name (str): The setting key.
            new_value (Any): The value to store.
        """
        if not SettingsManager.settings:
            err("JSON is not loaded, no range to retrieve.")
            return

        try:
            SettingsManager.settings[subdict.value][setting_name]['value'] = new_value
        except KeyError:
            err(
                "The given subdict key combo does not exist, "
                "could not set value."
            )

        return
    