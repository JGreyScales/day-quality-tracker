from datetime import datetime
from pstats import Stats

from dqt.graph import Graph
from dqt.dqt_json import DQTJSON
from dqt.dqt_manager import Manager
from dqt.dqt_stats import Stats
from ui_utils import *
from styletext import StyleText as Txt

_UNSET = object()


class Tracker:
    """Track and visualize day quality ratings in a graph."""
    
    def __init__(self):
        """Load saved data, initialize settings and Graph instance."""
        # Initialize settings
        self.min_time = 20  # Earliest hour the of day to enter rating
        self.min_rating = 1  # 1 recommended
        self.max_rating = 20  # Even number recommended
        self.neutral_rating = self.max_rating / 2  # Rating for an average day
        self.rating_inp_dp = 2
        
        self.date_format = '%Y-%m-%d'
        self.date_format_print = "YYYY-MM-DD"
        # Format printed time using 12-hour clock if True
        self.clock_format_12 = True
        
        self.json = DQTJSON(self)
        self.graph = Graph(self)
        self.manager = Manager(self)
        self.stats = Stats(self)
        
        self.enable_ansi = None
        Txt.set_ansi(self.enable_ansi)
    
    def run(self) -> None:
        """Run Day Quality Tracker."""
        print(Txt("\n*--- Day Quality Tracker! ---*").bold().yellow())
        sleep(1)
        
        choice = self.manager.handle_missing_logs()
        
        if choice in ['1', '3', None]:
            if not self.json.today_rated():
                self.manager.input_todays_log()
        
        while True:
            print("\n*❖* —————————————————————————————— *❖*")
            print(
                Txt("\nMAIN MENU").blue().underline().bold(),
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
                    self.graph.view_ratings_graph()
                
                case '2' | 't':
                    if not self.json.today_rated():
                        print("\n You haven't entered today's log yet!")
                        sleep(1)
                        continue
                    
                    print(Txt("\nToday's log:").bold())
                    today = datetime.today().strftime(self.date_format)
                    self.json.print_log(
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
                                self.manager.change_todays_rating()
                            case '2' | 'm':
                                self.manager.change_todays_rating()
                            case '3' | 'c':
                                break
                            case _:
                                err(
                                    "Only enter 1~3 or the given letters."
                                )
                                continue
                        break
                
                case '3' | 'p':
                    while True:
                        selected_d = self.manager.prompt_prev_date()
                        print(Txt("\nSelected log:").bold())
                        self.json.print_log(
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
                                    self.manager.change_previous_rating(
                                        selected_d
                                    )
                                case '2' | 'm':
                                    self.manager.change_previous_memory(
                                        selected_d
                                    )
                                case '3' | 'b':
                                    self.manager.change_previous_rating(
                                        selected_d
                                    )
                                    self.manager.change_previous_memory(
                                        selected_d
                                    )
                                case '4' | 'd':
                                    break
                                case '5' | 'c':
                                    break
                                case _:
                                    err(
                                        "Only enter 1~5 or the given letters."
                                    )
                                    continue
                            break
                        
                        if choice in ['4', 'd']:
                            continue
                        break
                
                case '4' | 's':
                    self.stats.show_stats()
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
                                self.json.print_logs_to_stdout()
                            case '2' | 'o':
                                self.json.open_json_file()
                            case '3' | 'c':
                                break
                            case _:
                                err(
                                    "Only enter 1~3 or the given letters."
                                )
                                continue
                        break
                
                case '6' | 'x':
                    print("\n*⎋* —————————————————————————————— *⎋*")
                    print("\nBye!")
                    raise SystemExit()
                
                case _:
                    err("Only enter 1~6 or the given letters.")
