import tkinter as tk
from tkinter import ttk, messagebox

class Process:
    def __init__(self, pid, arrival, burst, priority):
        self.id = pid
        self.arrival = arrival
        self.burst = burst
        self.priority = priority
        self.completion = 0
        self.turnaround = 0
        self.waiting = 0
        self.remaining = burst

class SchedulerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced CPU Scheduling Simulator")
        self.root.geometry("900x750")
        self.processes = []
        self.pid_counter = 1

        # --- Input Frame ---
        input_frame = tk.Frame(root)
        input_frame.pack(pady=10)

        tk.Label(input_frame, text="Arrival Time:").grid(row=0, column=0, padx=5)
        self.at_entry = tk.Entry(input_frame, width=8)
        self.at_entry.grid(row=0, column=1, padx=5)

        tk.Label(input_frame, text="Burst Time:").grid(row=0, column=2, padx=5)
        self.bt_entry = tk.Entry(input_frame, width=8)
        self.bt_entry.grid(row=0, column=3, padx=5)

        tk.Label(input_frame, text="Priority:").grid(row=0, column=4, padx=5)
        self.pr_entry = tk.Entry(input_frame, width=8)
        self.pr_entry.grid(row=0, column=5, padx=5)

        tk.Button(input_frame, text="Add Process", command=self.add_process, bg="#4CAF50", fg="white").grid(row=0, column=6, padx=10)

        # --- Algorithm Selection ---
        algo_frame = tk.Frame(root)
        algo_frame.pack(pady=5)
        
        tk.Label(algo_frame, text="Algorithm:").grid(row=0, column=0)
        self.algo_var = tk.StringVar(value="FCFS")
        algos = ["FCFS", "SJF (Non-Preemptive)", "Priority (Non-Preemptive)", "Round Robin"]
        self.algo_dropdown = ttk.Combobox(algo_frame, textvariable=self.algo_var, values=algos, state="readonly", width=25)
        self.algo_dropdown.grid(row=0, column=1, padx=5)

        tk.Label(algo_frame, text="Time Quantum (RR):").grid(row=0, column=2)
        self.tq_entry = tk.Entry(algo_frame, width=5)
        self.tq_entry.grid(row=0, column=3, padx=5)
        self.tq_entry.insert(0, "2")

        tk.Button(algo_frame, text="Run Simulation", command=self.run_simulation, bg="#2196F3", fg="white").grid(row=0, column=4, padx=10)
        tk.Button(algo_frame, text="Clear All", command=self.clear_data, bg="#f44336", fg="white").grid(row=0, column=5)

        # --- Results Table ---
        columns = ("ID", "Arrival", "Burst", "Priority", "Completion", "Turnaround", "Waiting")
        self.tree = ttk.Treeview(root, columns=columns, show="headings", height=6)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=90, anchor="center")
        self.tree.pack(pady=10)

        # --- Averages Label ---
        self.avg_label = tk.Label(root, text="Average WT: 0.00 | Average TAT: 0.00", font=("Arial", 11, "bold"))
        self.avg_label.pack(pady=5)

        # --- Visual Gantt Chart (Canvas) ---
        tk.Label(root, text="Visual Gantt Chart Timeline:", font=("Arial", 10, "bold")).pack(anchor="w", padx=20)
        self.gantt_canvas = tk.Canvas(root, height=90, bg="white", highlightthickness=1, highlightbackground="black")
        self.gantt_canvas.pack(fill=tk.X, padx=20, pady=5)

        # --- Detailed Execution Flow Log ---
        tk.Label(root, text="Detailed CPU Execution Flow:", font=("Arial", 10, "bold")).pack(anchor="w", padx=20)
        self.log_text = tk.Text(root, height=12, width=100, bg="#f4f4f4")
        self.log_text.pack(padx=20, pady=5)

    def add_process(self):
        try:
            at = int(self.at_entry.get())
            bt = int(self.bt_entry.get())
            pr = int(self.pr_entry.get() or 0)
            self.processes.append(Process(self.pid_counter, at, bt, pr))
            self.tree.insert("", "end", values=(f"P{self.pid_counter}", at, bt, pr, "-", "-", "-"))
            self.pid_counter += 1
            self.at_entry.delete(0, tk.END)
            self.bt_entry.delete(0, tk.END)
            self.pr_entry.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("Error", "Please enter valid integers.")

    def clear_data(self):
        self.processes = []
        self.pid_counter = 1
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.log_text.delete(1.0, tk.END)
        self.gantt_canvas.delete("all")
        self.avg_label.config(text="Average WT: 0.00 | Average TAT: 0.00")

    def draw_gantt(self, timeline):
        self.gantt_canvas.delete("all")
        if not timeline: return
        
        self.gantt_canvas.update()
        canvas_width = self.gantt_canvas.winfo_width() - 40 # Padding
        total_time = timeline[-1]['end']
        scale = canvas_width / total_time if total_time > 0 else 1
        
        colors = ["#FF9999", "#99CCFF", "#99FF99", "#FFD700", "#E6E6FA", "#FFB6C1"]

        for block in timeline:
            pid = block['pid']
            start = block['start']
            end = block['end']
            
            x1 = 20 + (start * scale)
            x2 = 20 + (end * scale)
            
            color = "white" if pid == 'IDLE' else colors[int(pid[1:]) % len(colors)]
            self.gantt_canvas.create_rectangle(x1, 15, x2, 55, fill=color, outline="black")
            self.gantt_canvas.create_text((x1+x2)/2, 35, text=pid, font=("Arial", 9, "bold"))
            self.gantt_canvas.create_text(x1, 65, text=str(start), anchor="n", font=("Arial", 8))
            
        # Draw final end time
        self.gantt_canvas.create_text(20 + (timeline[-1]['end'] * scale), 65, text=str(timeline[-1]['end']), anchor="n", font=("Arial", 8))

    def run_simulation(self):
        if not self.processes:
            messagebox.showwarning("Warning", "No processes added!")
            return

        algo = self.algo_var.get()
        for p in self.processes:
            p.completion = p.turnaround = p.waiting = 0
            p.remaining = p.burst
            
        p_copy = sorted(self.processes, key=lambda x: x.arrival)
        timeline = [] # Stores dicts: {pid, start, end}
        flow_log = [] # Stores strings for detailed explanation

        if algo == "FCFS":
            time = 0
            for p in p_copy:
                if time < p.arrival:
                    timeline.append({'pid': 'IDLE', 'start': time, 'end': p.arrival})
                    flow_log.append(f"[Time {time} to {p.arrival}] CPU is IDLE waiting for P{p.id}.")
                    time = p.arrival
                
                start_time = time
                time += p.burst
                timeline.append({'pid': f'P{p.id}', 'start': start_time, 'end': time})
                flow_log.append(f"[Time {start_time} to {time}] P{p.id} executes and completes its burst.")
                
                p.completion = time
                p.turnaround = p.completion - p.arrival
                p.waiting = p.turnaround - p.burst

        elif algo in ["SJF (Non-Preemptive)", "Priority (Non-Preemptive)"]:
            n = len(p_copy)
            done = [False] * n
            completed = time = 0
            
            while completed != n:
                idx = -1
                best_val = float('inf')
                
                for i in range(n):
                    if not done[i] and p_copy[i].arrival <= time:
                        compare_val = p_copy[i].burst if "SJF" in algo else p_copy[i].priority
                        if compare_val < best_val:
                            best_val = compare_val
                            idx = i
                            
                if idx == -1:
                    if not timeline or timeline[-1]['pid'] != 'IDLE':
                        timeline.append({'pid': 'IDLE', 'start': time, 'end': time + 1})
                        flow_log.append(f"[Time {time}] CPU is IDLE. No processes have arrived yet.")
                    else:
                        timeline[-1]['end'] += 1
                    time += 1
                else:
                    start_time = time
                    p = p_copy[idx]
                    time += p.burst
                    timeline.append({'pid': f'P{p.id}', 'start': start_time, 'end': time})
                    flow_log.append(f"[Time {start_time} to {time}] P{p.id} is selected and executes until completion.")
                    
                    p.completion = time
                    p.turnaround = p.completion - p.arrival
                    p.waiting = p.turnaround - p.burst
                    done[idx] = True
                    completed += 1

        elif algo == "Round Robin":
            try:
                quantum = int(self.tq_entry.get())
            except ValueError:
                messagebox.showerror("Error", "Enter a valid integer for Time Quantum.")
                return
                
            n = len(p_copy)
            q = []
            time = completed = i = 0
            
            while completed != n:
                while i < n and p_copy[i].arrival <= time:
                    q.append(i)
                    flow_log.append(f"[Time {p_copy[i].arrival}] P{p_copy[i].id} arrives and joins the Ready Queue.")
                    i += 1
                    
                if not q:
                    if not timeline or timeline[-1]['pid'] != 'IDLE':
                        timeline.append({'pid': 'IDLE', 'start': time, 'end': time + 1})
                    else:
                        timeline[-1]['end'] += 1
                    time += 1
                    continue
                
                idx = q.pop(0)
                p = p_copy[idx]
                start_time = time
                
                if p.remaining > quantum:
                    time += quantum
                    p.remaining -= quantum
                    timeline.append({'pid': f'P{p.id}', 'start': start_time, 'end': time})
                    flow_log.append(f"[Time {start_time} to {time}] P{p.id} executes for quantum ({quantum}). Remaining burst: {p.remaining}. Moves to back of queue.")
                else:
                    time += p.remaining
                    exec_time = p.remaining
                    p.remaining = 0
                    p.completion = time
                    p.turnaround = p.completion - p.arrival
                    p.waiting = p.turnaround - p.burst
                    completed += 1
                    timeline.append({'pid': f'P{p.id}', 'start': start_time, 'end': time})
                    flow_log.append(f"[Time {start_time} to {time}] P{p.id} executes for its final {exec_time} units and COMPLETES.")
                    
                while i < n and p_copy[i].arrival <= time:
                    q.append(i)
                    flow_log.append(f"[Time {p_copy[i].arrival}] P{p_copy[i].id} arrives and joins the Ready Queue.")
                    i += 1
                    
                if p.remaining > 0:
                    q.append(idx)

        # Update UI
        self.update_results_ui(p_copy, timeline, flow_log)

    def update_results_ui(self, p_list, timeline, flow_log):
        # Update Table
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        p_list.sort(key=lambda x: x.id)
        total_wt = total_tat = 0
        
        for p in p_list:
            self.tree.insert("", "end", values=(f"P{p.id}", p.arrival, p.burst, p.priority, p.completion, p.turnaround, p.waiting))
            total_wt += p.waiting
            total_tat += p.turnaround
            
        # Update Averages
        avg_wt = total_wt / len(p_list) if p_list else 0
        avg_tat = total_tat / len(p_list) if p_list else 0
        self.avg_label.config(text=f"Average Waiting Time: {avg_wt:.2f}  |  Average Turnaround Time: {avg_tat:.2f}")

        # Update Visuals
        self.draw_gantt(timeline)
        
        # Update Flow Log
        self.log_text.delete(1.0, tk.END)
        for log in flow_log:
            self.log_text.insert(tk.END, log + "\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = SchedulerApp(root)
    root.mainloop()