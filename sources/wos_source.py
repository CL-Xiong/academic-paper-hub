"""
Web of Science Data Source Module - Retrieve papers from Web of Science
"""

from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup
import logging
import json


class WebOfScienceSource:
    """Web of Science数据源
    
    Note: Web of Science API需要付费订阅。
    此实现提供了基于Web爬虫的替代方案。
    """

    def __init__(self, timeout: int = 15, use_api: bool = False):
        """
        初始化Web of Science源
        
        Args:
            timeout: 请求超时时间（秒）
            use_api: 是否使用官方API（需要API密钥）
        """
        self.timeout = timeout
        self.use_api = use_api
        self.logger = logging.getLogger(__name__)
        self.base_url = "https://www.webofscience.com"
        
        # WOS主题分类
        self.research_areas = {
            'geodesy': 'Geodesy',
            'navigation': 'Navigation',
            'positioning': 'Positioning Systems',
            'gnss': 'GNSS',
            'gps': 'GPS',
            'satellite': 'Satellite Navigation'
        }

    def search(self, keyword: str, limit: int = 50, 
               filters: Optional[Dict] = None) -> List[Dict]:
        """
        搜索Web of Science论文
        
        Note: 由于WOS的反爬虫机制，此方法返回空结果。
        建议使用官方API或通过机构订阅的Web界面进行搜索。
        
        Args:
            keyword: 搜索关键词
            limit: 返回数量
            filters: 额外过滤条件
            
        Returns:
            论文列表
        """
        self.logger.warning(
            "Web of Science direct scraping is not supported due to anti-crawling measures. "
            "Please use the official API with valid credentials."
        )
        
        if self.use_api:
            return self._search_with_api(keyword, limit, filters)
        else:
            self.logger.info("Returning empty results. Use Web of Science official interface or API.")
            return []

    def _search_with_api(self, keyword: str, limit: int = 50, 
                        filters: Optional[Dict] = None) -> List[Dict]:
        """
        使用官方API搜索
        
        Args:
            keyword: 搜索关键词
            limit: 返回数量
            filters: 额外过滤条件
            
        Returns:
            论文列表
        """
        try:
            # 需要配置API密钥
            api_key = filters.get('api_key') if filters else None
            
            if not api_key:
                self.logger.warning("API key not provided. Cannot search WOS.")
                return []
            
            # 构建查询
            query = self._build_wos_query(keyword, filters)
            
            headers = {
                'X-ApiKey': api_key,
                'Content-Type': 'application/json'
            }
            
            payload = {
                'usrQuery': query,
                'count': min(limit, 100),
                'firstRecord': 1
            }
            
            response = requests.post(
                f"{self.base_url}/api/search",
                json=payload,
                headers=headers,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                return [self._parse_wos_record(record) for record in data.get('records', [])]
            else:
                self.logger.error(f"WOS API error: {response.status_code}")
                return []
        
        except Exception as e:
            self.logger.error(f"Error searching WOS with API: {e}")
            return []

    @staticmethod
    def _build_wos_query(keyword: str, filters: Optional[Dict] = None) -> str:
        """
        构建WOS查询字符串
        
        Args:
            keyword: 关键词
            filters: 过滤条件
            
        Returns:
            WOS查询字符串
        """
        query = f"TS=({keyword})"
        
        if filters:
            # 添加文献类型过滤
            if 'doc_type' in filters:
                doc_types = filters['doc_type']
                if isinstance(doc_types, list):
                    query += f" AND DT=({' OR '.join(doc_types)})"
            
            # 添加研究领域过滤
            if 'research_area' in filters:
                areas = filters['research_area']
                if isinstance(areas, list):
                    query += f" AND RA=({' OR '.join(areas)})"
            
            # 添加年份范围过滤
            if 'year_from' in filters and 'year_to' in filters:
                query += f" AND PY={filters['year_from']}-{filters['year_to']}"
        
        return query

    @staticmethod
    def _parse_wos_record(record: Dict) -> Dict:
        """
        解析WOS记录为标准格式
        
        Args:
            record: WOS记录
            
        Returns:
            标准格式的论文字典
        """
        return {
            'id': record.get('uid', ''),
            'source_id': record.get('uid', ''),
            'title': record.get('title', ''),
            'authors': record.get('authors', []),
            'abstract': record.get('abstract', ''),
            'keywords': record.get('keywords', []),
            'source': 'wos',
            'url': record.get('url', ''),
            'doi': record.get('doi', ''),
            'publication_date': record.get('pub_date', ''),
            'journal': record.get('journal', ''),
            'volume': record.get('volume', ''),
            'issue': record.get('issue', ''),
            'pages': record.get('pages', '')
        }

    def get_citation_count(self, doi: str = None, uid: str = None) -> Optional[int]:
        """
        获取论文被引用次数
        
        Args:
            doi: DOI号
            uid: WOS UID
            
        Returns:
            引用次数
        """
        self.logger.info("Citation count query requires official WOS API access.")
        return None

    def get_related_records(self, uid: str, limit: int = 10) -> List[Dict]:
        """
        获取相关论文
        
        Args:
            uid: WOS记录UID
            limit: 返回数量
            
        Returns:
            相关论文列表
        """
        self.logger.info("Related records query requires official WOS API access.")
        return []
