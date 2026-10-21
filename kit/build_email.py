"""Build The Brand Gambit assembly-pack email from an issue.json.

Usage:
  python3 build_email.py issues/<NN>/issue.json <image_base_url> <out_dir>

Writes:
  <out_dir>/preview.html  — the issue as readers will see it (email-safe tables, inline styles)
  <out_dir>/pack.html     — what gets emailed to QSHI: send checklist on top, the full issue below
  <out_dir>/pack.txt      — plain-text fallback
"""
import json, sys, html, pathlib

PAPER, CARD, INK, INK2, MUTED, LINE, RED = "#F5F4F0", "#FFFFFF", "#0C0C0C", "#3A3A38", "#8A8985", "#DEDCD6", "#E8001D"
FONT = "Outfit, 'Helvetica Neue', Helvetica, Arial, sans-serif"
MONO = "'JetBrains Mono', Menlo, Consolas, monospace"
e = html.escape

def p(text, size=17, color=INK2, weight=400, mt=0, mb=18, lh=1.65):
    return (f'<p style="margin:{mt}px 0 {mb}px;font-family:{FONT};font-size:{size}px;line-height:{lh};'
            f'color:{color};font-weight:{weight};">{text}</p>')

def label(text, color=MUTED, mb=10):
    return (f'<p style="margin:0 0 {mb}px;font-family:{MONO};font-size:11px;letter-spacing:1.6px;'
            f'text-transform:uppercase;color:{color};">{e(text)}</p>')

def img(url, alt):
    return (f'<img src="{e(url)}" alt="{e(alt)}" width="552" '
            f'style="display:block;width:100%;max-width:552px;height:auto;border:1px solid {LINE};border-radius:10px;">')

def preview(d, base):
    rows = []
    # header
    rows.append(f'''<tr><td style="padding:28px 24px 8px;">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0"><tr>
        <td style="font-family:{FONT};font-weight:600;font-size:13px;letter-spacing:2.4px;text-transform:uppercase;color:{INK};">The Brand Gambit</td>
        <td align="right" style="font-family:{MONO};font-size:11px;letter-spacing:1.4px;text-transform:uppercase;color:{MUTED};">Issue {e(d["issue_no"])}</td>
      </tr></table></td></tr>''')
    body = []
    if d.get("intro_note"):
        body.append(f'<div style="border:1px dashed #B9B7B0;border-radius:10px;padding:16px 18px;margin:0 0 26px;">'
                    + p(e(d["intro_note"]), size=15, color=INK2, mb=0, lh=1.6) + '</div>')
    body.append(img(f'{base}/cover.jpg', d["cover_alt"]))
    body.append(f'<h1 style="margin:30px 0 18px;font-family:{FONT};font-size:30px;line-height:1.2;font-weight:700;letter-spacing:-0.5px;color:{INK};">{e(d["headline"])}</h1>')
    body += [p(e(x)) for x in d["lead_before_diagram"]]
    body.append('<div style="margin:8px 0 26px;">' + img(f'{base}/diagram.jpg', d["diagram_alt"]) + '</div>')
    body += [p(e(x)) for x in d["lead_after_diagram"]]
    body.append(f'<h2 style="margin:34px 0 14px;font-family:{FONT};font-size:22px;line-height:1.25;font-weight:600;color:{INK};">{e(d["section_title"])}</h2>')
    body.append(p(e(d["section_intro"])))
    for i, s in enumerate(d["steps"], 1):
        body.append(f'''<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 12px;background:{CARD};border:1px solid {LINE};border-radius:10px;"><tr>
          <td valign="top" width="44" style="padding:16px 0 16px 18px;font-family:{MONO};font-size:12px;color:{MUTED};">0{i}</td>
          <td style="padding:14px 18px 14px 4px;font-family:{FONT};font-size:16px;line-height:1.55;color:{INK2};"><b style="color:{INK};font-weight:600;">{e(s["title"])}</b> {e(s["body"])}</td></tr></table>''')
    body.append(p(f'<b style="font-weight:600;">{e(d["closer"])}</b>', size=19, color=INK, mt=22, mb=8))
    srcs = " · ".join(f'<a href="{e(s["url"])}" style="color:{MUTED};">{e(s["name"])}</a>' for s in d["lead_sources"])
    body.append(f'<p style="margin:0 0 34px;font-family:{MONO};font-size:11px;letter-spacing:1px;color:{MUTED};">SOURCE: {srcs} · company-reported figures</p>')
    # short takes
    body.append(f'<div style="border-top:1.5px solid {INK};padding-top:22px;">' + label("Also this week", INK, 16) + '</div>')
    for t in d["short_takes"]:
        body.append(f'''<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 18px;"><tr>
          <td valign="top" width="112" style="padding:2px 14px 0 0;font-family:{FONT};font-size:26px;font-weight:700;letter-spacing:-0.5px;color:{INK};white-space:nowrap;">{e(t["stat"])}</td>
          <td valign="top" style="font-family:{FONT};font-size:15px;line-height:1.6;color:{INK2};">
            <b style="color:{INK};font-weight:600;">{e(t["name"])}.</b> {e(t["body"])}
            <a href="{e(t["source_url"])}" style="color:{MUTED};font-size:13px;">{e(t["source_name"])} &rarr;</a></td></tr></table>''')
    # question
    body.append(f'''<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:18px 0 26px;background:{INK};border-radius:12px;"><tr><td style="padding:24px 24px;">
      <p style="margin:0 0 10px;font-family:{MONO};font-size:11px;letter-spacing:1.6px;text-transform:uppercase;color:#BDBBB5;"><span style="color:{RED};">&#9679;</span>&nbsp; One question</p>
      <p style="margin:0;font-family:{FONT};font-size:19px;line-height:1.45;color:{PAPER};font-weight:500;">{e(d["question"])}</p></td></tr></table>''')
    body.append(p(f'{e(d["studio_line"])} <a href="https://kushigrafixx.in" style="color:{INK};font-weight:600;">kushigrafixx.in &rarr;</a>', size=15))
    body.append(p(f'See you next Saturday,<br><b style="color:{INK};font-weight:600;">{e(d["signoff_name"])}</b><br><span style="color:{MUTED};font-size:14px;">{e(d["signoff_title"])}</span>', size=16, mt=10, mb=0))
    rows.append(f'<tr><td style="padding:16px 24px 36px;">{"".join(body)}</td></tr>')
    return (f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:{PAPER};"><tr><td align="center">'
            f'<table role="presentation" width="600" cellpadding="0" cellspacing="0" style="width:100%;max-width:600px;background:{PAPER};">'
            + "".join(rows) + '</table></td></tr></table>')

