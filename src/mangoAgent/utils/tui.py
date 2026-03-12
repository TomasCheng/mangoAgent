import json
from pathlib import Path
from typing import Optional
from rich.console import Console, Group
from rich.panel import Panel
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt
from rich.layout import Layout
from rich.live import Live
from rich.spinner import Spinner
from rich.text import Text
from prompt_toolkit import PromptSession, prompt
from prompt_toolkit.styles import Style
from prompt_toolkit.completion import PathCompleter

console = Console()

class TUI:
    def __init__(self):
        self.console = console
        # Initialize prompt_toolkit session
        self.session = PromptSession()
        self.style = Style.from_dict({
            'prompt': 'bold cyan',
        })
        self._live: Optional[Live] = None
        self._thinking_text = ""
        self._response_text = ""

    def print_welcome(self):
        # A more colorful version using rich's color tags
        mango_art = (
            "       [bold green]_[/bold green][bold green]..[/bold green][bold green].[/bold green][bold green]_[/bold green]\n"
            "     [bold yellow].'[/bold yellow]     [bold yellow]'.[/bold yellow]\n"
            "    [bold yellow]/  [/bold yellow][bold green]_[/bold green]      [bold yellow]\\\\[/bold yellow]\n"
            "   [bold yellow]|  [/bold yellow][bold green](_)[/bold green]      [bold yellow]| [/bold yellow]\n"
            "    [bold yellow]\\\\        / [/bold yellow]\n"
            "     [bold yellow]'.____.' [/bold yellow]"
        )
        
        # Create a more integrated welcome message
        welcome_text = (
            "[bold green]Mango Agent[/bold green] [yellow](Enhanced)[/yellow]\n"
            "An autonomous coding agent with git worktree isolation.\n\n"
            "[dim]Type '?' for help, 'q' to exit.[/dim]"
        )
        
        # Combine them in a single panel
        content = Table.grid(padding=1)
        content.add_column(justify="center")
        content.add_column(justify="left", vertical="middle")
        content.add_row(mango_art.strip(), welcome_text)
        
        self.console.print(Panel(
            content,
            title="🥭 Welcome",
            border_style="green",
            padding=(1, 2)
        ))

    def print_system_message(self, message: str):
        self.console.print(f"[bold cyan]System:[/bold cyan] {message}")

    def print_user_message(self, message: str, files: Optional[list[Path]] = None):
        """Display user message with optional list of attached files."""
        content = Group()
        
        # Add the text message
        if message:
            content.renderables.append(Text(message))
            
        # Add attached files section if any
        if files:
            if message:
                content.renderables.append(Text("\n" + "─" * 20 + "\n", style="dim blue"))
            
            file_list = Text("📎 Attached Files:\n", style="bold cyan")
            for f in files:
                file_list.append(f"  • {f.name}\n", style="italic blue")
            content.renderables.append(file_list)

        self.console.print(Panel(content, title="User", border_style="blue", title_align="left"))

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

    def start_thinking(self):
        """Start a live display for thinking process."""
        self._thinking_text = ""
        self._live = Live(
            self._render_thinking(),
            console=self.console,
            refresh_per_second=10,
            transient=False # Keep it visible after thinking
        )
        self._live.start()

    def _render_thinking(self):
        """Render the thinking block with spinner and text inside a panel."""
        spinner = Spinner("dots", text=Text("Thinking...", style="bold magenta"))
        content = Text(self._thinking_text, style="dim italic white")
        return Panel(
            Group(spinner, content),
            title="🤔 Reasoning",
            border_style="magenta",
            title_align="left"
        )

    def print_thinking_chunk(self, text: str):
        """Update the thinking process text."""
        self._thinking_text += text
        if self._live:
            self._live.update(self._render_thinking())

    def stop_thinking(self):
        """Finalize thinking and prepare for response."""
        if self._live:
            # Update one last time without the spinner
            final_content = Panel(
                Text(self._thinking_text, style="dim italic white"),
                title="🤔 Reasoning (Finished)",
                border_style="dim magenta",
                title_align="left"
            )
            self._live.update(final_content)
            self._live.stop()
            self._live = None
        self.console.print() # Spacer

    def start_responding(self):
        """Start a live display for assistant response."""
        self._response_text = ""
        self._live = Live(
            self._render_response(),
            console=self.console,
            refresh_per_second=10,
            transient=False
        )
        self._live.start()

    def _render_response(self):
        """Render the assistant response block."""
        return Panel(
            Markdown(self._response_text),
            title="Mango",
            border_style="green",
            title_align="left"
        )

    def print_stream_chunk(self, text: str):
        """Update the assistant response text."""
        self._response_text += text
        if self._live:
            self._live.update(self._render_response())
        else:
            # Fallback for raw streaming if start_responding wasn't called
            self.console.print(text, end="")

    def stop_responding(self):
        """Finalize response display."""
        if self._live:
            self._live.stop()
            self._live = None
        self.console.print()

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

    def print_help(self):
        """Display help information with available commands."""
        table = Table(show_header=True, header_style="bold cyan", box=None, padding=(0, 2))
        table.add_column("Command", style="bold yellow")
        table.add_column("Description", style="dim")

        commands = [
            ("?, /help", "Show this help message"),
            ("/add", "Add file content to context (with path completion)"),
            ("/reload", "Save session and restart Mango Agent (Hot Reload)"),
            ("/tasks", "List all git worktree tasks"),
            ("/team", "List status of all teammates"),
            ("/inbox", "Read messages in the lead inbox"),
            ("/compact", "Manually compact conversation history"),
            ("q, exit", "Quit Mango Agent"),
        ]

        for cmd, desc in commands:
            table.add_row(cmd, desc)

        self.console.print(Panel(
            table,
            title="❓ Available Commands",
            border_style="cyan",
            padding=(1, 2),
            expand=False
        ))

    def input_prompt(self) -> str:
        # Using prompt_toolkit for robust input handling, including:
        # - Proper CJK (wide character) support
        # - History navigation (up/down arrows)
        # - Advanced editing shortcuts
        
        # We explicitly set completer=None to avoid "stickiness" from other prompts
        return self.session.prompt(
            [('class:prompt', 'mango >> ')], 
            style=self.style,
            completer=None
        )

    def input_file_path(self, message: str = "Select file: ") -> str:
        """Interactive file path selection with autocompletion."""
        completer = PathCompleter(expanduser=True)
        # Use global prompt() instead of self.session.prompt() to avoid contaminating main session
        return prompt(
            [('class:prompt', message)],
            style=self.style,
            completer=completer
        )

    def spinner(self, message: str):
        return self.console.status(f"[bold green]{message}[/bold green]", spinner="dots")

tui = TUI()
