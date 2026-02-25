"""Run this module to start Day Quality Tracker."""
if __name__ == '__main__':
    try:
        try:
            import sys
            import traceback
            
            from dqt.tracker import Tracker
            from dqt.styletext import StyleText as Txt
            from dqt.json_manager import JsonManager
        except ModuleNotFoundError as e:
            try:
                from dqt.styletext import StyleText as Txt
                print("\n*!* —————————————————————————————— *!*")
                print(Txt("\n❌ Error!").bold().red())
                print(f"{e}.")
                print(f"Ensure that module '{e.name}' exists in the current "
                      "working directory.")
            except ModuleNotFoundError as e:
                print("\n*!* —————————————————————————————— *!*")
                print("\n❌ Error!")
                print(f"{e}.")
                print(f"Ensure that module '{e.name}' exists in the current "
                      "working directory.")
            finally:
                sys.exit(1)
        
        dqt: Tracker = Tracker()
        
        try:
            print("Loading configurations...")
            if not JsonManager.load_json():
                raise ValueError(
                    "Configurations could not be loaded from settings.json."
                )
    
            dqt.configure()
            dqt.graph.configure()
            print("Config loaded")
        
        except ValueError as e:
            print("\n*!* —————————————————————————————— *!*")
            print(Txt("\n❌ Error!").bold().red())
            print(f"{e}.")
            print("Ensure that you have passed valid configuration keys in "
                  "`settings.json`.")
            sys.exit(1)
        except FileNotFoundError as e:
            print("\n*!* —————————————————————————————— *!*")
            print(Txt("\n❌ Error!").bold().red())
            print(f"{e}.")
            print("Ensure that you have passed valid configuration keys in "
                  "`settings.json`.")
            sys.exit(1)            
   
        try:
            dqt.run()
        except KeyboardInterrupt as e:
            print("\n\n*⎋* —————————————————————————————— *⎋*")
            print("\nUser interrupted the program.")
            print("\nSaving changes...")
            dqt.json.update()
            print(Txt("Success!").bold().green())
            sys.exit()
    except Exception:
        try:
            from dqt.styletext import StyleText as Txt
            print("\n*!* —————————————————————————————— *!*")
            print(Txt("\n❌ Error!").bold().red())
            print("An unexpected error occurred...")
            traceback.print_exc()
        except ModuleNotFoundError as e:
            print("\n*!* —————————————————————————————— *!*")
            print("\n❌ Error!")
            print("An unexpected error occurred...")
            traceback.print_exc()
        finally:
            sys.exit(1)
    