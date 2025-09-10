from typing import List, Optional

from arxiv_client import ArxivClient
from models import Paper, ReadingStatus
from storage import PaperStore


class CommandHandler:
    def __init__(self):
        self.arxiv_client = ArxivClient()
        self.paper_store = PaperStore()
    
    def search(self, query: str, max_results: int = 10) -> List[Paper]:
        papers = self.arxiv_client.search_papers(query, max_results)
        
        if not papers:
            print(f"No papers found for query: {query}")
            return []
        
        print(f"\nFound {len(papers)} papers for '{query}':\n")
        for i, paper in enumerate(papers, 1):
            existing = self.paper_store.get_paper(paper.arxiv_id)
            status = f"[{existing.status.value}]" if existing else "[new]"
            print(f"{i}. {paper.title}")
            print(f"   Authors: {', '.join(paper.authors[:3])}{'...' if len(paper.authors) > 3 else ''}")
            print(f"   ID: {paper.arxiv_id} {status}")
            print(f"   Published: {paper.published.strftime('%Y-%m-%d')}")
            print(f"   Summary: {paper.summary[:100]}...")
            print()
        
        return papers
    
    def later(self, arxiv_id: str) -> bool:
        if self.paper_store.paper_exists(arxiv_id):
            paper = self.paper_store.get_paper(arxiv_id)
            if paper.status != ReadingStatus.TO_READ:
                self.paper_store.update_paper_status(arxiv_id, ReadingStatus.TO_READ)
                print(f"Paper '{paper.title}' moved back to 'to read' list")
            else:
                print(f"Paper '{paper.title}' is already in your 'to read' list")
            return True
        
        paper = self.arxiv_client.get_paper_by_id(arxiv_id)
        if not paper:
            print(f"Paper with ID '{arxiv_id}' not found on arXiv")
            return False
        
        self.paper_store.add_paper(paper)
        print(f"Added '{paper.title}' to your reading list")
        return True
    
    def read(self, arxiv_id: str) -> bool:
        if not self.paper_store.paper_exists(arxiv_id):
            paper = self.arxiv_client.get_paper_by_id(arxiv_id)
            if not paper:
                print(f"Paper with ID '{arxiv_id}' not found on arXiv")
                return False
            self.paper_store.add_paper(paper)
        
        success = self.paper_store.update_paper_status(arxiv_id, ReadingStatus.READING)
        if success:
            paper = self.paper_store.get_paper(arxiv_id)
            print(f"Started reading '{paper.title}'")
        return success
    
    def done(self, arxiv_id: str) -> bool:
        if not self.paper_store.paper_exists(arxiv_id):
            print(f"Paper with ID '{arxiv_id}' not found in your reading list")
            return False
        
        success = self.paper_store.update_paper_status(arxiv_id, ReadingStatus.READ)
        if success:
            paper = self.paper_store.get_paper(arxiv_id)
            print(f"Completed reading '{paper.title}'")
        return success
    
    def info(self, arxiv_id: str) -> bool:
        paper = self.paper_store.get_paper(arxiv_id)
        
        if not paper:
            paper = self.arxiv_client.get_paper_by_id(arxiv_id)
            if not paper:
                print(f"Paper with ID '{arxiv_id}' not found")
                return False
            print("\nPaper found on arXiv (not in your reading list):\n")
        else:
            print(f"\nPaper in your reading list:\n")
        
        print(f"Title: {paper.title}")
        print(f"Authors: {', '.join(paper.authors)}")
        print(f"arXiv ID: {paper.arxiv_id}")
        print(f"Published: {paper.published.strftime('%Y-%m-%d')}")
        print(f"PDF URL: {paper.pdf_url}")
        
        if paper in self.paper_store.get_all_papers():
            print(f"Status: {paper.status.value}")
            print(f"Added to list: {paper.added_date.strftime('%Y-%m-%d')}")
            if paper.started_date:
                print(f"Started reading: {paper.started_date.strftime('%Y-%m-%d')}")
            if paper.completed_date:
                print(f"Completed: {paper.completed_date.strftime('%Y-%m-%d')}")
        
        print(f"\nSummary:\n{paper.summary}")
        return True
    
    def list_papers(self, status: Optional[str] = None):
        if status:
            try:
                status_enum = ReadingStatus(status)
                papers = self.paper_store.get_papers_by_status(status_enum)
                title = f"{status.replace('_', ' ').title()} papers"
            except ValueError:
                print(f"Invalid status: {status}")
                print(f"Valid statuses: {[s.value for s in ReadingStatus]}")
                return
        else:
            papers = self.paper_store.get_all_papers()
            title = "All papers in your reading list"
        
        if not papers:
            print(f"No {title.lower()} found")
            return
        
        print(f"\n{title} ({len(papers)}):\n")
        for paper in papers:
            print(f"• {paper.title}")
            print(f"  ID: {paper.arxiv_id} | Status: {paper.status.value}")
            print(f"  Authors: {', '.join(paper.authors[:2])}{'...' if len(paper.authors) > 2 else ''}")
            print()