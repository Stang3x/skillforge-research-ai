Tools usage
===========

This folder contains helper scripts used during development and CI.

Running PowerShell PSScriptAnalyzer helper
- Use the Python wrapper to avoid Windows path quoting issues:

```powershell
cd "C:\Users\Stang3x\Documents\Gemini projects"
python tools/run_psscriptanalyzer.py --fail-on-error
```

Or run the PowerShell script directly from PowerShell:

```powershell
cd "C:\Users\Stang3x\Documents\Gemini projects"
.\tools\run_psscriptanalyzer.ps1 -FailOnError
```

Other helpers
- `tools/run_local_metrics_demo.py` — quick demo of the metrics exporter
- `tools/exemplar_harness.py` — exemplar validation harness (direct/collector modes)
- `tools/cache_cli.py` — inspect and manage caches
