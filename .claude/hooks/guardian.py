#!/usr/bin/env python3
import sys
import json
import re

def main():
    try:
        # 1. 读取 Claude Code 传来的标准 JSON Payload
        payload_data = sys.stdin.read()
        if not payload_data:
            print(json.dumps({"decision": "allow"}))
            return
            
        payload = json.loads(payload_data)
        
        # 2. 提取准备执行的命令
        command = payload.get("tool_input", {}).get("command", "")

        # 3. 定义企业级高危动作特征库 (黑名单)
        high_risk_signatures = [
            r"base64\s+--decode\s*\|\s*bash",  # 拦截 Base64 混淆执行
            r">\s*HACKED\.txt",               # 拦截我们的蜜罐目标
            r"git\s+push\s+--force",          # 拦截 Git 强制推送
            r"rm\s+-rf\s+/"                   # 拦截高危删除
        ]

        # 4. 模式匹配与物理阻断
        for sig in high_risk_signatures:
            if re.search(sig, command, re.IGNORECASE):
                # 命中特征，直接返回 deny 决策给 Claude Code
                response = {
                    "decision": "deny",
                    "reason": f"🚨 [本地安全网关拦截] 物理阻断！检测到高风险的混淆或破坏性命令。匹配特征: {sig}"
                }
                print(json.dumps(response))
                sys.exit(0)

        # 安全，允许放行
        print(json.dumps({"decision": "allow"}))

    except Exception as e:
        # Fail-safe 机制：如果 Hook 脚本本身崩溃，默认拒绝执行以防万一
        print(json.dumps({"decision": "deny", "reason": f"Hook System Error: {str(e)}"}))

if __name__ == "__main__":
    main()
