import sys
import requests
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn, MofNCompleteColumn
from rich.text import Text
from rich.rule import Rule
from rich.align import Align
from rich import box
from concurrent.futures import ThreadPoolExecutor, as_completed

console = Console()

BANNER = r"""
    _______________     ___________           __         
   / ____/_  __/ __ \  / ____/  _/ /___  ____/ /__  _____
  / /_    / / / /_/ / / /_   / // / __ \/ __  / _ \/ ___/
 / __/   / / / ____/ / __/ _/ // / / / / /_/ /  __/ /    
/_/     /_/ /_/     /_/   /___/_/_/ /_/\__,_/\___/_/     
"""

class FTP_Finder:
    def __init__(self) -> None:
        self.ftp_json_file_link = "https://raw.githubusercontent.com/aymanibnezakir/ftp-server-finder/main/all_ftp.json"

        # Fetch list
        try:
            self.ftp_dict = self.fetch_list()
            if len(self.ftp_dict) == 0:
                raise Exception("Broken List")
            else:
                console.print(f"  [dim]Fetched [bold white]{len(self.ftp_dict)}[/bold white] servers from remote list[/dim]\n")

        except Exception as e:
            console.print(Panel(
                f"[bold red]An error occurred:[/bold red] {e}",
                border_style="red",
                title="[bold red]✗ Error[/bold red]",
                padding=(1, 2),
            ))
            sys.exit(1)

    def fetch_list(self):
        with console.status("[bold cyan]Fetching server list…[/bold cyan]", spinner="dots"):
            response = requests.get(self.ftp_json_file_link)
            return response.json()

    def scan_servers(self):
        def check_server(server_name, server_url):
            try:
                headers = {"User-Agent": "Mozilla/5.0"}
    
                response = requests.get(
                    server_url, headers=headers, timeout=10, allow_redirects=True
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

        available_ftp_dict = {}
        total = len(self.ftp_dict)
        
        with Progress(
            SpinnerColumn(style="cyan"),
            TextColumn("[bold white]{task.description}[/bold white]"),
            BarColumn(bar_width=40, style="dim white", complete_style="cyan", finished_style="green"),
            MofNCompleteColumn(),
            TextColumn("[dim]•[/dim]"),
            TimeElapsedColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("Scanning servers", total=total)

            with ThreadPoolExecutor(max_workers=50) as executor:
                futures = [
                    executor.submit(check_server, name, url)
                    for name, url in self.ftp_dict.items()
                ]

                for future in as_completed(futures):
                    progress.advance(task)

                    result = future.result()

                    if result:
                        name, url = result
                        available_ftp_dict[name] = url

        console.print()
        return available_ftp_dict


# Header 
console.print()
console.print(Align.center(Text(BANNER, style="bold cyan")))
console.print(Align.center(Text("by Ayman Zakir", style="dim")))
console.print()
console.print(Rule(style="dim cyan"))
console.print()

# Run
available_servers: dict = FTP_Finder().scan_servers()

if len(available_servers) == 0:
    console.print(Panel(
        "[bold red]Oops! We found no working servers for you.[/bold red]",
        border_style="red",
        title="[red]✗ No Results[/red]",
        padding=(1, 2),
    ))

else:
    # Results summary
    console.print(Panel(
        f"[bold green]✓[/bold green] Found [bold white]{len(available_servers)}[/bold white] working servers",
        border_style="green",
        padding=(0, 2),
    ))
    console.print("[dim]  Ctrl + click a URL to open it in your browser[/dim]\n")

    # Results table 
    table = Table(
        box=box.ROUNDED,
        border_style="bright_cyan",
        header_style="bold bright_white on grey23",
        row_styles=["", "on grey7"],
        padding=(0, 2),
        show_lines=True,
        expand=True,
    )

    table.add_column("#", style="dim cyan", justify="right", width=4)
    table.add_column("Server Name", style="bold white", ratio=2)
    table.add_column("URL", style="cyan", ratio=3)

    for i, (name, url) in enumerate(available_servers.items(), start=1):
        table.add_row(str(i), name, url)

    console.print(table)

# Security notice
console.print()
notice_text = Text.assemble(
    ("For an enhanced browsing experience and improved protection\n", "white"),
    ("against unwanted redirects, pop-ups, and potentially intrusive\n", "white"),
    ("content, it is recommended to use a privacy-focused browser\n", "white"),
    ("such as ", "white"),
    ("Brave", "bold orange3"),
    (" or a reputable content-blocking extension\n", "white"),
    ("such as ", "white"),
    ("uBlock Origin ", "bold red"),
    ("(https://github.com/gorhill/uBlock/)", "cyan underline"),
    ("\n\nIf you believe a server result is incorrect, please report\nit to the author (github.com/aymanibnezakir)", "dim yellow")
)

console.print(Panel(
    Align.center(notice_text),
    title="[bold bright_yellow]Important Notice[/bold bright_yellow]",
    border_style="bright_yellow",
    padding=(1, 3),
))


input("\nPress ENTER to exit...  ")
