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
        self.json_name = 'dq_logs.json'
        self.json_name_pre5 = 'dq_ratings.json'
        self.json_path = self.parent_dir / self.json_name
        self.json_path_pre5 = self.parent_dir / self.json_name_pre5

        self.rating_key_name = 'rating'
        self.mem_entry_key_name = 'memory'

        self._touch()

        self.logs = self._load_json()

    def _touch(self) -> None:
        """Check if JSON file exists, create if not."""
        if not self.json_path.exists():
            if self.json_path_pre5.exists():
                self.json_path_pre5.rename(self.json_path)
            else:
                self.json_path.touch()

    def update(self):
        """Dump updated `saved_ratings` dict to JSON file."""
        with open(self.json_path, 'w') as json_file:
            json.dump(self.logs, json_file, indent=4)

    def _load_json(self) -> dict[str, dict[str, float | str]]:
        """Load JSON file contents and return dict.

        Validate dict before returning. If the dict is missing a rating item,
        raise a KeyError. If a memory entry item is missing, add default memory
        entry. If date keys are not in increasing consecutive order, raise a
        ValueError.
        """
        if not self.json_path.exists():
            return {}
        if not self.json_path.read_text().strip():
            return {}

        with open(self.json_path, 'r') as file:
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
                    self.rating_key_name: float(value),
                    self.mem_entry_key_name: ""  # Default to empty mem-entry
                }
                updated = True
                continue

            # ---------- ≥ DQT-5 format ----------
            # { "YYYY-MM-DD": { "rating": rating, "memory": memory entry } }
            if isinstance(value, dict):
                if self.rating_key_name not in value:
                    raise KeyError(f"Missing rating for date {date}")

                rating = float(value[self.rating_key_name])
                memory = value.get(self.mem_entry_key_name, '')

                # Auto-fix missing memory entry
                if self.mem_entry_key_name not in value:
                    updated = True

                validated[date] = {
                    self.rating_key_name: rating,
                    self.mem_entry_key_name: memory
                }
                continue

            # ---------- invalid format ----------
            raise ValueError(f"Invalid log format for date {date}")

        # Sync JSON if any fixes were applied
        if updated:
            with open(self.json_path, 'w') as file:
                json.dump(validated, file, indent=4)

        return validated
