import json
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt
from rich.layout import Layout
from rich.live import Live
from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style

console = Console()

class TUI:
    def __init__(self):
        self.console = console
        # Initialize prompt_toolkit session
        self.session = PromptSession()
        self.style = Style.from_dict({
            'prompt': 'bold cyan',
        })

    def print_welcome(self):
        self.console.print(Panel.fit(
            "[bold green]Mango Agent[/bold green] [yellow](Enhanced)[/yellow]\n"
            "An autonomous coding agent with git worktree isolation.",
            title="🥭 Welcome",
            border_style="green"
        ))

    def print_system_message(self, message: str):
        self.console.print(f"[bold cyan]System:[/bold cyan] {message}")

    def print_user_message(self, message: str):
        self.console.print(Panel(message, title="User", border_style="blue", title_align="left"))

    def print_assistant_message(self, message: str):
        md = Markdown(message)
        self.console.print(Panel(md, title="Mango", border_style="green", title_align="left"))

    def print_tool_call(self, tool_name: str, args: dict):
        args_json = json.dumps(args, indent=2, ensure_ascii=False)
        syntax = Syntax(args_json, "json", theme="monokai", word_wrap=True)
        self.console.print(Panel(syntax, title=f"🛠️ Tool Call: {tool_name}", border_style="yellow", title_align="left"))

    def print_tool_result(self, result: str):
        # Truncate if too long
        display_result = result[:500] + "... (truncated)" if len(result) > 500 else result
        self.console.print(Panel(display_result, title="✅ Result", border_style="dim white", title_align="left"))

    def print_error(self, error: str):
        self.console.print(f"[bold red]Error:[/bold red] {error}")

    def print_usage(self, in_tokens: int, out_tokens: int, total_tokens: int, ctx_percent: float):
        table = Table(show_header=True, header_style="bold magenta", box=None)
        table.add_column("Input", justify="right")
        table.add_column("Output", justify="right")
        table.add_column("Total", justify="right")
        table.add_column("Context Usage", justify="right")
        
        ctx_color = "green" if ctx_percent < 50 else "yellow" if ctx_percent < 80 else "red"
        
        table.add_row(
            str(in_tokens),
            str(out_tokens),
            str(total_tokens),
            f"[{ctx_color}]{ctx_percent:.1f}%[/{ctx_color}]"
        )
        self.console.print(Panel(table, title="📊 Token Usage", border_style="blue", expand=False))

    def input_prompt(self) -> str:
        # Using prompt_toolkit for robust input handling, including:
        # - Proper CJK (wide character) support
        # - History navigation (up/down arrows)
        # - Advanced editing shortcuts
        
        # The prompt method takes an HTML formatted string or list of (style, text) tuples.
        # We can use the style dict we defined in __init__.
        return self.session.prompt([('class:prompt', 'mango >> ')], style=self.style)

    def spinner(self, message: str):
        return self.console.status(f"[bold green]{message}[/bold green]", spinner="dots")

tui = TUI()
