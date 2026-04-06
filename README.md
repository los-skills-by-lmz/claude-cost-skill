# AI成本优化Skill使用指南

## 概述
这是一个用于分析AI API账单日志、识别Token浪费点的Skill，帮助您优化AI服务使用成本。

## 文件结构
```
skills/
└── cost-optimizer/
    ├── SKILL.md          # Skill定义文件
    ├── analyze_bill.py   # Python分析脚本
    └── README.md         # 使用说明
```

## 使用方法

### 1. 激活Skill
当您需要分析API账单时，在对话中说：
- "分析这份账单，找出浪费点"
- "帮我优化AI使用成本"
- "看看钱花哪了"

### 2. 准备账单数据
支持以下格式的账单数据：
- **JSON格式**：从OpenAI/Anthropic控制台导出的账单文件
- **CSV格式**：包含调用记录、成本、Token数等信息的CSV文件

### 3. 使用Python脚本分析（可选）
```bash
# 分析JSON账单
python analyze_bill.py --file bill.json

# 分析CSV账单
python analyze_bill.py --file bill.csv --format csv
```

## 账单数据格式要求

### JSON格式示例
```json
[
  {
    "timestamp": "2024-01-01T10:00:00",
    "prompt": "用户的问题内容...",
    "total_tokens": 1500,
    "cost": 0.03,
    "tools_used": ["search", "calculator"],
    "tool_result": "搜索结果..."
  }
]
```

### CSV格式示例
```csv
timestamp,prompt,total_tokens,cost,tools_used,tool_result
2024-01-01T10:00:00,"用户的问题内容...",1500,0.03,"search,calculator","搜索结果..."
```

## 分析维度

### 成本浪费检测
- **重复调用**：识别相同或相似的prompt重复调用
- **过长上下文**：检测携带过多历史消息的调用
- **无效工具调用**：工具调用后未使用结果的情况
- **异常大额调用**：单次成本超过平均值3倍的调用

### 时间段分析
- 识别成本激增的时间段
- 建议在低成本时段执行批量任务

## 优化建议

基于分析结果，Skill会提供具体的优化方案：
- 缓存策略：减少重复调用
- prompt优化：精简system prompt和上下文
- 工具调用优化：确保工具调用后消费结果
- 时间段调整：合理安排任务执行时间

## 示例输出

```markdown
# 成本分析报告

## 概览
- 总调用次数：150
- 总Token消耗：225,000
- 总成本：$4.50
- **可节省：$1.20 (26.7%)**

## 浪费点Top 3
1. [重复调用] 相同prompt重复调用5次 | 浪费$0.75 | 启用缓存机制
2. [异常调用] 单次调用成本$0.45 | 浪费$0.30 | 检查prompt长度
3. [工具浪费] 3次工具调用未使用结果 | 浪费$0.15 | 优化工具调用逻辑

## 具体优化清单
- [ ] 启用Redis缓存，减少重复调用，预计节省$0.75
- [ ] 裁剪system prompt，从200 token降至100 token
- [ ] 设置工具调用超时，避免无效等待
```

## 扩展功能

未来可扩展的功能包括：
- 自动从AWS Cost Explorer拉取数据
- 定期推送成本报告到Slack/钉钉
- 对比不同AI模型的性价比
- 自动生成优化的prompt版本