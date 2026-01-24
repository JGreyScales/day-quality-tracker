from datetime import datetime
from pstats import Stats

from dqt.graph import Graph
from dqt.dqt_json import DQTJSON
from dqt.dqt_manager import Manager
from dqt.dqt_stats import Stats
from dqt.ui_utils import *

_UNSET = object()
_today = datetime.today()


class Tracker:
    """Track and visualize day quality ratings in a graph."""
    
    VERSION = 5
    SEMVER = '0.5.0'
    
    _CONFIG_KEYS = {
        "min_time",
        "min_rating",
        "max_rating",
        "neutral_rating",
        "rating_inp_dp",
        "date_format",
        "date_format_print",
        "clock_format_12",
        "enable_ansi",
    }
    
    def __init__(self):
        """Load saved data, initialize settings and Graph instance."""
        # Initialize settings
        self.min_time = 20  # Earliest hour the of day to enter rating
        self.min_rating = 1  # 1 recommended
        self.max_rating = 20  # Even number recommended
        self.neutral_rating = round(self.max_rating / 2)
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
        print(
            Txt(
                f"\n*--- Day Quality Tracker {self.VERSION}! ---*"
            ).bold().yellow()
        )
        print(Txt(f"        (Version {self.SEMVER})").dim())
        
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
                    if not self.graph.graph_show_block:
                        cont_on_enter()
                        self.graph.close()
                    else:
                        print("\nGraph closed.")
                
                case '2' | 't':
                    if not self.json.today_rated():
                        err("You haven't entered today's log yet!")
                        continue
                    
                    print(Txt("\nToday's log:").bold())
                    today = _today.strftime(self.date_format)
                    self.json.print_log(
                        date=today,
                        rating=self.json.get_rating(today),
                        memory=self.json.get_memory(today),
                    )
                    
                    while True:
                        print(Txt("\nSelect:"))
                        print("1) Edit [R]ating")
                        print("2) Edit [M]emory entry")
                        print("3) Edit [B]oth")
                        print("4) [C]ancel -> Main menu")
                        
                        match input("> ").strip().lower():
                            case '1' | 'r':
                                self.manager.change_todays_rating()
                            case '2' | 'm':
                                self.manager.change_todays_memory()
                            case '3' | 'b':
                                self.manager.change_todays_rating()
                                self.manager.change_todays_memory()
                            case '4' | 'c':
                                break
                            case _:
                                err(
                                    "Only enter 1~4 or the given letters."
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
                    cont_on_enter()
                
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
                                cont_on_enter()
                            case '3' | 'c':
                                break
                            case _:
                                err("Only enter 1~3 or the given letters.")
                                continue
                        break
                
                case '6' | 'x':
                    print("\n*⎋* —————————————————————————————— *⎋*")
                    print("\nBye!")
                    raise SystemExit()
                
                case _:
                    err("Only enter 1~6 or the given letters.")
    
    def configure(self, **kwargs) -> None:
        """Update configuration options via keyword arguments."""
        for key, value in kwargs.items():
            if key not in self._CONFIG_KEYS:
                raise ValueError(f"Unknown configuration option: '{key}'")
            setattr(self, key, value)
