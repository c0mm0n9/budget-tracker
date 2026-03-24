import csv
import os


def read_csv_dicts(file_path: str) -> list[dict[str, str | None]]:
    """
    Read a CSV with a header row into a list of dicts (string cell values).
    Returns an empty list if the file is missing or has no header.
    """
    try:
        with open(file_path, "r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            if reader.fieldnames is None:
                return []
            return list(reader)
    except FileNotFoundError:
        return []


def write_csv_dicts(file_path: str, rows: list[dict], fieldnames: list[str]) -> None:
    """Write dict rows using the given column order; writes header only if rows is empty."""
    directory = os.path.dirname(file_path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    with open(file_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fieldnames})
            