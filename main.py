"""Run this module to start Day Quality Tracker."""

if __name__ == '__main__':
    try:
        import sys
        import traceback
        
        from dqt.styletext import StyleText as Txt
        from dqt.tracker import Tracker
    except ModuleNotFoundError as e:
        print("\n*!* —————————————————————————————— *!*")
        print(Txt("\n❌Error!").bold().red())
        print(e)
        print(f"Ensure that module '{e.name}' exists in the current "
              f"working directory.")
        sys.exit(1)
    
    try:
        dqt = Tracker()
    
        # Custom configurations go here ↴
        dqt.configure(
        
        )
        dqt.manager.configure(
        
        )
        dqt.json.configure(
        
        )
        dqt.graph.configure(
        
        )
    except ValueError as e:
        print("\n*!* —————————————————————————————— *!*")
        print(Txt("\n❌Error!").bold().red())
        print(e)
        print("Ensure that you have passed valid configuration keys into the "
              "`configure()` methods in main.py.")
        sys.exit(1)
    except Exception:
        print("\n*!* —————————————————————————————— *!*")
        print(Txt("\n❌Error!").bold().red())
        print(traceback.format_exc())
        sys.exit(1)
        
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
