import markdown


def fix_markdown_lists(text: str) -> str:
    lines = text.splitlines()
    result = []

    for i, line in enumerate(lines):
        if (
            line.lstrip().startswith(("* ", "*\t", "- ", "+ "))
            and result
            and result[-1].strip() != ""
        ):
            result.append("")

        result.append(line)
    return "\n".join(result)

def convert_response_to_html(raw_text: str) -> str:
    text = raw_text.strip()

    text = text.replace("\\n", "\n")

    # Fix Markdown list formatting
    text = fix_markdown_lists(text)
    return markdown.markdown(
        text,
        extensions=["extra", "tables", "fenced_code", "sane_lists"],
    )
