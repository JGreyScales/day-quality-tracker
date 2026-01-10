import json
from pathlib import Path
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from day_quality_tracker import DayQualityTracker


class DQTJSON:
    """A class to manage Day Quality Tracker JSON contents handling."""

    def __init__(self, dqt: DayQualityTracker):
        self.dqt = dqt
        self.date_format = self.dqt.date_format

        self.parent_dir = Path(__file__).resolve().parent
        self.filename = 'dq_logs.json'
        self.filepath = self.parent_dir / self.filename
        self.filename_pre5 = 'dq_ratings.json'
        self.filepath_pre5 = self.parent_dir / self.filename_pre5

        self.rating_kyname = 'rating'
        self.memory_kyname = 'memory'

        self._touch()

        self.logs = self._load_json()

    def update(self):
        """Dump updated `saved_ratings` dict to JSON file."""
        with open(self.filepath, 'w') as json_file:
            json.dump(self.logs, json_file, indent=4)

    def get_rating(self, date: str) -> float | None:
        return self.logs[date][self.rating_kyname]

    def get_memory(self, date: str) -> str:
        return self.logs[date][self.memory_kyname]

    def _touch(self) -> None:
        """Check if JSON file exists, create if not."""
        if not self.filepath.exists():
            if self.filepath_pre5.exists():
                self.filepath_pre5.rename(self.filepath)
            else:
                self.filepath.touch()

    def _load_json(self) -> dict[str, dict[str, float | str]]:
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
        validated: dict[str, dict[str, float | str]] = {}

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

                rating = float(value[self.rating_kyname])
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
            with open(self.filepath, 'w') as file:
                json.dump(validated, file, indent=4)

        return validated
