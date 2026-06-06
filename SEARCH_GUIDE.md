# 相对论重力位差测量论文搜索 - 完整执行指南

## 🚀 快速开始 (3步)

### 步骤 1: 克隆项目
```bash
git clone https://github.com/CL-Xiong/academic-paper-hub.git
cd academic-paper-hub
```

### 步骤 2: 安装依赖
```bash
pip install -r requirements.txt
```

### 步骤 3: 执行搜索
```bash
python search_relativistic_gravity.py
```

---

## 📊 执行流程详解

### 搜索将自动进行以下操作：

#### **第1阶段：多源搜索**
```
🔍 搜索: '相对论重力位差' | 来源: CNKI | 限制: 100
   → 连接知网 API
   → 解析搜索结果
   → 提取论文元数据
   ✅ 找到 X 篇论文

🔍 搜索: 'relativistic gravity measurement' | 来源: ARXIV | 限制: 100
   → 连接 arXiv API
   → 检索论文信息
   → 获取 PDF 下载链接
   ✅ 找到 X 篇论文

... 继续其他关键词搜索 ...
```

#### **第2阶段：结果统计**
```
📊 搜索结果统计

📄 arXiv 论文:  250+ 篇
📄 知网 论文:   150+ 篇
📄 总计:        400+ 篇
```

#### **第3阶段：结果展示**
```
🌍 arXiv 国际论文 (前15篇)

1. Relativistic treatment of gravitational measurements...
   👤 Einstein, A.
   📅 2024-06-01 | DOI: 10.1234/arxiv.12345
   🔗 https://arxiv.org/pdf/2406.xxxxx.pdf

2. Advanced geodetic techniques for gravity potential differences...
   👤 Newton, I.
   📅 2024-05-15 | DOI: 10.5678/arxiv.67890
   🔗 https://arxiv.org/pdf/2405.xxxxx.pdf

... 更多论文 ...

🇨🇳 知网中文论文 (前15篇)

1. 相对论框架下的重力位差精密测量方法研究
   👤 王大明, 李小红
   📅 2024-05-10 | 期刊: 大地测量学报

2. 基于相对论修正的万有引力位测量精度提升
   👤 张三, 李四
   📅 2024-04-20 | 期刊: 测绘学报

... 更多论文 ...
```

#### **第4阶段：保存结果**
```
💾 保存搜索结果

✅ 搜索结果已保存到: search_results_relativistic_gravity.json
   • arXiv 论文: 250+ 篇
   • 知网论文: 150+ 篇
   • 总计: 400+ 篇
```

#### **第5阶段：更新本地库**
```
📚 本地论文库统计

==============================================================================
📚 Academic Paper Hub - 本地库统计
==============================================================================
📄 总论文数:           400+
✅ 已下载:             0
📦 总大小:             0 GB

按来源统计:
  - ARXIV: 250+
  - CNKI: 150+

最近检索:
  - '相对论重力位差' (cnki): 100 结果
  - 'relativistic gravity measurement' (arxiv): 100 结果
  ... 更多搜索记录 ...
==============================================================================
```

---

## 🎯 搜索完成后可用的操作

### 查看所有论文
```bash
python cli.py list -l 50
```

### 按来源过滤
```bash
python cli.py list -l 30 -s arxiv
python cli.py list -l 30 -s cnki
```

### 查看详细统计
```bash
python cli.py stats
```

### 获取某篇论文详情
```bash
python cli.py info <paper_id>
```

### 查看搜索结果 JSON
```bash
cat search_results_relativistic_gravity.json | python -m json.tool
```

---

## 📁 输出文件说明

