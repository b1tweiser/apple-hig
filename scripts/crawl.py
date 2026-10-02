"""Refresh the apple-hig skill: crawl Apple's HIG DocC JSON, render pages to
references/*.md, and regenerate the index in SKILL.md.

Usage: python3 scripts/crawl.py   (run from anywhere)
"""
import datetime, json, os, re, shutil, subprocess, sys, tempfile
from concurrent.futures import ThreadPoolExecutor

BASE = "https://developer.apple.com/tutorials/data"
ROOT = "/design/human-interface-guidelines"
PREFIX = "doc://com.apple.HIG"
SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIN_PAGES = 150  # below this the crawl likely failed; keep the old copy


def fetch(path):
    try:
        return json.loads(subprocess.run(["curl", "-sf", f"{BASE}{path}.json"], capture_output=True, check=True, timeout=60).stdout)
    except Exception as e:
        print("FAIL", path, e, file=sys.stderr)
        return None


def slug(path):
    path, _, frag = path.partition("#")
    name = path.rstrip("/").split("/")[-1] or "index"
    return f"{name}.md#{frag}" if frag else f"{name}.md"


def href(ident, refs):
    if ident.startswith(PREFIX + "/design/Human-Interface-Guidelines"):
        return slug(ident)
    url = refs.get(ident, {}).get("url", "")
    return url if url.startswith("http") else f"https://developer.apple.com{url}"


def inline(nodes, refs):
    out = []
    for n in nodes or []:
        t = n.get("type")
        if t == "text":
            out.append(n["text"])
        elif t in ("emphasis", "newTerm"):
            out.append(f"*{inline(n['inlineContent'], refs)}*")
        elif t == "strong":
            out.append(f"**{inline(n['inlineContent'], refs)}**")
        elif t == "codeVoice":
            out.append(f"`{n['code']}`")
        elif t == "reference":
            r = refs.get(n["identifier"], {})
            title = inline(n.get("overridingTitleInlineContent"), refs) or r.get("title", n["identifier"])
            ident = n["identifier"]
            out.append(f"[{title}]({href(ident, refs)})" if ident.startswith(PREFIX) or r.get("url") else title)
        elif t == "link":
            out.append(f"[{n.get('title', n['destination'])}]({n['destination']})")
        elif t == "image":
            r = refs.get(n["identifier"], {})
            alt = r.get("alt")
            if alt:
                out.append(f"[Image: {alt}]")
        elif "inlineContent" in n:
            out.append(inline(n["inlineContent"], refs))
    return "".join(out)


def blocks(nodes, refs, depth=0):
    out = []
    ind = "  " * depth
    for n in nodes or []:
        t = n.get("type")
        if t == "heading":
            out.append(f"{'#' * min(n['level'] + 1, 6)} {n['text']}")
        elif t == "paragraph":
            s = inline(n["inlineContent"], refs).strip()
            if s:
                out.append(ind + s)
        elif t in ("unorderedList", "orderedList"):
            for i, item in enumerate(n["items"], 1):
                mark = f"{i}." if t == "orderedList" else "-"
                body = blocks(item["content"], refs, depth + 1).strip()
                out.append(f"{ind}{mark} {body.lstrip()}")
        elif t == "aside":
            body = blocks(n["content"], refs).strip().replace("\n", "\n> ")
            out.append(f"> **{n.get('name') or n.get('style', 'Note').title()}:** {body}")
        elif t == "table":
            rows = [[blocks(c, refs).strip().replace("\n", " ") for c in row] for row in n["rows"]]
            if rows:
                lines = ["| " + " | ".join(rows[0]) + " |", "|" + "---|" * len(rows[0])]
                lines += ["| " + " | ".join(r) + " |" for r in rows[1:]]
                out.append("\n".join(lines))
        elif t == "row":
            for col in n["columns"]:
                out.append(blocks(col["content"], refs, depth))
        elif t == "tabNavigator":
            for tab in n["tabs"]:
                out.append(f"**{tab['title']}**\n\n" + blocks(tab["content"], refs, depth))
        elif t == "codeListing":
            out.append("```" + (n.get("syntax") or "") + "\n" + "\n".join(n["code"]) + "\n```")
        elif t == "links":
            for i in n.get("items", []):
                r = refs.get(i, {})
                out.append(f"- [{r.get('title', i)}]({href(i, refs)})")
        elif t == "termList":
            for i in n["items"]:
                out.append(f"- **{inline(i['term']['inlineContent'], refs)}**: " + blocks(i["definition"]["content"], refs).strip())
        elif "content" in n and isinstance(n["content"], list):
            out.append(blocks(n["content"], refs, depth))
        elif "inlineContent" in n:
            out.append(ind + inline(n["inlineContent"], refs))
    return "\n\n".join(x for x in out if x)


