from pathlib import Path


def test_rename_spaces(tmp_path):
    f1 = tmp_path / "my file.txt"
    f2 = tmp_path / "another file.md"
    f1.write_text("1")
    f2.write_text("2")

    import tools.demo_file_renamer as mod

    mod.rename_spaces(tmp_path)

    assert (tmp_path / "my_file.txt").exists()
    assert (tmp_path / "another_file.md").exists()