### 1️⃣ `search_results_relativistic_gravity.json`
```json
{
  "arxiv": [
    {
      "id": "2406.xxxxx",
      "title": "Relativistic treatment of gravitational measurements",
      "authors": ["Einstein, A.", "..."],
      "abstract": "...",
      "url": "https://arxiv.org/pdf/2406.xxxxx.pdf",
      "doi": "10.1234/arxiv.12345",
      "publication_date": "2024-06-01",
      "source": "arxiv"
    },
    ... 更多论文 ...
  ],
  "cnki": [
    {
      "id": "cnki_12345",
      "title": "相对论框架下的重力位差精密测量方法研究",
      "authors": ["王大明", "李小红"],
      "abstract": "...",
      "journal": "大地测量学报",
      "publication_date": "2024-05-10",
      "source": "cnki"
    },
    ... 更多论文 ...
  ],
  "search_summary": [
    {
      "keyword": "相对论重力位差",
      "source": "cnki",
      "count": 100,
      "timestamp": "2026-06-06T12:00:00"
    },
    ... 更多搜索记录 ...
  ]
}
```

### 2️⃣ `papers.db` (SQLite 数据库)
位置: `./papers/papers.db`

包含的表：
- **papers**: 所有论文元数据
- **download_history**: 下载历史
- **search_history**: 搜索历史

---

## ⚡ 性能指标

| 指标 | 预期值 |
|------|--------|
| 搜索耗时 | 30-60 秒 |
| 返回论文数 | 400+ 篇 |
| JSON 文件大小 | 5-10 MB |
| 数据库大小 | 1-2 MB |

---

## 🔍 搜索覆盖的关键词

### 中文关键词 (CNKI)
- ✅ 相对论重力位差
- ✅ 重力位差测量
- ✅ 大地测量定位
- ✅ 重力加速度测量

### 英文关键词 (arXiv)
- ✅ relativistic gravity measurement
- ✅ gravitational potential difference
- ✅ relativistic geodesy
- ✅ satellite gravity missions

---

## 📈 数据分析建议

搜索完成后，你可以：

1. **统计分析**
   ```python
   import json
   with open('search_results_relativistic_gravity.json') as f:
       data = json.load(f)
       print(f"arXiv: {len(data['arxiv'])} papers")
       print(f"CNKI: {len(data['cnki'])} papers")
   ```

2. **按年份分析**
   - 查看论文发表趋势
   - 识别热门研究时期

3. **作者分析**
   - 找出高产作者
   - 追踪特定研究团队

4. **期刊分析**
   - 识别相关学术期刊
   - 选择投稿目标

---

## 💾 批量下载 (可选)

如需下载所有论文 PDF，可修改 `examples.py` 中的下载函数：

```python
# examples.py 中的 example_batch_download() 函数

def example_batch_download():
    retriever = PaperRetriever()
    
    # 加载搜索结果
    with open('search_results_relativistic_gravity.json') as f:
        results = json.load(f)
    
    # 合并所有论文
    all_papers = results['arxiv'] + results['cnki']
    
    # 批量下载（仅 arXiv 有效，知网需特殊处理）
    download_result = retriever.batch_download(all_papers)
    
    print(f"成功下载: {download_result['success']}")
    print(f"失败: {download_result['failed']}")
```

---

## 🆘 故障排除

### 问题 1: ImportError
```
ModuleNotFoundError: No module named 'arxiv'
```
**解决**: 重新安装依赖
```bash
pip install --upgrade -r requirements.txt
```

### 问题 2: 网络超时
```
requests.exceptions.ConnectTimeout
```
**解决**: 增加超时时间或使用 VPN

### 问题 3: 知网无结果
```
CNKI search returned 0 results
```
**解决**: 知网可能需要登录，尝试其他关键词

---

## 📞 需要帮助？

1. 查看项目文档: `docs/USAGE.md`
2. 检查 API 文档: `docs/API.md`
3. 查看示例: `examples.py`
4. 查看源代码: `sources/*.py`

---

## ✨ 功能亮点

✅ **多源集成** - 同时搜索 arXiv、知网、WOS  
✅ **智能去重** - 自动去除重复论文  
✅ **元数据提取** - 完整的作者、DOI、摘要  
✅ **PDF 链接** - 自动获取下载链接  
✅ **本地存储** - SQLite 数据库管理  
✅ **搜索历史** - 记录所有搜索  
✅ **统计分析** - 详细的统计报告  

---

**🎉 现在你已准备好进行搜索了！运行 `python search_relativistic_gravity.py` 开始吧！** 🚀
