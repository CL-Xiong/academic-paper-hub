"""
Download Management Module - Handle paper downloading with retry and progress tracking
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Optional, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import requests
from datetime import datetime
import logging
import sqlite3

from .storage import StorageManager


class PaperDownloader:
    """论文下载管理器"""

    def __init__(self, storage_manager: StorageManager, max_workers: int = 5, 
                 timeout: int = 30, retry_times: int = 3):
        """
        初始化下载管理器
        
        Args:
            storage_manager: 存储管理器实例
            max_workers: 最大并发下载数
            timeout: 下载超时时间（秒）
            retry_times: 重试次数
        """
        self.storage = storage_manager
        self.max_workers = max_workers
        self.timeout = timeout
        self.retry_times = retry_times
        
        # 设置日志
        self.logger = logging.getLogger(__name__)
        log_file = storage_manager.base_path / "logs" / "download.log"
        handler = logging.FileHandler(log_file)
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def batch_download(self, papers: List[Dict], progress_callback: Optional[Callable] = None) -> Dict:
        """
        批量下载论文
        
        Args:
            papers: 论文列表，每个元素包含 url, title, paper_id 等信息
            progress_callback: 进度回调函数
            
        Returns:
            下载统计信息
        """
        results = {
            'total': len(papers),
            'success': 0,
            'failed': 0,
            'skipped': 0,
            'details': []
        }
        
        # 过滤已下载的论文
        papers_to_download = []
        for paper in papers:
            if self.storage.get_paper(paper.get('id')):
                results['skipped'] += 1
                results['details'].append({
                    'paper_id': paper.get('id'),
                    'title': paper.get('title'),
                    'status': 'skipped',
                    'reason': 'already_exists'
                })
            else:
                papers_to_download.append(paper)
        
        # 使用线程池并发下载
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self._download_paper, paper): paper 
                for paper in papers_to_download
            }
            
            with tqdm(total=len(papers_to_download), desc="Downloading papers") as pbar:
                for future in as_completed(futures):
                    paper = futures[future]
                    try:
                        success, message = future.result()
                        if success:
                            results['success'] += 1
                            status = 'success'
                        else:
                            results['failed'] += 1
                            status = 'failed'
                        
                        results['details'].append({
                            'paper_id': paper.get('id'),
                            'title': paper.get('title'),
                            'status': status,
                            'message': message
                        })
                        
                        if progress_callback:
                            progress_callback(status, paper.get('title'))
                    except Exception as e:
                        results['failed'] += 1
                        results['details'].append({
                            'paper_id': paper.get('id'),
                            'title': paper.get('title'),
                            'status': 'failed',
                            'message': str(e)
                        })
                    finally:
                        pbar.update(1)
        
        return results

    def _download_paper(self, paper: Dict) -> tuple:
        """
        下载单个论文
        
        Args:
            paper: 论文信息字典
            
        Returns:
            (是否成功, 消息)
        """
        paper_id = paper.get('id')
        url = paper.get('url')
        title = paper.get('title', 'unknown')
        
        if not url:
            return False, "No download URL provided"
        
        # 检查重复
        if self.storage.check_duplicate(
            doi=paper.get('doi'),
            title=title
        ):
            return False, "Paper already exists"
        
        # 重试下载
        for attempt in range(self.retry_times):
            try:
                response = requests.get(url, timeout=self.timeout, stream=True)
                response.raise_for_status()
                
                # 保存PDF文件
                filename = self._sanitize_filename(title)
                pdf_path = self.storage.base_path / "pdfs" / f"{filename}.pdf"
                
                # 处理重名文件
                counter = 1
                base_pdf_path = pdf_path
                while pdf_path.exists():
                    pdf_path = Path(str(base_pdf_path).replace('.pdf', f'_{counter}.pdf'))
                    counter += 1
                
                # 写入文件
                file_size = 0
                with open(pdf_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            file_size += len(chunk)
                
                # 保存元数据
                metadata_path = self.storage.base_path / "metadata" / f"{paper_id}.json"
                with open(metadata_path, 'w', encoding='utf-8') as f:
                    json.dump(paper, f, ensure_ascii=False, indent=2)
                
                # 更新数据库
                self.storage.update_download_info(paper_id, str(pdf_path), file_size)
                
                self.logger.info(f"Downloaded: {title} ({file_size} bytes)")
                return True, f"Downloaded successfully ({file_size} bytes)"
                
            except requests.RequestException as e:
                if attempt == self.retry_times - 1:
                    error_msg = f"Failed after {self.retry_times} retries: {str(e)}"
                    self.logger.error(f"Download failed for {title}: {error_msg}")
                    return False, error_msg
                continue
            except Exception as e:
                error_msg = f"Unexpected error: {str(e)}"
                self.logger.error(f"Download error for {title}: {error_msg}")
                return False, error_msg
        
        return False, "Download failed"

    @staticmethod
    def _sanitize_filename(filename: str) -> str:
        """清理文件名，移除非��字符"""
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # 限制长度
        filename = filename[:200]
        return filename.strip()

    def get_download_history(self, limit: int = 100) -> List[Dict]:
        """获取下载历史"""
        try:
            conn = sqlite3.connect(self.storage.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT dh.*, p.title FROM download_history dh
                LEFT JOIN papers p ON dh.paper_id = p.id
                ORDER BY dh.download_time DESC
                LIMIT ?
            ''', (limit,))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [dict(row) for row in rows]
        except Exception as e:
            self.logger.error(f"Error getting download history: {e}")
            return []
