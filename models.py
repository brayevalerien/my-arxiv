from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class ReadingStatus(Enum):
    TO_READ = "to_read"
    READING = "reading"
    READ = "read"


@dataclass
class Paper:
    arxiv_id: str
    title: str
    authors: list[str]
    summary: str
    published: datetime
    pdf_url: str
    status: ReadingStatus = ReadingStatus.TO_READ
    added_date: datetime = None
    started_date: Optional[datetime] = None
    completed_date: Optional[datetime] = None
    
    def __post_init__(self):
        if self.added_date is None:
            self.added_date = datetime.now()
    
    def to_dict(self) -> dict:
        return {
            "arxiv_id": self.arxiv_id,
            "title": self.title,
            "authors": self.authors,
            "summary": self.summary,
            "published": self.published.isoformat(),
            "pdf_url": self.pdf_url,
            "status": self.status.value,
            "added_date": self.added_date.isoformat(),
            "started_date": self.started_date.isoformat() if self.started_date else None,
            "completed_date": self.completed_date.isoformat() if self.completed_date else None,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Paper":
        return cls(
            arxiv_id=data["arxiv_id"],
            title=data["title"],
            authors=data["authors"],
            summary=data["summary"],
            published=datetime.fromisoformat(data["published"]),
            pdf_url=data["pdf_url"],
            status=ReadingStatus(data["status"]),
            added_date=datetime.fromisoformat(data["added_date"]),
            started_date=datetime.fromisoformat(data["started_date"]) if data["started_date"] else None,
            completed_date=datetime.fromisoformat(data["completed_date"]) if data["completed_date"] else None,
        )
    
    def start_reading(self):
        self.status = ReadingStatus.READING
        self.started_date = datetime.now()
    
    def mark_as_read(self):
        self.status = ReadingStatus.READ
        self.completed_date = datetime.now()
    
    def mark_as_later(self):
        self.status = ReadingStatus.TO_READ
        self.started_date = None
        self.completed_date = None