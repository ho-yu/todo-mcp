"""HTTP로 떠 있는 MCP 서버에 접속해 기능 목록을 보고, 원하면 Tool 하나를 호출하는 최소 클라이언트.

먼저 다른 터미널에서 서버를 켭니다:   uv run python server.py --http
목록만 보기:                          uv run python call_remote.py
Tool 호출하기:                        uv run python call_remote.py list_todos '{"status": "open"}'
다른 주소로 접속하기:                  uv run python call_remote.py --url http://127.0.0.1:9000/mcp
"""

import argparse
import json

import anyio
from mcp import Client

parser = argparse.ArgumentParser(description="원격 MCP 서버 점검용 클라이언트")
parser.add_argument("--url", default="http://127.0.0.1:8000/mcp", help="서버 주소 (기본 http://127.0.0.1:8000/mcp)")
parser.add_argument("tool", nargs="?", help="호출할 Tool 이름 (생략하면 목록만 출력)")
parser.add_argument("args", nargs="?", default="{}", help='Tool 입력값(JSON). 예: \'{"status": "open"}\'')
opts = parser.parse_args()


async def main() -> None:
    async with Client(opts.url) as client:
        tools = await client.list_tools()
        resources = await client.list_resources()
        templates = await client.list_resource_templates()
        prompts = await client.list_prompts()
        print(f"연결 성공: {opts.url}")
        print("Tools:", [t.name for t in tools.tools])
        print("Resources:", [str(r.uri) for r in resources.resources] + [t.uri_template for t in templates.resource_templates])
        print("Prompts:", [p.name for p in prompts.prompts])
        if opts.tool:
            result = await client.call_tool(opts.tool, json.loads(opts.args))
            label = "오류" if result.is_error else "결과"
            print(f"{opts.tool} {label}:", [getattr(c, "text", c) for c in result.content])


anyio.run(main)
