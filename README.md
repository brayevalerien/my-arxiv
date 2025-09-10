# my-arxiv
Manage academic papers using the Arxiv API and keep track of what you want to read and what you've already read.

## Getting Started
- Run `pip install arxiv textual` to install required libraries,
- Run `python main.py` to launch the TUI application for paper management.

## Navigation
- Use number keys (1-6) to select menu options
- Use arrow keys for navigation within screens
- Press Enter to confirm selections, Esc to go back

## Commands
- `search <query>`: Search arXiv for papers matching your query
- `later <arxiv_id>`: Add a paper to your reading list
- `read <arxiv_id>`: Mark a paper as currently being read
- `done <arxiv_id>`: Mark a paper as completed
- `info <arxiv_id>`: Show details and status of a paper
- `list [status]`: List all papers or filter by a specific status

## Data Storage
Paper data is stored in `papers.json` within the current working directory.

## Requirements
- Python 3.12+
- arxiv library (version 2.2.0 or higher)
- textual library (for the TUI experience)