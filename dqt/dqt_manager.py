from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from dqt.ui_utils import err, notify_log_saved
from dqt.styletext import StyleText as Txt

if TYPE_CHECKING:
    from tracker import Tracker
    
_today = datetime.today()


class Manager:
    """A class to manage Day Quality Tracker JSON contents handling."""
    
    def __init__(self, dqt: Tracker):
        self.dqt = dqt
        self.json = dqt.json
        
        self.date_format = self.dqt.date_format
        self.date_format_print = self.dqt.date_format_print
        self.min_rating = self.dqt.min_rating
        self.max_rating = self.dqt.max_rating
        self.neutral_rating = self.dqt.neutral_rating
        self.rating_inp_dp = self.dqt.rating_inp_dp
        self.min_time = self.dqt.min_time
        self.clock_format_12 = self.dqt.clock_format_12
    
    def handle_missing_logs(self) -> str | None:
        """Check if any previous days are missing ratings.

        User chooses to enter missing ratings or not. If they do,
        loop through each missing date and prompt rating.
        Return the option the user chose if missed prior dates.
        """
        if not self.dqt.json.logs:  # Ignore for first-time runs (empty dict)
            return None
        
        last_date_str = max(self.dqt.json.logs.keys())
        last_date = datetime.strptime(last_date_str, self.date_format).date()
        days_since_last = (_today.date() - last_date).days
        
        if days_since_last <= 1:
            return None
        
        # Else:
        print(f"\nYou haven't logged data since {last_date} (last log).")
        
        while True:
            print(Txt("\nChoose what to do:").bold())
            print("1) Enter missing logs now")
            print("2) Enter missing logs later -> Main menu")
            print("3) Skip missing logs -> Enter today's log")
            
            choice = input("> ").strip()
            
            match choice:
                
                case '1':
                    # Get list of missed dates
                    missed_dates = []
                    curr_loop_date = last_date + timedelta(days=1)
                    #                               Exclude today
                    while len(missed_dates) < days_since_last - 1:
                        missed_dates.append(curr_loop_date)
                        curr_loop_date += timedelta(days=1)
                    
                    for date in missed_dates:
                        rating = self._input_rating(
                            f"Enter your rating for {date} "
                            f"({self.min_rating}~{self.max_rating}, "
                            f"or 'null' to skip): ",
                        )
                        
                        memory = self._input_memory(
                            "Enter a memory entry (leave blank to skip): "
                        )
                        
                        date_str = datetime.strftime(date, self.date_format)
                        
                        self.json.add(date_str, rating, memory)
                    
                    notify_log_saved()
                    
                    return choice
                
                case '2':
                    print("\nRestart the program later to enter your missing "
                          "logs!")
                    print("(You can only enter today's log after entering the "
                          "missed logs, unless you choose to skip them.)")
                    
                    return choice
                
                case '3':
                    print("\nYou will have to enter the missed logs later "
                          f"manually in `{self.json.filename}`, unless you "
                          f"don't enter today's log yet.")
                    print("You can open the file by selecting:")
                    print("Main menu -> 4) View [A]ll logs "
                          "-> 2) [O]pen JSON file in default viewer/editor")
                    print("Make sure you save any changed before closing "
                          "the file.")
                    
                    return choice
                
                case _:
                    err("Only enter a number from 1~3.")
                    continue
    
    def input_todays_log(self) -> None:
        """Get today's rating and memory entry if not entered yet.

        Reject if the specified earliest time to collect data has not
        passed yet.
        """
        print("\n*❖* —————————————————————————————— *❖*")
        if datetime.now().time().hour >= self.min_time:
            if (input("\nWould you like to enter today's log now? (y/n): ")
                    .strip().lower() != 'y'):
                print("\nRerun the program later to enter your log!")
                return
            
            tdys_rating = self._input_rating(
                f"Rate your day from {self.min_rating} to {self.max_rating}, "
                f"{self.neutral_rating} being an average day "
                f"\n(enter 'null' to skip): "
            )
            
            if (input("\nWould you like to enter a memory entry? (y/n): ")
                    .strip().lower() != 'y'):
                print(
                    "\nTo enter your memory entry later: "
                    "Main menu -> Edit today's/previous log -> Edit memory"
                )
                tdys_memory = ''
            else:
                tdys_memory = self._input_memory(
                    f"Enter a memory entry; write a few sentences about your "
                    f"day. \nLeave this blank to skip: "
                )
            
            # Save data
            today = _today.strftime(self.date_format)
            self.json.add(today, tdys_rating, tdys_memory)
            notify_log_saved()
        
        else:
            # Format time in 12-hour or 24-hour clock
            if self.clock_format_12:
                hour = self.min_time % 12 if self.min_time % 12 != 0 else 12
                suffix = 'AM' if self.min_time < 12 else 'PM'
                formatted_time = f"{hour} {suffix}"
            else:
                formatted_time = str(self.min_time)
            
            print(f"\nYou can only input today's log after {formatted_time}.")
            print("\nCome back later to enter today's log!")
        
    def change_todays_rating(self) -> None:
        """Prompt the user to change today's rating."""
        tdys_rating = self._input_rating(
            "Enter new rating for today "
            f"({self.min_rating}~{self.max_rating}): "
        )
        # Save data
        today = _today.strftime(self.date_format)
        self.json.update(date=today, rating=tdys_rating)
        notify_log_saved("Rating updated and saved!")
        
    def change_todays_memory(self) -> None:
        """Prompt the user to change today's memory entry."""
        tdys_memory = self._input_memory(
            "Enter new memory entry for today: "
        )
        # Save data
        today = _today.strftime(self.date_format)
        self.json.update(date=today, memory=tdys_memory)
        notify_log_saved("Memory entry updated and saved!")
        
    def prompt_prev_date(self) -> str:
        """Prompt the user to enter a previous date."""
        while True:
            inp = input("\nEnter the number of days ago or exact date "
                        f"('{self.date_format_print}'): ").strip()
            selected_date = None
            
            # If number of days ago specified, get date
            if inp.isdigit():
                inp = int(inp)
                selected_date = _today - timedelta(days=inp)
                selected_date = selected_date.strftime(self.date_format)
                print(Txt(f"Date selected: {selected_date}").bold())
            
            # Else, validate date str
            else:
                try:
                    datetime.strptime(inp, self.date_format)
                except ValueError:
                    err("Enter wither a valid date in the "
                        f"format {self.date_format_print} or a positive "
                        "interger.")
                    continue
                selected_date = inp
            
            # Check if date exists in saved ratings
            try:
                self.json.logs[selected_date]
            except KeyError:
                err(
                    "Rating for specified date not found.",
                    "Ensure you have already entered a "
                    "rating for that date.",
                    "\nTry again."
                )
                continue
            
            break
        return selected_date
    
    def change_previous_rating(self, selected_date: str) -> None:
        """Prompt the user to change a rating from a previous day."""
        new_rating = self._input_rating(
            f"Enter new rating for {selected_date} "
            f"({self.min_rating}~{self.max_rating}): ",
        )
        
        # Save data
        self.json.update(date=selected_date, rating=new_rating)
        notify_log_saved("Rating updated and saved!")
    
    def change_previous_memory(self, selected_date: str) -> None:
        """Prompt the user to change a memory entry from a previous day."""
        new_memory = self._input_memory(
            f"Enter new memory entry for {selected_date}: "
        )
        
        self.json.update(date=selected_date, memory=new_memory)
        notify_log_saved("Memory entry updated and saved!")
    
    def _input_rating(self, prompt: str) -> float | None:
        """Get and validate user float input."""
        error_msg = (
            f"Please enter a valid number from "
            f"{self.min_rating} to {self.max_rating}."
        )
        
        while True:
            raw = input(f"\n{prompt}").lower().strip()
            
            if raw == 'null':
                if input(
                        "\nAre you sure you want to enter an empty (null) rating? (y/n): "
                ).lower().strip() == 'y':
                    return None
                continue
            
            try:
                value = float(raw)
            except ValueError:
                err(error_msg)
                continue
            
            if not (self.min_rating <= value <= self.max_rating):
                err(error_msg)
                continue
            
            return round(value, self.rating_inp_dp)
    
    @staticmethod
    def _input_memory(prompt: str) -> str:
        """Prompt user for today's memory entry."""
        while True:
            tdys_mem = input(
                f"\n{prompt}\n\n"
            ).strip()
            
            if not tdys_mem:
                if input(
                        "\nAre you sure you want to enter an empty memory "
                        "entry? (y/n): "
                ).lower().strip() == 'y':
                    return tdys_mem
                continue
            break
        
        return tdys_mem
    