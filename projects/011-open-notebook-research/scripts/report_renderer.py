"""Small, escaped Markdown renderer for reviewed scientific reports."""
from html import escape
import re
from urllib.parse import urlsplit


def inline(text, asset_prefix=""):
    text = text.replace(r"\|", "|")
    tokens = []

    def keep(html):
        tokens.append(html)
        return f"\x00{len(tokens)-1}\x00"

    def link(match):
        label, raw = match.groups()
        raw = raw.replace("../../assets/", "assets/").replace("../assets/", "assets/")
        parsed = urlsplit(raw)
        if parsed.scheme not in ("", "https", "http") or (not parsed.scheme and ".." in parsed.path.split("/")):
            return label
        if raw.startswith("assets/"):
            raw = asset_prefix + raw
        return keep(f'<a href="{escape(raw, quote=True)}" target="_blank" rel="noopener noreferrer">{escape(label)}</a>')

    text = re.sub(r"\[([^\]]+)\]\(([^\s)]+)\)", link, text)
    text = re.sub(r"`([^`]+)`", lambda m: keep("<code>" + escape(m[1]) + "</code>"), text)
    text = escape(text)
    text = re.sub(r"\*\*([^*\n]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<em>\1</em>", text)
    for i, token in enumerate(tokens):
        text = text.replace(f"\x00{i}\x00", token)
    return text


def render(text, prefix, asset_prefix=""):
    lines = text.splitlines()
    out, toc, paragraph, listing = [], [], [], []
    list_type = None

    def flush():
        nonlocal list_type
        if paragraph:
            out.append("<p>" + inline(" ".join(paragraph), asset_prefix) + "</p>")
            paragraph.clear()
        if listing:
            out.append(f"<{list_type}>" + "".join("<li>" + inline(x, asset_prefix) + "</li>" for x in listing) + f"</{list_type}>")
            listing.clear()
            list_type = None

    i = 0
    heading_index = 0
    while i < len(lines):
        line = lines[i].strip()
        heading = re.match(r"^(#{1,6})\s+(.+)$", line)
        list_item = re.match(r"^(?:(\d+)[.)]|[-*])\s+(.+)$", line)
        if not line:
            flush()
        elif heading:
            flush()
            heading_index += 1
            id_ = f"{prefix}-s{heading_index}"
            level = min(len(heading[1]) + 1, 6)
            out.append(f'<h{level} id="{id_}">' + inline(heading[2], asset_prefix) + f"</h{level}>")
            if len(heading[1]) == 2:
                toc.append({"id": id_, "title": re.sub(r"\*|`", "", heading[2])})
        elif line.startswith("|") and i + 1 < len(lines) and re.fullmatch(r"[\s|:\-]+", lines[i + 1]):
            flush()
            header = [x.strip() for x in re.split(r"(?<!\\)\|", line.strip("|"))]
            rows = []
            i += 2
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append([x.strip() for x in re.split(r"(?<!\\)\|", lines[i].strip().strip("|"))])
                i += 1
            out.append('<div class="report-table-wrap"><table><thead><tr>' + "".join("<th scope=\"col\">" + inline(x, asset_prefix) + "</th>" for x in header) + "</tr></thead><tbody>" + "".join("<tr>" + "".join("<td>" + inline(x, asset_prefix) + "</td>" for x in row) + "</tr>" for row in rows) + "</tbody></table></div>")
            continue
        elif list_item:
            kind = "ol" if list_item[1] else "ul"
            if paragraph or (list_type and kind != list_type):
                flush()
            list_type = kind
            listing.append(list_item[2])
        elif line.startswith(">"):
            flush()
            out.append("<blockquote>" + inline(line.lstrip("> "), asset_prefix) + "</blockquote>")
        elif re.fullmatch(r"[-*_]{3,}", line):
            flush()
            out.append("<hr>")
        else:
            if listing:
                flush()
            paragraph.append(line)
        i += 1
    flush()
    return "\n".join(out), toc
