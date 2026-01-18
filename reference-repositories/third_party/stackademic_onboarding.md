# Stackademic Onboarding Exercises

This short onboarding maps 3 hands-on exercises (inspired by the Stackademic list) to the safe demo scripts under `tools/`.

Exercises
---------

1. File Renamer
- Goal: Replace spaces in file names with underscores.
- Demo: `tools/demo_file_renamer.py`
- Run:

```powershell
python tools/demo_file_renamer.py C:\path\to\sample_folder
```

2. File Organizer
- Goal: Move files into folders named by extension (e.g., `pdf/`, `jpg/`).
- Demo: `tools/demo_file_organizer.py`
- Run:

```powershell
python tools/demo_file_organizer.py C:\path\to\sample_folder
```

3. Run-Then-Notify
- Goal: Demonstrate long-running job pattern and notification hook.
- Demo: `tools/demo_run_then_notify.py`
- Run:

```powershell
python tools/demo_run_then_notify.py --duration 10
```

Next steps for contributors
---------------------------
- Map each exercise to a canonical implementation in `reference-repositories/third_party/wasmerio-Python-Scripts` and `awesome-scripts-dedsecinside`.
- Create small unit tests (in `tests/tools/`) that exercise each demo in a sandboxed tempdir.
- If a script requires external deps, create a lightweight wrapper that checks and documents required packages.

Security note: do not run demo scripts on sensitive directories — use a disposable sample folder for testing.
