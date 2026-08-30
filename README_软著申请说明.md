# 基于知识图谱与大模型的无人机多源感知融合分析系统 V1.0

本项目是面向软件著作权申请和系统运行说明的 Web 应用版本，重点提供完整页面、可点击交互、系统数据呈现、知识图谱可视化、融合候选分析、大模型辅助研判、性能结果分析和报告生成闭环。

系统不依赖实时无人机接入。后端启动时会优先读取当前工程已有数据；若缺少真实文件，会自动生成本地运行数据，保证页面可运行、可查看、可截图。

## 技术栈

- 前端：Vue 3、Element Plus、ECharts、Axios、Vue Router、Vite
- 后端：Python FastAPI、Pandas、Uvicorn
- 数据：JSON / JSONL / CSV 文件，支持可选 Neo4j 连接

## 目录结构

```text
UAV-KGllm-Web/
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   ├── routers/
│   ├── services/
│   ├── data/
│   └── outputs/reports/
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   └── src/
└── docs/
```

## 启动方式

后端：

```powershell
cd E:\MutiInteface\UAV-KGllm-Web\backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

前端：

```powershell
cd E:\MutiInteface\UAV-KGllm-Web\frontend
npm install
npm run dev
```

访问地址：

```text
http://localhost:5173
```

后端接口：

```text
http://localhost:8000
```

默认账号：

```text
admin / 123456
```

## 主要功能

1. 登录与系统首页驾驶舱
2. 多模态数据管理
3. 轨迹证据管理
4. 知识图谱可视化
5. KG 融合候选分析
6. 大模型智能研判
7. 大模型对话助手
8. 实验结果对比
9. 研判报告生成
10. 系统设置

## Neo4j 说明

系统设置中可启用 Neo4j 图谱读取。默认关闭，使用本地 `backend/data/nodes.csv` 与 `backend/data/edges.csv` 作为图谱数据源。启用 Neo4j 后，后端会尝试连接：

```text
bolt://localhost:7687
neo4j / 12345678
database: neo4j
```

若数据库不可用，系统自动回落到本地 CSV 图谱，不影响页面运行。

## 软著截图建议

建议截图顺序：

1. 登录页
2. 系统首页数据驾驶舱
3. 多模态数据管理表格与详情抽屉
4. 轨迹证据管理与特征雷达图
5. 知识图谱可视化页面
6. KG 融合候选分析页面
7. 大模型智能研判页面
8. 大模型对话助手页面
9. 实验结果对比页面
10. 研判报告生成页面
11. 系统设置页面
