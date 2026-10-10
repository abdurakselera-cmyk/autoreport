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
URL = re.compile(r"(https?://[^\s<>\"]+)")

# Gaya inline disalin dari export HTML minggu sebelumnya di Google Doc (28 Sep–3 Okt 2026),
# supaya hasil tempel identik: ukuran font, tebal, perataan, lebar kolom, dan garis tabel.
F = "font-family:Arial;color:#000000;font-style:normal;text-decoration:none"
S_PERIODE_H = "padding-top:16pt;padding-bottom:4pt;line-height:1.15;text-align:left;margin:0"
S_PERIODE = f"{F};font-size:14pt;font-weight:700"
S_ABDUR_H = "padding-top:18pt;padding-bottom:6pt;line-height:1.0;text-align:center;margin:0"
S_ABDUR = f"{F};font-size:17pt;font-weight:700"
BORDER = "border:1pt solid #000000;padding:5pt;vertical-align:top"
S_LABEL = f"{F};font-size:12pt;font-weight:700"
S_HARI_H = "padding-top:12pt;padding-bottom:2pt;line-height:1.0;text-align:left;margin:0"
S_HARI = f"{F};font-size:11pt;font-weight:700"
# Jarak paragraf meniru tampilan minggu lama: item daftar yang berurutan rapat (0pt), blok daftar dan
# paragraf biasa diberi jarak 12pt di atasnya. (Teks lama memakai contextual spacing yang tidak ikut di export.)
S_P = "padding-top:12pt;padding-bottom:0pt;line-height:1.0;text-align:left;margin:0"
S_P0 = "padding-top:0pt;padding-bottom:0pt;line-height:1.0;text-align:left;margin:0"
S_LI = "padding-top:12pt;padding-bottom:0pt;line-height:1.0;text-align:left;margin:0"
S_LI0 = "padding-top:0pt;padding-bottom:0pt;line-height:1.0;text-align:left;margin:0"
S_B12 = f"{F};font-size:12pt;font-weight:700"
S_N12 = f"{F};font-size:12pt;font-weight:400"
S_N11 = f"{F};font-size:11pt;font-weight:400"
S_LINK = "color:#1155cc;text-decoration:underline"


def tgl_panjang(iso):
    d = dt.date.fromisoformat(iso)
    return f"{HARI[d.weekday()]}, {d.day} {BULAN[d.month - 1]} {d.year}"


def span(text, style):
    """Teks dalam span bergaya; URL di dalamnya jadi link biru bergaris bawah."""
    out, last = [], 0
    for m in URL.finditer(text):
        if m.start() > last:
            out.append(f'<span style="{style}">{html.escape(text[last:m.start()])}</span>')
        u = m.group(1)
        out.append(f'<span style="{style}"><a href="{html.escape(u)}" style="{S_LINK}">{html.escape(u)}</a></span>')
        last = m.end()
    if last < len(text):
        out.append(f'<span style="{style}">{html.escape(text[last:])}</span>')
    return "".join(out)


def link_text(l):
    return f"{l['label']}: {l['url']}" if l.get("label") else l["url"]


def li_item(item):
    """Sub-bullet Pekerjaan (○): label tebal + isi normal 12pt; daftar link jadi sub-sub bullet (■)."""
    label = span(f"{item['label']}: ", S_B12) if item.get("label") else ""
    if "links" in item:
        sub = "".join(f'<li style="{S_LI0}">{span(link_text(l), S_N12)}</li>' for l in item["links"])
        return f'<li style="{S_LI0}">{label}<ul style="list-style-type:square;margin:0">{sub}</ul></li>'
    return f'<li style="{S_LI0}">{label}{span(item.get("text", ""), S_N12)}</li>'


def item_md(item, indent="   "):
    label = f"{item['label']}: " if item.get("label") else ""
    if "links" in item:
        lines = [f"{indent}* {label}".rstrip()]
        lines += [f"{indent}   * {link_text(l)}" for l in item["links"]]
        return "\n".join(lines)
    return f"{indent}* {label}{item.get('text', '')}"


def ringkasan(data):
    tasks = [t for k in data["progres"] for t in k["tasks"]]
    on = [t for t in tasks if t.get("status_kategori") == "on_process"]
    return len(tasks), len(tasks) - len(on), on


def on_process_text(on):
    return f"{len(on)} task" + (f" ({', '.join(t['judul'] for t in on)})" if on else "")


def progres_urut(data):
    """Kategori selesai dulu, lalu kategori on process (di bawah judul DALAM PROSES)."""
    return sorted(data["progres"], key=lambda k: bool(k.get("on_process")))


def task_lines(t):
    lines = [f"{t['judul']} ({t['tanggal']})"]
    for i in t["items"]:
        if "links" in i:
            lines.append(f"{i['label']}:")
            lines += [link_text(l) for l in i["links"]]
        else:
            lines.append(f"{i['label']}: {i['text']}")
    return lines


