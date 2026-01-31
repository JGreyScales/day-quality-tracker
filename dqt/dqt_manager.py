from textwrap import dedent
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from dqt.ui_utils import err, notify_log_saved, print_wrapped
from dqt.styletext import StyleText as Txt

if TYPE_CHECKING:
    from tracker import Tracker

_today = datetime.today()


class Manager:
    """A class to manage Day Quality Tracker JSON contents handling."""
    
    def __init__(self, dqt: Tracker):
        self.dqt = dqt
        self.json = dqt.json
    
    def handle_missing_logs(self) -> str | None:
        """Check if any previous days are missing ratings.

        User chooses to enter missing ratings or not. If they do,
        loop through each missing date and prompt rating.
        Return the option the user chose if missed prior dates.
        """
        if not self.dqt.json.logs:  # Ignore for first-time runs (empty dict)
            return None
        
        last_date_str = max(self.dqt.json.logs.keys())
        last_date = datetime.strptime(
            last_date_str, self.dqt.date_format
        ).date()
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
                            f"({self.dqt.min_rating}~{self.dqt.max_rating}, "
                            f"or 'null' to skip): ",
                        )
                        
                        memory = self._input_memory(
                            "Enter a memory entry (leave blank to skip): "
                        )
                        
                        date_str = datetime.strftime(date, self.dqt.date_format)
                        
                        self.json.add(date_str, rating, memory)
                    
                    notify_log_saved()
                    
                    return choice
                
                case '2':
                    print_wrapped(
                        "\nRestart the program later to enter your missing "
                        "logs! (You can only enter today's log after "
                        "entering the missed logs, unless you choose to skip "
                        "them.)",
                        self.dqt.linewrap_maxcol
                    )
                    
                    return choice
                
                case '3':
                    print_wrapped(
                        "\nYou will have to enter the missed logs later "
                        f"manually in `{self.json.filename}`, unless you "
                        "don't enter today's log yet."
                        "\nYou can open the file by selecting:"
                        "\nMain menu -> 4) View [A]ll logs "
                        "-> 2) [O]pen JSON file in default viewer/editor"
                        "\nMake sure you save any changed before closing "
                        "the file.",
                        self.dqt.linewrap_maxcol
                    )
                    
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
        if datetime.now().time().hour >= self.dqt.min_time:
            if (input("\nWould you like to enter today's log now? (y/n): ")
                    .strip().lower() != 'y'):
                print("\nRerun the program later to enter your log!")
                return
            
            tdys_rating = self._input_rating(
                f"Rate your day from {self.dqt.min_rating} to "
                f"{self.dqt.max_rating}, {self.dqt.neutral_rating} being an "
                f"average day "
                f"\n(enter 'null' to skip): "
            )
            
            if (input("\nWould you like to enter a memory entry? (y/n): ")
                    .strip().lower() != 'y'):
                print(
                    "\nTo enter your memory entry later: "
                    "\nMain menu -> Edit today's/previous log -> Edit memory"
                )
                tdys_memory = ''
            else:
                tdys_memory = self._input_memory(
                    f"Enter a memory entry; write a few sentences about your "
                    f"day. \nLeave this blank to skip: "
                )
            
            # Save data
            today = _today.strftime(self.dqt.date_format)
            self.json.add(today, tdys_rating, tdys_memory)
            notify_log_saved()
        
        else:
            # Format time in 12-hour or 24-hour clock
            if self.dqt.clock_format_12:
                hour = self.dqt.min_time % 12 \
                    if self.dqt.min_time % 12 != 0 \
                    else 12
                suffix = 'AM' if self.dqt.min_time < 12 else 'PM'
                formatted_time = f"{hour} {suffix}"
            else:
                formatted_time = str(self.dqt.min_time)
            
            print(f"\nYou can only input today's log after {formatted_time}.")
            print("\nCome back later to enter today's log!")
    
    def change_todays_rating(self) -> None:
        """Prompt the user to change today's rating."""
        self._change_data('today', self.json.rating_kyname)
    
    def change_todays_memory(self) -> None:
        """Prompt the user to change today's memory entry."""
        self._change_data('today', self.json.memory_kyname)
    
    def prompt_prev_date(self) -> str:
        """Prompt the user to enter a previous date."""
        while True:
            inp = input("\nEnter the number of days ago or exact date "
                        f"('{self.dqt.date_format_print}'): ").strip()
            selected_date = None
            
            # If number of days ago specified, get date
            if inp.isdigit():
                inp = int(inp)
                selected_date = _today - timedelta(days=inp)
                selected_date = selected_date.strftime(self.dqt.date_format)
                print(Txt(f"Date selected: {selected_date}").bold())
            
            # Else, validate date str
            else:
                try:
                    datetime.strptime(inp, self.dqt.date_format)
                except ValueError:
                    err("Enter wither a valid date in the "
                        f"format {self.dqt.date_format_print} or a positive "
                        "integer.")
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
        self._change_data(selected_date, self.json.rating_kyname)
    
    def change_previous_memory(self, selected_date: str) -> None:
        """Prompt the user to change a memory entry from a previous day."""
        self._change_data(selected_date, self.json.memory_kyname)
    
    def _change_data(self, selected_date: str, changing: str) -> None:
        """Change data for the selected date and update JSON.
        
        If the specified date is the string 'today', today's date (or rather,
        the date specified in the global variable `_today`, which is evaluated
        at the start of runtime) will be used.
        
        Parameter `changing` must be either the rating or memory key name
        specified in DQTJSON (raises a ValueError otherwise).
        """
        if changing not in [self.json.rating_kyname, self.json.memory_kyname]:
            raise ValueError(
                f"Parameter 'changing' must be '{self.json.rating_kyname}' "
                f"or '{self.json.memory_kyname}'"
            )
        if selected_date == 'today':
            selected_date = _today.strftime(self.dqt.date_format)
        
        # Changing rating
        if changing == self.json.rating_kyname:
            new_rating = self._input_rating(
                f"Enter new rating for {selected_date} "
                f"({self.dqt.min_rating}~{self.dqt.max_rating}): ",
            )
            self.json.update(date=selected_date, rating=new_rating)
            notify_log_saved("Rating updated and saved!")
        # Changing memory entry
        else:
            tmp = self.dqt.memory_edit_placeholder
            #  ^ Cuz the variable attribute name is way too long
            new_memory = self._input_memory(dedent(f"""
                Enter new memory entry for {selected_date}.
                
                You can copy and paste from your original entry above.
                
                To insert your original memory entry into your edit,
                use curly brackets ({tmp}).

                For example:
                  * To append to the end of your original entry, input:
                      → {tmp} This is a new sentence.
                  * To append to the start of your original entry, input:
                      → This is a new sentence. {tmp}
                  * To append around your original entry, input:
                      → This is a new sentence. {tmp} This is another sentence.

                (The program replaces the first occurrence of '{tmp}' in your
                input with your original entry)
            """))
            original_mem = (
                self.json.logs[selected_date][self.json.memory_kyname]
            )
            new_memory = self._resolve_memory_edit(new_memory, original_mem)
            self.json.update(date=selected_date, memory=new_memory)
            notify_log_saved("Memory entry updated and saved!")
    
    def _resolve_memory_edit(self, mem_input: str, original_mem: str) -> str:
        """Replace the first instance of the placeholder with the original."""
        if self.dqt.memory_edit_placeholder in mem_input:
            print("\n(Original memory entry has been inserted into your edit)")
            return mem_input.replace(
                self.dqt.memory_edit_placeholder, original_mem, 1
            )
        return mem_input
    
    def _input_rating(self, prompt: str) -> float | None:
        """Get and validate user float input."""
        error_msg = (
            f"Please enter a valid number from "
            f"{self.dqt.min_rating} to {self.dqt.max_rating}."
        )
        
        while True:
            raw = input(f"\n{prompt}").lower().strip()
            
            if raw in ['null', '-']:
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
            
            if not (self.dqt.min_rating <= value <= self.dqt.max_rating):
                err(error_msg)
                continue
            
            return round(value, self.dqt.rating_inp_dp)
    
    @staticmethod
    def _input_memory(prompt: str) -> str:
        """Prompt user for today's memory entry."""
        while True:
            tdys_mem = input(
                f"\n{prompt}\n\n->: "
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
