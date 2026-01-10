import sys
import os
import subprocess
from time import sleep
from datetime import datetime, timedelta

from dqt_graph import DQTGraph
from dqt_json import DQTJSON


class DayQualityTracker:
    """Track and visualize day quality ratings in a graph."""

    def __init__(self):
        """Load saved data, initialize settings and DQTGraph instance."""
        # Initialize settings
        self.min_time = 20  # Earliest hour the of day to enter rating
        self.min_rating = 1  # 1 recommended
        self.max_rating = 20
        self.median_rating = 10  # Rating for an average day
        self.rating_inp_dp = 3

        self.date_format = '%Y-%m-%d'
        self.date_format_print = "YYYY-MM-DD"
        # Format printed time using 12-hour clock if True
        self.clock_format_12 = True

        # JSON manager instance
        self.json = DQTJSON(self)

        # Graph manager instance
        self.graph = DQTGraph(self)

    def run(self) -> None:
        """Run Day Quality Tracker."""
        print("\n*--- Day Quality Tracker! ---*")
        sleep(1)

        choice = self._handle_missing_logs()

        if choice in ['1', '3', None]:
            if not self._today_rated():
                self._input_todays_log()

        while True:
            print("\nMAIN MENU — choose what to do: ")
            print("1) View ratings [G]raph")
            print("2) Edit [T]oday's log...")
            print("3) Edit [P]revious log...")
            print("4) View [A]ll logs...")
            print("5) E[x]it")

            match input("> ").lower().strip():
                case '1' | 'g':
                    self._view_ratings_graph()

                case '2' | 't':
                    print("\nToday's log:")
                    today = datetime.today().strftime(self.date_format)
                    print(f"Rating: "
                          f"{self.json.get_rating(today)}/{self.max_rating}")
                    print("Memory:")
                    print(self.json.get_memory(today))

                    while True:
                        print("\nSelect:")
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
                                print("\nError: Only enter 1~3 "
                                      "or the given letters.")
                                sleep(1)
                                continue
                        break

                case '3' | 'p':
                    while True:
                        selected_d = self._prompt_prev_date()
                        print("\nSelected log:")
                        print(f"Date: {selected_d}")
                        print(f"Rating:"
                              f"{self.json.get_rating(selected_d)}"
                              f"/{self.max_rating}")
                        print("Memory:")
                        print(self.json.get_memory(selected_d))

                        while True:
                            print("\nSelect:")
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
                                    print("\nError: Only enter 1~5 "
                                          "or the given letters.")
                                    sleep(1)
                                    continue
                            break

                        if choice in ['5', 'c']:
                            break

                case '4' | 'a':
                    while True:
                        print("\nSelect:")
                        print("1) [P]rint logs to standard output")
                        print("2) [O]pen JSON file in default viewer/editor")
                        print("3) [C]ancel -> Main menu")

                        choice = input("> ").strip().lower()
                        match choice:
                            case '1' | 'p':
                                self._print_logs()
                            case '2' | 'o':
                                self._open_json_file()
                            case '3' | 'c':
                                break
                            case _:
                                print("\nError: Only enter 1~3 "
                                      "or the given letters.")
                                sleep(1)
                                continue
                        break

                case '5' | 'x':
                    print("\nBye!")
                    raise SystemExit()

                case _:
                    print("\nError: Only enter 1~5 or the given letters.")
                    sleep(1)

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
            print("\nChoose what to do:")
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

                    new_ratings = {}
                    for date in missed_dates:
                        rating = self._input_rating(
                            f"Enter your rating for {date} "
                            f"({self.min_rating}~{self.max_rating}): ",
                        )

                        memory = self._input_memory(
                            "Enter a memory entry (leave blank to skip): "
                        )

                        date_str = datetime.strftime(date, self.date_format)

                        new_ratings[date_str] = {
                            self.json.rating_kyname: rating,
                            self.json.memory_kyname: memory
                        }

                    self.json.logs.update(new_ratings)
                    self.json.update()
                    print("\nLog saved!")
                    sleep(1)

                    return choice

                case '2':
                    print("\nRestart the program later to enter your missing "
                          "logs!")

                    return choice

                case '3':
                    print("\nYou will have to enter the missed logs later "
                          "manually in `dq_logs.json`.")

                    return choice

                case _:
                    print("\nError: Only enter a number from 1~3.")
                    sleep(1)
                    continue

    def _input_todays_log(self) -> None:
        """Get today's rating and memory entry if not entered yet.

        Reject if the specified earliest time to collect data has not
        passed yet.
        """
        if datetime.now().time().hour >= self.min_time:
            if (input("\nWould you like to enter today's log now? (y/n): ")
                    .strip().lower() != 'y'):
                print("\nRerun the program later to enter your log!")
                return

            tdys_rating = self._input_rating(
                f"Rate your day from {self.min_rating} to {self.max_rating}, "
                f"{self.median_rating} being an average day: "
            )

            if (input("\nWould you like to enter a memory entry now? (y/n): ")
                    .strip().lower() != 'y'):
                print("\n'Edit today's log' to enter your memory entry later!")
                tdys_memory = ''
            else:
                tdys_memory = self._input_memory(
                    f"Enter a memory entry; write a few sentences about your day."
                    f"\nLeave this blank to skip: "
                )

            # Save data
            today = datetime.today().strftime(self.date_format)
            self._update_logs(today, tdys_rating, tdys_memory)
            print("\nLog saved!")
            sleep(1)

        else:
            # Format time in 12-hour or 24-hour clock
            if self.clock_format_12:
                hour = self.min_time % 12 if self.min_time % 12 != 0 else 12
                suffix = 'AM' if self.min_time < 12 else 'PM'
                formatted_time = f"{hour} {suffix}"
            else:
                formatted_time = str(self.min_time)

            print(f"\nYou can only input data after {formatted_time}.")
            print("\nCome back later!")

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

    # ####################### 2) Edit today's log ####################### #

    def _change_todays_rating(self) -> None:
        """Prompt the user to change today's rating."""
        if self._today_rated():

            today = datetime.today().strftime(self.date_format)
            print(
                f"Rating to change: ",
                self.json.get_rating(today),
            )
            sleep(1)

            tdys_rating = self._input_rating(
                "Enter new rating for today "
                f"({self.min_rating}~{self.max_rating}): "
            )

            # Save data
            today = datetime.today().strftime(self.date_format)
            self.json.logs[today][self.json.rating_kyname] = tdys_rating
            self.json.update()
            print("\nRating updated and saved!")
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
                prev_mem = "(No entry)"
            print(f"Memory entry to change: ")
            print(prev_mem)
            sleep(1)

            tdys_memory = self._input_memory(
                "Enter new memory entry for today: "
            )

            # Save data
            today = datetime.today().strftime(self.date_format)
            self.json.logs[today][self.json.memory_kyname] = tdys_memory
            self.json.update()
            print("\nMemory entry updated and saved!")
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
                print(f"Date selected: {selected_date}")

            # Else, validate date str
            else:
                try:
                    datetime.strptime(inp, self.date_format)
                except ValueError:
                    print("\nError: Enter wither a valid date in the "
                          f"format {self.date_format_print} or a positive"
                          "interger.")
                    sleep(1)
                    continue
                selected_date = inp

            # Check if date exists in saved ratings
            try:
                self.json.logs[selected_date]
            except KeyError:
                print("\nError: Rating for specified date not found.")
                print("Ensure you have already entered a "
                      "rating for that date.")
                print("\nTry again.")
                sleep(1)
                continue

            break
        return selected_date

    def _change_previous_rating(self, selected_date: str) -> None:
        """Prompt the user to change a rating from a previous day."""
        print("\nUpdating:")
        print(f"Date: {selected_date}")
        print(f"Rating: "
              f"{self.json.get_rating(selected_date)}"
              f"/{self.max_rating}")
        new_rating = self._input_rating(
            f"Enter new rating for {selected_date} "
            f"({self.min_rating}~{self.max_rating}): ",
        )

        # Save data
        self.json.logs[selected_date][self.json.rating_kyname] = new_rating
        self.json.update()
        print("\nRating updated and saved!")
        sleep(1)

    def _change_previous_memory(self, selected_date: str) -> None:
        """Prompt the user to change a memory entry from a previous day."""
        prev_mem = self.json.get_memory(selected_date)
        if not prev_mem:
            prev_mem = "(No entry)"

        print("\nUpdating:")
        print(f"Date: {selected_date}")
        print(f"Memory: ")
        print(prev_mem)

        new_mem = self._input_memory(
            f"Enter new memory entry for {selected_date}: "
        )

        self.json.logs[selected_date][self.json.memory_kyname] = new_mem
        self.json.update()
        print("\nMemory entry updated and saved!")
        sleep(1)

    # ######################## 4) View all logs ######################## #

    def _print_logs(self) -> None:
        """Print last 30 saved logs.

        The user can choose whether to show the rest of the logs.
        """
        print("\nLogs from the last 30 days: \n")

        # Convert dictionary items to a list of tuples
        items_list = list(self.json.logs.items())
        # Get the last 30 items or all items if less than 30
        last_30_items = items_list[-30:]

        self._loop_print_logs(last_30_items)

        choice = input("\nShow the rest of the logs? (y/n): ").strip().lower()
        if choice != 'y':
            return

        print()
        items_until_last_30th = items_list[:-30]

        self._loop_print_logs(items_until_last_30th)

        input("\n[Press ENTER to return to main menu] ")

    def _loop_print_logs(self,
                         items: list[tuple[str, dict[str, float | str]]]
                         ) -> None:
        """Print all logs in the given list."""
        for date, log in items:
            print(f"Date: {date}")
            print(f"Rating: {log[self.json.rating_kyname]}/{self.max_rating}")
            print(f"Memory: "
                  f"\n{log[self.json.memory_kyname]}")

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

    def _update_logs(self,
                     date: str,
                     rating: float | None = None,
                     memory: str | None = None) -> None:
        """Update saved logs in the JSON file with new values"""
        if rating is not None:
            self.json.logs[date][self.json.rating_kyname] = rating

        if memory is not None:
            self.json.logs[date][self.json.memory_kyname] = memory

        else:
            raise ValueError("No new rating and/or memory provided")

        self.json.update()

    # ################################################################## #

    def _input_rating(self, prompt: str) -> float:
        """Get and validate user float input."""
        error_msg = (f"Please enter a valid number from "
                     f"{self.min_rating} to {self.max_rating}.")
        while True:
            inp = input(f"\n{prompt}").strip()
            try:
                inp = float(inp)
            except ValueError:
                print(f"\nError: {error_msg}")
                sleep(1)
                continue

            if self.min_rating <= inp <= self.max_rating:
                break

            print(f"\nError: {error_msg}")
            sleep(1)
            continue
        return round(inp, self.rating_inp_dp)

    @staticmethod
    def _input_memory(prompt: str) -> str:
        """Prompt user for today's memory entry."""
        while True:
            tdys_mem = input(
                f"{prompt}\n\n"
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