def pack(d, base, issue_html):
    li = lambda t: f'<li style="margin:0 0 8px;">{t}</li>'
    steps = "".join([
        li(f'<b>Subject:</b> {e(d["subject"])}'),
        li(f'<b>Preview text:</b> {e(d["preview_text"])}'),
        li(f'<b>Images:</b> <a href="{e(base)}/cover.jpg">cover.jpg</a> and <a href="{e(base)}/diagram.jpg">diagram.jpg</a> (open, then save to your computer)'),
        li('In beehiiv: <b>Posts → New post</b> using your <b>Brand Gambit Weekly</b> template. Set the subject and preview text.'),
        li('Copy the issue below the line, section by section, into the editor. Replace each image with the downloaded file.'),
        li(f'Schedule for <b>{e(d["send_date"])}, 9:00 AM IST</b>. Send yourself a test first.'),
    ])
    check = (f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:{CARD};border:1px solid {LINE};border-radius:12px;"><tr><td style="padding:22px 24px;">'
             + label(f'Assembly pack · Issue {d["issue_no"]} · for {d["send_date"]}', RED, 12)
             + f'<ol style="margin:0;padding-left:20px;font-family:{FONT};font-size:15px;line-height:1.55;color:{INK2};">{steps}</ol>'
             + p('About 10 minutes. The issue below is exactly what subscribers should see.', size=13, color=MUTED, mt=14, mb=0)
             + (p(e(d["pack_note"]), size=14, color=INK, mt=14, mb=0) if d.get("pack_note") else '')
             + '</td></tr></table>')
    divider = (f'<p style="margin:28px 0 0;text-align:center;font-family:{MONO};font-size:11px;letter-spacing:2px;color:{MUTED};">'
               '&mdash;&mdash;&mdash;&nbsp; ISSUE STARTS BELOW &nbsp;&mdash;&mdash;&mdash;</p>')
    return (f'<div style="background:{PAPER};padding:24px 12px;"><div style="max-width:600px;margin:0 auto;">'
            f'{check}{divider}</div>{issue_html}</div>')

def text_version(d, base):
    out = ([d["pack_note"], ""] if d.get("pack_note") else []) + [f"ASSEMBLY PACK - Issue {d['issue_no']} - send {d['send_date']} 9:00 AM IST",
           f"Subject: {d['subject']}", f"Preview: {d['preview_text']}",
           f"Cover: {base}/cover.jpg", f"Diagram: {base}/diagram.jpg", "", "----", ""]
    if d.get("intro_note"): out += [d["intro_note"], ""]
    out += ["[COVER IMAGE]", "", d["headline"], ""] + d["lead_before_diagram"] + ["", "[DIAGRAM]", ""] + d["lead_after_diagram"]
    out += ["", d["section_title"], d["section_intro"]] + [f"{i}. {s['title']} {s['body']}" for i, s in enumerate(d["steps"], 1)]
    out += ["", d["closer"], "", "ALSO THIS WEEK"] + [f"{t['stat']} - {t['name']}. {t['body']} ({t['source_url']})" for t in d["short_takes"]]
    out += ["", d["question"], "", d["studio_line"] + " https://kushigrafixx.in", "", "See you next Saturday,", d["signoff_name"]]
    return "\n".join(out)

if __name__ == "__main__":
    src, base, outdir = sys.argv[1], sys.argv[2].rstrip("/"), pathlib.Path(sys.argv[3])
    d = json.loads(pathlib.Path(src).read_text())
    outdir.mkdir(parents=True, exist_ok=True)
    issue_html = preview(d, base)
    (outdir / "preview.html").write_text(issue_html)
    (outdir / "pack.html").write_text(pack(d, base, issue_html))
    (outdir / "pack.txt").write_text(text_version(d, base))
    print("built", outdir)
