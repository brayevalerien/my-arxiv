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


class PaperListItem(ListItem):
    """Custom list item for displaying paper information."""
    
    def __init__(self, paper: Paper, existing_status: str = None):
        super().__init__()
        self.paper = paper
        self.existing_status = existing_status
    
    def compose(self) -> ComposeResult:
        status_text = f"[{self.paper.status.value}]"
        if self.existing_status:
            status_text = f"[{self.existing_status}]"
        
        # Color coding based on status
        if self.paper.status == ReadingStatus.TO_READ or self.existing_status == "to_read":
            status_color = "green"
        elif self.paper.status == ReadingStatus.READING or self.existing_status == "reading":
            status_color = "yellow"
        else:  # READ
            status_color = "dim"
        
        # Create rich text with colors
        title_text = Text(self.paper.title, style="bold")
        authors_text = Text(f"Authors: {', '.join(self.paper.authors[:3])}{'...' if len(self.paper.authors) > 3 else ''}", style="dim")
        id_text = Text(f"ID: {self.paper.arxiv_id} ", style="")
        status_label = Text(status_text, style=status_color)
        date_text = Text(f"Published: {self.paper.published.strftime('%Y-%m-%d')}", style="dim")
        summary_text = Text(f"Summary: {self.paper.summary[:80]}...", style="italic dim")
        
        item_text = Text.assemble(
            title_text, "\n",
            authors_text, "\n",
            id_text, status_label, "\n",
            date_text, "\n",
            summary_text
        )
        
        yield Label(item_text)


class SearchScreen(Screen):
    """Enhanced search interface with interactive results."""
    
    BINDINGS = [
        Binding("escape", "back", "Back"),
        Binding("enter", "search", "Search"),
        Binding("up", "navigate_up", "Navigate Up"),
        Binding("down", "navigate_down", "Navigate Down"),
        Binding("1", "mark_to_read", "Mark To Read"),
        Binding("2", "mark_reading", "Mark Reading"),
        Binding("3", "mark_read", "Mark Read"),
        Binding("a", "add_to_list", "Add to List"),
        Binding("i", "view_details", "View Details"),
    ]
    
    def __init__(self):
        super().__init__()
        self.search_results = []
        self.current_search_query = ""
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("Search Papers", classes="screen-title")
        yield Input(placeholder="Type your search query and press Enter", id="search-input")
        yield Static("Search Results:", classes="results-header")
        yield ListView(id="search-results")
        yield Static("↑↓:Navigate  1/2/3:Status  a:Add  i:Details  Enter:Search  Esc:Back", classes="help")
        yield Footer()
    
    def on_mount(self):
        self.query_one("#search-input").focus()
    
    def action_back(self):
        self.app.pop_screen()
    
    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle when user presses Enter in the input field."""
        if event.input.id == "search-input":
            query = event.value.strip()
            if query:
                self.current_search_query = query
                self.perform_search(query)
    
    def action_search(self):
        """Handle search action from key binding."""
        input_widget = self.query_one("#search-input")
        query = input_widget.value.strip()
        if query:
            self.current_search_query = query
            self.perform_search(query)
    
    def action_navigate_up(self):
        """Navigate up in the results list."""
        results_list = self.query_one("#search-results")
        if results_list.children:
            current_index = results_list.index or 0
            if current_index > 0:
                results_list.index = current_index - 1
    
    def action_navigate_down(self):
        """Navigate down in the results list."""
        results_list = self.query_one("#search-results")
        if results_list.children:
            current_index = results_list.index or 0
            if current_index < len(results_list.children) - 1:
                results_list.index = current_index + 1
    
    def action_mark_to_read(self):
        """Mark selected paper as to_read."""
        self.update_selected_paper_status(ReadingStatus.TO_READ)
    
    def action_mark_reading(self):
        """Mark selected paper as reading."""
        self.update_selected_paper_status(ReadingStatus.READING)
    
    def action_mark_read(self):
        """Mark selected paper as read."""
        self.update_selected_paper_status(ReadingStatus.READ)
    
    def action_add_to_list(self):
        """Add selected paper to reading list."""
        results_list = self.query_one("#search-results")
        if results_list.index is not None and results_list.index < len(self.search_results):
            paper = self.search_results[results_list.index]
            handler = self.app.command_handler
            
            # Check if paper already exists
            if handler.paper_store.paper_exists(paper.arxiv_id):
                self.app.notify(f"Paper '{paper.title}' is already in your reading list")
            else:
                handler.paper_store.add_paper(paper)
                self.app.notify(f"Added '{paper.title}' to your reading list")
                # Refresh the search results to show updated status
                self.perform_search(self.current_search_query)
    
    def action_view_details(self):
        """View details of selected paper."""
        results_list = self.query_one("#search-results")
        if results_list.index is not None and results_list.index < len(self.search_results):
            paper = self.search_results[results_list.index]
            self.app.notify(f"Selected: {paper.title} (ID: {paper.arxiv_id})")
    
    def update_selected_paper_status(self, status: ReadingStatus):
        """Update the status of the selected paper."""
        results_list = self.query_one("#search-results")
        if results_list.index is not None and results_list.index < len(self.search_results):
            paper = self.search_results[results_list.index]
            handler = self.app.command_handler
            
            # Check if paper exists in store, if not add it first
            if not handler.paper_store.paper_exists(paper.arxiv_id):
                handler.paper_store.add_paper(paper)
            
            # Update the status
            handler.paper_store.update_paper_status(paper.arxiv_id, status)
            
            status_name = status.value.replace('_', ' ')
            self.app.notify(f"Marked '{paper.title}' as {status_name}")
            
            # Refresh the search results to show updated status
            self.perform_search(self.current_search_query)
    
    def perform_search(self, query: str):
        """Perform the search and update the results display."""
        try:
            handler = self.app.command_handler
            papers = handler.arxiv_client.search_papers(query, 15)  # Increased to 15 results
            self.search_results = papers
            
            results_list = self.query_one("#search-results")
            results_list.clear()
            
            if papers:
                for paper in papers:
                    existing = handler.paper_store.get_paper(paper.arxiv_id)
                    existing_status = existing.status.value if existing else None
                    
                    list_item = PaperListItem(paper, existing_status)
                    results_list.append(list_item)
                
                # Select first item if available
                if results_list.children:
                    results_list.index = 0
                
                self.app.notify(f"Found {len(papers)} papers for '{query}'")
            else:
                results_list.append(ListItem(Label("No papers found for your search.")))
                self.app.notify(f"No papers found for '{query}'")
                
        except Exception as e:
            results_list = self.query_one("#search-results")
            results_list.clear()
            results_list.append(ListItem(Label(f"Error searching: {str(e)}")))
            self.app.notify(f"Search error: {str(e)}")


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
    
    .results-header {
        text-style: bold;
        color: $primary;
        margin: 1 0 0 0;
    }
    
    #search-results {
        height: 1fr;
        border: solid $primary;
        padding: 0;
        margin: 1 0;
        background: $surface;
    }
    
    #search-results > ListItem {
        height: auto;
        padding: 1;
        border-bottom: solid $primary 20%;
    }
    
    #search-results > ListItem:hover {
        background: $primary 10%;
    }
    
    #search-results > ListItem.--highlight {
        background: $primary 20%;
    }
    
    #search-input {
        margin: 1 0;
        border: solid $primary;
    }
    
    /* Status color coding */
    .status-to-read {
        color: $success;
    }
    
    .status-reading {
        color: $warning;
    }
    
    .status-read {
        color: $error;
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