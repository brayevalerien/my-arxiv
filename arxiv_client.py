import arxiv
from datetime import datetime
from typing import List, Optional

from models import Paper, ReadingStatus


class ArxivClient:
    def __init__(self):
        self.client = arxiv.Client()
    
    def search_papers(self, query: str, max_results: int = 10) -> List[Paper]:
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance
        )
        
        papers = []
        for result in self.client.results(search):
            paper = Paper(
                arxiv_id=result.entry_id.split('/')[-1],
                title=result.title,
                authors=[str(author) for author in result.authors],
                summary=result.summary,
                published=result.published,
                pdf_url=result.pdf_url,
                status=ReadingStatus.TO_READ
            )
            papers.append(paper)
        
        return papers
    
    def get_paper_by_id(self, arxiv_id: str) -> Optional[Paper]:
        try:
            search = arxiv.Search(id_list=[arxiv_id])
            result = next(self.client.results(search))
            
            return Paper(
                arxiv_id=arxiv_id,
                title=result.title,
                authors=[str(author) for author in result.authors],
                summary=result.summary,
                published=result.published,
                pdf_url=result.pdf_url,
                status=ReadingStatus.TO_READ
            )
        except StopIteration:
            return None
    
    def download_pdf(self, paper: Paper, filename: str = None):
        search = arxiv.Search(id_list=[paper.arxiv_id])
        result = next(self.client.results(search))
        result.download_pdf(filename=filename)