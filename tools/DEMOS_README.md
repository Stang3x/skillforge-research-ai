Demo scripts for onboarding and safe experiments.

Available demos:
- `demo_file_organizer.py` — organize files into extension folders
- `demo_file_renamer.py` — replace spaces with underscores in filenames
- `demo_run_then_notify.py` — simulate long-running task then print notification

Run examples:

```powershell
python tools/demo_file_renamer.py C:\path\to\sample
python tools/demo_file_organizer.py C:\path\to\sample
python tools/demo_run_then_notify.py --duration 10
```

Notes:
- Use small sample folders.
- Scripts use only the Python standard library.
