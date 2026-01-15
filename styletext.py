class StyleText:
    """A class to create basic styled text with ANSI escape codes."""

    RESET = "\033[0m"

    def __init__(self, text: object, prefix: str = "", reset: bool = True):
        self.text = str(text)
        self.prefix = prefix
        self.reset = reset

    def _add(self, code: str, reset: bool) -> "StyleText":
        return StyleText(
            self.text,
            self.prefix + code,
            reset=reset
        )

    # --- styles ---
    def bold(self, reset: bool = True) -> "StyleText":
        return self._add("\033[1m", reset)

    def dim(self, reset: bool = True) -> "StyleText":
        return self._add("\033[2m", reset)

    def italic(self, reset: bool = True) -> "StyleText":
        return self._add("\033[3m", reset)

    def underline(self, reset: bool = True) -> "StyleText":
        return self._add("\033[4m", reset)

    # --- colors ---
    def red(self, reset: bool = True) -> "StyleText":
        return self._add("\033[31m", reset)

    def green(self, reset: bool = True) -> "StyleText":
        return self._add("\033[32m", reset)

    def yellow(self, reset: bool = True) -> "StyleText":
        return self._add("\033[33m", reset)

    def blue(self, reset: bool = True) -> "StyleText":
        return self._add("\033[34m", reset)

    def magenta(self, reset: bool = True) -> "StyleText":
        return self._add("\033[35m", reset)

    def cyan(self, reset: bool = True) -> "StyleText":
        return self._add("\033[36m", reset)

    def white(self, reset: bool = True) -> "StyleText":
        return self._add("\033[37m", reset)

    def __str__(self) -> str:
        if self.reset:
            return f"{self.prefix}{self.text}{self.RESET}"
        return f"{self.prefix}{self.text}"

    def __add__(self, other: str) -> "StyleText":
        if not isinstance(other, str):
            return NotImplemented
        return StyleText(
            self.text + other,
            self.prefix,
            reset=self.reset
        )

    def __radd__(self, other: str) -> "StyleText":
        if not isinstance(other, str):
            return NotImplemented
        return StyleText(
            other + self.text,
            self.prefix,
            reset=self.reset
        )
