from typing import Final
from pathlib import Path


class MagicNums:
    """
    Used for storing constants that don't make sense to exist in the 
    settings file or must exist in the context of a Python class.

    Attributes:
        SETTINGS_FILE: The relative path to the settings option JSON file.
    """
    
    # this assumes that this magic_nums file is located in a subdir from the
    # root of the project
    _ROOT_PATH: Final[Path] = Path(__file__).resolve().parent.parent
    SETTINGS_FILE: Final[str] = str(_ROOT_PATH / "settings.json")