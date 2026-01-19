from datetime import datetime
from collections import defaultdict
from typing import TYPE_CHECKING

from styletext import StyleText as Txt

if TYPE_CHECKING:
    from tracker import Tracker


class Stats:
    """A class to manage stats display."""
    
    def __init__(self, dqt: Tracker):
        """Initialize attributes."""
        self.dqt = dqt
        self.json = dqt.json
        
        self.date_format = self.dqt.date_format
        self.max_rating = self.dqt.max_rating
        self.rating_inp_dp = self.dqt.rating_inp_dp
    
    def show_stats(self) -> None:
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
        """Format dates as a string, separated by commas."""
        return ", ".join(dates)

    