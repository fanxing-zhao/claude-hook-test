#!/usr/bin/env python3
import sys
import json
import re

RULES = [
    {
        "name": "高维资产越权 (Credential Access)",
        "level": "FATAL",
        "patterns": [
            r"/\.ssh",                   # 直接封杀任何试图触碰 .ssh 目录的行为
            r"\.aws/credentials",
            r"\.kube/config",
            r"/\.npmrc"
        ],
        "reason": "严禁 AI 越权读取、修改或扫描 SSH、AWS、Kube 等高维环境凭证。"
    },
    {
        "name": "网络防泄漏 (Data Exfiltration)",
        "level": "CRITICAL",
        "patterns": [
            r"curl.*?-X\s*POST", 
            r"wget\s+--post-data",
            r"nc\s+-e"
        ],
        "reason": "拦截未经授权的网络出站请求。"
    },
    {
        "name": "毁灭性操作 (Destructive Ops)",
        "level": "FATAL",
        "patterns": [
            r"rm\s+-rf\s+(/|\*|~\/|\.|/\w+)",
            r"chmod\s+-R\s+777\s+/"
        ],
        "reason": "禁止执行全局删除或最高权限篡改。"
    },
    {
        "name": "版本库审计 (VCS Protection)",
        "level": "WARNING",
        "patterns": [
            r"git\s+push\s+(--force|-f)",         
            r"git\s+branch\s+-D"
        ],
        "reason": "禁止强制覆盖 Git 历史。"
    }
]

def main():
    try:
        payload_data = sys.stdin.read()
        if not payload_data:
            sys.exit(0)
            
        payload = json.loads(payload_data)
        
        # 【核心补丁】提取工具名称，并将所有的工具输入（不论是 command 还是 path）转换为文本扫描！
        tool_name = payload.get("tool", "Unknown")
        tool_input = payload.get("tool_input", {})
        action_payload = json.dumps(tool_input, ensure_ascii=False)

        # 遍历引擎
        for rule in RULES:
            for pattern in rule["patterns"]:
                if re.search(pattern, action_payload, re.IGNORECASE):
                    error_msg = (
                        f"\n╔═══════════════════════════════════════════════════════════╗\n"
                        f"║ 🛡️ [全天候网关] AI 动作被物理拦截！\n"
                        f"╠═══════════════════════════════════════════════════════════╣\n"
                        f"║ 🔧 使用工具: {tool_name}\n"
                        f"║ ❌ 触发防线: {rule['name']} \n"
                        f"║ 🛑 风险参数: {action_payload[:100]}...\n"
                        f"║ 💡 系统判决: {rule['reason']} \n"
                        f"╚═══════════════════════════════════════════════════════════╝\n"
                    )
                    print(error_msg, file=sys.stderr)
                    sys.exit(2)

        sys.exit(0)
    except Exception as e:
        print(f"\n[Security Gateway Error]: {str(e)}", file=sys.stderr)
        sys.exit(2)

if __name__ == "__main__":
    main()
