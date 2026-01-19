# Day Quality Tracker 5 <sub><sup>(v0.5.0)</sup></sub>

This is a simple Python CLI that helps you track your day quality ratings and visualize them on a graph using the 
Matplotlib.pyplot module.

## How to use

Before using the program, ensure you have a Python interpreter installed on your system **(version 3.12+ recommended)**.

To start the program, **run `main.py`**, or
   
   ```python
   from dqt.tracker import Tracker
   
   dqt = Tracker()
   dqt.run()
   ```

Every day, if you have not yet entered a rating, the program will prompt you to do so.
The default earliest time you can enter a rating is 8 PM. You can change this by:


## License

This project is licensed under the MIT License.
