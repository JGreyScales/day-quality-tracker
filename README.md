# Day Quality Tracker 5 <sub><sup>(v0.5.0-beta)</sup></sub>

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

### Ratings

Every day, if you have not yet entered a rating, the program will prompt you to do so.
The default earliest time you can enter a rating is 8 PM. You can change this by adding the following keyword 
argument in `main.py`:

```python
dqt.configure(
    min_time=0  # Earliest hour of day to enter rating
)
```

You can change the range of ratings by (default is 1~20):

```python
dqt.configure(
    max_rating=10,
    min_rating=1,
)
```

You can choose to enter a null rating, meaning you are unable or unwilling to rate your date for now. You can edit 
ratings at any time.

### Memory entries

You can also choose to enter a memory entry. Memory entries are similar to diary entries, and are a few lines long. 
You can enter anything you wish to remember for the future.

You can enter empty memory entries if you do not wish to enter one.

### Main menu

After entering your log for the day, you have a number of options:

#### View ratings graph

Visually see your ratings plotted on a line graph. You can also see your average, highest, and lowest ratings.

#### Edit today's log

Choose to edit the rating or memory (or both) you entered today.

#### Edit previous log

To choose the log to edit, the program will prompt you to enter either:
* The date of the log you wish to edit
    * By default, the format you must use is `YYYY-MM-DD` (e.g., `2026-01-20`)
* The number of days ago the log is for
    * e.g., Yesterday's log: `1`, log from last week: `7`

Choose to edit the rating or memory (or both) you entered for that day

#### See stats

See your rating stats! You can find out your average, highest, and lowest rating and more.

#### View all logs

Choose either to:
* Print logs as standard output
* Open the file with your system's default application

### Missed logs

After the running the program, the program first checks if you've missed any prior logs.
You can choose whether to enter the missed logs now or later.

If you choose to skip the missed logs, you will have to enter them later manually (unless you stop the program 
before entering today's log). This is because the program determines if you've missed a log by checking the last log 
recorded.

### Back up logs

Sometimes an error can occur while the program is running, which can corrupt or accidentally erase the JSON file 
where your logs are stored. It is good practice to back up your logs every once in a while.

The program creates a copy of the JSON file with your logs in it into the chosen directory.

### Custom Configurations

To add custom configurations, pass any valid keyword argument into the provided empty `configure()` calls in `main.py`.

## License

This project is licensed under the MIT License.
