# 项目方案：金融市场情绪与行情关联分析系统 (Cloud-Native Implementation)

## 1. 核心架构：离线回测 + 实时分析
*   **规模化 (Scalability)**：利用 Kaggle 历史新闻与行情数据集（1GB+）模拟大规模回测。
*   **实时性 (Simulated Real-time)**：利用 Alpha Vantage API 动态拉取当日数据。
*   **云计算 (Cloud Integration)**：全量组件采用云端托管，保证高可用性与水平扩展能力。

## 2. 云端技术栈 (Cloud Tech Stack)
*   **数据入湖 (NoSQL)**：**AWS DynamoDB** (作为云端数据湖，存储原始新闻 JSON)。
*   **结构化存储 (SQL)**：**AWS Aurora (PostgreSQL compatible)** (存储清洗后的金融指标)。
*   **云分布式处理**：**PySpark** (连接云端数据源进行分布式大规模情感计算)。
*   //**云存储**：**AWS S3 / Google Cloud Storage** (存放 Kaggle 历史大数据集，供 Spark 调用)。 (optional)

## 3. 云数据流水线 (Cloud Data Pipeline)
1.  **数据采集**：部署在云端的 Python 脚本定时触发，拉取 Alpha Vantage 数据。
2.  **云端持久化**：
    *   原始文本流入 **AWS DynamoDB**。
    *   行情指标清洗后流入 **AWS Aurora**。
3.  **云端分析 (Process)**：PySpark 从云存储读取百万级历史数据，与实时情绪进行交叉比对。
4.  **展示层 (Service)**：通过云服务器开放公网 URL，实时展示 Dashboard 看板。

## 4. 方案亮点 (Highlights)
*   **云计算的必要性**：方案通过 **AWS/GCP** 架构解决了本地存储不足的问题。利用云端的托管数据库（RDS/Atlas），实现了团队成员间的无缝数据共享，并为未来处理 TB 级数据提供了“按需扩展”的基础。
*   **Big Data 处理**：引入 PySpark 处理云存储中的海量历史新闻，解决了单机在进行 NLP 情感计算时的内存瓶颈。
*   **混合云存储**：通过 SQL 与 NoSQL 的云端协作，完美平衡了金融数据的严谨性与新闻舆情的灵活性。
