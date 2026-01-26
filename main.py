"""Run this module to start Day Quality Tracker."""

import sys
import traceback

from dqt.tracker import Tracker
from dqt.styletext import StyleText as Txt

if __name__ == '__main__':
    dqt = Tracker()

    # Custom configurations go here ↴
    dqt.configure(
    
    )
    dqt.json.configure(
    
    )
    dqt.graph.configure(
    
    )

    try:
        dqt.run()
    except KeyboardInterrupt:
        print("\n\n*⎋* —————————————————————————————— *⎋*")
        print("\nUser interrupted the program.")
        print("\nSaving changes...")
        dqt.json.update()
        print(Txt("Success!").bold().green())
        sys.exit()
    except Exception:
        print("\n*!* —————————————————————————————— *!*")
        print(Txt("\n❌Error!").bold().red())
        print(traceback.format_exc())
        sys.exit(1)
