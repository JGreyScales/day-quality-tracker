from typing import TypeVar, List, Union
from enum import Enum
from settings import CONFIGS

T = TypeVar("T", int, float)
Special = Union[T, str]

class subDictEnum(Enum):
    """Storage of the sub dict we are accessing, to allow us to easily compute keys"""
    # this string represents the key to access this dict in settings.py
    TRACKER = 'tracker'
    GRAPH = 'graph'

class IterableSettings:
    """Iterable settings class, controls the backend logic of the display and handling 
    updating and getting values from config"""
    config: dict[str, ...] #type: ignore
    subdictType: subDictEnum
        
    def __init__(self, subDict: subDictEnum):
        """Stores the enum to the instance followed up by loading the current config from memory
        a new instance of this class is created each time the settings menu is entered"""
        # subdict is stored seperately so it will be easier to write conditionals for the eventually implimention of graph
        # and if future dicts exist in the future
        self.subdictType = subDict
        self.loadCurrentConfig(**CONFIGS)

    # ai generated function for debugging
    # prints all properties at runtime excluding private properties
    def displayRanges(self) -> None:
        """A debug function which will dump all the ranges currently assiocated with the instance at runtime
        useful for double checking values while creating new settings"""
        if not hasattr(self, "config"):
            print("no config loaded, therefore no ranges created")
            return
        
        print("loaded config file:", self.config)
        for attr_name in dir(self):
            attr_value = getattr(self, attr_name)
            if isinstance(attr_value, list) and not attr_name.startswith("__"):
                print(f"{attr_name} range:", attr_value)


    def replace_config_value(self, target_key: str, new_value: Special):
        """Replaces a config value in current memory, and in the file for next load
        keeps formatting & comments in the file"""
        if (target_key == 'min_time' and new_value == "no limit"):
            new_value = 0

        # replace the value in memory
        self.config[target_key] = new_value

        # replace the value in the file
        sub_key = self.subdictType.value
        file_path = "settings.py"
        new_lines = []
        inside_subdict = False
        indent = ""
        
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                stripped = line.strip()
                
                # Detect the start of the sub-dictionary
                if stripped.startswith(f"'{sub_key}':"):
                    inside_subdict = True
                    indent = line[:line.find("'")]
                
                # Detect the end of the sub-dictionary
                if inside_subdict and stripped.startswith("},"):
                    inside_subdict = False
                
                # Replace the target key value
                if inside_subdict and stripped.startswith(f"'{target_key}'"):
                    # Preserve comments after '#'
                    if "#" in line:
                        comment = line[line.index("#"):]
                    else:
                        comment = ""

                        
                    new_line = f"{indent}    '{target_key}': {repr(new_value)},  {comment}"
                    new_lines.append(new_line)
                else:
                    new_lines.append(line)
        
        # Write back to file
        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)

    # returns a list of all the properties of the class at runtime excluding private properties
    # this allows iteration over keys and references to values (since all values are lists)
    def returnRanges(self) -> dict[str, List[Special]]:
        """Similiar to the displayRanges function, except it returns it as a key value pair
        this is primarily used in the rendering of the scroll menus in the terminal"""
        returnValue: dict[str, list[Special]] = {}
        if not hasattr(self, "config"):
            print("no config loaded, therefore no ranges created")
            return
        
        for attr_name in dir(self):
            attr_value = getattr(self, attr_name)
            if isinstance(attr_value, list) and not attr_name.startswith("__"):
                returnValue[attr_name] = attr_value

        return returnValue
    

    # generates class properties for usage later
    def loadCurrentConfig(self, **configs: int | str | bool | None) -> None:
        """loads the current config, determines the sub dict and creates preset ranges
        it should be noted ranges can be computed at runtime, such as the min and max rating values"""
        self.config: dict[str, ...] = configs[self.subdictType.value] #type: ignore

        if (self.subdictType == subDictEnum.TRACKER):
            self.min_time: List[Special] = IterableSettings.registerRange(1, 24, special_values=["no limit"])
            self.min_rating: List[int] = IterableSettings.registerRange(1, self.config['max_rating'] - 1)
            self.max_rating: List[int] = IterableSettings.registerRange(self.config['min_rating'], 20)
            self.rating_inp_dp: List[int] = IterableSettings.registerRange(0, 5)
            self.linewrap_maxcol: List[Special] = IterableSettings.registerRange(0, 100, 10, ["inf"])
            self.date_format: List[str] = ["%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y", "%d %b %Y", "%d %B %Y"]
            self.date_format_print: List[str] = ["YYYY-MM-DD","DD-MM-YYYY","MM/DD/YYYY","DD Mon YYYY","DD Month YYYY"]
            self.clock_format_12: List[bool] = IterableSettings.registerBoolean()
            self.enable_ansi: List[bool] = IterableSettings.registerBoolean()
            self.autofill_json: List[bool] = IterableSettings.registerBoolean()
            return
        
        elif(self.subdictType == subDictEnum.GRAPH):
            print("NOT IMPLIMENTED YET")
            return

    @staticmethod
    # a static method for standarizing the creation of numeric ranges
    def registerRange(min: T, max: T, step: int = 1, special_values: List[str] = []) -> List[Special]:
        """a simple helper function to create a list from a range, supporting special value inserts"""
        curList: List[Special] = []
        curList.extend(special_values)
        current = min
        while current <= max:
            curList.append(current)
            current += step
        return curList
    
    @staticmethod
    # a static method for standarizing the creation of boolean ranges
    def registerBoolean() -> List[bool]:
        """ standarization of list creation"""
        return [True, False]
    

# for testing and debugging this class
# run from project root as ```python -m dqt.iterableSettings```
if __name__ == '__main__':
    """used for running this file directly for testing"""
    test = IterableSettings(subDictEnum.TRACKER)
    test.displayRanges()
