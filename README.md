# Stress and Craving Annotator

This repository contains a small Python desktop tool for recording participant
stress and craving reports during the Zoom/video experiment.

During the experiment, participants are prompted in the video to report stress
and craving levels on a `0-3` scale. This tool lets the experimenter mark the
start and end of the session, enter the current task or video section for each
stress/craving response, and export a timestamped CSV file for the participant.

## What the Tool Records

Each annotation entry includes:

- Participant ID
- Experiment start timestamp
- Experiment end timestamp
- Entry number
- Task or video section label
- Elapsed seconds from the moment **Start Experiment** was clicked
- Wall-clock timestamp for the entry
- Stress score
- Craving score

Scores are restricted to:

- `0`
- `1`
- `2`
- `3`

## Requirements

The tool uses only the Python standard library:

- `tkinter` for the desktop interface
- `csv` for CSV export
- `datetime` and `time` for timestamps

No third-party Python packages are required.

You should have Python 3 installed. The tool has been syntax-checked locally
with Python 3.13.

## Files

- `stress_craving_annotator.py`: Main annotation application.
- `README.md`: Usage and project documentation.
- `.gitignore`: Prevents large local videos, generated CSVs, and Python cache
  files from being committed.

The experiment video file is intentionally not included in git because it is a
large local study asset.

## Running the Tool

From this project directory, run:

```bash
python3 stress_craving_annotator.py
```

This opens the annotation window.

## Experiment Workflow

1. Open the Zoom/video experiment setup as usual.
2. Open the annotator app:

   ```bash
   python stress_craving_annotator.py
   ```

3. Enter the participant ID in the **Participant ID** field.
4. Click **Start Experiment** at the moment the experiment begins.
5. When the participant reports their levels, enter:
   - Current task or video section in the **Task/Section** box
   - Stress score in the **Stress (0-3)** box
   - Craving score in the **Craving (0-3)** box
6. Click **Add Entry**.
   - You can also press `Enter` after filling the task, stress, and craving fields.
   - The task/section text stays filled in after adding an entry, which is
     useful when several prompts occur within the same video task.
7. Repeat this for each prompt in the video. Update **Task/Section** whenever
   the video moves into a new task.
8. Click **End Experiment** when the experiment is complete.
9. Click **Save CSV**.

## Output

CSV files are saved in an `annotations/` folder using this naming format:

```text
PARTICIPANTID_YYYYMMDD_HHMMSS_stress_craving.csv
```

Example:

```text
annotations/TEST001_20260512_054402_stress_craving.csv
```

The CSV columns are:

```text
participant_id,experiment_start,experiment_end,entry_number,task,elapsed_seconds,wall_clock_timestamp,stress,craving
```

Example row:

```csv
TEST001,2026-05-12T05:44:02,2026-05-12T05:52:10,1,baseline,42.318,2026-05-12T05:44:44,2,1
```

## Important Notes

- Click **Start Experiment** at the exact point you want elapsed timestamps to
  begin.
- Each saved row requires a task/section label.
- Scores must be single values from `0` to `3`.
- The CSV is saved only after **End Experiment** is clicked.
- Generated CSV files are ignored by git so participant data is not pushed to
  GitHub by accident.
- The video file is ignored by git because it is large and may be a protected
  study asset.

## Git Hygiene

The repository ignores:

- `*.mp4`
- `annotations/`
- `__pycache__/`
- Python build/cache artifacts
- local virtual environments
- common editor and OS metadata

