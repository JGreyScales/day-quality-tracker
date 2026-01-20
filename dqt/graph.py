import sys
from time import sleep
from subprocess import check_call
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
except ModuleNotFoundError:
    print("\nThe python package 'matplotlib' is required before running.")
    if input("Install now? (y/n): ").lower() != 'y':
        raise SystemExit()
    check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'])
    check_call([sys.executable, '-m', 'pip', 'install', 'matplotlib'])
    print("\nInstallation complete!")
    print("Resuming program...\n")
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates

if TYPE_CHECKING:
    from dqt.tracker import Tracker


class Graph:
    """A class to manage graph plotting for day_quality_tracker."""
    
    _CONFIG_KEYS = {
        "graph_date_format",
        "graph_style",
        "title",
        "title_fontsize",
        "title_padding",
        "xlabel",
        "xlabel_fontsize",
        "ylabel",
        "ylabel_fontsize",
        "tick_params_fontsize",
        "autofmt_xdates",
        "year_labels_fontsize",
        "year_labels_fontweight",
        "line_label",
        "line_width",
        "line_color",
        "line_style",
        "marker",
        "marker_size",
        "marker_face_color",
        "marker_edge_width",
        "neutralline_label",
        "neautralline_width",
        "neutralline_color",
        "neutralline_style",
        "averageline_label",
        "averageline_width",
        "averageline_color",
        "averageline_style",
        "highest_rating_label",
        "highest_rating_point_size",
        "highest_rating_point_color",
        "highest_rating_point_zorder",
        "lowest_rating_label",
        "lowest_rating_point_size",
        "lowest_rating_point_color",
        "lowest_rating_point_zorder",
        "legend_label",
        "legend_loc",
        "legend_frameon",
    }

    def __init__(self, dqt: Tracker):
        """Get required DQT attributes and initialize graph settings."""
        # DayQualityTracker attributes
        self.dqt = dqt
        self.dqt_date_format = dqt.date_format
        self.min_rating = dqt.min_rating
        self.max_rating = dqt.max_rating
        self.neutral_rating = dqt.neutral_rating
        self.json = dqt.json

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
        
        self.marker = 'o'
        self.marker_size = 4
        self.marker_face_color = None
        self.marker_edge_width = 0
        
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
    
    def view_ratings_graph(self) -> None:
        """Display current ratings graph."""
        if not self.json.logs:
            print("\nYou haven't entered any ratings yet!")
            sleep(1)
            return
        
        print("\nBuilding graph...")
        
        self.build()
        
        print("\nDisplaying graph...")
        print("Close the graph window to proceed.")
        
        self.show()
        
        print("\nGraph closed.")
        print("Returning to main menu...")

    def build(self) -> None:
        """Build the graph and initialize plt, fig, and ax properties."""
        logs = self.json.logs
        if not logs:
            raise ValueError("No logs saved")
        
        dates, ratings = self._fill_missing(
            sorted(
                datetime.strptime(d, self.dqt_date_format)
                for d in self.json.logs.keys()
            )
        )
        
        # Close existing windows to prevent overlapping
        plt.close('all')
        
        # Get JSON stuff
        if not logs:
            raise ValueError("No logs saved")
        
        plt.style.use(self.graph_style)
        fig, ax = plt.subplots()
        
        self._set_title(ax)
        self._draw_xylabels(ax)
        self._set_ticks(fig, ax)
        
        self._plot_ratings(ax, dates, ratings)
        self._draw_neutral_rating_line(ax)
        self._draw_average_rating_line(ax, ratings)
        self._plot_highest_lowest_ratings(ax, dates, ratings)
        
        self._draw_year_labels(ax, dates)
        
        self._set_ylimits(ax)
        
        self._draw_legend(ax)
        
    @staticmethod
    def show() -> None:
        """Show the graph."""
        plt.show()
        
    def configure(self, **kwargs) -> None:
        """Update configuration options via keyword arguments."""
        for key, value in kwargs.items():
            if key not in self._CONFIG_KEYS:
                raise ValueError(
                    f"Unknown configuration option: '{key}'"
                )
            setattr(self, key, value)
        
    def _fill_missing(self, dates: list[datetime]) \
            -> tuple[list[datetime], list[float | None]]:
        """Fill in missing ratings with None."""
        start = dates[0]
        end = dates[-1]
        
        full_dates = []
        full_ratings = []
        
        current = start
        while current <= end:
            key = current.strftime(self.dqt_date_format)
            full_dates.append(current)
            full_ratings.append(
                self.json.logs.get(key, {}).get(self.json.rating_kyname)
            )
            current += timedelta(days=1)
            
        return full_dates, full_ratings
    
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
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter(self.graph_date_format))
        ax.set_yticks(
            range(self.min_rating, self.max_rating + 1)
        )
    
    def _draw_year_labels(self, ax: plt.Axes, dates: list[datetime]) -> None:
        """Draw year labels."""
        shown_years = set()
        for i, date in enumerate(dates):
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
    
    def _plot_ratings(self, ax: plt.Axes, dates: list[datetime],
                      ratings: list[float | None]) -> None:
        """Plot rating values."""
        ax.plot(
            dates,
            ratings,
            linewidth=self.line_width,
            linestyle=self.line_style,
            marker=self.marker,
            markersize=self.marker_size,
            markerfacecolor=self.marker_face_color,
            markeredgewidth=self.marker_edge_width,
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
                                     dates: list[datetime],
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
            [dates[i] for i in max_indices],
            [max_val] * len(max_indices),
            label=self.highest_rating_label,
            s=self.highest_rating_point_size,
            color=self.highest_rating_point_color,
            zorder=self.highest_rating_point_zorder,
        )
        
        ax.scatter(
            [dates[i] for i in min_indices],
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
