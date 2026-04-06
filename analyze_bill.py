#!/usr/bin/env python3
"""
API账单分析工具
使用：python analyze_bill.py --file bill.json
"""

import json
import sys
import argparse
from collections import Counter
from datetime import datetime

def analyze_bill(bill_data):
    calls = []
    total_cost = 0
    total_tokens = 0
    
    for entry in bill_data:
        cost = entry.get('cost', 0)
        tokens = entry.get('total_tokens', 0)
        prompt = entry.get('prompt', '')[:200]
        calls.append({
            'cost': cost,
            'tokens': tokens,
            'prompt': prompt,
            'timestamp': entry.get('timestamp'),
            'tools': entry.get('tools_used', []),
            'tool_result': entry.get('tool_result')
        })
        total_cost += cost
        total_tokens += tokens
    
    # 1. 重复调用检测
    prompts = [c['prompt'] for c in calls]
    dup_counts = Counter(prompts)
    dup_cost = sum(c['cost'] for i, c in enumerate(calls)
                   if prompts.count(prompts[i]) > 1 and c['cost'] > 0)
    
    # 2. 异常大额调用
    avg_cost = total_cost / len(calls) if calls else 0
    expensive = [c for c in calls if c['cost'] > avg_cost * 3]
    expensive_cost = sum(c['cost'] for c in expensive)
    
    # 3. 工具调用浪费
    empty_tool_calls = [c for c in calls if c['tools'] and not c.get('tool_result')]
    tool_waste = sum(c['cost'] for c in empty_tool_calls)
    
    # 4. 时间段分析
    time_groups = {}
    for c in calls:
        if c.get('timestamp'):
            try:
                hour = datetime.fromisoformat(c['timestamp']).hour
                time_group = f"{hour:02d}:00-{hour:02d}:59"
                time_groups[time_group] = time_groups.get(time_group, 0) + c['cost']
            except:
                pass
    
    # 生成报告
    print(f"""
=== API成本分析报告 ===

总调用: {len(calls)}
总Token: {total_tokens:,}
总成本: ${total_cost:.4f}

--- 浪费点分析 ---
重复调用浪费: ${dup_cost:.4f} ({len([p for p in prompts if prompts.count(p) > 1])}次重复)
异常大额调用: ${expensive_cost:.4f} ({len(expensive)}次)
无效工具调用: ${tool_waste:.4f} ({len(empty_tool_calls)}次)

可优化总额: ${dup_cost + expensive_cost + tool_waste:.4f}

--- 时间段成本分布 ---""")
    
    for time_group, cost in sorted(time_groups.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"{time_group}: ${cost:.4f}")
    
    print(f"""
--- 优化建议 ---
1. 启用缓存: 消除重复调用，预计节省${dup_cost:.4f}
2. 检查异常调用: 重点关注{len(expensive)}次成本>平均值3倍的调用
3. 工具调用优化: 确保工具调用后消费结果，预计节省${tool_waste:.4f}
4. 时间段优化: 考虑在低成本时段执行批量任务
""")

def main():
    parser = argparse.ArgumentParser(description='API账单分析工具')
    parser.add_argument('--file', required=True, help='账单文件路径')
    parser.add_argument('--format', choices=['json', 'csv'], default='json', help='文件格式')
    
    args = parser.parse_args()
    
    try:
        with open(args.file, 'r', encoding='utf-8') as f:
            if args.format == 'json':
                data = json.load(f)
            else:
                # CSV格式处理（简化版）
                import csv
                reader = csv.DictReader(f)
                data = list(reader)
        
        analyze_bill(data)
    except FileNotFoundError:
        print(f"错误: 文件 {args.file} 不存在")
        sys.exit(1)
    except json.JSONDecodeError:
        print("错误: 文件格式不正确，请检查是否为有效的JSON格式")
        sys.exit(1)
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()