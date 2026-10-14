"""Scheduling algorithms (pure logic, no GUI).

Every algorithm works on a list of `Process` objects and produces:
  * a timeline  - list of {"pid", "start", "end"} blocks used for the Gantt chart
  * a log       - human-readable explanation of what the CPU did and when

Priority scheduling follows the usual OS-textbook convention:
a LOWER number means a HIGHER priority.
"""

from dataclasses import dataclass, field
from typing import List, Tuple

FCFS = "FCFS"
SJF = "SJF (Non-Preemptive)"
PRIORITY = "Priority (Non-Preemptive)"
ROUND_ROBIN = "Round Robin"
ALGORITHMS = [FCFS, SJF, PRIORITY, ROUND_ROBIN]

IDLE = "IDLE"


@dataclass
class Process:
    id: int
    arrival: int
    burst: int
    priority: int = 0
    completion: int = 0
    turnaround: int = 0
    waiting: int = 0
    remaining: int = field(init=False)

    def __post_init__(self):
        self.remaining = self.burst

    @property
    def name(self) -> str:
        return f"P{self.id}"

    def finish(self, time: int) -> None:
        """Record completion and compute turnaround / waiting time."""
        self.completion = time
        self.turnaround = self.completion - self.arrival
        self.waiting = self.turnaround - self.burst


@dataclass
class SimulationResult:
    processes: List[Process]
    timeline: List[dict]
    log: List[str]
    avg_waiting: float
    avg_turnaround: float


# --------------------------------------------------------------------------- #
# Algorithms
# --------------------------------------------------------------------------- #
def _fcfs(procs: List[Process]) -> Tuple[List[dict], List[str]]:
    timeline, log = [], []
    time = 0
    for p in procs:
        if time < p.arrival:
            timeline.append({"pid": IDLE, "start": time, "end": p.arrival})
            log.append(f"[Time {time} to {p.arrival}] CPU is IDLE waiting for {p.name}.")
            time = p.arrival

        start = time
        time += p.burst
        timeline.append({"pid": p.name, "start": start, "end": time})
        log.append(f"[Time {start} to {time}] {p.name} executes and completes its burst.")
        p.finish(time)
    return timeline, log


def _non_preemptive(procs: List[Process], key) -> Tuple[List[dict], List[str]]:
    """Shared engine for SJF and Priority: pick the best ready process by `key`."""
    timeline, log = [], []
    n = len(procs)
    done = [False] * n
    completed = time = 0

    while completed != n:
        idx, best = -1, float("inf")
        for i, p in enumerate(procs):
            if not done[i] and p.arrival <= time and key(p) < best:
                best, idx = key(p), i

        if idx == -1:  # nothing has arrived yet -> jump to the next arrival
            next_arrival = min(p.arrival for i, p in enumerate(procs) if not done[i])
            timeline.append({"pid": IDLE, "start": time, "end": next_arrival})
            log.append(f"[Time {time} to {next_arrival}] CPU is IDLE. No processes have arrived yet.")
            time = next_arrival
            continue

        p = procs[idx]
        start = time
        time += p.burst
        timeline.append({"pid": p.name, "start": start, "end": time})
        log.append(f"[Time {start} to {time}] {p.name} is selected and executes until completion.")
        p.finish(time)
        done[idx] = True
        completed += 1
    return timeline, log


def _round_robin(procs: List[Process], quantum: int) -> Tuple[List[dict], List[str]]:
    timeline, log = [], []
    n = len(procs)
    queue: List[int] = []
    time = completed = i = 0

    def admit_arrivals():
        nonlocal i
        while i < n and procs[i].arrival <= time:
            queue.append(i)
            log.append(f"[Time {procs[i].arrival}] {procs[i].name} arrives and joins the Ready Queue.")
            i += 1

    while completed != n:
        admit_arrivals()

        if not queue:  # CPU idle until the next process arrives
            next_arrival = procs[i].arrival
            timeline.append({"pid": IDLE, "start": time, "end": next_arrival})
            log.append(f"[Time {time} to {next_arrival}] CPU is IDLE. Ready Queue is empty.")
            time = next_arrival
            continue

        idx = queue.pop(0)
        p = procs[idx]
        start = time

        if p.remaining > quantum:
            time += quantum
            p.remaining -= quantum
            timeline.append({"pid": p.name, "start": start, "end": time})
            log.append(
                f"[Time {start} to {time}] {p.name} executes for quantum ({quantum}). "
                f"Remaining burst: {p.remaining}. Moves to back of queue."
            )
        else:
            ran = p.remaining
            time += ran
            p.remaining = 0
            p.finish(time)
            completed += 1
            timeline.append({"pid": p.name, "start": start, "end": time})
            log.append(f"[Time {start} to {time}] {p.name} executes for its final {ran} units and COMPLETES.")

        admit_arrivals()  # newcomers queue up before the pre-empted process
        if p.remaining > 0:
            queue.append(idx)
    return timeline, log


# --------------------------------------------------------------------------- #
# Public API
# --------------------------------------------------------------------------- #
def simulate(processes: List[Process], algorithm: str, quantum: int = 2) -> SimulationResult:
    """Run `algorithm` on `processes` and return the full result.

    The input processes are never modified; results are returned on fresh
    copies sorted by process id.
    """
    if not processes:
        raise ValueError("No processes to simulate.")
    if algorithm not in ALGORITHMS:
        raise ValueError(f"Unknown algorithm: {algorithm!r}")
    for p in processes:
        if p.arrival < 0:
            raise ValueError(f"{p.name}: arrival time cannot be negative.")
        if p.burst <= 0:
            raise ValueError(f"{p.name}: burst time must be greater than 0.")
    if algorithm == ROUND_ROBIN and quantum <= 0:
        raise ValueError("Time quantum must be greater than 0.")

    # Work on copies, ordered by arrival (stable, so ties keep input order)
    procs = sorted(
        (Process(p.id, p.arrival, p.burst, p.priority) for p in processes),
        key=lambda p: p.arrival,
    )

    if algorithm == FCFS:
        timeline, log = _fcfs(procs)
    elif algorithm == SJF:
        timeline, log = _non_preemptive(procs, key=lambda p: p.burst)
    elif algorithm == PRIORITY:
        timeline, log = _non_preemptive(procs, key=lambda p: p.priority)
    else:
        timeline, log = _round_robin(procs, quantum)

    procs.sort(key=lambda p: p.id)
    count = len(procs)
    return SimulationResult(
        processes=procs,
        timeline=timeline,
        log=log,
        avg_waiting=sum(p.waiting for p in procs) / count,
        avg_turnaround=sum(p.turnaround for p in procs) / count,
    )
