"""Todo MCP 서버.

할 일을 추가·조회·완료·수정·삭제하는 개인용 MCP 서버입니다.
설계는 설계표.txt를 따르고, 저장 방식은 example/server.py를 참고합니다.
할 일은 이 파일 옆의 todos.json에 저장되어, 서버를 다시 켜도 남아 있습니다.
서버 이름, 함수 이름, 독스트링은 모델이 읽는 정보입니다. 분명하게 적으세요.

실행 방법 두 가지
  로컬(stdio):   uv run python server.py
  원격(HTTP):    uv run python server.py --http            (기본 주소 http://127.0.0.1:8000/mcp)
                 uv run python server.py --http --port 9000

Inspector 열기:        uv run mcp dev server.py
기능 목록 점검(stdio): uv run python list_features.py server.py
원격 서버 점검(HTTP):  uv run python call_remote.py
"""

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Annotated, Literal

from mcp.types import ToolAnnotations
from pydantic import Field

from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError  # 예상한 실패를 모델에게 알릴 때 사용

mcp = MCPServer("Todo")


# ── 저장소: todos.json 읽기/쓰기 ─────────────────────────────────────────────
# TODO 1: 할 일을 파일에 저장하고 불러오는 함수를 만드세요. (example의 load_notes/save_notes 참고)
#   - 경로는 서버 파일 기준으로: Path(__file__).with_name("todos.json")
#     (Claude Desktop은 다른 폴더에서 서버를 실행하므로 "todos.json" 같은 상대 경로는 쓰지 않습니다)
#   - 파일이 없으면 빈 목록 [] 을 돌려줍니다
#   - 저장할 때는 encoding="utf-8", ensure_ascii=False 로 한글이 깨지지 않게 합니다
#   - 할 일 하나의 모양: {"id": 1, "title": "우유 사기", "done": False, "created_at": "2026-11-19T09:30:00"}
#   - 새 id는 len(todos) + 1 이 아니라 max(id) + 1 로 만드세요 (삭제 후 id가 겹치지 않게)

DATA_FILE = Path(__file__).with_name("todos.json")


def load_todos() -> list[dict]:
    if not DATA_FILE.exists():
        return []
    return json.loads(DATA_FILE.read_text(encoding="utf-8"))


def save_todos(todos: list[dict]) -> None:
    DATA_FILE.write_text(json.dumps(todos, ensure_ascii=False, indent=2), encoding="utf-8")


def next_id(todos: list[dict]) -> int:
    # 삭제된 번호를 다시 쓰지 않도록 가장 큰 id 다음 번호를 쓴다.
    return max((t["id"] for t in todos), default=0) + 1


# ── Tool: 서버가 실행하는 동작 ──────────────────────────────────────────────
# TODO 2: 설계표의 Tool 5개를 구현하세요. add_todo, list_todos부터 만들고 Inspector로 확인한 뒤 나머지를 추가합니다.
#   - 독스트링: 모델이 언제 이 도구를 쓸지 알 수 있게 한 문장으로
#   - 각 Tool은 "load_todos() → 수정 → save_todos()" 순서로 동작합니다
#   - 예상한 실패는 raise ToolError("무엇이 문제인지") 로 알려 주세요 (ValueError는 메시지가 모델에 전달되지 않습니다)
#     실패 메시지에는 해결 방법도 함께 적습니다. 예: "7번 할 일이 없습니다. list_todos로 번호를 먼저 확인해 주세요."
#   - 입력값마다 Annotated[타입, Field(description="...")]로 설명을 붙이면 모델이 인자를 더 정확히 채웁니다
#   - annotations는 도구의 성격을 앱에 알리는 힌트입니다 (서버 동작을 막아 주지는 않음)
#       읽기만 하는 도구: @mcp.tool(annotations=ToolAnnotations(read_only_hint=True))
#       되돌릴 수 없는 도구(delete_todo): @mcp.tool(annotations=ToolAnnotations(destructive_hint=True))
#
#   1) add_todo(title: str) -> dict          새 할 일을 만들어 돌려준다.   실패: 제목이 비었거나 공백뿐
#   2) list_todos(status: Literal["all", "open", "done"] = "all") -> list[dict]
#                                             조건에 맞는 할 일 목록.       실패 없음 (빈 목록도 정상)
#   3) complete_todo(todo_id: int) -> dict    done=True로 바꿔 돌려준다.    실패: 없는 id
#   4) update_todo(todo_id: int, title: str) -> dict
#                                             제목을 바꿔 돌려준다.         실패: 없는 id, 빈 제목
#   5) delete_todo(todo_id: int) -> str       삭제 안내 문구를 돌려준다.    실패: 없는 id


