import os
import sys
from rich import print as cprint
import tempfile

import ftp
from json_handler import read_file
import github

class Menu:
    def __init__(self) -> None:
        self.ftp_json_file_location = os.path.join(
            tempfile.gettempdir(),
            "ftp.json"
        )
        self.available_ftp_json_file_location = os.path.join(
            tempfile.gettempdir(),
            "available_ftp.json"
        )

    def build_and_show_menu_selection_list(self):
        def check_previous_scan_is_available():
            if os.path.exists(self.available_ftp_json_file_location):
                data = read_file(self.available_ftp_json_file_location)
                date = data["$$Scan_Time_And_Date$$"]
                return date, data
            else:
                return None

        if not os.path.exists(self.ftp_json_file_location):
            cprint(
                "[italic bright_black]Fetching FTP servers, please wait...[/italic bright_black]"
            )
            result = github.download_file_from_github(self.ftp_json_file_location)

        result = check_previous_scan_is_available()
        item_count = 2
        
        cprint(
            "1. Scan for available FTPs" if result is None else "1. Re-scan for available FTPs"
        )
        
        if result is not None:
            cprint(
                f"2. Show previously scanned FTPs [bright_black](last scan: {result[0]})[/bright_black]",
                "3. Quit"
            )
            item_count += 1
        else:
            cprint("2. Quit")

        user_inp = int(input(f"\nEnter your choice (1 - {item_count}) > "))

        if user_inp == 1:
            os.system('cls')
            scanner = ftp.Ftp(self.ftp_json_file_location, self.available_ftp_json_file_location)
            scanner.load_server_dict()
            servers = scanner.scan_servers()

            for i, (name, url) in enumerate(servers.items(), start=1):
                cprint(f"[{i}] [bold]{name}[/bold] --> {url}")

            input("Press enter to exit...")

        if user_inp == 2:
            if item_count == 2:
                sys.exit(0)
        
            else:
                os.system('cls')
                for i, (name, url) in enumerate(result[1], start=1):
                    cprint(f"[{i}] [bold]{name}[/bold] --> {url}")

                input("Press enter to exit...")

        if user_inp == 3:
            sys.exit(0)

try:
    menu = Menu()
    menu.build_and_show_menu_selection_list()

except Exception as e:
    print(f"An error occured:  {e}")