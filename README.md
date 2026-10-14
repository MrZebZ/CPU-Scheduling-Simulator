# 🖥️ CPU Scheduling Simulator

![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![GUI](https://img.shields.io/badge/GUI-Tkinter-orange)
![License](https://img.shields.io/badge/license-MIT-green)
![Tests](https://github.com/YOUR-USERNAME/cpu-scheduling-simulator/actions/workflows/ci.yml/badge.svg)

An interactive desktop application that simulates how an operating system schedules processes on the CPU. Enter your own processes, pick a scheduling algorithm, and instantly see the results: a per-process metrics table, a visual **Gantt chart**, and a step-by-step explanation of what the CPU did.

Built as an **Operating Systems** course project.

<!-- Add a screenshot here once you have one:
![Screenshot](docs/screenshots/demo.png)
-->

## Features

- **4 scheduling algorithms:** FCFS, SJF (non-preemptive), Priority (non-preemptive) and Round Robin
- **Custom processes:** add any number of processes with arrival time, burst time and priority
- **Metrics table:** completion, turnaround and waiting time for every process, plus averages
- **Visual Gantt chart:** colour-coded timeline drawn on a canvas, including CPU idle gaps
- **Execution log:** plain-English explanation of every scheduling decision (great for learning and exams)
- **Input validation:** rejects invalid values such as zero burst time or a zero time quantum
- **Separated logic and UI:** the algorithms contain no GUI code, so they are unit-tested

## Algorithms

| Algorithm | Type | How the next process is chosen |
|---|---|---|
| **FCFS** (First Come First Served) | Non-preemptive | Whoever arrived first runs first |
| **SJF** (Shortest Job First) | Non-preemptive | The ready process with the smallest burst time |
| **Priority** | Non-preemptive | The ready process with the highest priority (**lower number = higher priority**) |
| **Round Robin** | Preemptive | Each process runs for at most one time quantum, then goes to the back of the queue |

**Formulas used**

```
Turnaround Time = Completion Time - Arrival Time
Waiting Time    = Turnaround Time - Burst Time
```

## Getting Started

### Prerequisites

- Python 3.9+
- Tkinter (included with the standard Python installers for Windows and macOS)
  - On Debian/Ubuntu Linux: `sudo apt install python3-tk`

### Installation

```bash
git clone https://github.com/YOUR-USERNAME/cpu-scheduling-simulator.git
cd cpu-scheduling-simulator
```

No third-party packages are needed to run the app.

### Run

```bash
python -m cpu_scheduler
```

## Usage

1. Enter **Arrival Time**, **Burst Time** and (optionally) **Priority**, then click **Add Process**. Repeat for each process.
2. Choose an **algorithm** from the dropdown. For Round Robin, set the **Time Quantum**.
3. Click **Run Simulation** to see the metrics table, Gantt chart and execution log.
4. Click **Clear All** to start over.

### Example

| Process | Arrival | Burst |
|---|---|---|
| P1 | 0 | 5 |
| P2 | 1 | 3 |
| P3 | 2 | 8 |
| P4 | 3 | 6 |

| Algorithm | Execution order | Avg. waiting time | Avg. turnaround time |
|---|---|---|---|
| FCFS | P1 → P2 → P3 → P4 | 5.75 | 11.25 |
| SJF | P1 → P2 → P4 → P3 | 5.25 | 10.75 |

SJF gives a lower average waiting time here, which is why it is considered optimal for non-preemptive scheduling.

## Running Tests

```bash
pip install -r requirements.txt
pytest
```

The tests check known textbook examples, CPU idle handling, invalid input, and invariants such as `waiting = turnaround - burst` and a gap-free timeline.

## Project Structure

```
cpu-scheduling-simulator/
├── cpu_scheduler/
│   ├── __init__.py
│   ├── __main__.py          # Entry point (python -m cpu_scheduler)
│   ├── algorithms.py        # Scheduling logic (no GUI)
│   └── gui.py               # Tkinter interface
├── tests/
│   └── test_algorithms.py
├── docs/screenshots/        # Images for the README
├── .github/workflows/ci.yml # Automated tests
├── pytest.ini
├── requirements.txt
├── .gitignore
├── LICENSE
└── README.md
```

## Future Improvements

- Preemptive algorithms: SRTF (Shortest Remaining Time First) and preemptive Priority
- Side-by-side comparison of all algorithms on the same process set
- Export results to CSV or save the Gantt chart as an image
- Edit or delete individual processes
- Multilevel Queue / Multilevel Feedback Queue scheduling

## License

Distributed under the MIT License. See [LICENSE](LICENSE) for details.

## Author

**YOUR NAME**
[GitHub](https://github.com/YOUR-USERNAME) · [LinkedIn](https://linkedin.com/in/YOUR-PROFILE)
