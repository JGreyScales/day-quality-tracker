from dqt.iterableSettings import subDictEnum, IterableSettings, Special, T
from typing import TypeVar, List, Union
from dqt.ui_utils import cont_on_enter, err, invalid_choice, menu
from dqt.styletext import StyleText as Txt, clear_console
from itertools import cycle
import sys

class SettingsMenu:
    def __init__(self):
        self.choosenMenu: subDictEnum = self.getSubMenu()

        # if the exit command was invoked exit the class
        if (self.choosenMenu == False):
            return
        
        self.iterableObject: IterableSettings = IterableSettings(self.choosenMenu)
        self.displayOptionList()

    def displayOptionList(self) -> None:
        # dict is dynamically pulled from the runtime properties of the class
        # all display options, and handling of selection below is generic enough where
        # it will update as the class updates and the next returnRange call happens
        settings: dict[str, List[Special]] = self.iterableObject.returnRanges()
        currentYIndex: int = 0
        currentXIndex: int = 0
        keys = list(settings.keys())
        selecting: bool = True


        while selecting:
            chosenValues = settings[keys[currentYIndex]]
            cycled_values = cycle(chosenValues[currentXIndex - 2:] + chosenValues[:currentXIndex - 2])
            clear_console()

            print("\n*❖* —————————————————————————————— *❖*")
            print(
                f"\n🏠 {Txt(f"{self.choosenMenu.value.upper()} SETTINGS MENU").blue().underline().bold()} "
                f"{Txt("-- arrow keys to navigate menu, enter to confirm, q to exit:").bold()}"
            )
            print(f"{Txt(f"Current value of: {keys[currentYIndex]} = {self.iterableObject.config[keys[currentYIndex]]}")}")


            # doing it this way lets us pick our starting and ending positions
            cycled_keys = cycle(keys[currentYIndex - 3:] + keys[:currentYIndex - 3])

            # handling display
            for y in range (7):
                curSetting = next(cycled_keys)
                # highlight the middle element
                if (y == 3):
                    print(f"{Txt(curSetting).green().bold()}")
                    optionChoices = "["
                    for x in range (5):
                        curSettingChoice = next(cycled_values)
                        if (x == 2):
                            optionChoices += str(Txt(str(curSettingChoice)).blue().bold())
                        else:
                            optionChoices += str(Txt(str(curSettingChoice)))
                        optionChoices += " "
                    print(optionChoices + "]")
                else:
                    print(f"{Txt(curSetting).dim()}")

            # handling input
            inputedChar = SettingsMenu.__getchar()
            match inputedChar:
                case 'q':
                    selecting = False
                case 'UP':
                    currentYIndex = (currentYIndex - 1) % len(settings)
                    currentXIndex = 0
                case 'DOWN':
                    currentYIndex = (currentYIndex + 1) % len(settings)
                    currentXIndex = 0
                case 'LEFT':
                    currentXIndex = (currentXIndex - 1) % len(chosenValues)
                case 'RIGHT':
                    currentXIndex = (currentXIndex + 1) % len(chosenValues)
                case 'ENTER':
                    targetValue = chosenValues[currentXIndex]
                    targetKey = keys[currentYIndex]
                    self.iterableObject.config[targetKey] = targetValue
                    self.iterableObject.replace_config_value(targetKey, targetValue)

    def getSubMenu(self) -> subDictEnum | bool:
        print("\n*❖* —————————————————————————————— *❖*")
        print(
            f"\n🏠 {Txt("Settings MENU").blue().underline().bold()} "
            f"{Txt("— choose what to do:").bold()}"
        )
        selecting: bool = True
        while selecting:
            opts = menu(
                "1) [T]racker",
                "2) [G]raph (not yet implimented)",
                "3) [B]ack"
            )

            choice = input("> ").strip().lower()
            match choice:
                case '1' | 't':
                    return subDictEnum.TRACKER
                case '2' | 'g':
                    return subDictEnum.GRAPH
                case '3' | 'b':
                    return False
                case _:
                    invalid_choice(opts)
                    continue

    @staticmethod
    # ai generated helper function to allow cross platform get key presses
    def __getchar():
        """Return a single key press as a string. Arrow keys become 'UP', 'DOWN', etc., Enter becomes 'ENTER'."""
        if sys.platform.startswith("win"):
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
            import tty, termios
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                ch = sys.stdin.read(1)
                if ch == '\r' or ch == '\n':
                    return 'ENTER'
                if ch == '\x1b':  # ESC sequence for arrows
                    seq = sys.stdin.read(2)
                    arrows = {'[A': 'UP', '[B': 'DOWN', '[C': 'RIGHT', '[D': 'LEFT'}
                    return arrows.get(seq, '')
                return ch
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)