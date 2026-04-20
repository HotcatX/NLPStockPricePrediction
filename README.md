# 项目方案：金融市场情绪与行情关联分析系统 (Cloud-Native Implementation)

## 1. 核心架构：离线回测 + 实时分析
*   **规模化 (Scalability)**：利用 Kaggle 历史新闻与行情数据集（1GB+）模拟大规模回测。
*   **实时性 (Simulated Real-time)**：利用 Alpha Vantage API 动态拉取当日数据。
*   **云计算 (Cloud Integration)**：全量组件采用云端托管，保证高可用性与水平扩展能力。

## 2. 云端技术栈 (Cloud Tech Stack)
*   **安全凭证管理 (Security)**：**AWS Secrets Manager** (动态读取数据库密码，拒绝明文硬编码)。
*   **计算执行 (Compute)**：Jupyter Notebook 本地算力 (发起端到端 ETL)。
*   **数据入湖 (NoSQL)**：**AWS DynamoDB** (作为云端数据湖存储非结构化 API 行情数据)。
*   **结构化存储 (SQL)**：**AWS Aurora MySQL** (接收 Pandas 大批量 bulk insert 的时序金融数据)。
*   **云分布式处理**：**PySpark** (连接云端数据源进行分布式大规模情感计算)。

## 3. 端到端云数据流水线 (Cloud Data Pipeline)
1.  **数据采集**：本地环境调用 `Alpha Vantage API` 抓取最新数据。
2.  **云端无服务器入湖 (NoSQL)**：将原始 JSON Payload 配合复合 Key (`APAN5200CHY`) 即刻推入 **AWS DynamoDB**，保留数据最原始形态。
3.  **ETL 与结构化 (Process)**：本地 Pandas 从 JSON 提取时间序列、价格、交易量，建立标准结构化 DataFrame。
4.  **云端关系型入库 (SQL)**：
    *   通过 **AWS Secrets Manager** 安全获取密码。
    *   通过 `SQLAlchemy` 及 SSL 证书，将 DataFrame 批量推送覆盖至 **AWS Aurora MySQL**的 `stock_prices` 表中。
5.  **展示层 (Service)**：基于清洗好的结构化数据提供前端可视化面板。

## 4. 方案亮点 (Highlights)
*   **云计算的必要性**：方案通过 **AWS/GCP** 架构解决了本地存储不足的问题。利用云端的托管数据库（RDS/Atlas），实现了团队成员间的无缝数据共享，并为未来处理 TB 级数据提供了“按需扩展”的基础。
*   **高阶云安全 (Secret Scanning)**：系统强制移除了所有数据库的明文密码，改用 `AWS Secrets Manager` 生成动态 ARN 返回鉴权，完全符合真正的企业级生产云安全规范。
*   **混合云存储**：通过 SQL 与 NoSQL 的云端协作，完美平衡了金融数据的严谨性与新闻舆情的灵活性。
