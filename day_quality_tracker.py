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

        if not self._today_rated():
            self._input_todays_log()

        while True:
            self._check_missing_ratings()

            print("\nMAIN MENU — choose what to do: ")
            print("1) [V]iew ratings graph")
            print("2) Edit [T]oday's log...")
            print("3) Edit [P]revious log...")
            print("4) [S]how all logs...")
            print("5) E[x]it")

            match input("> ").lower().strip():
                case '1' | 'v':
                    self._view_ratings_graph()

                case '2' | 'c':
                    self._change_todays_rating()

                case '3':
                    self._change_previous_rating()

                case '4' | 'p':
                    self._print_ratings()

                case '5' | 'x':
                    print("\nBye!")
                    raise SystemExit()

                case _:
                    print("\nError: Only enter 1~5 or the given letters.")
                    sleep(1)

    # ################################################################## #
    # -------------------------- MAIN METHODS -------------------------- #
    # ################################################################## #

    def _input_todays_log(self) -> None:
        """Get today's rating and memory entry if not entered yet.

        Reject if the specified earliest time to collect data has not
        passed yet.
        """
        if datetime.now().time().hour >= self.min_time:

            if self.json.logs:
                self._check_missing_ratings()

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

    # ################################################################## #

    def _view_ratings_graph(self) -> None:
        """Display current ratings graph."""
        if not self.json.logs:
            print("\nYou haven't entered any ratings yet!")
            sleep(1)
            return

        self._check_missing_ratings()

        print("\nBuilding graph...")

        self.graph.build()

        print("\nDisplaying graph...")
        print("Close the graph window to proceed.")

        self.graph.show()

        print("\nGraph closed.")

    # ################################################################## #

    def _change_todays_rating(self) -> None:
        """Prompt the user to enter a new rating for today."""
        if self._today_rated():

            today = datetime.today().strftime(self.date_format)
            print(
                f"Rating to change: ",
                self.json.logs[today][self.json.rating_kyname],
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
        if self._today_rated():

            today = datetime.today().strftime(self.date_format)
            prev_mem = self.json.logs[today][self.json.memory_kyname]
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

    # ################################################################## #
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

    def _change_previous_rating(self) -> None:
        """Prompt the user to change a rating from a previous day."""
        selected_date = self._prompt_prev_date()

        print("\nUpdating:")
        print(f"Date: {selected_date}")
        print(f"Rating: "
              f"{self.json.logs[selected_date][self.json.rating_kyname]})"
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

    def _change_previous_memory(self) -> None:
        """Prompt the user to change a memory entry from a previous day."""
        selected_date = self._prompt_prev_date()

        prev_mem = self.json.logs[selected_date][self.json.memory_kyname]
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

    # ################################################################## #

    def _print_ratings(self) -> None:
        """Print all saved logs."""
        print("\nRatings from the last 30 days: ")

        # Convert dictionary items to a list of tuples
        items_list = list(self.json.logs.items())

        # Get the last 30 items or all items if less than 30
        last_30_items = items_list[-30:]

        for d, q in last_30_items:
            print(f"{d}: {q}/{self.max_rating}")

    # ########################################################## #
    # --------------------- HELPER METHODS --------------------- #
    # ########################################################## #

    def _today_rated(self) -> bool:
        """Check if a rating has been provided for today."""
        today = datetime.today().strftime(self.date_format)
        return today in self.json.logs

    def _check_missing_ratings(self) -> None:
        """Check if any previous days are missing ratings.

        User chooses to enter missing ratings or not. If they do,
        loop through each missing date and prompt rating.
        """
        if not self.json.logs:
            return

        last_date_str = max(self.json.logs.keys())
        last_date = datetime.strptime(last_date_str, self.date_format).date()
        todays_date = datetime.now().date()
        days_since_last = (todays_date - last_date).days

        # No missing ratings, return
        if days_since_last <= 1:
            return

        # Else:
        print(f"\nYou haven't entered a rating since {last_date}.")

        if input("Enter missing ratings now? [y/n]: ").lower().strip() != 'y':
            return

        # Get list of missed dates
        missed_dates = []
        curr_loop_date = last_date + timedelta(days=1)
        while len(missed_dates) < days_since_last - 1:  # Exclude today
            missed_dates.append(curr_loop_date)
            curr_loop_date += timedelta(days=1)

        new_ratings = {}
        for date in missed_dates:
            rating = self._input_rating(
                f"Enter your rating for {date} "
                f"({self.min_rating}~{self.max_rating}): ",
            )
            new_ratings[datetime.strftime(date, self.date_format)] = rating

        self.json.logs.update(new_ratings)
        self.json.update()
        print("Rating saved!")
        sleep(1)

    def _update_logs(self, date: str, rating: float, memory: str) -> None:
        self.json.logs[date][self.json.rating_kyname] = rating
        self.json.logs[date][self.json.memory_kyname] = memory
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