def render_html(data):
    nama = data.get("nama", "Abdur")
    p = data["periode"]
    periode = f"{tgl_panjang(p['mulai'])} - {tgl_panjang(p['selesai'])}"

    # Pekerjaan: H4 per hari → daftar bernomor (judul tebal 12pt) → bullet ○ (label tebal + isi 12pt)
    pk = []
    for hari in data["pekerjaan"]:
        pk.append(f'<h4 style="{S_HARI_H}">{span(tgl_panjang(hari["tanggal"]), S_HARI)}</h4>')
        pk.append('<ol style="margin:0">')
        for n, t in enumerate(hari["tasks"]):
            subs = "".join(li_item(i) for i in t["items"])
            pk.append(f'<li style="{S_LI if n == 0 else S_LI0}">{span(t["judul"], S_B12)}'
                      f'<ul style="list-style-type:circle;margin:0">{subs}</ul></li>')
        pk.append("</ol>")

    # Hasil pekerjaan: judul bernomor (11pt normal) lalu satu paragraf, tanpa garis pemisah
    hs = []
    for n, h in enumerate(data["hasil"], 1):
        hs.append(f'<ol start="{n}" style="margin:0"><li style="{S_LI}">{span(h["judul"], S_N11)}</li></ol>')
        hs.append(f'<p style="{S_P}">{span(h["isi"], S_N11)}</p>')

    # Progres: kategori = paragraf biasa; tiap task = satu item bernomor (nomor berlanjut) dengan baris <br>
    pr, no, last_on = [], 1, False
    for huruf, k in enumerate(progres_urut(data)):
        if k.get("on_process") and not last_on:
            pr.append(f'<p style="{S_P}">{span("DALAM PROSES (On Process)", S_N11)}</p>')
            last_on = True
        judul_k = f"{chr(65 + huruf)}. {k['kategori']} ({len(k['tasks'])} task)"
        pr.append(f'<p style="{S_P}">{span(judul_k, S_N11)}</p><ol start="{no}" style="margin:0">')
        for n, t in enumerate(k["tasks"]):
            pr.append(f'<li style="{S_LI if n == 0 else S_LI0}">' + "<br>".join(span(x, S_N11) for x in task_lines(t)) + "</li>")
            no += 1
        pr.append("</ol>")
    total, done, on = ringkasan(data)
    pr.append(f'<p style="{S_P}">{span("Ringkasan", S_N11)}</p>')
    pr.append(f'<p style="{S_P}">' + "<br>".join(span(x, S_N11) for x in (
        f"Total Task: {total}", f"Selesai: {done} task", f"On Process: {on_process_text(on)}")) + "</p>")

    def isi_bebas(teks, bullet):
        isi = span(teks, S_N11) if teks else "&nbsp;"
        if bullet:
            return f'<ul style="margin:0"><li style="{S_LI0}">{isi}</li></ul>'
        return f'<p style="{S_P0}">{isi}</p>'

    def row(label, body):
        return (f'<tr style="height:0pt"><td style="{BORDER};width:147.8pt"><p style="{S_P0}">{span(label, S_LABEL)}</p></td>'
                f'<td style="{BORDER};width:320.2pt">{body}</td></tr>')

    return f"""<!doctype html>
<html lang="id"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Weekly Journal {html.escape(nama)}</title>
<style>
/* Lebar render harus pas 468pt: Docs memakai lebar/tinggi hasil render saat menempel. */
body {{ background:#ffffff; color:#000000; font-family:Arial, sans-serif; margin:24px; }}
.hint {{ color:#5f6368; font-size:9pt; }}
#paste table {{ width:468pt; table-layout:fixed; }}
#paste td {{ overflow-wrap:anywhere; }}
</style></head><body>
<p class="hint">Blok di bawah ini yang disalin ke Google Doc journal (lihat SKILL.md langkah 6).</p>
<div id="paste">
<h3 style="{S_PERIODE_H}">{span(periode, S_PERIODE)}</h3>
<table style="border-collapse:collapse;border-spacing:0;margin-right:auto">
<colgroup><col style="width:147.8pt"><col style="width:320.2pt"></colgroup>
<tr style="height:29.6pt"><td colspan="2" style="{BORDER};width:468pt"><h2 style="{S_ABDUR_H}">{span(nama, S_ABDUR)}</h2></td></tr>
{row("Pekerjaan", "".join(pk))}
{row("Hasil pekerjaan", "".join(hs))}
{row("Progres", "".join(pr))}
{row("Kendala", isi_bebas(data.get("kendala", ""), False))}
{row("Solusi", isi_bebas(data.get("solusi", ""), True))}
{row("Pertanyaan", isi_bebas(data.get("pertanyaan", ""), True))}
</table>
</div>
</body></html>
"""


def render_md(data):
    nama = data.get("nama", "Abdur")
    p = data["periode"]
    out = [f"### {tgl_panjang(p['mulai'])} - {tgl_panjang(p['selesai'])}", "", f"## {nama}", "", "**Pekerjaan**"]
    for hari in data["pekerjaan"]:
        out.append(f"\n#### {tgl_panjang(hari['tanggal'])}")
        for n, t in enumerate(hari["tasks"], 1):
            out.append(f"{n}. **{t['judul']}**")
            out.extend(item_md(i) for i in t["items"])
    out.append("\n**Hasil pekerjaan**\n")
    for n, h in enumerate(data["hasil"], 1):
        out += [f"{n}. {h['judul']}", h["isi"], ""]
    out.append("**Progres**\n")
    no, last_on = 1, False
    for huruf, k in enumerate(progres_urut(data)):
        if k.get("on_process") and not last_on:
            out.append("DALAM PROSES (On Process)")
            last_on = True
        out.append(f"{chr(65 + huruf)}. {k['kategori']} ({len(k['tasks'])} task)")
        for t in k["tasks"]:
            lines = task_lines(t)
            out.append(f"{no}. {lines[0]}")
            out += [f"   {x}" for x in lines[1:]]
            no += 1
    total, done, on = ringkasan(data)
    out += ["Ringkasan", f"Total Task: {total}", f"Selesai: {done} task", f"On Process: {on_process_text(on)}",
            "", "**Kendala**", data.get("kendala", ""), "", "**Solusi**", data.get("solusi", ""),
            "", "**Pertanyaan**", data.get("pertanyaan", ""), ""]
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
