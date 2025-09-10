# my-arxiv

Manage academic papers using the Arxiv API and keep track of what you want to read and what you've already read.

## Installation

```bash
pip install arxiv
```

## Usage

```bash
python main.py search "machine learning" 5     # Search for papers
python main.py later 1909.03550v1              # Add paper to reading list
python main.py read 1909.03550v1               # Mark as currently reading
python main.py done 1909.03550v1               # Mark as completed
python main.py info 1909.03550v1               # Show paper details
python main.py list                            # List all papers
python main.py list reading                    # List by status
```

## Commands

- `search <query> [max_results]` - Search arXiv for papers
- `later <arxiv_id>` - Add paper to reading list
- `read <arxiv_id>` - Mark paper as currently reading
- `done <arxiv_id>` - Mark paper as completed
- `info <arxiv_id>` - Show paper details and status
- `list [status]` - List papers (optionally filtered by status)

## Data Storage

Paper data is stored in `papers.json` in the current directory.

## Requirements

- Python 3.12+
- arxiv library (>=2.2.0)