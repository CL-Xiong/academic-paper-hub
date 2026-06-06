"""
arXiv Data Source Module - Retrieve papers from arXiv
"""

import arxiv
from typing import List, Dict, Optional
import logging
from datetime import datetime


class ArxivSource:
    """arXiv数据源"""

    def __init__(self, timeout: int = 10):
        """
        初始化arXiv源
        
        Args:
            timeout: 请求超时时间（秒）
        """
        self.timeout = timeout
        self.logger = logging.getLogger(__name__)
        # arXiv相关领域分类
        self.categories = {
            'physics': 'physics.geo-ph',  # 地球物理
            'cs': 'cs.SY',  # 计算机系统
            'math': 'math.NA',  # 数值分析
            'eess': 'eess.SY'  # 电气工程
        }

    def search(self, keyword: str, limit: int = 50, 
               filters: Optional[Dict] = None, category: str = 'physics') -> List[Dict]:
        """
        搜索arXiv论文
        
        Args:
            keyword: 搜索关键词
            limit: 返回结果数量
            filters: 额外过滤条件（如date范围）
            category: 论文分类
            
        Returns:
            论文列表
        """
        try:
            # 构建查询字符串
            query = f"all:{keyword}"
            
            # 添加分类过滤
            if category in self.categories:
                query += f" AND cat:{self.categories[category]}"
            
            # 添加日期过滤
            if filters and 'date_from' in filters:
                query += f" AND submittedDate:[{filters['date_from']} TO {filters.get('date_to', '9999-12-31')}]"
            
            self.logger.info(f"Searching arXiv with query: {query}")
            
            # 执行查询
            client = arxiv.Client()
            results = []
            
            search = arxiv.Search(
                query=query,
                max_results=limit,
                sort_by=arxiv.SortCriterion.SubmittedDate,
                sort_order=arxiv.SortOrder.Descending
            )
            
            for entry in client.results(search):
                paper = self._parse_entry(entry)
                results.append(paper)
            
            self.logger.info(f"Found {len(results)} papers from arXiv")
            return results
        
        except Exception as e:
            self.logger.error(f"Error searching arXiv: {e}")
            return []

    def get_paper(self, arxiv_id: str) -> Optional[Dict]:
        """
        获取单个论文详情
        
        Args:
            arxiv_id: arXiv ID (如 2101.12345)
            
        Returns:
            论文字典
        """
        try:
            client = arxiv.Client()
            search = arxiv.Search(id_list=[arxiv_id])
            
            for entry in client.results(search):
                return self._parse_entry(entry)
            
            return None
        
        except Exception as e:
            self.logger.error(f"Error getting paper {arxiv_id}: {e}")
            return None

    @staticmethod
    def _parse_entry(entry) -> Dict:
        """
        解析arXiv条目为标准格式
        
        Args:
            entry: arXiv entry对象
            
        Returns:
            标准格式的论文字典
        """
        # 获取下载链接（PDF）
        pdf_url = entry.pdf_url if hasattr(entry, 'pdf_url') else None
        if not pdf_url and hasattr(entry, 'entries') and entry.entries:
            pdf_url = entry.entries[0].get('arxiv_pdf_url')
        
        return {
            'id': entry.entry_id.split('/abs/')[-1] if '/' in entry.entry_id else entry.entry_id,
            'source_id': entry.entry_id,
            'title': entry.title,
            'authors': [author.name for author in entry.authors],
            'abstract': entry.summary,
            'keywords': [],
            'source': 'arxiv',
            'url': pdf_url or entry.entry_id.replace('abs', 'pdf') + '.pdf',
            'doi': entry.doi,
            'publication_date': entry.published.strftime('%Y-%m-%d') if hasattr(entry, 'published') else None,
            'categories': entry.categories if hasattr(entry, 'categories') else []
        }

    def search_by_author(self, author: str, limit: int = 50) -> List[Dict]:
        """
        按作者搜索
        
        Args:
            author: 作者名
            limit: 返回数量
            
        Returns:
            论文列表
        """
        try:
            query = f"au:{author}"
            client = arxiv.Client()
            results = []
            
            search = arxiv.Search(
                query=query,
                max_results=limit,
                sort_by=arxiv.SortCriterion.SubmittedDate,
                sort_order=arxiv.SortOrder.Descending
            )
            
            for entry in client.results(search):
                paper = self._parse_entry(entry)
                results.append(paper)
            
            return results
        
        except Exception as e:
            self.logger.error(f"Error searching by author: {e}")
            return []
