import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from models import Paper, ReadingStatus


class PaperStore:
    def __init__(self, data_file: str = "papers.json"):
        self.data_file = Path(data_file)
        self.papers: Dict[str, Paper] = {}
        self.load()
    
    def load(self):
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.papers = {
                        arxiv_id: Paper.from_dict(paper_data)
                        for arxiv_id, paper_data in data.items()
                    }
            except (json.JSONDecodeError, KeyError, ValueError):
                self.papers = {}
    
    def save(self):
        data = {
            arxiv_id: paper.to_dict()
            for arxiv_id, paper in self.papers.items()
        }
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def add_paper(self, paper: Paper):
        self.papers[paper.arxiv_id] = paper
        self.save()
    
    def get_paper(self, arxiv_id: str) -> Optional[Paper]:
        return self.papers.get(arxiv_id)
    
    def get_all_papers(self) -> List[Paper]:
        return list(self.papers.values())
    
    def get_papers_by_status(self, status: ReadingStatus) -> List[Paper]:
        return [paper for paper in self.papers.values() if paper.status == status]
    
    def update_paper_status(self, arxiv_id: str, status: ReadingStatus):
        if paper := self.get_paper(arxiv_id):
            if status == ReadingStatus.READING:
                paper.start_reading()
            elif status == ReadingStatus.READ:
                paper.mark_as_read()
            elif status == ReadingStatus.TO_READ:
                paper.mark_as_later()
            self.save()
            return True
        return False
    
    def paper_exists(self, arxiv_id: str) -> bool:
        return arxiv_id in self.papers