import sys
from subprocess import check_call
from datetime import datetime
from typing import TYPE_CHECKING

try:
    import matplotlib.pyplot as plt
except ModuleNotFoundError:
    print("\nA python package 'matplotlib' is required before running.")
    if input("Install now? (y/n): ").lower() != 'y':
        raise SystemExit()
    check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'])
    check_call([sys.executable, '-m', 'pip', 'install', 'matplotlib'])
    print("\nInstallation complete!")
    print("Resuming program...\n")
    import matplotlib.pyplot as plt

if TYPE_CHECKING:
    from day_quality_tracker import DayQualityTracker
    from dqt_json import DQTJSON


class DQTGraph:
    """A class to manage graph plotting for day_quality_tracker."""

    def __init__(self, dqt: DayQualityTracker):
        """Get required DQT attributes and initialize graph settings."""
        # DayQualityTracker attributes
        self.dqt = dqt
        self.dqt_date_format = dqt.date_format
        self.min_rating = dqt.min_rating
        self.max_rating = dqt.max_rating
        self.neutral_rating = dqt.neutral_rating
        self.json: DQTJSON = dqt.json

        # Graph settings
        self.graph_date_format = '%a %b %d'

        self.graph_style = 'ggplot'

        self.title = "Day Quality Ratings"
        self.title_fontsize = 20
        self.title_padding = 18

        self.xlabel = "Date"
        self.xlabel_fontsize = 14
        self.ylabel = "Rating"
        self.ylabel_fontsize = 14

        self.tick_params_fontsize = 7
        
        self.autofmt_xdates = True
        
        self.year_labels_fontsize = 9
        self.year_labels_fontweight = 'bold'
        
        self.line_label = "Ratings"
        self.line_width = 2
        self.line_color = None
        self.line_style = '-'
        
        self.neutralline_label = 'Neutral rating (baseline)'
        self.neutralline_width = 1
        self.neutralline_color = 'black'
        self.neutralline_style = '--'
        
        self.averageline_label = 'Average rating'
        self.averageline_width = 1
        self.averageline_color = 'red'
        self.averageline_style = '-.'
        
        self.highest_rating_label = 'Highest rating'
        self.highest_rating_point_size = 20
        self.highest_rating_point_color = 'green'
        self.highest_rating_point_zorder = 5
        
        self.lowest_rating_label = 'Lowest rating'
        self.lowest_rating_point_size = 20
        self.lowest_rating_point_color = 'orange'
        self.lowest_rating_point_zorder = 5
        
        self.legend_fontsize = 8
        self.legend_loc = 'upper right'
        self.legend_frameon = True

    def build(self) -> None:
        """Build the graph and initialize plt, fig, and ax properties."""
        logs = self.json.logs
        if not logs:
            raise ValueError("No logs saved")
        
        dates = list(logs.keys())
        ratings = [
            log[self.json.rating_kyname]
            for log in logs.values()
        ]
        
        # Close existing windows to prevent overlapping
        plt.close('all')
        
        # Get JSON stuff
        if not logs:
            raise ValueError("No logs saved")
        
        # Make formated dates for displaying
        formatted_dates: list[str] = [
            datetime.strptime(date, self.dqt_date_format)
            .strftime(self.graph_date_format)
            for date in dates
        ]
        
        plt.style.use(self.graph_style)
        fig, ax = plt.subplots()
        
        self._set_title(ax)
        self._draw_xylabels(ax)
        self._set_ticks(fig, ax)
        
        self._plot_ratings(ax, formatted_dates, ratings)
        self._draw_neutral_rating_line(ax)
        self._draw_average_rating_line(ax, ratings)
        self._plot_highest_lowest_ratings(ax, formatted_dates, ratings)
        
        self._draw_year_labels(ax, dates)
        
        self._set_ylimits(ax)
        
        self._draw_legend(ax)
        
    @staticmethod
    def show() -> None:
        """Show the graph."""
        plt.show()
        
    def _set_title(self, ax: plt.Axes) -> None:
        """Set the title of the graph."""
        ax.set_title(
            self.title,
            fontsize=self.title_fontsize,
            pad=self.title_padding,
        )
        
    def _draw_xylabels(self, ax: plt.Axes) -> None:
        """Draw x and y labels."""
        ax.set_xlabel(self.xlabel, fontsize=self.xlabel_fontsize)
        ax.set_ylabel(self.ylabel, fontsize=self.ylabel_fontsize)
        
    def _set_ticks(self, fig: plt.Figure, ax: plt.Axes) -> None:
        """Set tick label sizes, format dates, and set y-tic increments."""
        ax.tick_params(labelsize=self.tick_params_fontsize)
        if self.autofmt_xdates:
            fig.autofmt_xdate()
        ax.set_yticks(
            range(self.min_rating, self.max_rating + 1)
        )
    
    def _draw_year_labels(self, ax: plt.Axes, dates: list[str]) -> None:
        """Draw year labels."""
        shown_years = set()
        for i, date_str in enumerate(dates):
            date = datetime.strptime(date_str, self.dqt_date_format)
            year = date.year
            
            if year not in shown_years:
                x = i / (len(dates) - 1) if len(dates) > 1 else 0.5
                ax.text(
                    x,
                    1,
                    str(year),
                    transform=ax.transAxes,
                    ha='center',
                    va='bottom',
                    fontsize=self.year_labels_fontsize,
                    fontweight=self.year_labels_fontweight
                )
                shown_years.add(year)
    
    def _plot_ratings(self, ax: plt.Axes, fdates: list[str],
                      ratings: list[float | None]) -> None:
        """Plot rating values."""
        ax.plot(
            fdates,
            ratings,
            linewidth=self.line_width,
            color=self.line_color,
            label=self.line_label,
        )
        
    def _draw_neutral_rating_line(self, ax: plt.Axes) -> None:
        """Draw horizontal neutral rating line."""
        ax.axhline(
            y=self.dqt.neutral_rating,
            color=self.neutralline_color,
            linewidth=self.neutralline_width,
            linestyle=self.neutralline_style,
            label=self.neutralline_label,
        )
        
    def _draw_average_rating_line(self, ax: plt.Axes,
                                  ratings: list[float | None],) -> None:
        """Draw horizontal average rating line."""
        avg = self._average_rating(ratings)
        if avg is None:
            return
        ax.axhline(
            y=round(avg, self.dqt.rating_inp_dp),
            color=self.averageline_color,
            linewidth=self.averageline_width,
            linestyle=self.averageline_style,
            label=self.averageline_label,
        )
    
    def _average_rating(self, ratings: list[float | None]) -> float | None:
        """Return average rating."""
        clean = [r for r in ratings if r is not None]
        if not clean:
            return None
        return round(sum(clean) / len(clean), self.dqt.rating_inp_dp)
    
    def _plot_highest_lowest_ratings(self,
                                     ax: plt.Axes,
                                     fdates: list[str],
                                     ratings: list[float | None]) -> None:
        """Plot highest and lowest rating values as points."""
        indexed = [(i, r) for i, r in enumerate(ratings) if r is not None]
        if not indexed:
            return
        
        values = [r for _, r in indexed]
        max_val = max(values)
        min_val = min(values)
        
        max_indices = [i for i, r in indexed if r == max_val]
        min_indices = [i for i, r in indexed if r == min_val]
        
        ax.scatter(
            [fdates[i] for i in max_indices],
            [max_val] * len(max_indices),
            label=self.highest_rating_label,
            s=self.highest_rating_point_size,
            color=self.highest_rating_point_color,
            zorder=self.highest_rating_point_zorder,
        )
        
        ax.scatter(
            [fdates[i] for i in min_indices],
            [min_val] * len(min_indices),
            label=self.lowest_rating_label,
            s=self.lowest_rating_point_size,
            color=self.lowest_rating_point_color,
            zorder=self.lowest_rating_point_zorder,
        )
    
    def _set_ylimits(self, ax: plt.Axes) -> None:
        """Set y-limits."""
        ax.set_ylim(self.min_rating, self.max_rating + 1)
    
    def _draw_legend(self, ax: plt.Axes) -> None:
        """Draw legend."""
        ax.legend(
            fontsize=self.legend_fontsize,
            loc=self.legend_loc,
            frameon=self.legend_frameon,
        )
