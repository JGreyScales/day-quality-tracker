"""Run this module to start Day Quality Tracker."""

if __name__ == '__main__':
    try:
        try:
            import sys
            import traceback
            
            from dqt.styletext import StyleText as Txt
            from dqt.tracker import Tracker
            from settings import CONFIGS
        except ModuleNotFoundError as e:
            print("\n*!* —————————————————————————————— *!*")
            print(Txt("\n❌Error!").bold().red())
            print(e)
            print(f"Ensure that module '{e.name}' exists in the current "
                  f"working directory.")
            sys.exit(1)
        
        dqt = Tracker()
        
        try:
            
            dqt.configure(**CONFIGS['tracker'])
            dqt.graph.configure(**CONFIGS['graph'])
        
        except ValueError as e:
            print("\n*!* —————————————————————————————— *!*")
            print(Txt("\n❌Error!").bold().red())
            print(e)
            print("Ensure that you have passed valid configuration keys into "
                  "the `configure()` calls in main.py.")
            sys.exit(1)
            
        try:
            dqt.run()
            
        except KeyboardInterrupt as e:
            print("\n\n*⎋* —————————————————————————————— *⎋*")
            print("\nUser interrupted the program.")
            print("\nSaving changes...")
            dqt.json.update_json()
            print(Txt("Success!").bold().green())
            sys.exit()
    except Exception:
        print("\n*!* —————————————————————————————— *!*")
        print(Txt("\n❌Error!").bold().red())
        traceback.print_exc()
        sys.exit(1)
    