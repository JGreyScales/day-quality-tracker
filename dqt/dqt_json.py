import json
import sys
import os
import subprocess
import textwrap
from pathlib import Path
from datetime import datetime
from typing import TYPE_CHECKING

from dqt.styletext import StyleText as Txt
from dqt.ui_utils import cont_on_enter

if TYPE_CHECKING:
    from tracker import Tracker

_UNSET = object()
_today = datetime.today()


class DQTJSON:
    """A class to manage Day Quality Tracker JSON contents handling."""
    
    _CONFIG_KEYS = {
        "filedirname",
        "filedirpath",
        "filename",
        "filepath",
        "json_indent",
        "rating_kyname",
        "memory_kyname",
    }

    def __init__(self, dqt: Tracker):
        """Initialize attributes."""
        self.dqt = dqt
        self.date_format = self.dqt.date_format
        
        self.filedirname = 'data'
        self.filedirpath = (Path(__file__).resolve().parent.parent
                            / self.filedirname)
        self.filename = 'dq_logs.json'
        self.filepath = self.filedirpath / self.filename
        self._filename_pre5 = 'dq_ratings.json'
        self._filepath_pre5 = self.filedirpath / self._filename_pre5

        self.rating_kyname = 'rating'
        self.memory_kyname = 'memory'

        self.json_indent = 4
        
        self.memory_print_linewrap_maxcol = 60
        
        self._touch()

        self.logs = self._load_json()

    def update(self,
               date: str = None,
               rating: float | None = _UNSET,
               memory: str = _UNSET) -> None:
        """Dump updated logs to JSON file.

        Update with new rating and memory values if provided before dumping.
        Attempted creation of new items will raise a KeyError. Use extend()
        instead to add a new log.
        """
        if date is None:
            if rating is not _UNSET or memory is not _UNSET:
                raise ValueError("Missing date argument")
            return
        if date not in self.logs:
            raise KeyError(f"Date '{date}' not found.")
        if rating is not _UNSET:
            self.logs[date][self.rating_kyname] = rating
        if memory is not _UNSET:
            self.logs[date][self.memory_kyname] = memory

        self._dump()

    def add(self,
            date: str,
            rating: float | None = None,
            memory: str = '') -> None:
        """Update logs with new log and dump to JSON file.

        Attempted rewrite of previous items will raise a KeyError.
        Use extend() instead to add a new log.

        It is recommended to explicitly provide both rating and memory
        arguments, even if it is equal to the default value.
        """
        if date in self.logs:
            raise KeyError(f"Log with date '{date}' already exists.")

        self.logs[date] = {
            self.rating_kyname: rating,
            self.memory_kyname: memory
        }

        self._dump()

    def get_rating(self, date: str) -> float | None:
        """Return rating for given date."""
        return self.logs[date][self.rating_kyname]

    def get_memory(self, date: str) -> str:
        """Return memory entry for given date."""
        return self.logs[date][self.memory_kyname]
    
    def today_rated(self) -> bool:
        """Check if a rating has been provided for today."""
        today = _today.strftime(self.date_format)
        return today in self.logs
    
    def print_log(self,
                  date: str = _UNSET,
                  rating: float | None = _UNSET,
                  memory: str = _UNSET) -> None:
        """Print a formatted log, and represent 'empty' values with text.

        Null (None) ratings are printed as "[No rating]".
        Empty memory entries (empty str) are printed as "[Empty entry]".

        If date is unfilled, it will not be printed.
        If date == 'today', "Today's log:" will be printed at the start.
        Else, f"Date: {date}" will be printed.
        """
        
        # ----- Date -----
        if date is not _UNSET:
            if date == 'today':
                print(Txt("\nToday's log:").bold().yellow())
            else:
                print(Txt(f"Date: ").bold() + date)
        
        # ----- Rating -----
        if rating is not _UNSET:
            if rating is None:
                print(Txt("Rating: ").bold() + "-")
            else:
                print(
                    f"{Txt("Rating:").bold()}",
                    f"{rating:g}/{self.dqt.max_rating}"
                )
        
        # ----- Memory -----
        if memory is not _UNSET:
            if memory:
                print(Txt("Memory:").bold())
                print(textwrap.fill(memory, self.memory_print_linewrap_maxcol))
            else:
                print(Txt("Memory: ").bold() + "-")
    
    def print_logs_to_stdout(self) -> None:
        """Print last 30 saved logs.

        The user can choose whether to show the rest of the logs.
        """
        
        def _loop_print(items: list):
            print("\n* —————————————————————————————— *")
            for date, log in items:
                print()
                self.print_log(
                    date=date,
                    rating=log[self.rating_kyname],
                    memory=log[self.memory_kyname]
                )
            print("\n* —————————————————————————————— *")
        
        print("\nLast 30 logs, most recent last:")
        
        if not self.logs:
            print("\n[No logs found]")
            return
        
        # Convert dictionary items to a list of tuples
        items_list = list(self.logs.items())
        # Get the last 30 items or all items if less than 30
        last_30_items = items_list[-30:]
        
        _loop_print(last_30_items)
        
        if len(items_list) > 30:
            choice = input("\nShow the rest of the logs? (y/n): ").strip().lower()
            if choice != 'y':
                return
            
            items_until_last_30th = items_list[:-30]
            items_until_last_30th.reverse()
            
            _loop_print(items_until_last_30th)
        
        cont_on_enter()
            
    def open_json_file(self) -> None:
        """Open the JSON file in the default system applicaiton."""
        print("\nOpening JSON file...")
        
        if sys.platform == "win32":
            os.startfile(self.filepath)  # Windows
        elif sys.platform == "darwin":
            subprocess.call(["open", self.filepath])  # macOS
        elif sys.platform.startswith("linux"):
            subprocess.call(["xdg-open", self.filepath])  # Linux
        else:
            print("\nYou will have to open the file manually. "
                  f"\nPath: {self.filepath}")
            print("(Incompatible OS: unable to open the file with the program)")
            return
        
        print(f"File opened in a new window!")
        print("Remember to save changes before closing the file.")
        
    def configure(self, **kwargs) -> None:
        """Update configuration options via keyword arguments."""
        for key, value in kwargs.items():
            if key not in self._CONFIG_KEYS:
                raise ValueError(f"Unknown configuration option: '{key}'")
            setattr(self, key, value)

    def _touch(self) -> None:
        """Check if JSON file exists, create if not."""
        if not self.filepath.exists():
            if self._filepath_pre5.exists():
                self._filepath_pre5.rename(self.filepath)
            else:
                self.filepath.touch()

    def _load_json(self) -> dict[str, dict[str, float | None | str]]:
        """Load JSON file contents and return dict.

        Validate dict before returning. If the dict is missing a rating item,
        raise a KeyError. If a memory entry item is missing, add default memory
        entry. If date keys are not in increasing consecutive order, raise a
        ValueError.
        """
        if not self.filepath.exists():
            return {}
        if not self.filepath.read_text().strip():
            return {}

        with open(self.filepath, 'r') as file:
            contents = json.load(file)

        updated = False
        prev_date = None
        validated: dict[str, dict[str, float | None | str]] = {}

        for date, value in contents.items():

            # Validate date keys
            if prev_date is not None:
                prev_d = datetime.strptime(prev_date, self.date_format)
                d = datetime.strptime(date, self.date_format)
                diff = (d - prev_d).days
                if diff < 0:
                    raise ValueError(
                        f"Date {date} is older than previous date {prev_date}"
                    )
                if diff == 0:
                    raise ValueError(
                        f"Date {prev_date} is repeated"
                    )

            prev_date = date

            # ---------- pre-DQT-5 format ----------
            # { "YYYY-MM-DD": rating }
            if isinstance(value, (int, float)):
                validated[date] = {
                    self.rating_kyname: float(value),
                    self.memory_kyname: ""  # Default to empty mem-entry
                }
                updated = True
                continue

            # ---------- ≥ DQT-5 format ----------
            # { "YYYY-MM-DD": { "rating": rating, "memory": memory entry } }
            if isinstance(value, dict):
                if self.rating_kyname not in value:
                    raise KeyError(f"Missing rating for date {date}")

                raw_rating = value[self.rating_kyname]  # Handle null ratings
                rating = None if raw_rating is None else float(raw_rating)
                memory = value.get(self.memory_kyname, '')

                # Auto-fix missing memory entry
                if self.memory_kyname not in value:
                    updated = True

                validated[date] = {
                    self.rating_kyname: rating,
                    self.memory_kyname: memory
                }
                continue

            # ---------- invalid format ----------
            raise ValueError(f"Invalid log format for date {date}")

        # Sync JSON if any fixes were applied
        if updated:
            self._dump()

        return validated

    def _dump(self) -> None:
        """Dump JSON file contents."""
        with open(self.filepath, 'w') as file:
            json.dump(self.logs, file, indent=self.json_indent)
