import sys


def test_run_then_notify_no_sleep(monkeypatch, capsys):
    # prevent actual sleeping
    monkeypatch.setattr('time.sleep', lambda s: None)

    monkeypatch.setattr(sys, 'argv', ['demo_run_then_notify.py', '--duration', '0'])

    import tools.demo_run_then_notify as mod

    mod.main()

    captured = capsys.readouterr()
    assert 'Starting long task' in captured.out
    assert 'Task complete' in captured.out
