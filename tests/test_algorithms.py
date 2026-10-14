import pytest

from cpu_scheduler.algorithms import (
    FCFS, PRIORITY, ROUND_ROBIN, SJF, Process, simulate,
)


def by_name(result):
    return {p.name: p for p in result.processes}


def classic_set():
    return [Process(1, 0, 5), Process(2, 1, 3), Process(3, 2, 8), Process(4, 3, 6)]


def test_fcfs_completion_and_averages():
    result = simulate(classic_set(), FCFS)
    p = by_name(result)
    assert [p[f"P{i}"].completion for i in (1, 2, 3, 4)] == [5, 8, 16, 22]
    assert result.avg_waiting == pytest.approx(5.75)
    assert result.avg_turnaround == pytest.approx(11.25)


def test_sjf_picks_shortest_ready_job():
    result = simulate(classic_set(), SJF)
    order = [b["pid"] for b in result.timeline]
    assert order == ["P1", "P2", "P4", "P3"]
    assert result.avg_waiting == pytest.approx(5.25)


def test_priority_lower_number_runs_first():
    procs = [Process(1, 0, 3, priority=3), Process(2, 0, 2, priority=1), Process(3, 0, 1, priority=2)]
    result = simulate(procs, PRIORITY)
    assert [b["pid"] for b in result.timeline] == ["P2", "P3", "P1"]


def test_round_robin_known_example():
    procs = [Process(1, 0, 4), Process(2, 0, 3)]
    result = simulate(procs, ROUND_ROBIN, quantum=2)
    p = by_name(result)
    assert (p["P1"].completion, p["P2"].completion) == (6, 7)
    assert (p["P1"].waiting, p["P2"].waiting) == (2, 4)
    assert [b["pid"] for b in result.timeline] == ["P1", "P2", "P1", "P2"]


@pytest.mark.parametrize("algo", [FCFS, SJF, PRIORITY, ROUND_ROBIN])
def test_idle_time_is_inserted_when_cpu_waits(algo):
    result = simulate([Process(1, 3, 2)], algo)
    assert result.timeline[0] == {"pid": "IDLE", "start": 0, "end": 3}
    assert result.timeline[1] == {"pid": "P1", "start": 3, "end": 5}
    assert by_name(result)["P1"].waiting == 0


@pytest.mark.parametrize("algo", [FCFS, SJF, PRIORITY, ROUND_ROBIN])
def test_waiting_equals_turnaround_minus_burst(algo):
    result = simulate(classic_set(), algo, quantum=3)
    for p in result.processes:
        assert p.waiting == p.turnaround - p.burst
        assert p.waiting >= 0


@pytest.mark.parametrize("algo", [FCFS, SJF, PRIORITY, ROUND_ROBIN])
def test_timeline_is_contiguous_and_covers_all_burst_time(algo):
    procs = classic_set()
    result = simulate(procs, algo, quantum=2)
    for prev, nxt in zip(result.timeline, result.timeline[1:]):
        assert prev["end"] == nxt["start"]
    busy = sum(b["end"] - b["start"] for b in result.timeline if b["pid"] != "IDLE")
    assert busy == sum(p.burst for p in procs)


def test_input_processes_are_not_modified():
    procs = classic_set()
    simulate(procs, FCFS)
    assert all(p.completion == 0 and p.remaining == p.burst for p in procs)


def test_invalid_inputs_raise_errors():
    with pytest.raises(ValueError):
        simulate([], FCFS)
    with pytest.raises(ValueError):
        simulate([Process(1, 0, 0)], FCFS)
    with pytest.raises(ValueError):
        simulate([Process(1, -1, 3)], FCFS)
    with pytest.raises(ValueError):
        simulate([Process(1, 0, 3)], ROUND_ROBIN, quantum=0)
    with pytest.raises(ValueError):
        simulate([Process(1, 0, 3)], "Made Up Algo")
