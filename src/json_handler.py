from datetime import datetime
import json


def sort_file_content(_file_content: dict[str, str]) -> dict[str, str]:
    return dict(sorted(_file_content.items()))


def write_to_file(file_loc: str, file_content, add_date_time: bool = False):
    if add_date_time:
        file_content["$$Scan_Time_And_Date$$"] = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    with open(file_loc, "w") as f:
        json.dump(sort_file_content(file_content), f, indent=2)


def read_file(file_loc: str) -> dict[str, str]:
    with open(file_loc, "r") as f:
        dat = json.load(f)
    return dat
