"""2회차 내 서버 v1 시작 틀.

1) 먼저 핸드아웃의 '설계표'를 채우세요. 코드는 그다음입니다.
2) 아래 TODO를 내 주제에 맞게 바꿔 가며 채웁니다.
3) 서버 이름, 함수 이름, 독스트링은 모델이 읽는 정보입니다. 분명하게 적으세요.

실행(Inspector 열기): uv run mcp dev server.py
"""

from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError  # 예상한 실패를 모델에게 알릴 때 사용

# TODO 1: 서버 이름을 내 주제에 맞게 바꾸세요. (예: "Reading Notes")
mcp = MCPServer("Todo")


# ── Tool: 서버가 실행하는 동작 ──────────────────────────────────────────────
# TODO 2: 설계표에서 Tool로 정한 것 중 하나를 구현하세요.
#   - 함수 이름: 동사로 시작 (예: search_notes)
#   - 독스트링: 모델이 언제 이 도구를 쓸지 알 수 있게 한 문장으로
#   - 입력값에 타입 힌트를 붙이세요 (str, int, list[str] 등)
#   - 잘못된 입력은 raise ToolError("무엇이 문제인지") 로 알려 주세요 (ValueError는 메시지가 모델에 전달되지 않습니다)
#
# @mcp.tool()
# def my_tool(arg: str) -> str:
#     """이 도구가 하는 일을 한 문장으로."""
#     ...


# ── Resource: 읽기 전용 데이터 ──────────────────────────────────────────────
# TODO 3: 설계표에서 Resource로 정한 것을 구현하세요.
#   - 고정 주소:  @mcp.resource("myapp://all")
#   - 매개변수 주소: @mcp.resource("myapp://item/{name}")  (함수 인자 이름과 {name}이 같아야 함)
#
# @mcp.resource("myapp://all")
# def everything() -> str:
#     """무엇을 보여 주는 데이터인지 한 문장으로."""
#     ...


# ── Prompt: 사용자가 고르는 프롬프트 틀 ─────────────────────────────────────
# TODO 4 (선택): 설계표에서 Prompt로 정한 것이 있으면 구현하세요.
#
# @mcp.prompt()
# def my_prompt(topic: str) -> str:
#     """이 프롬프트가 요청하는 일을 한 문장으로."""
#     return f"... {topic} ..."


if __name__ == "__main__":
    mcp.run()
