from typing import TypeVar, List, Union
from enum import Enum
from settings import CONFIGS

T = TypeVar("T", int, float)
Special = Union[T, str]

class subDictEnum(Enum):
    # this string represents the key to access this dict in settings.py
    TRACKER = 'tracker'
    GRAPH = 'graph'

class IterableSettings:
    config: dict[str, ...] #type: ignore
    subdictType: subDictEnum
        
    def __init__(self, subDict: subDictEnum):

        # subdict is stored seperately so it will be easier to write conditionals for the eventually implimention of graph
        # and if future dicts exist in the future
        self.subdictType = subDict
        self.loadCurrentConfig(**CONFIGS)

    # ai generated function for debugging
    # prints all properties at runtime excluding private properties
    def displayRanges(self) -> None:
        if not hasattr(self, "config"):
            print("no config loaded, therefore no ranges created")
            return
        
        print("loaded config file:", self.config)
        for attr_name in dir(self):
            attr_value = getattr(self, attr_name)
            if isinstance(attr_value, list) and not attr_name.startswith("__"):
                print(f"{attr_name} range:", attr_value)


    def replace_config_value(self, target_key: str, new_value: Special):
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
        return [True, False]
    

# for testing and debugging this class
# run from project root as ```python -m dqt.iterableSettings```
if __name__ == '__main__':
    test = IterableSettings(subDictEnum.TRACKER)
    test.displayRanges()