@mcp.tool()
def add_todo(
    title: Annotated[str, Field(description="할 일 내용 한 줄. 예: 우유 사기")],
) -> dict:
    """할 일을 하나 추가한다. 만든 할 일(id 포함)을 돌려준다."""
    title = title.strip()
    if not title:
        raise ToolError("title은 비어 있을 수 없습니다. 할 일 내용을 한 줄로 적어 주세요.")
    todos = load_todos()
    todo = {
        "id": next_id(todos),
        "title": title,
        "done": False,
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }
    todos.append(todo)
    save_todos(todos)
    return todo


@mcp.tool(annotations=ToolAnnotations(read_only_hint=True))
def list_todos(
    status: Annotated[
        Literal["all", "open", "done"],
        Field(description="all: 전체, open: 아직 안 끝낸 것, done: 완료한 것"),
    ] = "all",
) -> list[dict]:
    """할 일 목록을 돌려준다. status로 전체(all), 남은 것(open), 완료한 것(done)을 고른다."""
    todos = load_todos()
    if status == "open":
        return [t for t in todos if not t["done"]]
    if status == "done":
        return [t for t in todos if t["done"]]
    return todos


# TODO 2-3 ~ 2-5: complete_todo, update_todo, delete_todo 를 위와 같은 방식으로 추가하세요.
#   - todo_id 인자에도 Field(description="... (add_todo나 list_todos 결과의 id)")를 붙이세요
#   - 없는 id면 ToolError(f"{todo_id}번 할 일이 없습니다. list_todos로 번호를 먼저 확인해 주세요.")
#   - delete_todo에는 annotations=ToolAnnotations(destructive_hint=True)를 붙이세요


# ── Resource: 읽기 전용 데이터 ──────────────────────────────────────────────
# TODO 3 (선택): 할 일 개수 요약을 Resource로 내놓으세요.
#   - 반환 예: "전체 5개 / 남은 것 3개 / 완료 2개"
#   - 할 일이 없으면 "아직 등록된 할 일이 없습니다." 처럼 안내 문구를 돌려줍니다
#
# @mcp.resource("todo://summary")
# def todo_summary() -> str:
#     """전체·남은·완료 할 일 개수를 요약해 보여 준다."""
#     ...


# ── Prompt: 사용자가 고르는 프롬프트 틀 ─────────────────────────────────────
# TODO 4 (선택): 남은 할 일로 오늘 계획을 세워 달라고 요청하는 Prompt를 만드세요.
#   - 입력은 없어도 됩니다
#   - 프롬프트 안에서 list_todos(status="open")이나 todo://summary를 활용하라고 알려 주면 좋습니다
#
# @mcp.prompt()
# def plan_my_day() -> str:
#     """남은 할 일을 바탕으로 오늘 계획을 세워 달라고 요청하는 프롬프트."""
#     return "..."


# ── 실행 방식 선택 ───────────────────────────────────────────────────────────


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--http", action="store_true", help="stdio 대신 Streamable HTTP로 실행")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    if args.http:
        mcp.run("streamable-http", host=args.host, port=args.port)
    else:
        mcp.run()


if __name__ == "__main__":
    main()
