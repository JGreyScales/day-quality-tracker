from enum import Enum
import sys, os
from itertools import cycle
from typing import Any

from readchar import readkey, key

from dqt.json_manager import SubDictEnum, JsonManager
from dqt.ui_utils import invalid_choice, menu, clear_console
from dqt.styletext import StyleText as Txt


class readMode(Enum):
    input = 'input'
    read_key = 'readkey'

class SettingsMenu:
    """Display and control configurations menu.

    This class handles the interactive terminal UI for navigating and
    modifying settings stored via the JsonManager.
    """

    def __init__(self) -> None:
        """Initialize the settings menu and starts the rendering process.

        If SubDictEnum.NONE_SELECTED is returned from the submenu,
        the initialization terminates early.
        """
        self.chosen_menu: SubDictEnum = self.get_submenu()

        # If the exit command was invoked, exit the class
        if self.chosen_menu == SubDictEnum.NONE_SELECTED:
            return

        self.display_option_list()

    @staticmethod
    def __get_best_input_method() -> readMode:
        if not sys.stdin.isatty():
            return readMode.input
            
        # PyCharm sets 'PYCHARM_HOSTED' to '1'
        if os.environ.get("PYCHARM_HOSTED") == "1":
            return readMode.input
            
        # Otherwise, we are likely in a real terminal
        return readMode.read_key

    def display_option_list(self) -> None:
        """Display the settings and fetch user input for navigation.

        Both the x (values) and y (keys) directions loop infinitely.
        The UI highlights the current selection and updates the JsonManager
        upon confirmation.
        """
        # Dict is dynamically pulled from the runtime properties of the class.
        settings: list[tuple[str, list[Any]]] = JsonManager.get_subdict_ranges(
            self.chosen_menu
        )
        
        current_yindex: int = 0
        current_xindex: int = 0
        keys: list[str] = list(map(lambda setting: setting[0], settings))
        values: list[Any] = list(map(lambda setting: setting[1], settings))
        selecting: bool = True

        while selecting:
            chosen_values: Any = values[current_yindex]
            # Slicing for the infinite loop display effect
            cycled_values: cycle[Any] = cycle(
                chosen_values[current_xindex - 2:]
                + chosen_values[:current_xindex - 2]
            )

            menu_output: list[str] = []
            menu_output.append("\n*❖* —————————————————————————————— *❖*")
            header_txt: str = Txt(
                f"{self.chosen_menu.value.upper()} SETTINGS MENU"
            ).blue().underline().bold().text
            
            help_txt: Txt = Txt(
                "— arrow keys to navigate menu, enter to confirm, q to exit:"
            ).bold()

            menu_output.append(f"\n⚙️ {header_txt} {help_txt}")

            current_val: Any = JsonManager.get_value(
                self.chosen_menu, keys[current_yindex]
            )
            print(
                Txt(
                    f'Current value of: {keys[current_yindex]} = {current_val}'
                )
            )

            # Handling display rotation for keys
            cycled_keys: cycle[str] = cycle(
                keys[current_yindex - 3:] + keys[:current_yindex - 3]
            )

            vertical_range: int = 7
            horizontal_range: int = 5
            # Handling display rendering
            for y in range(vertical_range):
                cur_setting: str = next(cycled_keys)
                # Highlight the middle element
                if y == vertical_range // 2:
                    print(f"{Txt(cur_setting).green().bold()}")
                    option_choices: str = '['
                    for x in range(horizontal_range):
                        cur_setting_choice: Any = next(cycled_values)
                        if x == horizontal_range // 2:
                            option_choices += str(
                                Txt(str(cur_setting_choice)).blue().bold()
                            )
                        else:
                            option_choices += str(Txt(str(cur_setting_choice)))
                        option_choices += ' '
                    print(option_choices + ']')
                else:
                    print(f"{Txt(cur_setting).dim()}")

            # Handling input
            inputted_char: str = SettingsMenu._getchar()
            match inputted_char:
                case 'q':
                    selecting = False
                case 'UP':
                    current_yindex = (current_yindex - 1) % len(keys)
                    current_xindex = 0
                case 'DOWN':
                    current_yindex = (current_yindex + 1) % len(keys)
                    current_xindex = 0
                case 'LEFT':
                    current_xindex = (current_xindex - 1) % len(chosen_values)
                case 'RIGHT':
                    current_xindex = (current_xindex + 1) % len(chosen_values)
                case 'ENTER':
                    JsonManager.set_value(
                        self.chosen_menu, 
                        keys[current_yindex], 
                        chosen_values[current_xindex]
                    )
                    if not JsonManager.save_json():
                        print("Error saving to json")
                        selecting = False
                case _:
                    pass

            ## count the amount of new lines in our output and add four for unaccounted whitespace and lines, add 7 for the vertical range
            clear_console(menu_output.count("\n") + 4 + vertical_range)

    @staticmethod
    def get_submenu() -> SubDictEnum:
        """Prompt user to select a settings category submenu.

        Returns:
            SubDictEnum: The selected category or NONE_SELECTED to exit.
        """
        print("\n*❖* —————————————————————————————— *❖*")
        print(f"\n⚙️ {Txt('SETTINGS MENU').blue().underline().bold()} ")
        
        selecting: bool = True
        while selecting:
            opts: int = menu(
                "1) [T]racker",
                "2) [G]raph",
                "3) [R]eturn to Main Menu",
                title="Select settings category:"
            )

            choice: str = input("> ").strip().lower()
            match choice:
                case '1' | 't':
                    return SubDictEnum.TRACKER
                case '2' | 'g':
                    return SubDictEnum.GRAPH
                case '3' | 'r':
                    return SubDictEnum.NONE_SELECTED
                case _:
                    invalid_choice(opts)
                    continue
        
        return SubDictEnum.NONE_SELECTED

    @staticmethod
    def _getchar() -> str:
        """Return a single key press as a string.

        Convert hardware-specific codes into standard strings:
        'UP', 'DOWN', 'LEFT', 'RIGHT', 'ENTER', or the character pressed.

        Returns:
            str: The interpreted key name or character.
        """

        if (SettingsMenu.__get_best_input_method() == readMode.read_key):
            key_mappings: dict[str, str] = {
                key.DOWN: "DOWN", 
                key.UP: "UP", 
                key.RIGHT: "RIGHT", 
                key.LEFT: "LEFT", 
                key.ENTER: "ENTER"
                }
            entered_key: str = readkey()

            return key_mappings.get(entered_key, entered_key)
        # only other option is "input"
        else:
            entered_text: str = input().strip().upper()
            
            input_mappings: dict[str, str] = {
                "UP": "UP",
                "W": "UP",
                "DOWN": "DOWN",
                "S": "DOWN",
                "LEFT": "LEFT",
                "A": "LEFT",
                "RIGHT": "RIGHT",
                "D": "RIGHT",
                "ENTER": "ENTER",
                "": "ENTER" # Allows just pressing Enter to count as "ENTER"
            }

            return input_mappings.get(entered_text, entered_text)