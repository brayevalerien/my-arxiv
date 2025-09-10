from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, Button, Input, ListView, ListItem, Label
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.binding import Binding
from textual.color import Color
from rich.text import Text

from commands import CommandHandler
from models import Paper, ReadingStatus


class MainMenuScreen(Screen):
    """Main menu screen with numbered options."""
    
    BINDINGS = [
        Binding("1", "select_search", "Search Papers"),
        Binding("2", "select_browse", "Browse List"),
        Binding("3", "select_details", "View Details"),
        Binding("4", "select_import", "Import/Export"),
        Binding("5", "select_settings", "Settings"),
        Binding("6", "select_exit", "Exit"),
        Binding("q", "quit", "Quit"),
    ]
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("my-arxiv - Academic Paper Manager", classes="title")
        yield Static("")
        yield Static("1. Search Papers")
        yield Static("2. Browse Reading List")
        yield Static("3. View Paper Details")
        yield Static("4. Import/Export")
        yield Static("5. Settings")
        yield Static("6. Exit")
        yield Static("")
        yield Static("Use number keys or arrow keys to select", classes="help")
        yield Footer()
    
    def action_select_search(self):
        self.app.push_screen("search")
    
    def action_select_browse(self):
        self.app.push_screen("browse")
    
    def action_select_details(self):
        self.app.push_screen("details")
    
    def action_select_import(self):
        self.app.push_screen("import")
    
    def action_select_settings(self):
        self.app.push_screen("settings")
    
    def action_select_exit(self):
        self.app.exit()
    
    def action_quit(self):
        self.app.exit()


class SearchScreen(Screen):
    """Simple search interface."""
    
    BINDINGS = [
        Binding("escape", "back", "Back"),
        Binding("enter", "search", "Search"),
    ]
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("Search Papers", classes="screen-title")
        yield Static("")
        yield Input(placeholder="Enter search query and press Enter", id="search-input")
        yield Static("")
        yield Static("Results will appear below...", id="search-results")
        yield Static("")
        yield Static("Press Enter to search, Esc to go back", classes="help")
        yield Footer()
    
    def on_mount(self):
        self.query_one("#search-input").focus()
    
    def action_back(self):
        self.app.pop_screen()
    
    def action_search(self):
        input_widget = self.query_one("#search-input")
        query = input_widget.value.strip()
        if query:
            self.perform_search(query)
    
    def perform_search(self, query: str):
        handler = self.app.command_handler
        papers = handler.search(query, 10)
        
        results_widget = self.query_one("#search-results")
        if papers:
            results_text = f"Found {len(papers)} papers:\n\n"
            for i, paper in enumerate(papers, 1):
                existing = handler.paper_store.get_paper(paper.arxiv_id)
                status = f"[{existing.status.value}]" if existing else "[new]"
                results_text += f"{i}. {paper.title}\n"
                results_text += f"   ID: {paper.arxiv_id} {status}\n\n"
            results_widget.update(results_text)
        else:
            results_widget.update("No papers found for your search.")


class BrowseScreen(Screen):
    """Paper browsing with keyboard navigation."""
    
    BINDINGS = [
        Binding("escape", "back", "Back"),
        Binding("enter", "select_paper", "Select"),
        Binding("1", "mark_to_read", "Mark To Read"),
        Binding("2", "mark_reading", "Mark Reading"),
        Binding("3", "mark_read", "Mark Read"),
    ]
    
    def __init__(self):
        super().__init__()
        self.papers = []
        self.current_filter = None
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("Reading List", classes="screen-title")
        yield Static("")
        yield ListView(id="paper-list")
        yield Static("")
        yield Static("↑↓:Navigate  Enter:Details  1/2/3:Status  Esc:Back", classes="help")
        yield Footer()
    
    def on_mount(self):
        self.load_papers()
    
    def load_papers(self):
        handler = self.app.command_handler
        if self.current_filter:
            self.papers = handler.paper_store.get_papers_by_status(self.current_filter)
        else:
            self.papers = handler.paper_store.get_all_papers()
        
        list_view = self.query_one("#paper-list")
        list_view.clear()
        
        if not self.papers:
            list_view.append(ListItem(Label("No papers in your reading list")))
            return
        
        for paper in self.papers:
            status_text = f"[{paper.status.value}]"
            
            # Color coding based on status
            if paper.status == ReadingStatus.TO_READ:
                status_color = "green"
            elif paper.status == ReadingStatus.READING:
                status_color = "yellow"
            else:  # READ
                status_color = "dim"
            
            # Create rich text with colors
            title_text = Text(paper.title, style="bold")
            id_text = Text(f"  ID: {paper.arxiv_id} ", style="")
            status_label = Text(status_text, style=status_color)
            
            item_text = Text.assemble(title_text, "\n", id_text, status_label)
            list_view.append(ListItem(Label(item_text)))
    
    def action_back(self):
        self.app.pop_screen()
    
    def action_mark_to_read(self):
        list_view = self.query_one("#paper-list")
        if list_view.index is not None and list_view.index < len(self.papers):
            paper = self.papers[list_view.index]
            self.app.command_handler.paper_store.update_paper_status(paper.arxiv_id, ReadingStatus.TO_READ)
            self.load_papers()
            self.app.notify(f"Marked as to read: {paper.title}")
    
    def action_mark_reading(self):
        list_view = self.query_one("#paper-list")
        if list_view.index is not None and list_view.index < len(self.papers):
            paper = self.papers[list_view.index]
            self.app.command_handler.paper_store.update_paper_status(paper.arxiv_id, ReadingStatus.READING)
            self.load_papers()
            self.app.notify(f"Marked as reading: {paper.title}")
    
    def action_mark_read(self):
        list_view = self.query_one("#paper-list")
        if list_view.index is not None and list_view.index < len(self.papers):
            paper = self.papers[list_view.index]
            self.app.command_handler.paper_store.update_paper_status(paper.arxiv_id, ReadingStatus.READ)
            self.load_papers()
            self.app.notify(f"Marked as read: {paper.title}")
    
    def action_select_paper(self):
        list_view = self.query_one("#paper-list")
        if list_view.index is not None and list_view.index < len(self.papers):
            paper = self.papers[list_view.index]
            # TODO: Implement detail view
            self.app.notify(f"Selected: {paper.title}")


class ArxivTUIApp(App):
    """Main TUI application."""
    
    CSS = """
    .title {
        text-align: center;
        text-style: bold;
        margin: 1;
    }
    
    .screen-title {
        text-align: center;
        text-style: bold;
        margin: 1;
    }
    
    .help {
        text-style: dim;
        text-align: center;
        margin: 1;
    }
    """
    
    SCREENS = {
        "main": MainMenuScreen,
        "search": SearchScreen,
        "browse": BrowseScreen,
    }
    
    def __init__(self):
        super().__init__()
        self.command_handler = CommandHandler()
    
    def on_mount(self):
        self.push_screen("main")


def run_tui():
    """Run the TUI application."""
    app = ArxivTUIApp()
    app.run()