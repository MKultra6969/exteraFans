from typing import List
import html

MAX_MESSAGE_LENGTH = 4096


def build_fan_list_messages(fan_lines: List[str]) -> List[str]:

    if not fan_lines:
        return []

    chunks = []
    current_chunk = ""

    for line in fan_lines:
        safe_line = html.escape(line)
        formatted_line = f"<blockquote>{safe_line}</blockquote>"

        if len(current_chunk) + len(formatted_line) + 1 > MAX_MESSAGE_LENGTH:
            chunks.append(current_chunk.strip())
            current_chunk = formatted_line + "\n"
        else:
            current_chunk += formatted_line + "\n"

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks