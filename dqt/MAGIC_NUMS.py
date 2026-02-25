from typing import Final


class MagicNums:
    """
    Used for storing constants that don't make sense to exist in the 
    settings file or must exist in the context of a Python class.

    Attributes:
        SETTINGS_FILE: The relative path to the settings option JSON file.
    """
    SETTINGS_FILE: Final[str] = "settings.json"