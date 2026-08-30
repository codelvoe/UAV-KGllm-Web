"""System catalog service for the UAV KG-LLM application.

The functions in this module expose structured software capability metadata
for documentation, system inspection, and operations support.
"""


SYSTEM_NAME = "基于知识图谱与大模型的无人机多源感知融合分析系统 V1.0"


def module_item(order, key, name, route, role, inputs, outputs, screenshots):
    return {
        "order": order,
        "key": key,
        "name": name,
        "route": route,
        "role": role,
        "inputs": inputs,
        "outputs": outputs,
        "screenshots": screenshots,
    }


SYSTEM_MODULES = [
    module_item(1, "login", "登录页", "/login", "提供固定账号登录入口，进入系统运行界面。", ["username", "password"], ["local-token", "username"], ["登录表单", "系统名称", "登录按钮"]),
    module_item(2, "dashboard", "系统首页", "/dashboard", "汇总多模态数据规模、图谱规模、性能指标和功能入口。", ["dashboard summary", "dashboard charts"], ["统计卡片", "records 柱状图", "F1/FAR 图表"], ["顶部指标卡", "运行分析图表", "功能入口卡片"]),
    module_item(3, "data", "多模态数据管理", "/data", "呈现 radar、spectrum、recognize、pho_status、decrypt 标准化记录。", ["jsonl records", "source filter", "keyword"], ["records table", "record summary", "modality statistics"], ["模态筛选栏", "数据表格", "记录摘要"]),
    module_item(4, "tracks", "轨迹证据管理", "/tracks", "呈现轨迹级摘要，支持按模态和目标类型检索。", ["track summaries", "source", "target_type"], ["track table", "feature chart", "timeline"], ["轨迹表格", "特征图", "时间线"]),
    module_item(5, "kg", "知识图谱可视化", "/kg", "呈现知识图谱节点、边、邻居和节点属性。", ["nodes.csv", "edges.csv", "neo4j optional"], ["graph nodes", "graph edges", "node detail"], ["图谱画布", "筛选栏", "属性面板"]),
    module_item(6, "fusion", "KG 融合候选分析", "/fusion", "呈现 KG Fusion 候选池、得分、排序和冲突标记。", ["fusion_candidates.json", "scenario"], ["candidate table", "score breakdown", "rank chart"], ["候选列表", "得分图", "排名图"]),
    module_item(7, "llm_decision", "大模型智能研判", "/llm-decision", "面向候选目标生成 confirm/reject/uncertain 辅助研判。", ["candidate_id", "scenario", "local_rule_mode"], ["decision", "risk_level", "reason", "suggestion"], ["候选证据卡", "研判结果卡", "处置建议"]),
    module_item(8, "chat", "大模型对话助手", "/chat", "围绕数据概况、图谱、融合结果和性能指标进行问答。", ["session_id", "message", "context_type"], ["answer", "evidence", "suggested_questions"], ["历史会话", "消息气泡", "证据引用"]),
    module_item(9, "experiments", "性能评估与运行分析", "/experiments", "呈现检测性能、资源开销和模态缺失稳定性。", ["experiment_results.csv"], ["detection table", "efficiency table", "robustness table"], ["性能表", "F1 图", "FAR 图"]),
    module_item(10, "yolo", "YOLO目标探测", "/yolo-detection", "基于本地 YOLO 模型进行图片和视频目标探测。", ["image", "video", "best.pt"], ["detections", "analysis", "metrics"], ["输入区", "检测画面", "目标列表"]),
    module_item(11, "settings", "系统设置", "/settings", "配置数据目录、模型接口、Top-K、Neo4j 和运维策略。", ["settings.json"], ["saved settings"], ["配置表单", "服务健康", "保存提示"]),
]


MODALITY_FIELDS = [
    {
        "source": "radar",
        "role": "空间/运动候选",
        "fields": ["record_id", "track_id", "time", "target_type", "azimuth", "distance", "altitude", "speed", "snr"],
        "view": "表格、轨迹摘要、候选证据卡",
    },
    {
        "source": "spectrum",
        "role": "无线电语义证据",
        "fields": ["record_id", "track_id", "time", "model", "target_type", "azimuth", "signal_db_mean", "confidence"],
        "view": "表格、轨迹摘要、融合候选详情",
    },
    {
        "source": "recognize",
        "role": "视觉识别辅助证据",
        "fields": ["record_id", "track_id", "time", "target_type", "bbox", "similarity", "confidence"],
        "view": "表格、轨迹摘要、LLM 证据摘要",
    },
    {
        "source": "pho_status",
        "role": "光电状态和视线可用性",
        "fields": ["record_id", "device_id", "time", "azimuth", "pitch", "status"],
        "view": "状态表、研判上下文",
    },
    {
        "source": "decrypt",
        "role": "隐藏标签，仅用于评价",
        "fields": ["record_id", "track_id", "time", "model", "target_type", "identity"],
        "view": "隐藏标签统计、性能指标来源",
    },
]


