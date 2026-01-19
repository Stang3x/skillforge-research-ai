from pathlib import Path


def test_organize_moves_files(tmp_path):
    # create sample files
    a = tmp_path / "a.txt"
    b = tmp_path / "b.jpg"
    c = tmp_path / "README"
    a.write_text("hello")
    b.write_text("img")
    c.write_text("noext")

    import tools.demo_file_organizer as mod

    mod.organize(tmp_path)

    assert (tmp_path / "txt" / "a.txt").exists()
    assert (tmp_path / "jpg" / "b.jpg").exists()
    assert (tmp_path / "noext" / "README").exists()
