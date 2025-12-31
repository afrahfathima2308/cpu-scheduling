from dataclasses import dataclass
import matplotlib.pyplot as plt
from collections import deque

@dataclass
class Process:
    pid: str
    arrival: int
    burst: int
    priority: int = 0

# ---------- Common function to calculate metrics ----------
def compute_metrics(processes, completion_times):
    tat, wt = {}, {}
    for p in processes:
        tat[p.pid] = completion_times[p.pid] - p.arrival
        wt[p.pid] = tat[p.pid] - p.burst
    avg_tat = sum(tat.values()) / len(processes)
    avg_wt = sum(wt.values()) / len(processes)
    return tat, wt, avg_tat, avg_wt

# ---------- 1. FCFS ----------
def fcfs(processes):
    procs = sorted(processes, key=lambda p: p.arrival)
    time = 0
    segments, completion = {p.pid: [] for p in procs}, {}
    for p in procs:
        start = max(time, p.arrival)
        segments[p.pid].append((start, p.burst))
        time = start + p.burst
        completion[p.pid] = time
    return segments, completion

# ---------- 2. SJF (Non-preemptive) ----------
def sjf_nonpreemptive(processes):
    n = len(processes)
    done, time = set(), 0
    segments, completion = {p.pid: [] for p in processes}, {}
    while len(done) < n:
        ready = [p for p in processes if p.arrival <= time and p.pid not in done]
        if not ready:
            time += 1
            continue
        cur = min(ready, key=lambda p: p.burst)
        segments[cur.pid].append((time, cur.burst))
        time += cur.burst
        completion[cur.pid] = time
        done.add(cur.pid)
    return segments, completion

# ---------- 3. SRTF (Preemptive SJF) ----------
def srtf(processes):
    remaining = {p.pid: p.burst for p in processes}
    segments, completion = {p.pid: [] for p in processes}, {}
    time, last_pid = 0, None
    while len(completion) < len(processes):
        ready = [p for p in processes if p.arrival <= time and p.pid not in completion]
        if not ready:
            time += 1
            continue
        cur = min(ready, key=lambda p: remaining[p.pid])
        if last_pid != cur.pid:
            segments[cur.pid].append((time, 0))
        remaining[cur.pid] -= 1
        start, dur = segments[cur.pid][-1]
        segments[cur.pid][-1] = (start, dur + 1)
        time += 1
        if remaining[cur.pid] == 0:
            completion[cur.pid] = time
        last_pid = cur.pid
    return segments, completion

# ---------- 4. Round Robin ----------
def rr(processes, quantum=2):
    remaining = {p.pid: p.burst for p in processes}
    queue, time, segments, completion = deque(), 0, {p.pid: [] for p in processes}, {}
    arrived = set()
    while len(completion) < len(processes):
        for p in processes:
            if p.arrival <= time and p.pid not in arrived:
                queue.append(p.pid)
                arrived.add(p.pid)
        if not queue:
            time += 1
            continue
        pid = queue.popleft()
        run = min(quantum, remaining[pid])
        segments[pid].append((time, run))
        time += run
        remaining[pid] -= run
        for p in processes:
            if p.arrival <= time and p.pid not in arrived:
                queue.append(p.pid)
                arrived.add(p.pid)
        if remaining[pid] > 0:
            queue.append(pid)
        else:
            completion[pid] = time
    return segments, completion

# ---------- Function to plot Gantt Chart ----------
def plot_gantt(segments, title):
    fig, ax = plt.subplots(figsize=(9, 3))
    y = 10
    for pid, segs in segments.items():
        for (start, dur) in segs:
            ax.broken_barh([(start, dur)], (y, 9))
            ax.text(start + dur/2, y + 4.5, pid, ha='center', va='center', fontsize=8)
        y += 10
    ax.set_xlabel("Time")
    ax.set_ylabel("Processes")
    ax.set_title(title)
    ax.grid(True)
    plt.show()

# ---------- MAIN ----------
if __name__ == "_main_":
    processes = [
        Process("P1", 0, 5),
        Process("P2", 1, 3),
        Process("P3", 2, 8),
    ]

    print("Choose Algorithm:")
    print("1. FCFS\n2. SJF\n3. SRTF\n4. Round Robin")
    ch = int(input("Enter choice (1-4): "))

    if ch == 1:
        segs, comp = fcfs(processes)
        title = "FCFS Scheduling"
    elif ch == 2:
        segs, comp = sjf_nonpreemptive(processes)
        title = "SJF (Non-Preemptive) Scheduling"
    elif ch == 3:
        segs, comp = srtf(processes)
        title = "SRTF Scheduling"
    elif ch == 4:
        q = int(input("Enter time quantum: "))
        segs, comp = rr(processes, q)
        title = f"Round Robin (q={q})"
    else:
        print("Invalid choice!")
        exit()

    tat, wt, atat, awt = compute_metrics(processes, comp)
    print("\nCompletion Time:", comp)
    print("Turnaround Time:", tat)
    print("Waiting Time:", wt)
    print(f"Average TAT: {atat:.2f}, Average WT: {awt:.2f}")
    plot_gantt(segs, title)