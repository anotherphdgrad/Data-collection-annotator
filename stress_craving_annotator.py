#!/usr/bin/env python3
"""
Simple stress/craving annotation tool for the OUD Mayo Zoom experiment.

The app timestamps each stress/craving report relative to the moment the
experimenter clicks "Start Experiment" and writes one CSV per participant.
"""

from __future__ import annotations

import csv
import re
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from tkinter import END, N, S, W, E, StringVar, Tk, messagebox, ttk


SCORE_PATTERN = re.compile(r"^[0-3]$")
OUTPUT_DIR = Path("annotations")


@dataclass
class Annotation:
    entry_number: int
    elapsed_seconds: float
    wall_clock_timestamp: str
    stress: int
    craving: int


class StressCravingAnnotator:
    def __init__(self, root: Tk) -> None:
        self.root = root
        self.root.title("Stress and Craving Annotator")
        self.root.minsize(760, 520)

        self.participant_id = StringVar()
        self.stress_value = StringVar()
        self.craving_value = StringVar()
        self.status = StringVar(value="Enter participant ID, then click Start Experiment.")
        self.timer_text = StringVar(value="Elapsed: 00:00.0")

        self.experiment_started = False
        self.experiment_ended = False
        self.start_monotonic: float | None = None
        self.start_wall_clock: datetime | None = None
        self.end_wall_clock: datetime | None = None
        self.annotations: list[Annotation] = []

        self._build_ui()
        self._tick_timer()

    def _build_ui(self) -> None:
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(2, weight=1)

        top = ttk.Frame(self.root, padding=16)
        top.grid(row=0, column=0, sticky=(W, E))
        top.columnconfigure(1, weight=1)

        ttk.Label(top, text="Participant ID").grid(row=0, column=0, sticky=W, padx=(0, 10))
        participant_entry = ttk.Entry(top, textvariable=self.participant_id, width=28)
        participant_entry.grid(row=0, column=1, sticky=(W, E), padx=(0, 16))
        participant_entry.focus()

        ttk.Label(top, textvariable=self.timer_text, font=("TkDefaultFont", 14, "bold")).grid(
            row=0, column=2, sticky=E
        )

        controls = ttk.Frame(self.root, padding=(16, 0, 16, 12))
        controls.grid(row=1, column=0, sticky=(W, E))
        controls.columnconfigure(5, weight=1)

        self.start_button = ttk.Button(
            controls, text="Start Experiment", command=self.start_experiment
        )
        self.start_button.grid(row=0, column=0, sticky=W, padx=(0, 8))

        self.end_button = ttk.Button(
            controls,
            text="End Experiment",
            command=self.end_experiment,
            state="disabled",
        )
        self.end_button.grid(row=0, column=1, sticky=W, padx=(0, 24))

        ttk.Label(controls, text="Stress (0-3)").grid(row=0, column=2, sticky=W, padx=(0, 8))
        self.stress_entry = ttk.Entry(controls, textvariable=self.stress_value, width=8)
        self.stress_entry.grid(row=0, column=3, sticky=W, padx=(0, 16))

        ttk.Label(controls, text="Craving (0-3)").grid(row=0, column=4, sticky=W, padx=(0, 8))
        self.craving_entry = ttk.Entry(controls, textvariable=self.craving_value, width=8)
        self.craving_entry.grid(row=0, column=5, sticky=W, padx=(0, 16))

        self.add_button = ttk.Button(
            controls,
            text="Add Entry",
            command=self.add_annotation,
            state="disabled",
        )
        self.add_button.grid(row=0, column=6, sticky=E)

        self.root.bind("<Return>", lambda _event: self.add_annotation())

        table_frame = ttk.Frame(self.root, padding=(16, 0, 16, 12))
        table_frame.grid(row=2, column=0, sticky=(N, S, W, E))
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        columns = ("entry", "elapsed", "timestamp", "stress", "craving")
        self.table = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)
        self.table.heading("entry", text="#")
        self.table.heading("elapsed", text="Elapsed Seconds")
        self.table.heading("timestamp", text="Wall Clock Timestamp")
        self.table.heading("stress", text="Stress")
        self.table.heading("craving", text="Craving")
        self.table.column("entry", width=50, anchor="center")
        self.table.column("elapsed", width=130, anchor="center")
        self.table.column("timestamp", width=260, anchor="center")
        self.table.column("stress", width=90, anchor="center")
        self.table.column("craving", width=90, anchor="center")
        self.table.grid(row=0, column=0, sticky=(N, S, W, E))

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.table.yview)
        scrollbar.grid(row=0, column=1, sticky=(N, S))
        self.table.configure(yscrollcommand=scrollbar.set)

        bottom = ttk.Frame(self.root, padding=(16, 0, 16, 16))
        bottom.grid(row=3, column=0, sticky=(W, E))
        bottom.columnconfigure(0, weight=1)

        ttk.Label(bottom, textvariable=self.status).grid(row=0, column=0, sticky=W)
        self.export_button = ttk.Button(
            bottom,
            text="Save CSV",
            command=self.save_csv,
            state="disabled",
        )
        self.export_button.grid(row=0, column=1, sticky=E)

    def start_experiment(self) -> None:
        participant = self.participant_id.get().strip()
        if not participant:
            messagebox.showerror("Missing participant ID", "Please enter a participant ID first.")
            return

        self.experiment_started = True
        self.experiment_ended = False
        self.start_monotonic = time.monotonic()
        self.start_wall_clock = datetime.now()
        self.end_wall_clock = None
        self.annotations.clear()
        self.table.delete(*self.table.get_children())

        self.start_button.configure(state="disabled")
        self.end_button.configure(state="normal")
        self.add_button.configure(state="normal")
        self.export_button.configure(state="disabled")
        self.stress_entry.focus()
        self.status.set("Experiment running. Enter stress and craving, then click Add Entry.")

    def end_experiment(self) -> None:
        if not self.experiment_started:
            return

        self.experiment_ended = True
        self.end_wall_clock = datetime.now()
        self.end_button.configure(state="disabled")
        self.add_button.configure(state="disabled")
        self.export_button.configure(state="normal")
        self.status.set("Experiment ended. Click Save CSV to write the participant file.")

    def add_annotation(self) -> None:
        if not self.experiment_started or self.experiment_ended:
            return

        stress = self._validated_score(self.stress_value.get(), "stress")
        craving = self._validated_score(self.craving_value.get(), "craving")
        if stress is None or craving is None:
            return

        assert self.start_monotonic is not None
        elapsed = time.monotonic() - self.start_monotonic
        annotation = Annotation(
            entry_number=len(self.annotations) + 1,
            elapsed_seconds=round(elapsed, 3),
            wall_clock_timestamp=datetime.now().isoformat(timespec="seconds"),
            stress=stress,
            craving=craving,
        )
        self.annotations.append(annotation)
        self.table.insert(
            "",
            END,
            values=(
                annotation.entry_number,
                f"{annotation.elapsed_seconds:.3f}",
                annotation.wall_clock_timestamp,
                annotation.stress,
                annotation.craving,
            ),
        )
        self.stress_value.set("")
        self.craving_value.set("")
        self.stress_entry.focus()
        self.status.set(f"Added entry {annotation.entry_number}.")

    def save_csv(self) -> None:
        if not self.experiment_started or not self.experiment_ended:
            messagebox.showerror("Experiment still running", "Click End Experiment before saving.")
            return

        participant = self.participant_id.get().strip()
        if not participant:
            messagebox.showerror("Missing participant ID", "Please enter a participant ID.")
            return

        OUTPUT_DIR.mkdir(exist_ok=True)
        safe_participant = re.sub(r"[^A-Za-z0-9_.-]+", "_", participant).strip("_")
        run_stamp = self.start_wall_clock.strftime("%Y%m%d_%H%M%S") if self.start_wall_clock else "run"
        output_path = OUTPUT_DIR / f"{safe_participant}_{run_stamp}_stress_craving.csv"

        with output_path.open("w", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(
                csv_file,
                fieldnames=[
                    "participant_id",
                    "experiment_start",
                    "experiment_end",
                    "entry_number",
                    "elapsed_seconds",
                    "wall_clock_timestamp",
                    "stress",
                    "craving",
                ],
            )
            writer.writeheader()
            for annotation in self.annotations:
                writer.writerow(
                    {
                        "participant_id": participant,
                        "experiment_start": self._format_datetime(self.start_wall_clock),
                        "experiment_end": self._format_datetime(self.end_wall_clock),
                        "entry_number": annotation.entry_number,
                        "elapsed_seconds": f"{annotation.elapsed_seconds:.3f}",
                        "wall_clock_timestamp": annotation.wall_clock_timestamp,
                        "stress": annotation.stress,
                        "craving": annotation.craving,
                    }
                )

        self.status.set(f"Saved {output_path}")
        messagebox.showinfo("CSV saved", f"Saved annotation file:\n{output_path}")
        self.start_button.configure(state="normal")

    def _validated_score(self, raw_value: str, field_name: str) -> int | None:
        value = raw_value.strip()
        if not SCORE_PATTERN.match(value):
            messagebox.showerror(
                "Invalid score",
                f"Please enter a {field_name} score from 0 to 3.",
            )
            return None
        return int(value)

    def _tick_timer(self) -> None:
        if self.experiment_started and not self.experiment_ended and self.start_monotonic is not None:
            elapsed = time.monotonic() - self.start_monotonic
            minutes, seconds = divmod(elapsed, 60)
            self.timer_text.set(f"Elapsed: {int(minutes):02d}:{seconds:04.1f}")
        self.root.after(100, self._tick_timer)

    @staticmethod
    def _format_datetime(value: datetime | None) -> str:
        if value is None:
            return ""
        return value.isoformat(timespec="seconds")


def main() -> None:
    root = Tk()
    StressCravingAnnotator(root)
    root.mainloop()


if __name__ == "__main__":
    main()
