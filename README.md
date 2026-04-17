# 项目方案：金融市场情绪与行情关联分析系统

## 1. 核心架构
**历史回测（大数据基石） + 端到端实时分析（Demo 展示）**
*   **规模化 (Scalability)**：利用 Kaggle 历史新闻与行情数据集（1GB+）模拟大规模回测，验证策略有效性。
*   **实时性 (Simulated Real-time)**：利用 Alpha Vantage API 动态拉取当日数据，演示系统在流水线中的数据流转。

## 2. 技术栈 (Tech Stack)
*   **数据采集 (Ingestion)**：Alpha Vantage API (News & Prices)
*   **SQL 数据库**：PostgreSQL (存储结构化指标、关联后的价格与情绪分)
*   **NoSQL 数据库**：MongoDB (作为数据湖，存储原始、非结构化的新闻 JSON 数据)
*   **大数据处理**：PySpark (用于处理数百万条历史数据，进行分布式的词云分析和情感计算)
*   **前端展示**：Flask / FastAPI (轻量级看板)

## 3. 数据流水线 (Pipeline)
1.  **数据入湖 (Stage 1)**：Alpha Vantage 拉取的原始 JSON 数据直接持久化至 **MongoDB**，保证数据完整性且方便后续扩展字段。
2.  **ETL 与结构化 (Stage 2)**：将清洗后的股票指标、股票代号、日期及格式化后的行情数据写入 **PostgreSQL**。
3.  **分布式分析 (Stage 3)**：**PySpark** 读取 MongoDB 里的非结构化文本与 PostgreSQL 里的行情数据：
    *   **NLP 处理**：计算历史百万级新闻的情绪得分、提取热点词。
    *   **聚合分析**：计算情绪指标与股价波动率的相关性。
4.  **展示层 (Stage 4)**：Flask 服务从数据库提取聚合后的结果，通过 Dashboard 展示：
    *   情绪趋势 vs 股价涨跌图
    *   行业热点词云
    *   股票情绪对比排名

## 4. 方案亮点 (Highlights)
*   **Big Data 必要性**：为了处理数百万条历史新闻的全文分析、词云提取 and 情感计算，我们引入了 PySpark 进行分布式处理，解决了单机处理大规模文本数据的性能瓶颈。
*   **混合存储架构**：结合了 SQL 的严谨关联性（用于金融指标）和 NoSQL 的灵活 schema（用于新闻文本），体现了对不同数据形态的针对性处理。