API_ENDPOINTS = [
    {"group": "auth", "method": "POST", "path": "/api/auth/login", "purpose": "固定账号登录", "request": {"username": "admin", "password": "123456"}, "response": {"success": True, "token": "local-token"}},
    {"group": "dashboard", "method": "GET", "path": "/api/dashboard/summary", "purpose": "首页统计卡片", "request": {}, "response": {"radar_tracks": 294, "kg_nodes": 53619}},
    {"group": "data", "method": "GET", "path": "/api/data/records", "purpose": "分页查询 records", "request": {"source": "radar", "page": 1, "page_size": 20}, "response": {"items": [], "total": 0}},
    {"group": "tracks", "method": "GET", "path": "/api/tracks", "purpose": "轨迹摘要列表", "request": {"source": "radar"}, "response": [{"track_id": "trk_track_radar_001"}]},
    {"group": "kg", "method": "GET", "path": "/api/kg/graph", "purpose": "知识图谱可视化数据", "request": {"limit": 300}, "response": {"nodes": [], "edges": []}},
    {"group": "fusion", "method": "GET", "path": "/api/fusion/candidates", "purpose": "KG 融合候选列表", "request": {"scenario": "完整模态"}, "response": [{"candidate_id": "C01"}]},
    {"group": "llm", "method": "POST", "path": "/api/llm/decision", "purpose": "候选目标大模型研判", "request": {"candidate_id": "C01", "local_rule_mode": True}, "response": {"decision": "confirm", "risk_level": "高"}},
    {"group": "chat", "method": "POST", "path": "/api/chat/send", "purpose": "大模型对话问答", "request": {"session_id": "chat_001", "message": "数据概况"}, "response": {"answer": "当前数据包含多模态记录。"}},
    {"group": "experiments", "method": "GET", "path": "/api/experiments/detection", "purpose": "检测性能表", "request": {}, "response": [{"Precision": 1.0, "F1": 1.0}]},
    {"group": "settings", "method": "POST", "path": "/api/settings", "purpose": "保存设置", "request": {"top_k": 5}, "response": {"success": True}},
]


OPERATION_WORKFLOW = [
    {"step": 1, "name": "登录系统", "description": "使用固定账号进入系统。", "expected_result": "进入系统首页。"},
    {"step": 2, "name": "查看首页", "description": "确认轨迹数量、图谱规模和性能指标。", "expected_result": "顶部卡片和运行分析图表正常呈现。"},
    {"step": 3, "name": "查看多模态数据", "description": "选择 radar 或 spectrum，查看记录列表。", "expected_result": "表格分页呈现，并可查看记录摘要。"},
    {"step": 4, "name": "查看轨迹证据", "description": "选择轨迹类型，点击轨迹查看特征。", "expected_result": "轨迹详情、特征图和时间线正常呈现。"},
    {"step": 5, "name": "查看知识图谱", "description": "加载节点和边，点击节点查看属性。", "expected_result": "ECharts graph 可以缩放、拖拽、点击。"},
    {"step": 6, "name": "分析融合候选", "description": "切换场景并查看 KG score 排名。", "expected_result": "候选列表和得分组成图正常呈现。"},
    {"step": 7, "name": "调用大模型研判", "description": "选择候选并点击生成研判。", "expected_result": "返回裁决结果、风险等级、理由和建议。"},
    {"step": 8, "name": "进行对话问答", "description": "点击快捷问题或输入自定义问题。", "expected_result": "聊天窗口返回带证据引用的回答。"},
]


def get_system_catalog():
    return {
        "system_name": SYSTEM_NAME,
        "modules": SYSTEM_MODULES,
        "modalities": MODALITY_FIELDS,
        "apis": API_ENDPOINTS,
        "screenshots": OPERATION_WORKFLOW,
        "workflow": OPERATION_WORKFLOW,
    }


def get_module_catalog():
    return SYSTEM_MODULES


def get_api_catalog():
    return API_ENDPOINTS


def get_screenshot_catalog():
    return OPERATION_WORKFLOW


def get_modality_catalog():
    return MODALITY_FIELDS


def find_module(key):
    return next((item for item in SYSTEM_MODULES if item["key"] == key), None)


def summarize_capability():
    return {
        "system_name": SYSTEM_NAME,
        "module_count": len(SYSTEM_MODULES),
        "api_count": len(API_ENDPOINTS),
        "modality_count": len(MODALITY_FIELDS),
        "workflow_steps": len(OPERATION_WORKFLOW),
    }


def build_manual_outline():
    return [
        {
            "chapter": f"{module['order']}. {module['name']}",
            "route": module["route"],
            "description": module["role"],
            "operation": "、".join(module["screenshots"]),
        }
        for module in SYSTEM_MODULES
    ]


def build_api_markdown():
    lines = [f"# {SYSTEM_NAME} 接口清单", ""]
    for endpoint in API_ENDPOINTS:
        lines.extend(
            [
                f"## {endpoint['method']} {endpoint['path']}",
                "",
                f"- 分组：{endpoint['group']}",
                f"- 用途：{endpoint['purpose']}",
                f"- 请求样式：`{endpoint['request']}`",
                f"- 返回样式：`{endpoint['response']}`",
                "",
            ]
        )
    return "\n".join(lines)


def build_screenshot_markdown():
    lines = [f"# {SYSTEM_NAME} 页面采集清单", ""]
    for step in OPERATION_WORKFLOW:
        lines.append(f"{step['step']}. {step['name']}")
        lines.append(f"   - 操作建议：{step['description']}")
        lines.append(f"   - 预期结果：{step['expected_result']}")
    return "\n".join(lines)


def build_feature_matrix():
    return [
        {
            "module": module["name"],
            "route": module["route"],
            "has_page": True,
            "has_api": any(api["group"] == module["key"] for api in API_ENDPOINTS)
            or module["key"] in {"login", "dashboard", "kg", "llm_decision"},
            "has_runtime_data": True,
            "suitable_for_capture": True,
        }
        for module in SYSTEM_MODULES
    ]
