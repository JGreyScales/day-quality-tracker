import sys
import traceback

from dqt.tracker import Tracker

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
        print("Success!")
        sys.exit()
    except Exception:
        print("\n*!* —————————————————————————————— *!*")
        print("\n❌ \033[1m\033[31mError!\033[0m")
        print(traceback.format_exc())
        sys.exit(1)
