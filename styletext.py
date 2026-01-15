class StyleText:
    """A class to create basic styled text with ANSI escape codes."""

    RESET = "\033[0m"

    def __init__(self, text: object, prefix: str = ""):
        self.text = str(text)
        self.prefix = prefix

    def _add(self, code: str) -> StyleText:
        return StyleText(self.text, self.prefix + code)

    def bold(self) -> StyleText:
        return self._add("\033[1m")

    def dim(self) -> StyleText:
        return self._add("\033[2m")

    def italic(self) -> StyleText:
        return self._add("\033[3m")

    def underline(self) -> StyleText:
        return self._add("\033[4m")

    def red(self) -> StyleText:
        return self._add("\033[31m")

    def green(self) -> StyleText:
        return self._add("\033[32m")

    def yellow(self) -> StyleText:
        return self._add("\033[33m")

    def blue(self) -> StyleText:
        return self._add("\033[34m")

    def magenta(self) -> StyleText:
        return self._add("\033[35m")

    def cyan(self) -> StyleText:
        return self._add("\033[36m")

    def white(self) -> StyleText:
        return self._add("\033[37m")

    def __str__(self) -> str:
        return f"{self.prefix}{self.text}{self.RESET}"
    
    def __add__(self, other: str) -> "StyleText":
        if not isinstance(other, str):
            return NotImplemented
        
        combined = f"{self.prefix}{self.text}{self.RESET}{other}"
        return StyleText(combined)
    
    def __radd__(self, other: str) -> "StyleText":
        if not isinstance(other, str):
            return NotImplemented
        
        combined = f"{other}{self.prefix}{self.text}{self.RESET}"
        return StyleText(combined)