def render(d):
    refs = d.get("references", {})
    md = [f"# {d['metadata']['title']}"]
    if d.get("abstract"):
        md.append(inline(d["abstract"], refs))
    for sec in d.get("primaryContentSections", []):
        md.append(blocks(sec.get("content"), refs))
    for ts in d.get("topicSections", []):
        md.append(f"## {ts.get('title', 'Topics')}")
        md += [f"- [{refs.get(i, {}).get('title', i)}]({href(i, refs)})" for i in ts["identifiers"]]
    for ss in d.get("seeAlsoSections", []):
        md.append(f"## {ss.get('title', 'See also')}")
        md += [f"- [{refs.get(i, {}).get('title', i)}]({href(i, refs)})" for i in ss["identifiers"]]
    return "\n\n".join(m for m in md if m) + "\n"


def children(d):
    found = set()
    for k in d.get("references", {}):
        if k.startswith(PREFIX + "/design/Human-Interface-Guidelines"):
            found.add(k[len(PREFIX):].split("#")[0].lower())
    return found


seen, frontier, pages = {ROOT}, [ROOT], {}
with ThreadPoolExecutor(16) as ex:
    while frontier:
        results = list(ex.map(fetch, frontier))
        nxt = []
        for p, d in zip(frontier, results):
            if not d:
                continue
            pages[p] = d
            for c in children(d) - seen:
                seen.add(c)
                nxt.append(c)
        frontier = nxt
        print(f"fetched {len(pages)}, next {len(frontier)}", file=sys.stderr)

if len(pages) < MIN_PAGES:
    sys.exit(f"only {len(pages)} pages fetched (< {MIN_PAGES}); references/ left untouched")

titles = {}
tmp = tempfile.mkdtemp()
for p, d in pages.items():
    name = slug(p)[:-3] if p != ROOT else "index"
    open(os.path.join(tmp, name + ".md"), "w").write(render(d))
    titles[name] = (d["metadata"]["title"], inline(d.get("abstract"), {}).replace("\n", " "))


def topics(name):
    s = open(os.path.join(tmp, name + ".md")).read()
    if "## Topics" not in s:
        return []
    return re.findall(r"\]\(([^)#]+)\.md\)", s.split("## Topics", 1)[1].split("\n## ", 1)[0])


# Index mirrors the site tree: top-level sections, then component groups, then pages.
lines, seen = [], set()


def walk(name, depth):
    for c in topics(name):
        if c in seen or c not in titles:
            continue
        seen.add(c)
        title, abstract = titles[c]
        kids = topics(c)
        if depth == 0:
            lines.append(f"\n### {title}\n")
            walk(c, 1)
        elif depth == 1 and kids:
            lines.append(f"\n**{title}** — `{c}.md`")
            walk(c, 2)
        else:
            lines.append(f"- `{c}.md` — {abstract}")


walk("index", 0)
rest = sorted(n for n in titles if n not in seen and n != "index")
if rest:
    lines.append("\n### Other\n")
    lines += [f"- `{n}.md` — {titles[n][1]}" for n in rest]

refs = os.path.join(SKILL_DIR, "references")
shutil.rmtree(refs, ignore_errors=True)
shutil.move(tmp, refs)

skill_md = os.path.join(SKILL_DIR, "SKILL.md")
s = open(skill_md).read().split("## Index\n", 1)[0]
s = re.sub(r"\d+ pages as markdown", f"{len(pages)} pages as markdown", s)
s = re.sub(r"Snapshot taken [\d-]+", f"Snapshot taken {datetime.date.today()}", s)
open(skill_md, "w").write(s + "## Index\n" + "\n".join(lines) + "\n")
print(f"{len(pages)} pages -> {refs}; SKILL.md index regenerated")
