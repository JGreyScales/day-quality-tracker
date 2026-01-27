import textwrap
from time import sleep

from dqt.styletext import StyleText as Txt


def err(message: str, *desc: str) -> None:
    """Print formatted error message."""
    print(
        Txt("\nError: ").bold().red()
        + message
    )
    for d in desc:
        print(d)
    sleep(1)


def notify_log_saved(text: str = "Log saved!") -> None:
    """Print formatted message to inform user that log was saved."""
    print("\n" + Txt(text).bold().green())
    sleep(1)


def cont_on_enter(msg: str = "\n[Press ENTER to return to main menu]") -> None:
    """Pause the program until the user presses Enter."""
    input(msg)


def print_wrapped(text: str, maxcol: int):
    """Print line-wrapped text with a maximum of `maxcol` chars per line."""
    print(textwrap.fill(text, maxcol))
    