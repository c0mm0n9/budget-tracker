import csv

def read_csv(file_path: str) -> list[dict]:
    """
    Read a CSV file and return a list of dictionaries.
    """
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        return list(reader)

def write_csv(file_path: str, data: list[dict]) -> None:
    """
    Write a list of dictionaries to a CSV file.
    """
    with open(file_path, 'w') as file:
        writer = csv.writer(file)
        writer.writerows(data)

def append_csv(file_path: str, data: list[dict]) -> None:
    """
    Append a list of dictionaries to a CSV file.
    """
    with open(file_path, 'a') as file:
        writer = csv.writer(file)
        writer.writerows(data)

def update_record(file_path: str, target: dict, record: dict) -> dict:
    """
    Update a record in a CSV file.
    """
    data = read_csv(file_path)
    for record in data:
        if record == target:
            data.remove(target)
            data.append(record)
            return record
    return None

def delete_record(file_path: str, target: dict) -> dict:
    """
    Delete a record from a CSV file.
    """
    data = read_csv(file_path)
    for record in data:
        if record == target:
            data.remove(target)
            return record
    return None

def create_record(file_path: str, record: dict) -> dict:
    """
    Create a record in a CSV file.
    """
    data = read_csv(file_path)
    data.append(record)
    write_csv(file_path, data)
    return record