"""2회차 예시 서버: 독서 메모.

Tool 2개, Resource 2개, Prompt 1개로 구성한 v1 예시입니다.
메모는 이 파일 옆의 notes.json에 저장되어, 서버를 다시 켜도 남아 있습니다.

실행(Inspector 열기): uv run mcp dev example/server.py
"""

import json
from pathlib import Path

from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

mcp = MCPServer("Reading Notes")

DATA_FILE = Path(__file__).with_name("notes.json")


def load_notes() -> list[dict]:
    if not DATA_FILE.exists():
        return []
    return json.loads(DATA_FILE.read_text(encoding="utf-8"))


def save_notes(notes: list[dict]) -> None:
    DATA_FILE.write_text(json.dumps(notes, ensure_ascii=False, indent=2), encoding="utf-8")


# ── Tools: 서버가 실행하는 동작 (상태를 바꾸거나 계산이 필요한 것) ──────────


@mcp.tool()
def add_note(book: str, text: str) -> str:
    """읽은 책에 대한 메모를 하나 저장한다. 저장된 메모의 번호를 알려 준다."""
    if not book.strip() or not text.strip():
        # 예상한 실패는 ToolError로 알립니다. 이 메시지를 모델이 읽고 다음 행동을 정합니다.
        # (ValueError 같은 다른 예외는 '서버 고장'으로 취급되어 메시지가 모델에 전달되지 않습니다.)
        raise ToolError("book과 text는 비어 있을 수 없습니다.")
    notes = load_notes()
    note = {"id": len(notes) + 1, "book": book.strip(), "text": text.strip()}
    notes.append(note)
    save_notes(notes)
    return f"메모 {note['id']}번을 저장했습니다."


@mcp.tool()
def search_notes(keyword: str) -> list[dict]:
    """메모 본문이나 책 제목에 keyword가 들어간 메모를 찾아 돌려준다."""
    key = keyword.strip().lower()
    if not key:
        raise ToolError("keyword를 입력해 주세요.")
    return [n for n in load_notes() if key in n["text"].lower() or key in n["book"].lower()]


# ── Resources: 읽기 전용 데이터 (앱이 맥락으로 가져다 쓴다) ──────────────────


@mcp.resource("notes://all")
def all_notes() -> str:
    """저장된 모든 메모를 한 번에 보여 준다."""
    notes = load_notes()
    if not notes:
        return "아직 저장된 메모가 없습니다."
    return "\n".join(f"{n['id']}. [{n['book']}] {n['text']}" for n in notes)


@mcp.resource("notes://book/{title}")
def notes_of_book(title: str) -> str:
    """책 제목 하나에 해당하는 메모만 보여 준다."""
    found = [n for n in load_notes() if n["book"] == title]
    if not found:
        return f"'{title}'에 대한 메모가 없습니다."
    return "\n".join(f"{n['id']}. {n['text']}" for n in found)


# ── Prompts: 사용자가 직접 고르는 재사용 프롬프트 틀 ────────────────────────


@mcp.prompt()
def summarize_book(title: str) -> str:
    """책 한 권의 메모를 모아 독후감 초안을 요청하는 프롬프트."""
    return (
        f"'{title}'에 대한 내 메모를 읽고, 핵심 생각 세 가지와 "
        "독후감 초안(5문장)을 써 주세요. 메모는 notes://book/ 리소스에서 읽을 수 있습니다."
    )


if __name__ == "__main__":
    mcp.run()
