"""Render weekly report JSON -> HTML (siap copy-paste ke Google Docs) + Markdown.

Pemakaian:
    python -I render_weekly.py <weekly.json> <output_dir>

Menghasilkan <output_dir>/Weekly-Report_<mulai>_<selesai>.html dan .md.
Skema JSON dijelaskan di references/format.md.
"""
import datetime as dt
import html
import json
import re
import sys
from pathlib import Path

HARI = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
BULAN = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli",
         "Agustus", "September", "Oktober", "November", "Desember"]
SEP = "━" * 30
URL = re.compile(r"(https?://[^\s<>\"]+)")


def tgl_panjang(iso):
    d = dt.date.fromisoformat(iso)
    return f"{HARI[d.weekday()]}, {d.day} {BULAN[d.month - 1]} {d.year}"


def esc(text):
    """Escape HTML dan jadikan URL bisa diklik."""
    out, last = [], 0
    for m in URL.finditer(text):
        out.append(html.escape(text[last:m.start()]))
        u = m.group(1)
        out.append(f'<a href="{html.escape(u)}">{html.escape(u)}</a>')
        last = m.end()
    out.append(html.escape(text[last:]))
    return "".join(out)


def item_html(item):
    """item = {label, text} atau {label, links:[{label,url}]}"""
    label = f"<b>{esc(item['label'])}:</b> " if item.get("label") else ""
    if "links" in item:
        sub = "".join(
            f"<li>{esc(l['label'])}: {esc(l['url'])}</li>" if l.get("label") else f"<li>{esc(l['url'])}</li>"
            for l in item["links"])
        return f"<li>{label}<ul>{sub}</ul></li>"
    return f"<li>{label}{esc(item.get('text', ''))}</li>"


def item_md(item, indent="   "):
    label = f"{item['label']}: " if item.get("label") else ""
    if "links" in item:
        lines = [f"{indent}* {label}".rstrip()]
        for l in item["links"]:
            lines.append(f"{indent}   * {l['label']}: {l['url']}" if l.get("label") else f"{indent}   * {l['url']}")
        return "\n".join(lines)
    return f"{indent}* {label}{item.get('text', '')}"


def ringkasan(data):
    tasks = [t for k in data["progres"] for t in k["tasks"]]
    on = [t for t in tasks if t.get("status_kategori") == "on_process"]
    return len(tasks), len(tasks) - len(on), on


def render_html(data):
    nama = data.get("nama", "Abdur")
    p = data["periode"]
    periode = f"{tgl_panjang(p['mulai'])} - {tgl_panjang(p['selesai'])}"

    # Pekerjaan
    pk = []
    for hari in data["pekerjaan"]:
        pk.append(f"<h4>{tgl_panjang(hari['tanggal'])}</h4><ol>")
        for t in hari["tasks"]:
            pk.append(f"<li><b>{esc(t['judul'])}</b><ul>{''.join(item_html(i) for i in t['items'])}</ul></li>")
        pk.append("</ol>")

    # Hasil pekerjaan
    hs = []
    for n, h in enumerate(data["hasil"], 1):
        if n > 1:
            hs.append(f"<p>{SEP}</p>")
        hs.append(f"<p><b>{n}. {esc(h['judul'])}</b></p><p>{esc(h['isi'])}</p>")

    # Progres: kategori selesai dulu, lalu "DALAM PROSES (On Process)"
    pr, no, last_on = [], 1, False
    for huruf, k in enumerate(sorted(data["progres"], key=lambda k: bool(k.get("on_process")))):
        if huruf:
            pr.append(f"<p>{SEP}</p>")
        if k.get("on_process") and not last_on:
            pr.append("<p><b>DALAM PROSES (On Process)</b></p>")
            last_on = True
        pr.append(f"<p><b>{chr(65 + huruf)}. {esc(k['kategori'])} ({len(k['tasks'])} task)</b></p>")
        for t in k["tasks"]:
            pr.append(f"<p><b>{no}. {esc(t['judul'])} ({esc(t['tanggal'])})</b></p>")
            for i in t["items"]:
                if "links" in i:
                    pr.append(f"<p>{esc(i['label'])}:</p><ul>" + "".join(
                        f"<li>{esc(l['label'])}: {esc(l['url'])}</li>" if l.get("label") else f"<li>{esc(l['url'])}</li>"
                        for l in i["links"]) + "</ul>")
                else:
                    pr.append(f"<p>{esc(i['label'])}: {esc(i['text'])}</p>")
            no += 1
    total, done, on = ringkasan(data)
    on_txt = f"{len(on)} task" + (f" ({', '.join(t['judul'] for t in on)})" if on else "")
    pr.append(f"<p>{SEP}</p><p><b>Ringkasan</b></p><p>Total Task: {total}<br>Selesai: {done} task<br>On Process: {esc(on_txt)}</p>")

    def row(label, body):
        return f'<tr><td class="lbl">{label}</td><td>{body}</td></tr>'

    kendala = esc(data.get("kendala", "")) or "&nbsp;"
    solusi = esc(data.get("solusi", "")) or "&nbsp;"
    tanya = esc(data.get("pertanyaan", "")) or "&nbsp;"
    return f"""<!doctype html>
<html lang="id"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Weekly Journal {nama}</title>
<style>
:root {{ --bg:#fff; --fg:#1f1f1f; --line:#9e9e9e; --muted:#5f6368; --link:#1155cc; }}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{ --bg:#1e1e1e; --fg:#e8e8e8; --line:#5f6368; --muted:#aaa; --link:#8ab4f8; }} }}
body {{ background:var(--bg); color:var(--fg); font:11pt/1.5 Arial, sans-serif; max-width:960px; margin:24px auto; padding:0 16px; }}
table {{ border-collapse:collapse; width:100%; table-layout:fixed; }}
td {{ border:1px solid var(--line); padding:8px 10px; vertical-align:top; overflow-wrap:anywhere; }}
td.lbl {{ width:120px; font-weight:bold; }}
h1 {{ font-size:18pt; }} h2 {{ font-size:14pt; margin:0; }} h4 {{ margin:12px 0 4px; }}
a {{ color:var(--link); }} .hint {{ color:var(--muted); font-size:9pt; }}
</style></head><body>
<p class="hint">Tips: Ctrl+A lalu Ctrl+C, tempel ke Google Doc "WORK WEEKLY JOURNAL" di bawah minggu terakhir.</p>
<div id="paste">
<p><b>{periode}</b></p>
<table>
<tr><td colspan="2"><h2>{esc(nama)}</h2></td></tr>
{row("Pekerjaan", "".join(pk))}
{row("Hasil pekerjaan", "".join(hs))}
{row("Progres", "".join(pr))}
{row("Kendala", kendala)}
{row("Solusi", solusi)}
{row("Pertanyaan", tanya)}
</table>
</div>
</body></html>
"""


def render_md(data):
    nama = data.get("nama", "Abdur")
    p = data["periode"]
    out = [f"# WORK WEEKLY JOURNAL - {nama.upper()}",
           f"**{tgl_panjang(p['mulai'])} - {tgl_panjang(p['selesai'])}**", "", f"## {nama}", "", "### Pekerjaan"]
    for hari in data["pekerjaan"]:
        out.append(f"\n#### {tgl_panjang(hari['tanggal'])}")
        for n, t in enumerate(hari["tasks"], 1):
            out.append(f"{n}. {t['judul']}")
            out.extend(item_md(i) for i in t["items"])
    out.append("\n### Hasil pekerjaan")
    for n, h in enumerate(data["hasil"], 1):
        if n > 1:
            out.append(SEP)
        out += [f"**{n}. {h['judul']}**", h["isi"], ""]
    out.append("### Progres")
    no, huruf, last_on = 1, 0, False
    for k in sorted(data["progres"], key=lambda k: bool(k.get("on_process"))):
        if k.get("on_process") and not last_on:
            out.append("\n**DALAM PROSES (On Process)**")
            last_on = True
        out.append(f"\n**{chr(65 + huruf)}. {k['kategori']} ({len(k['tasks'])} task)**")
        huruf += 1
        for t in k["tasks"]:
            out.append(f"{no}. {t['judul']} ({t['tanggal']})")
            for i in t["items"]:
                if "links" in i:
                    out.append(f"{i['label']}:")
                    out.extend(f"   * {l['label']}: {l['url']}" if l.get("label") else f"   * {l['url']}" for l in i["links"])
                else:
                    out.append(f"{i['label']}: {i['text']}")
            no += 1
        out.append(SEP)
    total, done, on = ringkasan(data)
    out += ["**Ringkasan**", f"Total Task: {total}", f"Selesai: {done} task",
            f"On Process: {len(on)} task" + (f" ({', '.join(t['judul'] for t in on)})" if on else ""),
            "", "### Kendala", data.get("kendala", ""), "", "### Solusi", data.get("solusi", ""),
            "", "### Pertanyaan", data.get("pertanyaan", ""), ""]
    return "\n".join(out)


def main():
    src, outdir = Path(sys.argv[1]), Path(sys.argv[2])
    data = json.loads(src.read_text(encoding="utf-8"))
    # Tandai task on-process dari kategori on_process agar Ringkasan menghitung benar.
    for k in data["progres"]:
        for t in k["tasks"]:
            t.setdefault("status_kategori", "on_process" if k.get("on_process") else "selesai")
    outdir.mkdir(parents=True, exist_ok=True)
    base = f"Weekly-Report_{data['periode']['mulai']}_{data['periode']['selesai']}"
    (outdir / f"{base}.html").write_text(render_html(data), encoding="utf-8")
    (outdir / f"{base}.md").write_text(render_md(data), encoding="utf-8")
    total, done, on = ringkasan(data)
    print(f"OK {outdir / base}.html|.md  — {total} task, {done} selesai, {len(on)} on process")


if __name__ == "__main__":
    main()
