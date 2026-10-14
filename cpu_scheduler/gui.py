"""Tkinter GUI for the CPU Scheduling Simulator."""

import tkinter as tk
from tkinter import messagebox, ttk

from .algorithms import ALGORITHMS, FCFS, IDLE, ROUND_ROBIN, Process, simulate

GANTT_COLORS = ["#FF9999", "#99CCFF", "#99FF99", "#FFD700", "#E6E6FA", "#FFB6C1"]
RESET_AVG_TEXT = "Average Waiting Time: 0.00  |  Average Turnaround Time: 0.00"


class SchedulerApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Advanced CPU Scheduling Simulator")
        self.root.geometry("900x750")
        self.processes = []
        self.pid_counter = 1

        self._build_input_frame()
        self._build_algorithm_frame()
        self._build_results_table()
        self._build_output_area()

    # ------------------------------------------------------------------ UI --
    def _build_input_frame(self):
        frame = tk.Frame(self.root)
        frame.pack(pady=10)

        tk.Label(frame, text="Arrival Time:").grid(row=0, column=0, padx=5)
        self.at_entry = tk.Entry(frame, width=8)
        self.at_entry.grid(row=0, column=1, padx=5)

        tk.Label(frame, text="Burst Time:").grid(row=0, column=2, padx=5)
        self.bt_entry = tk.Entry(frame, width=8)
        self.bt_entry.grid(row=0, column=3, padx=5)

        tk.Label(frame, text="Priority:").grid(row=0, column=4, padx=5)
        self.pr_entry = tk.Entry(frame, width=8)
        self.pr_entry.grid(row=0, column=5, padx=5)

        tk.Button(
            frame, text="Add Process", command=self.add_process, bg="#4CAF50", fg="white"
        ).grid(row=0, column=6, padx=10)

        tk.Label(
            frame, text="(lower priority number = higher priority)", font=("Arial", 8), fg="gray"
        ).grid(row=1, column=4, columnspan=3, pady=(2, 0))

    def _build_algorithm_frame(self):
        frame = tk.Frame(self.root)
        frame.pack(pady=5)

        tk.Label(frame, text="Algorithm:").grid(row=0, column=0)
        self.algo_var = tk.StringVar(value=FCFS)
        self.algo_dropdown = ttk.Combobox(
            frame, textvariable=self.algo_var, values=ALGORITHMS, state="readonly", width=25
        )
        self.algo_dropdown.grid(row=0, column=1, padx=5)

        tk.Label(frame, text="Time Quantum (RR):").grid(row=0, column=2)
        self.tq_entry = tk.Entry(frame, width=5)
        self.tq_entry.grid(row=0, column=3, padx=5)
        self.tq_entry.insert(0, "2")

        tk.Button(
            frame, text="Run Simulation", command=self.run_simulation, bg="#2196F3", fg="white"
        ).grid(row=0, column=4, padx=10)
        tk.Button(
            frame, text="Clear All", command=self.clear_data, bg="#f44336", fg="white"
        ).grid(row=0, column=5)

    def _build_results_table(self):
        columns = ("ID", "Arrival", "Burst", "Priority", "Completion", "Turnaround", "Waiting")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings", height=6)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=90, anchor="center")
        self.tree.pack(pady=10)

        self.avg_label = tk.Label(self.root, text=RESET_AVG_TEXT, font=("Arial", 11, "bold"))
        self.avg_label.pack(pady=5)

    def _build_output_area(self):
        tk.Label(self.root, text="Visual Gantt Chart Timeline:", font=("Arial", 10, "bold")).pack(
            anchor="w", padx=20
        )
        self.gantt_canvas = tk.Canvas(
            self.root, height=90, bg="white", highlightthickness=1, highlightbackground="black"
        )
        self.gantt_canvas.pack(fill=tk.X, padx=20, pady=5)

        tk.Label(self.root, text="Detailed CPU Execution Flow:", font=("Arial", 10, "bold")).pack(
            anchor="w", padx=20
        )
        self.log_text = tk.Text(self.root, height=12, width=100, bg="#f4f4f4")
        self.log_text.pack(padx=20, pady=5)

    # ------------------------------------------------------------- Actions --
    def add_process(self):
        try:
            arrival = int(self.at_entry.get())
            burst = int(self.bt_entry.get())
            priority = int(self.pr_entry.get() or 0)
        except ValueError:
            messagebox.showerror("Error", "Please enter valid integers.")
            return

        if arrival < 0 or burst <= 0:
            messagebox.showerror(
                "Error", "Arrival time must be 0 or more, and burst time must be greater than 0."
            )
            return

        self.processes.append(Process(self.pid_counter, arrival, burst, priority))
        self.tree.insert(
            "", "end", values=(f"P{self.pid_counter}", arrival, burst, priority, "-", "-", "-")
        )
        self.pid_counter += 1
        for entry in (self.at_entry, self.bt_entry, self.pr_entry):
            entry.delete(0, tk.END)

    def clear_data(self):
        self.processes = []
        self.pid_counter = 1
        self.tree.delete(*self.tree.get_children())
        self.log_text.delete(1.0, tk.END)
        self.gantt_canvas.delete("all")
        self.avg_label.config(text=RESET_AVG_TEXT)

    def run_simulation(self):
        if not self.processes:
            messagebox.showwarning("Warning", "No processes added!")
            return

        algo = self.algo_var.get()
        quantum = 2
        if algo == ROUND_ROBIN:
            try:
                quantum = int(self.tq_entry.get())
            except ValueError:
                messagebox.showerror("Error", "Enter a valid integer for Time Quantum.")
                return

        try:
            result = simulate(self.processes, algo, quantum)
        except ValueError as error:
            messagebox.showerror("Error", str(error))
            return

        self._show_results(result)

    # ------------------------------------------------------------- Drawing --
    def _show_results(self, result):
        self.tree.delete(*self.tree.get_children())
        for p in result.processes:
            self.tree.insert(
                "",
                "end",
                values=(p.name, p.arrival, p.burst, p.priority, p.completion, p.turnaround, p.waiting),
            )

        self.avg_label.config(
            text=(
                f"Average Waiting Time: {result.avg_waiting:.2f}  |  "
                f"Average Turnaround Time: {result.avg_turnaround:.2f}"
            )
        )
        self.draw_gantt(result.timeline)

        self.log_text.delete(1.0, tk.END)
        for line in result.log:
            self.log_text.insert(tk.END, line + "\n")

    def draw_gantt(self, timeline):
        self.gantt_canvas.delete("all")
        if not timeline:
            return

        self.gantt_canvas.update()
        canvas_width = max(self.gantt_canvas.winfo_width() - 40, 100)  # side padding
        total_time = timeline[-1]["end"]
        scale = canvas_width / total_time if total_time > 0 else 1

        for block in timeline:
            pid, start, end = block["pid"], block["start"], block["end"]
            x1, x2 = 20 + start * scale, 20 + end * scale
            color = "white" if pid == IDLE else GANTT_COLORS[int(pid[1:]) % len(GANTT_COLORS)]
            self.gantt_canvas.create_rectangle(x1, 15, x2, 55, fill=color, outline="black")
            self.gantt_canvas.create_text((x1 + x2) / 2, 35, text=pid, font=("Arial", 9, "bold"))
            self.gantt_canvas.create_text(x1, 65, text=str(start), anchor="n", font=("Arial", 8))

        self.gantt_canvas.create_text(
            20 + total_time * scale, 65, text=str(total_time), anchor="n", font=("Arial", 8)
        )


def main():
    root = tk.Tk()
    SchedulerApp(root)
    root.mainloop()
