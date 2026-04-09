#!/usr/bin/env python3
import sys
import json
import re

def main():
    try:
        # 1. 准确接收 stdin 管道传来的 JSON Payload
        payload_data = sys.stdin.read()
        if not payload_data:
            sys.exit(0)
            
        payload = json.loads(payload_data)
        
        # 2. 提取准备执行的真实 Bash 命令
        command = payload.get("tool_input", {}).get("command", "")

        # 3. 高危动作特征库 (黑名单)
        high_risk_signatures = [
            r"base64\s+--decode\s*\|\s*bash",  
            r">\s*HACKED\.txt",               
            r"git\s+push\s+--force",          
            r"rm\s+-rf\s+/"                   
        ]

        # 4. 模式匹配与硬性阻断
        for sig in high_risk_signatures:
            if re.search(sig, command, re.IGNORECASE):
                # 必须向 stderr 输出报错信息，Claude Code 会捕捉并作为阻断理由展示给用户
                print(f"\n🚨 [本地安全网关] 致命拦截：禁止执行高危指令！匹配特征: {sig}", file=sys.stderr)
                
                # 核心修复：Exit Code 2 才是真正的硬阻断信号！
                sys.exit(2)

        # 安全放行
        sys.exit(0)

    except Exception as e:
        # 生产环境的 Fail-Closed 原则：如果安全脚本自身解析崩溃，直接拉闸 (Exit 2)，绝不放行！
        print(f"Hook System Error: {str(e)}", file=sys.stderr)
        sys.exit(2)

if __name__ == "__main__":
    main()
