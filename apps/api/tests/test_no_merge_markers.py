from pathlib import Path


CONFLICT_MARKERS = ("<<<<<<<", "=======", ">>>>>>>")


def test_repository_has_no_merge_conflict_markers() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    files_to_check = [
        repo_root / "apps/api/app/main.py",
        repo_root / "apps/api/app/models.py",
        repo_root / "apps/api/app/schemas.py",
        repo_root / "apps/api/app/seed.py",
        repo_root / "apps/api/requirements.txt",
    ]

    for file_path in files_to_check:
        content = file_path.read_text(encoding="utf-8")
        assert not any(marker in content for marker in CONFLICT_MARKERS), (
            f"Arquivo com marcador de conflito de merge: {file_path}"
        )
