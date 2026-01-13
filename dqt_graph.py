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
        self.median_rating = dqt.median_rating

        # Graph settings
        self.graph_date_format = '%a %b %d'

        self.graph_style = 'ggplot'

        self.line_width = 2
        self.line_color = 'red'

        self.title = "Day Quality Ratings"
        self.title_fontsize = 20
        self.title_padding = 18

        self.xlabel = "Date"
        self.xlabel_fontsize = 14
        self.ylabel = "Rating"
        self.ylabel_fontsize = 14

        self.tick_params_fontsize = 7
        self.yticks_steps = 2

        self.medianline_width = 1
        self.medianline_color = 'black'
        self.medianline_style = '--'
        self.medianline_label = ''

        self.year_labels_fontsize = 9
        self.year_labels_fontweight = 'bold'

    def build(self):
        """Initialize graph properties."""
        # TODO:
        #   - Show highest and lowest rating in graph as dots
        #   - Show average rating as horizontal line
        json: DQTJSON = self.dqt.json
        
        # Close existing windows to prevent overlapping
        plt.close('all')
        
        dates = list(json.logs.keys())
        ratings = [log[json.rating_kyname] for log in json.logs.values()]
        
        formatted_dates = [
            datetime.strptime(date, self.dqt_date_format)
            .strftime(self.graph_date_format)
            for date in dates
        ]
        
        # Initialize properties
        plt.style.use(self.graph_style)
        fig, ax = plt.subplots()
        ax.plot(formatted_dates, ratings, linewidth=self.line_width)
        
        # Set chart title and label axes
        ax.set_title(
            self.title,
            fontsize=self.title_fontsize,
            pad=self.title_padding,
        )
        ax.set_xlabel(self.xlabel, fontsize=self.xlabel_fontsize)
        ax.set_ylabel(self.ylabel, fontsize=self.ylabel_fontsize)
        
        # Mark median rating line
        plt.axhline(
            y=self.dqt.median_rating,
            color=self.medianline_color,
            linewidth=self.medianline_width,
            linestyle=self.medianline_style,
            label=self.medianline_label,
        )
        
        # Set size of tick labels
        ax.tick_params(labelsize=self.tick_params_fontsize)
        
        fig.autofmt_xdate()
        # TODO: Do something to prevent dates from becoming too clustered
        #       by hiding some dates on set intervals
        
        # Set y-axis ticks to increment by ytick_steps
        ax.set_yticks(range(0, self.max_rating + 1, self.yticks_steps))
        
        # Draw year labels on the top of the graph
        shown_years = set()
        for i, date_str in enumerate(dates):
            date = datetime.strptime(date_str, self.dqt_date_format)
            year = date.year
        
            if year not in shown_years:
                ax.text(
                    i,
                    ax.get_ylim()[1],
                    str(year),
                    ha='center',
                    va='bottom',
                    fontsize=self.year_labels_fontsize,
                    fontweight=self.year_labels_fontweight
                )
                shown_years.add(year)

    @staticmethod
    def show():
        """Show the graph."""
        plt.show()
