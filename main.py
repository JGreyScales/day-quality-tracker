"""Run this module to start Day Quality Tracker."""

if __name__ == '__main__':
    try:
        try:
            import sys
            import traceback
            
            try:
                from dqt.styletext import StyleText as Txt
            except ModuleNotFoundError:
                print("\n*!* —————————————————————————————— *!*")
                print("\n❌ Error!")
                print(f"Ensure that module 'styletext' is installed.")
                sys.exit(1)
            
            from dqt.tracker import Tracker
            from dqt.styletext import StyleText as Txt
            from dqt.settings_manager import SettingsManager
        except ModuleNotFoundError as e:
            from dqt.styletext import StyleText as Txt
            print("\n*!* —————————————————————————————— *!*")
            print(Txt("\n❌ Error!").bold().red())
            print(f"{e}.")
            print(f"Ensure that module '{e.name}' exists in the current "
                  "working directory.")
            sys.exit(1)
        
        dqt: Tracker = Tracker()
        
        try:
            print("Loading settings...")
            if not SettingsManager.load_json():
                raise ValueError(
                    "Settings could not be loaded from settings.json."
                )
    
            dqt.configure()
            dqt.graph.configure()
            print("Settings loaded successfully.")
        
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
            print("Ensure that `settings.json` exists in the directory.")
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
        print("\n*!* —————————————————————————————— *!*")
        print(Txt("\n❌ Error!").bold().red())
        print("An unexpected error occurred...")
        traceback.print_exc()

        sys.exit(1)
    