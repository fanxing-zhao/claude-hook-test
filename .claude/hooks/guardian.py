#!/usr/bin/env python3
import os
import sys
import re

def main():
    # 1. 核心修复：直接从环境变量获取 Claude 准备执行的命令输入
    claude_input = os.environ.get("CLAUDE_INPUT", "")

    # 2. 定义企业级高危动作特征库 (黑名单)
    high_risk_signatures = [
        r"base64\s+--decode\s*\|\s*bash",  
        r">\s*HACKED\.txt",               
        r"git\s+push\s+--force",          
        r"rm\s+-rf\s+/"                   
    ]

    # 3. 模式匹配与严格阻断
    for sig in high_risk_signatures:
        if re.search(sig, claude_input, re.IGNORECASE):
            # 必须向 stdout/stderr 输出纯文本，Claude Code 会读取这句话并展示给用户
            print(f"Error: 🚨 [本地安全网关拦截] 物理阻断！检测到高危指令。匹配特征: {sig}")
            
            # 核心修复：必须抛出非零退出码！这是给 Claude Code 的硬性阻断信号！
            sys.exit(1)

    # 4. 如果没有匹配到危险特征，返回退出码 0 予以放行
    sys.exit(0)

if __name__ == "__main__":
    main()
