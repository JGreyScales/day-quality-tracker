import sys
from itertools import cycle

from dqt.iterable_settings import SubDictEnum, IterableSettings, Special
from dqt.ui_utils import invalid_choice, menu, clear_console
from dqt.styletext import StyleText as Txt


class SettingsMenu:
    """Display and control configurations menu."""
    
    def __init__(self):
        """Handle the actual rendering of the settings menu in the terminal."""
        self.chosen_menu: SubDictEnum = self.get_submenu()
        
        # If the exit command was invoked, exit the class
        if self.chosen_menu == SubDictEnum.NONE_SELECTED:
            return
        
        self.iterable_object: IterableSettings = IterableSettings(
            self.chosen_menu
        )
        self.display_option_list()
    
    def display_option_list(self) -> None:
        """Display the settings and fetch user input.
        
        Both the x and y directions will loop infinitely when interacted with.
        """
        # Dict is dynamically pulled from the runtime properties of the class.
        # All display options, and handling of selection below is generic
        # enough where it will update as the class updates and the next
        # return_ranges() call happens.
        settings: dict[
            str, list[Special]] = self.iterable_object.return_ranges()
        current_yindex: int = 0
        current_xindex: int = 0
        keys = list(settings.keys())
        selecting: bool = True
        
        while selecting:
            chosen_values = settings[keys[current_yindex]]
            cycled_values = cycle(
                chosen_values[current_xindex - 2:]
                + chosen_values[:current_xindex - 2]
            )
            clear_console()
            
            print("\n*❖* —————————————————————————————— *❖*")
            print(
                f"\n⚙️ {Txt(
                    f"{self.chosen_menu.value.upper()} SETTINGS MENU"
                ).blue().underline().bold()}",
                f"{Txt(
                    "— arrow keys to navigate menu, enter to confirm, "
                    "q to exit:"
                ).bold()}"
            )
            print(
                f"{Txt(
                    f"Current value of: {keys[current_yindex]}"
                    f" = {self.iterable_object.config[keys[current_yindex]]}"
                )}"
            )
            
            # Doing it this way lets us pick our starting and ending positions
            cycled_keys = cycle(
                keys[current_yindex - 3:] + keys[:current_yindex - 3])
            
            # Handling display
            for y in range(7):
                cur_setting = next(cycled_keys)
                # highlight the middle element
                if y == 3:
                    print(f"{Txt(cur_setting).green().bold()}")
                    option_choices = '['
                    for x in range(5):
                        cur_setting_choice = next(cycled_values)
                        if x == 2:
                            option_choices += str(
                                Txt(str(cur_setting_choice)).blue().bold()
                            )
                        else:
                            option_choices += str(Txt(str(cur_setting_choice)))
                        option_choices += ' '
                    print(option_choices + ']')
                else:
                    print(f"{Txt(cur_setting).dim()}")
            
            # handling input
            inputted_char = SettingsMenu._getchar()
            match inputted_char:
                case 'q':
                    selecting = False
                case 'UP':
                    current_yindex = (current_yindex - 1) % len(settings)
                    current_xindex = 0
                case 'DOWN':
                    current_yindex = (current_yindex + 1) % len(settings)
                    current_xindex = 0
                case 'LEFT':
                    current_xindex = (current_xindex - 1) % len(chosen_values)
                case 'RIGHT':
                    current_xindex = (current_xindex + 1) % len(chosen_values)
                case 'ENTER':
                    target_value = chosen_values[current_xindex]
                    target_key = keys[current_yindex]
                    self.iterable_object.replace_config_value(
                        target_key,
                        target_value
                    )
                    
                    # Fetch the newest version of the config
                    settings: dict[str, list[Special]] = (
                        self.iterable_object.return_ranges()
                    )
    
    @staticmethod
    def get_submenu() -> SubDictEnum:
        """Prompt user to select submenu option.
        
        This is where the submenu is determined which is used in this
        class, the tracker class, and the iterableSettings class.
        """
        print("\n*❖* —————————————————————————————— *❖*")
        print(
            f"\n⚙️ {Txt("SETTINGS MENU").blue().underline().bold()} "
        )
        selecting: bool = True
        while selecting:
            opts = menu(
                "1) [T]racker",
                "2) [G]raph",
                "3) [R]eturn to Main Menu",
                title="Select settings category:"
            )
            
            choice = input("> ").strip().lower()
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
    
    @staticmethod
    def _getchar():
        """Return a single key press as a string.
        
        Arrow keys become 'UP', 'DOWN', etc., Enter becomes 'ENTER'.
        """
        if sys.platform.startswith('win'):
            import msvcrt
            ch = msvcrt.getch()
            if ch in {b'\x00', b'\xe0'}:  # special keys
                ch2 = msvcrt.getch()
                arrows = {b'H': 'UP', b'P': 'DOWN', b'K': 'LEFT', b'M': 'RIGHT'}
                return arrows.get(ch2, '')
            elif ch == b'\r':
                return 'ENTER'
            else:
                try:
                    return ch.decode('utf-8')
                except UnicodeDecodeError:
                    return ''
        else:
            import tty
            import termios
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                ch = sys.stdin.read(1)
                if ch == '\r' or ch == '\n':
                    return 'ENTER'
                if ch == '\x1b':  # ESC sequence for arrows
                    seq = sys.stdin.read(2)
                    arrows = {
                        '[A': 'UP', '[B': 'DOWN', '[C': 'RIGHT', '[D': 'LEFT'
                    }
                    return arrows.get(seq, '')
                return ch
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
