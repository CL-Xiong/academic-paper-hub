"""
Storage Management Module - Handle local paper storage and metadata
"""

import json
import os
import sqlite3
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import hashlib


class StorageManager:
    """管理本地论文存储和元数据"""

    def __init__(self, base_path: str = "./papers"):
        """
        初始化存储管理器
        
        Args:
            base_path: 论文存储根目录
        """
        self.base_path = Path(base_path)
        self.db_path = self.base_path / "papers.db"
        self._ensure_directories()
        self._init_database()

    def _ensure_directories(self):
        """创建必要的目录结构"""
        self.base_path.mkdir(parents=True, exist_ok=True)
        (self.base_path / "pdfs").mkdir(exist_ok=True)
        (self.base_path / "metadata").mkdir(exist_ok=True)
        (self.base_path / "logs").mkdir(exist_ok=True)

    def _init_database(self):
        """初始化SQLite数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建论文表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS papers (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                authors TEXT,
                abstract TEXT,
                keywords TEXT,
                source TEXT NOT NULL,
                source_id TEXT,
                url TEXT,
                doi TEXT,
                publication_date TEXT,
                pdf_path TEXT,
                metadata_path TEXT,
                file_hash TEXT,
                file_size INTEGER,
                downloaded_at TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')
        
        # 创建下载历史表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS download_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                paper_id TEXT NOT NULL,
                download_time TEXT NOT NULL,
                status TEXT NOT NULL,
                file_size INTEGER,
                error_message TEXT,
                FOREIGN KEY (paper_id) REFERENCES papers(id)
            )
        ''')
        
        # 创建检索历史表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS search_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                keyword TEXT NOT NULL,
                source TEXT NOT NULL,
                result_count INTEGER,
                search_time TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()

    def add_paper(self, paper_data: Dict) -> bool:
        """
        添加论文记录
        
        Args:
            paper_data: 论文数据字典
            
        Returns:
            成功返回True，失败返回False
        """
        try:
            paper_id = paper_data.get('id', self._generate_id(paper_data))
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            now = datetime.now().isoformat()
            
            cursor.execute('''
                INSERT OR REPLACE INTO papers (
                    id, title, authors, abstract, keywords, source, 
                    source_id, url, doi, publication_date, 
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                paper_id,
                paper_data.get('title'),
                json.dumps(paper_data.get('authors', [])),
                paper_data.get('abstract'),
                json.dumps(paper_data.get('keywords', [])),
                paper_data.get('source'),
                paper_data.get('source_id'),
                paper_data.get('url'),
                paper_data.get('doi'),
                paper_data.get('publication_date'),
                now,
                now
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding paper: {e}")
            return False

    def update_download_info(self, paper_id: str, pdf_path: str, file_size: int):
        """更新论文下载信息"""
        try:
            file_hash = self._calculate_hash(pdf_path)
            now = datetime.now().isoformat()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE papers SET 
                    pdf_path = ?, file_hash = ?, file_size = ?, 
                    downloaded_at = ?, updated_at = ?
                WHERE id = ?
            ''', (pdf_path, file_hash, file_size, now, now, paper_id))
            
            cursor.execute('''
                INSERT INTO download_history (paper_id, download_time, status, file_size)
                VALUES (?, ?, ?, ?)
            ''', (paper_id, now, 'success', file_size))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating download info: {e}")
            return False

    def get_paper(self, paper_id: str) -> Optional[Dict]:
        """获取论文信息"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM papers WHERE id = ?', (paper_id,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return dict(row)
            return None
        except Exception as e:
            print(f"Error getting paper: {e}")
            return None

    def list_papers(self, limit: int = 100, offset: int = 0, source: str = None) -> List[Dict]:
        """列出本地论文"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if source:
                cursor.execute('''
                    SELECT * FROM papers 
                    WHERE source = ?
                    ORDER BY created_at DESC 
                    LIMIT ? OFFSET ?
                ''', (source, limit, offset))
            else:
                cursor.execute('''
                    SELECT * FROM papers 
                    ORDER BY created_at DESC 
                    LIMIT ? OFFSET ?
                ''', (limit, offset))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [dict(row) for row in rows]
        except Exception as e:
            print(f"Error listing papers: {e}")
            return []

    def get_stats(self) -> Dict:
        """获取存储统计信息"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 总论文数
            cursor.execute('SELECT COUNT(*) FROM papers')
            total_papers = cursor.fetchone()[0]
            
            # 已下载数
            cursor.execute('SELECT COUNT(*) FROM papers WHERE pdf_path IS NOT NULL')
            downloaded_papers = cursor.fetchone()[0]
            
            # 按来源统计
            cursor.execute('''
                SELECT source, COUNT(*) as count 
                FROM papers 
                GROUP BY source
            ''')
            by_source = {row[0]: row[1] for row in cursor.fetchall()}
            
            # 总文件大小
            cursor.execute('SELECT SUM(file_size) FROM papers')
            total_size = cursor.fetchone()[0] or 0
            
            # 最近检索
            cursor.execute('''
                SELECT keyword, source, result_count, search_time 
                FROM search_history 
                ORDER BY search_time DESC 
                LIMIT 5
            ''')
            recent_searches = [
                {
                    'keyword': row[0],
                    'source': row[1],
                    'result_count': row[2],
                    'search_time': row[3]
                }
                for row in cursor.fetchall()
            ]
            
            conn.close()
            
            return {
                'total_papers': total_papers,
                'downloaded_papers': downloaded_papers,
                'by_source': by_source,
                'total_size_bytes': total_size,
                'total_size_gb': round(total_size / (1024**3), 2),
                'recent_searches': recent_searches
            }
        except Exception as e:
            print(f"Error getting stats: {e}")
            return {}

    def check_duplicate(self, doi: str = None, title: str = None) -> bool:
        """检查论文是否已存在（去重）"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if doi:
                cursor.execute('SELECT id FROM papers WHERE doi = ?', (doi,))
                if cursor.fetchone():
                    conn.close()
                    return True
            
            if title:
                cursor.execute('SELECT id FROM papers WHERE title = ?', (title,))
                if cursor.fetchone():
                    conn.close()
                    return True
            
            conn.close()
            return False
        except Exception as e:
            print(f"Error checking duplicate: {e}")
            return False

    def record_search(self, keyword: str, source: str, result_count: int):
        """记录检索历史"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO search_history (keyword, source, result_count, search_time)
                VALUES (?, ?, ?, ?)
            ''', (keyword, source, result_count, datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error recording search: {e}")

    @staticmethod
    def _generate_id(paper_data: Dict) -> str:
        """根据论文数据生成唯一ID"""
        title = paper_data.get('title', '')
        doi = paper_data.get('doi', '')
        source = paper_data.get('source', '')
        
        if doi:
            return hashlib.md5(doi.encode()).hexdigest()
        
        combined = f"{title}{source}".encode()
        return hashlib.md5(combined).hexdigest()

    @staticmethod
    def _calculate_hash(file_path: str) -> str:
        """计算文件哈希值"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
