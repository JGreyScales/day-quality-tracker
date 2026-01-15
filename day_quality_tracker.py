import sys
import os
import subprocess
from time import sleep
from datetime import datetime, timedelta
from collections import defaultdict

from dqt_graph import DQTGraph
from dqt_json import DQTJSON
from styletext import StyleText as Txt

_UNSET = object()


class DayQualityTracker:
    """Track and visualize day quality ratings in a graph."""
    
    def __init__(self):
        """Load saved data, initialize settings and DQTGraph instance."""
        # Initialize settings
        self.min_time = 20  # Earliest hour the of day to enter rating
        self.min_rating = 1  # 1 recommended
        self.max_rating = 20  # Even number recommended
        self.neutral_rating = 10  # Rating for an average day
        self.rating_inp_dp = 3
        
        self.date_format = '%Y-%m-%d'
        self.date_format_print = "YYYY-MM-DD"
        # Format printed time using 12-hour clock if True
        self.clock_format_12 = True
        
        # JSON manager instance
        self.json = DQTJSON(self)
        
        # Graph manager instance
        self.graph = DQTGraph(self)
        
        self.enable_ansi = None
        Txt.set_ansi(self.enable_ansi)
    
    def run(self) -> None:
        """Run Day Quality Tracker."""
        print(Txt("\n*--- Day Quality Tracker! ---*").bold().yellow())
        sleep(1)
        
        choice = self._handle_missing_logs()
        
        if choice in ['1', '3', None]:
            if not self._today_rated():
                self._input_todays_log()
        
        while True:
            print("\n*❖* —————————————————————————————— *❖*")
            print(
                Txt("MAIN MENU").blue().underline().bold(),
                Txt("— choose what to do: ").bold()
            )
            print("1) View ratings [G]raph")
            print("2) Edit [T]oday's log...")
            print("3) Edit [P]revious log...")
            print("4) See [S]tats")
            print("5) View [A]ll logs...")
            print("6) E[x]it")
            
            match input("> ").lower().strip():
                case '1' | 'g':
                    self._view_ratings_graph()
                
                case '2' | 't':
                    if not self._today_rated():
                        print("\n You haven't entered today's log yet!")
                        sleep(1)
                        continue
                    
                    print(Txt("\nToday's log:").bold())
                    today = datetime.today().strftime(self.date_format)
                    self._print_log(
                        date=today,
                        rating=self.json.get_rating(today),
                        memory=self.json.get_memory(today),
                    )
                    
                    while True:
                        print(Txt("\nSelect:"))
                        print("1) Edit [R]ating")
                        print("2) Edit [M]emory entry")
                        print("3) [C]ancel -> Main menu")
                        
                        match input("> ").strip().lower():
                            case '1' | 'r':
                                self._change_todays_rating()
                            case '2' | 'm':
                                self._change_todays_memory()
                            case '3' | 'c':
                                break
                            case _:
                                self._err(
                                    "Only enter 1~3 or the given letters."
                                )
                                continue
                        break
                
                case '3' | 'p':
                    while True:
                        selected_d = self._prompt_prev_date()
                        print(Txt("\nSelected log:").bold())
                        self._print_log(
                            date=selected_d,
                            rating=self.json.get_rating(selected_d),
                            memory=self.json.get_memory(selected_d),
                        )
                        
                        while True:
                            print(Txt("\nSelect:").bold())
                            print("1) Edit [R]ating")
                            print("2) Edit [M]emory entry")
                            print("3) Edit [B]oth")
                            print("4) Reselect [D]ate")
                            print("5) [C]ancel -> Main menu")
                            
                            choice = input("> ").strip().lower()
                            match choice:
                                case '1' | 'r':
                                    self._change_previous_rating(selected_d)
                                case '2' | 'm':
                                    self._change_previous_memory(selected_d)
                                case '3' | 'b':
                                    self._change_previous_rating(selected_d)
                                    self._change_previous_memory(selected_d)
                                case '4' | 'd':
                                    break
                                case '5' | 'c':
                                    break
                                case _:
                                    self._err(
                                        "Only enter 1~5 or the given letters."
                                    )
                                    continue
                            break
                        
                        if choice in ['5', 'c']:
                            break
                
                case '4' | 's':
                    self._show_stats()
                    input("\n[Press ENTER to return to main menu]")
                
                case '5' | 'a':
                    while True:
                        print(Txt("\nSelect:").bold())
                        print("1) [P]rint logs to standard output")
                        print("2) [O]pen JSON file in default viewer/editor")
                        print("3) [C]ancel -> Main menu")
                        
                        choice = input("> ").strip().lower()
                        match choice:
                            case '1' | 'p':
                                self._print_logs_to_stdout()
                            case '2' | 'o':
                                self._open_json_file()
                            case '3' | 'c':
                                break
                            case _:
                                self._err(
                                    "Only enter 1~3 or the given letters."
                                )
                                continue
                        break
                
                case '6' | 'x':
                    print("\nBye!")
                    raise SystemExit()
                
                case _:
                    self._err("Only enter 1~6 or the given letters.")
    
    # ################################################################## #
    # -------------------------- MAIN METHODS -------------------------- #
    # ################################################################## #
    
    # ########################### Upon Entry ########################### #
    
    def _handle_missing_logs(self) -> str | None:
        """Check if any previous days are missing ratings.

        User chooses to enter missing ratings or not. If they do,
        loop through each missing date and prompt rating.
        Return the option the user chose if missed prior dates.
        """
        if not self.json.logs:  # Ignore for first-time runs (empty dict)
            return None
        
        last_date_str = max(self.json.logs.keys())
        last_date = datetime.strptime(last_date_str, self.date_format).date()
        todays_date = datetime.now().date()
        days_since_last = (todays_date - last_date).days
        
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
                    
                    print(Txt("\nLog saved!").green())
                    sleep(1)
                    
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
                    self._err("Only enter a number from 1~3.")
                    continue
    
    def _input_todays_log(self) -> None:
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
                f"{self.neutral_rating} being an average day: "
            )
            
            if (input("\nWould you like to enter a memory entry now? (y/n): ")
                    .strip().lower() != 'y'):
                print("\n'Edit today's log' to enter your memory entry later!")
                tdys_memory = ''
            else:
                tdys_memory = self._input_memory(
                    f"Enter a memory entry; write a few sentences about your "
                    f"day. \nLeave this blank to skip: "
                )
            
            # Save data
            today = datetime.today().strftime(self.date_format)
            self.json.add(today, tdys_rating, tdys_memory)
            print(Txt("\nLog saved!").green())
            sleep(1)
        
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
    
    # ###################### 1) View Ratings Graph ###################### #
    
    def _view_ratings_graph(self) -> None:
        """Display current ratings graph."""
        if not self.json.logs:
            print("\nYou haven't entered any ratings yet!")
            sleep(1)
            return
        
        print("\nBuilding graph...")
        
        self.graph.build()
        
        print("\nDisplaying graph...")
        print("Close the graph window to proceed.")
        
        self.graph.show()
        
        print("\nGraph closed.")
        print("Returning to main menu...")
    
    # ####################### 2) Edit today's log ####################### #
    
    def _change_todays_rating(self) -> None:
        """Prompt the user to change today's rating."""
        if self._today_rated():
            
            today = datetime.today().strftime(self.date_format)
            
            todays_rating = self.json.get_rating(today)
            if todays_rating is None:
                rating_to_show = "[No rating]"
            else:
                rating_to_show = f"{todays_rating}/{self.max_rating}"
            
            print(Txt(f"Rating to change: {rating_to_show}").bold())
            sleep(1)
            
            tdys_rating = self._input_rating(
                "Enter new rating for today "
                f"({self.min_rating}~{self.max_rating}): "
            )
            
            # Save data
            today = datetime.today().strftime(self.date_format)
            self.json.update(date=today, rating=tdys_rating)
            print(Txt("\nRating updated and saved!").green())
            sleep(1)
        
        else:
            print("\nYou haven't entered a rating yet today!")
            sleep(1)
    
    def _change_todays_memory(self) -> None:
        """Prompt the user to change today's memory entry."""
        if self._today_rated():
            
            today = datetime.today().strftime(self.date_format)
            prev_mem = self.json.get_memory(today)
            if not prev_mem:
                prev_mem = "[Empty entry]"
            print(Txt(f"Memory entry to change: ").bold)
            print(prev_mem)
            sleep(1)
            
            tdys_memory = self._input_memory(
                "Enter new memory entry for today: "
            )
            
            # Save data
            today = datetime.today().strftime(self.date_format)
            self.json.update(date=today, memory=tdys_memory)
            print(Txt("\nMemory entry updated and saved!").green())
            sleep(1)
        
        else:
            print("\nYou haven't entered a log yet today!")
            sleep(1)
    
    # ###################### 3) Edit previous log ###################### #
    
    def _prompt_prev_date(self) -> str:
        """Prompt the user to enter a previous date."""
        while True:
            inp = input("\nEnter the number of days ago or exact date "
                        f"('{self.date_format_print}'): ").strip()
            selected_date = None
            
            # If number of days ago specified, get date
            if inp.isdigit():
                inp = int(inp)
                today = datetime.today()
                selected_date = today - timedelta(days=inp)
                selected_date = selected_date.strftime(self.date_format)
                print(Txt(f"Date selected: {selected_date}").bold())
            
            # Else, validate date str
            else:
                try:
                    datetime.strptime(inp, self.date_format)
                except ValueError:
                    self._err("Enter wither a valid date in the "
                              f"format {self.date_format_print} or a positive"
                              "interger.")
                    continue
                selected_date = inp
            
            # Check if date exists in saved ratings
            try:
                self.json.logs[selected_date]
            except KeyError:
                self._err(
                    "Rating for specified date not found.",
                    "Ensure you have already entered a "
                    "rating for that date.",
                    "\nTry again."
                )
                continue
            
            break
        return selected_date
    
    def _change_previous_rating(self, selected_date: str) -> None:
        """Prompt the user to change a rating from a previous day."""
        print(Txt("\nUpdating:").bold())
        self._print_log(
            date=selected_date,
            rating=self.json.get_rating(selected_date)
        )
        new_rating = self._input_rating(
            f"Enter new rating for {selected_date} "
            f"({self.min_rating}~{self.max_rating}): ",
        )
        
        # Save data
        self.json.update(date=selected_date, rating=new_rating)
        print(Txt("\nRating updated and saved!").green())
        sleep(1)
    
    def _change_previous_memory(self, selected_date: str) -> None:
        """Prompt the user to change a memory entry from a previous day."""
        print(Txt("\nUpdating:").bold())
        self._print_log(
            date=selected_date,
            memory=self.json.get_memory(selected_date)
        )
        
        new_memory = self._input_memory(
            f"Enter new memory entry for {selected_date}: "
        )
        
        self.json.update(date=selected_date, memory=new_memory)
        print(Txt("\nMemory entry updated and saved!").green())
        sleep(1)
    
    # ######################## 5) See stats ######################## #
    
    def _show_stats(self) -> None:
        """Show day quality rating stats.
        
        Print:
            - Days rated
            - Average rating
            - Highest rating
            - Lowest rating
            - Days of the week ranked from best to worst
        """
        print(Txt("\nDay Quality Rating Stats:").bold().cyan().underline())
        print()
        
        rating_key = self.json.rating_kyname
        logs = self.json.logs
        
        rated_items: list[tuple[str, float]] = [
            (date, log[rating_key])
            for date, log in logs.items()
            if log[rating_key] is not None
        ]
        
        self._print_days_rated(logs, rated_items)
        
        if not rated_items:
            print("Average rating: N/A")
            print("Highest rating: N/A")
            print("Lowest rating: N/A")
            print("Best days of the week: N/A")
            return
        
        ratings_only = [r for _, r in rated_items]
        
        self._print_average_rating(ratings_only)
        self._print_highest_lowest_rating(ratings_only, rated_items)
        self._print_days_of_the_week_ranked(rated_items)
    
    @staticmethod
    def _print_days_rated(logs: dict[str, dict[str, float | None | str]],
                          rated_items: list[tuple[str, float]]) -> None:
        days_total = len(logs)
        days_rated = len(rated_items)
        
        print(
            f"{Txt("Days rated:").bold()} {Txt(days_rated).bold()} "
            f"({days_total} including null ratings)"
        )
    
    def _print_average_rating(self, ratings_only: list[float]) -> None:
        """Print average rating for each day of the week."""
        avg = round(
            sum(ratings_only) / len(ratings_only),
            self.rating_inp_dp
        )
        print(f"{Txt("Average rating:").bold()} "
              f"{Txt(avg).bold()}/{self.max_rating}")
    
    def _print_highest_lowest_rating(
            self,
            ratings_only: list[float],
            rated_items: list[tuple[str, float]]) -> None:
        highest = max(ratings_only)
        lowest = min(ratings_only)
        
        highest_dates = [
            date for date, rating in rated_items
            if rating == highest
        ]
        
        lowest_dates = [
            date for date, rating in rated_items
            if rating == lowest
        ]
        
        print(
            f"{Txt("Highest rating:").bold()} "
            f"{Txt(highest).bold()}/{self.max_rating} "
            f"on {self._format_dates(highest_dates)}"
        )
        
        print(
            f"{Txt("Lowest rating:").bold()} "
            f"{Txt(lowest).bold()}/{self.max_rating} "
            f"on {self._format_dates(lowest_dates)}"
        )
    
    def _print_days_of_the_week_ranked(
            self, rated_items: list[tuple[str, float]]) -> None:
        """Print the days of the week in rank order of highest avg rating"""
        weekday_scores: dict[str, list[float]] = defaultdict(list)
        
        for date_str, rating in rated_items:
            date = datetime.strptime(date_str, self.date_format)
            weekday = date.strftime("%A")
            weekday_scores[weekday].append(rating)
        
        weekday_averages = {
            day: sum(vals) / len(vals)
            for day, vals in weekday_scores.items()
        }
        
        ranked_days = sorted(
            weekday_averages.items(),
            key=lambda item: item[1],
            reverse=True
        )
        
        print(f"\n{Txt("Best days of the week").bold()} "
              "(highest to lowest average rating):")
        for day, value in ranked_days:
            print(f"\t{Txt(day).bold()}: "
                  f"{Txt(round(value, self.rating_inp_dp)).bold()}"
                  f"/{self.max_rating}")
    
    @staticmethod
    def _format_dates(dates: list[str]) -> str:
        return ", ".join(dates)
    
    # ######################## 5) View all logs ######################## #
    
    def _print_logs_to_stdout(self) -> None:
        """Print last 30 saved logs.

        The user can choose whether to show the rest of the logs.
        """
        
        def _loop_print(items: list):
            print("\n* —————————————————————————————— *")
            for date, log in items:
                print()
                self._print_log(
                    date=date,
                    rating=log[self.json.rating_kyname],
                    memory=log[self.json.memory_kyname]
                )
            print("\n* —————————————————————————————— *")
        
        print("\nLast 30 logs, most recent first:")
        
        if not self.json.logs:
            print("\n[No logs found]")
            return
        
        # Convert dictionary items to a list of tuples
        items_list = list(self.json.logs.items())
        # Get the last 30 items or all items if less than 30
        last_30_items = items_list[-30:]
        # Reverse list to print most recent logs first
        last_30_items.reverse()
        
        _loop_print(last_30_items)
        
        if len(items_list) > 30:
            choice = input("\nShow the rest of the logs? (y/n): ").strip().lower()
            if choice != 'y':
                return
            
            items_until_last_30th = items_list[:-30]
            items_until_last_30th.reverse()
            
            _loop_print(items_until_last_30th)
            
            input("\n[Press ENTER to return to main menu] ")
    
    def _open_json_file(self) -> None:
        """Open the JSON file in the default system applicaiton."""
        print("\nOpening JSON file...")
        
        if sys.platform == "win32":
            os.startfile(self.json.filepath)  # Windows
        elif sys.platform == "darwin":
            subprocess.call(["open", self.json.filepath])  # macOS
        elif sys.platform.startswith("linux"):
            subprocess.call(["xdg-open", self.json.filepath])  # Linux
        else:
            print("\nYou will have to open the file manually. "
                  f"\nPath: {self.json.filepath}")
            print("(Incompatible OS: unable to open the file with the program)")
            return
        
        print(f"File opened in a new window!")
        print("Remember to save changes before closing the file.")
        input("\n[Press ENTER to return to main menu] ")
    
    # ########################################################## #
    # --------------------- HELPER METHODS --------------------- #
    # ########################################################## #
    
    def _today_rated(self) -> bool:
        """Check if a rating has been provided for today."""
        today = datetime.today().strftime(self.date_format)
        return today in self.json.logs
    
    # ################################################################## #
    
    def _print_log(self,
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
                print(Txt(f"Date:").bold() + date)
        
        # ----- Rating -----
        if rating is not _UNSET:
            if rating is None:
                print(f"{Txt("Rating:").bold} [No rating]")
            else:
                print(f"{Txt("Rating:").bold} {rating}/{self.max_rating}")
        
        # ----- Memory -----
        if memory is not _UNSET:
            if memory:
                print(Txt("Memory:").bold)
                print(memory)
            else:
                print("Memory: [Empty entry]")
    
    # ################################################################## #
    
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
                self._err(error_msg)
                continue
            
            if not (self.min_rating <= value <= self.max_rating):
                print(error_msg)
                sleep(1)
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
    
    @staticmethod
    def _err(message: str, *desc: str) -> None:
        """Print formatted error message."""
        print(
            Txt("\nError: ").bold().red()
            + message
        )
        for d in desc:
            print(d)
        sleep(1)
