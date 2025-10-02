# 将sql样例知识库处理为json格式
from pydoc import describe
import re
import json
from pathlib import Path


def read_and_split_by_marks(filepath: str) -> list[str]:
    """
    读取文本，按以 '###' 开头的段落进行切分。
    返回每段包含其自身标题（保留'### '前缀）。
    """
    p = Path(filepath)
    text = p.read_text(encoding="utf-8")

    # 基于行首 '###' 进行分段，使用前瞻以保留分隔符或手动加回
    parts = re.split(r"(?m)^###\s*", text)

    sections = []

    for part in parts:
        part = part.strip()
        if not part:
            continue
        # 还原前缀，保持段落清晰
        # sections.append(f"### {s}")
        sub_sec = {}
        sub_parts = re.split(r"\*\*question sample\*\*:\s*", part)
        sql_part = "**question sample**:" + "\n" + sub_parts[1]
        describe_part = sub_parts[0]
        question_part = "**SQL query sample**:" + "\n" + re.split(r"\*\*SQL query sample\*\*:\s*", sql_part)[0]

        sub_sec['description'] = describe_part + "\n" + question_part
        sub_sec['sql_example'] = sql_part
        sections.append(sub_sec)
    print(len(sections))
    return sections


if __name__ == "__main__":
    # 默认读取当前目录下的 sql_sample_kb3.txt
    base_dir = Path(__file__).parent
    src_txt = base_dir / "sql_sample_kb3.txt"

    sections = read_and_split_by_marks(str(src_txt))

    # # 打印段落数量与前两段示例
    # print(f"Total sections: {len(sections)}")
    # for i, sec in enumerate(sections[:2]):
    #     print(f"\n=== Section {i+1} ===\n{sec[:500]}" + ("..." if len(sec) > 500 else ""))

    # 如需落盘为 JSON，可解除注释
    out_json = base_dir / "sql_sample_kb3_sections.json"
    out_json.write_text(json.dumps(sections, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved: {out_json}")
