"""
CNKI (China National Knowledge Infrastructure) Data Source Module
"""

from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup
import logging
import json
from urllib.parse import urlencode
import time


class CNKISource:
    """知网(CNKI)数据源"""

    def __init__(self, timeout: int = 10):
        """
        初始化知网源
        
        Args:
            timeout: 请求超时时间（秒）
        """
        self.timeout = timeout
        self.logger = logging.getLogger(__name__)
        self.base_url = "https://www.cnki.net"
        
        # 请求头
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # 学科分类代码
        self.subjects = {
            'geodesy': 'P201',
            'navigation': 'V249',
            'positioning': 'P208',
            'gnss': 'P208'
        }

    def search(self, keyword: str, limit: int = 50, 
               filters: Optional[Dict] = None) -> List[Dict]:
        """
        搜索知网论文
        
        Args:
            keyword: 搜索关键词
            limit: 返回数量
            filters: 额外过滤条件（subject, year_from, year_to等）
            
        Returns:
            论文列表
        """
        try:
            self.logger.info(f"Searching CNKI for: {keyword}")
            
            # 构建查询参数
            params = self._build_search_params(keyword, limit, filters)
            
            # 执行搜索
            results = []
            
            # 知网搜索需要通过特定接口
            url = f"{self.base_url}/search"
            
            response = requests.get(
                url,
                params=params,
                headers=self.headers,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                # 解析HTML
                papers = self._parse_search_results(response.text, limit)
                results.extend(papers)
                self.logger.info(f"Found {len(results)} papers from CNKI")
            else:
                self.logger.warning(f"CNKI search returned status {response.status_code}")
            
            return results
        
        except Exception as e:
            self.logger.error(f"Error searching CNKI: {e}")
            return []

    def search_advanced(self, keyword: str, subject: str = None, 
                       year_from: int = None, year_to: int = None,
                       limit: int = 50) -> List[Dict]:
        """
        高级搜索
        
        Args:
            keyword: 搜索关键词
            subject: 学科分类
            year_from: 开始年份
            year_to: 结束年份
            limit: 返回数量
            
        Returns:
            论文列表
        """
        filters = {}
        
        if subject and subject in self.subjects:
            filters['subject_code'] = self.subjects[subject]
        
        if year_from:
            filters['year_from'] = year_from
        if year_to:
            filters['year_to'] = year_to
        
        return self.search(keyword, limit=limit, filters=filters)

    @staticmethod
    def _build_search_params(keyword: str, limit: int, 
                           filters: Optional[Dict] = None) -> Dict:
        """
        构建搜索参数
        
        Args:
            keyword: 关键词
            limit: 返回数量
            filters: 过滤条件
            
        Returns:
            查询参数字典
        """
        params = {
            'q': keyword,
            'pageSize': min(limit, 50),
            'pageNumber': 1
        }
        
        if filters:
            if 'subject_code' in filters:
                params['subject'] = filters['subject_code']
            if 'year_from' in filters:
                params['yearFrom'] = filters['year_from']
            if 'year_to' in filters:
                params['yearTo'] = filters['year_to']
            if 'database' in filters:
                params['db'] = filters['database']
        
        return params

    def _parse_search_results(self, html: str, limit: int) -> List[Dict]:
        """
        解析搜索结果
        
        Args:
            html: HTML内容
            limit: 返回数量
            
        Returns:
            论文列表
        """
        results = []
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # 查找论文项（具体选择器可能需要根据实际页面结构调整）
            papers = soup.find_all('div', class_='result-item')[:limit]
            
            for paper in papers:
                try:
                    parsed_paper = self._parse_paper_item(paper)
                    if parsed_paper:
                        results.append(parsed_paper)
                except Exception as e:
                    self.logger.warning(f"Error parsing paper item: {e}")
                    continue
            
        except Exception as e:
            self.logger.error(f"Error parsing search results: {e}")
        
        return results

    @staticmethod
    def _parse_paper_item(paper_element) -> Optional[Dict]:
        """
        解析单个论文项
        
        Args:
            paper_element: 论文DOM元素
            
        Returns:
            论文字典或None
        """
        try:
            # 提取标题
            title_elem = paper_element.find('a', class_='title')
            if not title_elem:
                return None
            
            title = title_elem.get_text(strip=True)
            paper_url = title_elem.get('href', '')
            
            # 提取作者
            authors = []
            author_elems = paper_element.find_all('a', class_='author')
            if author_elems:
                authors = [elem.get_text(strip=True) for elem in author_elems]
            
            # 提取摘要
            abstract_elem = paper_element.find('p', class_='abstract')
            abstract = abstract_elem.get_text(strip=True) if abstract_elem else ''
            
            # 提取出版信息
            info_elem = paper_element.find('div', class_='info')
            journal = ''
            publication_date = ''
            if info_elem:
                info_text = info_elem.get_text(strip=True)
                # 解析期刊和日期信息
                parts = info_text.split(',')
                if parts:
                    journal = parts[0]
                if len(parts) > 1:
                    publication_date = parts[-1]
            
            # 提取CNKI链接ID
            cnki_id = paper_url.split('/')[-1] if paper_url else ''
            
            return {
                'id': cnki_id,
                'source_id': cnki_id,
                'title': title,
                'authors': authors,
                'abstract': abstract,
                'keywords': [],
                'source': 'cnki',
                'url': paper_url,
                'doi': '',
                'publication_date': publication_date,
                'journal': journal
            }
        
        except Exception as e:
            return None

    def get_full_text(self, paper_id: str) -> Optional[str]:
        """
        获取论文全文URL
        
        Note: 知网全文下载通常需要登录或付费。
        
        Args:
            paper_id: 论文ID
            
        Returns:
            全文URL或None
        """
        try:
            # 构建论文详情页URL
            paper_url = f"{self.base_url}/paper/{paper_id}"
            
            response = requests.get(
                paper_url,
                headers=self.headers,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 查找下载链接
                download_btn = soup.find('a', class_='download')
                if download_btn:
                    return download_btn.get('href', '')
            
            return None
        
        except Exception as e:
            self.logger.error(f"Error getting full text URL: {e}")
            return None

    def get_paper_by_doi(self, doi: str) -> Optional[Dict]:
        """
        通过DOI获取论文信息
        
        Args:
            doi: DOI号
            
        Returns:
            论文字典或None
        """
        return self.search(doi, limit=1)[0] if self.search(doi, limit=1) else None
