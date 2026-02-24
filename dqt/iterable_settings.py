from enum import Enum
from typing import TypeVar, Union

from settings import CONFIGS

T: TypeVar = TypeVar('T', int, float)
Special: type = Union[T, str]


class SubDictEnum(Enum):
    """Store custom configurations subdict keys."""
    TRACKER = 'tracker'
    GRAPH = 'graph'
    NONE_SELECTED = 'none_selected'


class IterableSettings:
    """Control the display, handling, updating and fetching of configs."""
    config: dict[str, ...]  # type: ignore
    subdict_type: SubDictEnum
    
    def __init__(self, sub_dict: SubDictEnum):
        """Initialize attributes and load current configs.
        
        Store the enum to the instance followed up by loading the current
        config from memory. A new instance of this class is created each time
        the settings menu is entered.
        """
        # Subdict is stored separately so it will be easier to write conditionals for
        self.subdict_type = sub_dict
        self.load_current_config(**CONFIGS)

    def display_ranges(self) -> None:
        """Dump all ranges currently associated with the instance at runtime.
        
        AI generated function for debugging.
        Print all properties at runtime excluding private properties.
        Useful for double-checking values while creating new settings.
        """
        if not hasattr(self, "config"):
            print("no config loaded, therefore no ranges created")
            return
        
        print("loaded config file:", self.config)
        for attr_name in dir(self):
            attr_value = getattr(self, attr_name)
            if isinstance(attr_value, list) and not attr_name.startswith("__"):
                print(f"{attr_name} range:", attr_value)

    def replace_config_value(self, target_key: str, new_value: Special):
        """Replace a config value in current memory, and in the file.
        
        Keeps formatting & comments in the file
        """
        if target_key == 'min_time' and new_value == 'no limit':
            new_value = 0

        # Replace the value in memory
        self.config[target_key] = new_value

        # Replace the value in the file
        sub_key = self.subdict_type.value
        file_path = 'settings.py'
        new_lines = []
        inside_subdict = False
        indent = ''
        
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                stripped = line.strip()
                
                # Detect the start of the sub-dictionary
                if stripped.startswith(f"'{sub_key}':"):
                    inside_subdict = True
                    indent = line[:line.find('\'')]
                
                # Detect the end of the sub-dictionary
                if inside_subdict and stripped.startswith('},'):
                    inside_subdict = False
                
                # Replace the target key value
                if inside_subdict and stripped.startswith(f"'{target_key}'"):
                    # Preserve comments after '#'
                    if '#' in line:
                        comment = line[line.index('#'):]
                    else:
                        comment = ''

                    new_line = (f"{indent}    '{target_key}': "
                                f"{repr(new_value)},  {comment}")
                    new_lines.append(new_line)
                else:
                    new_lines.append(line)
        
        # Write back to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)

        # Refresh the current config so dynamic ranges are recomputed
        self.load_current_config(**CONFIGS)

    def return_ranges(self) -> dict[str, list[Special]]:
        """Similar to `display_ranges()`, except return as a key-value pair.
        
        This is primarily used in the rendering of the scroll menus in the
        terminal.
        
        Return a list of all the properties of the class at runtime excluding
        private properties. This allows iteration over keys and references to
        values (since all values are lists).
        """
        return_value: dict[str, list[Special]] = {}
        if not hasattr(self, 'config'):
            print("no config loaded, therefore no ranges created")
            return
        
        for attr_name in dir(self):
            attr_value = getattr(self, attr_name)
            if isinstance(attr_value, list) and not attr_name.startswith("__"):
                return_value[attr_name] = attr_value

        return return_value
    
    def load_current_config(self, **configs: int | str | bool | None) -> None:
        """Load current config, determine the subdict and create preset ranges
        
        It should be noted ranges can be computed at runtime, such as the min
        and max rating values
        """
        # type: ignore
        self.config: dict[str, ...] = configs[self.subdict_type.value]

        if self.subdict_type == SubDictEnum.TRACKER:
            self.min_time: list[Special] = IterableSettings.register_range(
                1, 24, special_values=["no limit"]
            )
            self.min_rating: list[int] = IterableSettings.register_range(
                1, self.config['max_rating'] - 1
            )
            self.max_rating: list[int] = IterableSettings.register_range(
                self.config['min_rating'], 20
            )
            self.rating_inp_dp: list[int] = IterableSettings.register_range(
                0, 5
            )
            self.linewrap_maxcol: list[Special] = (
                IterableSettings.register_range(
                    0, 100, 10, ["inf"]
                )
            )
            self.date_format: list[str] = [
                "%Y-%m-%d",
                "%d-%m-%Y",
                "%m/%d/%Y",
                "%d %b %Y",
                "%d %B %Y",
            ]
            self.date_format_print: list[str] = [
                "YYYY-MM-DD",
                "DD-MM-YYYY",
                "MM/DD/YYYY",
                "DD Mon YYYY",
                "DD Month YYYY"
            ]
            self.clock_format_12: list[bool] = IterableSettings.register_boolean()
            self.enable_ansi: list[bool] = IterableSettings.register_boolean()
            self.autofill_json: list[bool] = IterableSettings.register_boolean()
            return
        
        elif self.subdict_type == SubDictEnum.GRAPH:
            self.graph_style: list[str] = [
                'Solarize_Light2', '_classic_test_patch', '_mpl-gallery',
                '_mpl-gallery-nogrid', 'bmh', 'classic', 'dark_background',
                'fast', 'fivethirtyeight', 'ggplot', 'grayscale',
                'seaborn-v0_8', 'seaborn-v0_8-bright',
                'seaborn-v0_8-colorblind', 'seaborn-v0_8-dark',
                'seaborn-v0_8-dark-palette', 'seaborn-v0_8-darkgrid',
                'seaborn-v0_8-deep', 'seaborn-v0_8-muted',
                'seaborn-v0_8-notebook', 'seaborn-v0_8-paper',
                'seaborn-v0_8-pastel', 'seaborn-v0_8-poster',
                'seaborn-v0_8-talk', 'seaborn-v0_8-ticks', 'seaborn-v0_8-white',
                'seaborn-v0_8-whitegrid', 'tableau-colorblind10'
            ]
            self.graph_show_block: list[bool] = IterableSettings.register_boolean()
            self.title_fontsize: list[int] = IterableSettings.register_range(15, 30)
            self.title_padding: list[int] = IterableSettings.register_range(13, 25)
            self.xlabel_fontsize: list[int] = IterableSettings.register_range(8, 20)
            self.ylabel_fontsize: list[int] = IterableSettings.register_range(8, 20)
            self.tick_labels_fontsize: list[int] = IterableSettings.register_range(5, 15)
            self.graph_date_format: list[str] = [
                "%Y-%m-%d", "%d-%m-%y", "%m/%d", "%a %b %d", "%d %b %Y"
            ]
            self.autofmt_xdates: list[bool] = IterableSettings.register_boolean()
            self.year_labels_fontsize: list[int] = IterableSettings.register_range(5, 15)
            self.year_labels_fontweight: list[str] = ["normal", "bold", "light"]
            self.line_width: list[int] = IterableSettings.register_range(1, 10)
            self.line_color: list[Special] = [
                "blue", "red", "green", "black", "orange", "purple", "none"
            ]
            self.line_style: list[str] = ["-", "--", "-.", ":", "None"]
            self.marker: list[str] = ["o", "s", "D", "^", "v", "x", "+", "None"]
            self.marker_size: list[int] = IterableSettings.register_range(1, 20)
            self.marker_face_color: list[Special] = [
                "blue", "red", "green", "black", "white", "none"
            ]
            self.marker_edge_width: list[int] = IterableSettings.register_range(0, 10)
            self.neutralline_width: list[int] = IterableSettings.register_range(0, 5)
            self.neutralline_color: list[str] = ["black", "gray", "red", "blue"]
            self.neutralline_style: list[str] = ["-", "--", "-.", ":"]
            self.averageline_width: list[int] = IterableSettings.register_range(0, 5)
            self.averageline_color: list[str] = [
                "red", "blue", "black", "green"
            ]
            self.averageline_style: list[str] = ["-", "--", "-.", ":"]
            self.highest_rating_point_size: list[int] = IterableSettings.register_range(5, 50)
            self.highest_rating_point_color: list[Special] = [
                "green", "gold", "blue", "none"
            ]
            self.lowest_rating_point_size: list[int] = IterableSettings.register_range(5, 50)
            self.lowest_rating_point_color: list[Special] = [
                "orange", "red", "black", "none"
            ]
            self.legend_fontsize: list[int] = IterableSettings.register_range(5, 15)
            self.legend_loc: list[str] = [
                "best", "upper right", "upper left", "lower left",
                "lower right", "center"
            ]
            self.legend_frameon: list[bool] = IterableSettings.register_boolean()
            return

    @staticmethod
    def register_range(min_: T,
                       max_: T,
                       step: int = 1,
                       special_values: list[str]| None = None) -> list[Special]:
        """Create a list from a range, supporting special value inserts.
        
        A static method for standardizing the creation of numeric ranges.
        """



        cur_list: list[Special] = []
        if (special_values is not None):
            cur_list.extend(special_values)
        current = min_
        while current <= max_:
            cur_list.append(current)
            current += step
        return cur_list
    
    @staticmethod
    def register_boolean() -> list[bool]:
        """Standardize list creation.
        
        a static method for standardizing the creation of boolean ranges
        """
        return [True, False]
    

# for testing and debugging this class
# run from project root as ```python -m dqt.iterableSettings```
if __name__ == '__main__':
    """Used for running this file directly for testing."""
    test = IterableSettings(SubDictEnum.TRACKER)
    test.display_ranges()
