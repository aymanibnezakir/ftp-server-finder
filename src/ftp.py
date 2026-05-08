from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

import os
from rich import print as cprint

from json_handler import write_to_file, read_file


class Ftp:
    def __init__(self,
        ftp_json_file_location,
        available_ftp_json_file_location
    ) -> None:
        self.ftp_json_file_location = ftp_json_file_location
        self.available_ftp_json_file_location = available_ftp_json_file_location

    def write_available_dict(self):
        write_to_file(
            self.available_ftp_json_file_location,
            self.write_available_dict,
            add_date_time=True,
        )

    def load_server_dict(self):
        self.ftp_server_dict = read_file(self.ftp_json_file_location)

    def check_server(self, server_name, server_url):
        try:
            headers = {"User-Agent": "Mozilla/5.0"}

            response = requests.get(
                server_url, headers=headers, timeout=5, allow_redirects=True
            )

            if not response.ok:
                return None

            if len(response.history) > 8:
                return None

            content = response.text.lower()

            bad_patterns = [
                "redirecting...",
                "<title>redirecting</title>",
                "window.location",
                "location.href",
            ]

            if any(pattern in content for pattern in bad_patterns):
                if len(content.strip()) < 5000:
                    return None

            return server_name, server_url

        except requests.exceptions.RequestException:
            return None

    def scan_servers(self):
        self.available_ftp_dict = {}

        total = len(self.ftp_server_dict)
        completed = 0

        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = [
                executor.submit(self.check_server, name, url)
                for name, url in self.ftp_server_dict.items()
            ]

            for future in as_completed(futures):
                completed += 1

                progress = (completed / total) * 100

                print(f"\rScanning: {completed}/{total} ({progress:.1f}%)", end="")

                result = future.result()

                if result:
                    name, url = result
                    self.available_ftp_dict[name] = url

        print("\n")
        if len(self.available_ftp_dict) > 0:
            self.write_available_dict()
            return self.available_ftp_dict
        else:
            cprint("[yellow]Oops! We could not find any working server for you...[/yellow]")
            if os.path.exists(self.available_ftp_json_file_location):
                os.remove(self.available_ftp_json_file_location)

