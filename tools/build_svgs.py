"""Gera os SVGs da pagina de perfil usando tokens do IBM Carbon Design System v10, tema Gray 100."""
import sys, json, pathlib
from fontTools.ttLib import TTFont

SCR = pathlib.Path(sys.argv[1])
OUT = pathlib.Path(sys.argv[2])
OUT.mkdir(parents=True, exist_ok=True)
B64 = json.loads((SCR / "fonts_out" / "fonts.json").read_text(encoding="utf-8"))

# ---- Carbon v10 :: tema g100 (resolvido de @carbon/themes) -------------------
BG         = "#161616"  # ui-background / gray 100
LAYER      = "#262626"  # ui-01 / gray 90
LAYER_ACC  = "#393939"  # ui-02, ui-03 border-subtle / gray 80
BORDER_STR = "#6f6f6f"  # ui-04 border-strong / gray 60
TEXT_01    = "#f4f4f4"  # gray 10
TEXT_02    = "#c6c6c6"  # gray 30
TEXT_03    = "#6f6f6f"  # gray 60
TEXT_05    = "#8d8d8d"  # gray 50
BLUE_60    = "#0f62fe"  # interactive-01
BLUE_40    = "#78a9ff"  # link-01
GREEN_40   = "#42be65"  # support-02

# ---- medicao real pelas metricas da fonte -----------------------------------
_fonts, _cache = {}, {}
def _font(name):
    if name not in _fonts:
        f = TTFont(str(SCR / "fonts_out" / f"{name}.woff2"))
        _fonts[name] = (f.getBestCmap(), f["hmtx"], f["head"].unitsPerEm)
    return _fonts[name]

def w(text, name, size, tracking=0.0):
    key = (text, name, size, tracking)
    if key in _cache: return _cache[key]
    cmap, hmtx, upem = _font(name)
    total = 0
    for ch in text:
        g = cmap.get(ord(ch))
        total += hmtx[g][0] if g else 0
    r = total / upem * size + tracking * max(len(text) - 1, 0)
    _cache[key] = r
    return r

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

FACES = {"PlexSans-300": ("IBM Plex Sans", 300, "normal"),
         "PlexSans-400": ("IBM Plex Sans", 400, "normal"),
         "PlexSans-600": ("IBM Plex Sans", 600, "normal"),
         "PlexMono-400": ("IBM Plex Mono", 400, "normal"),
         "PlexMono-600": ("IBM Plex Mono", 600, "normal")}

def style(keys):
    out = []
    for k in keys:
        fam, wt, st = FACES[k]
        out.append(f"@font-face{{font-family:'{fam}';font-weight:{wt};font-style:{st};"
                   f"src:url(data:font/woff2;base64,{B64[k]}) format('woff2');}}")
    return "<style>" + "".join(out) + "</style>"

def txt(x, y, s, name, size, fill, tracking=0.0, anchor="start"):
    fam, wt, _ = FACES[name]
    a = f' text-anchor="{anchor}"' if anchor != "start" else ""
    t = f' letter-spacing="{tracking}"' if tracking else ""
    return (f'<text x="{x}" y="{y}" font-family="{fam}" font-weight="{wt}" '
            f'font-size="{size}" fill="{fill}"{t}{a}>{esc(s)}</text>')

def tag(x, y, label, bg=LAYER_ACC, fg=TEXT_01):
    """Carbon v10 Tag: altura 24, raio 15 (pilula), padding horizontal 8."""
    tw = w(label, "PlexSans-400", 12)
    bw = tw + 16
    return (f'<rect x="{x:.1f}" y="{y}" width="{bw:.1f}" height="24" rx="12" fill="{bg}"/>'
            + txt(round(x + 8, 1), y + 16, label, "PlexSans-400", 12, fg)), bw

def tagrow(x, y, labels, gap=8, maxx=None):
    """Dispoe tags em linha; quebra para a linha de baixo se passar de maxx."""
    parts, cx, cy, lines = [], x, y, 1
    for l in labels:
        bw = w(l, "PlexSans-400", 12) + 16
        if maxx and cx + bw > maxx and cx > x:
            cx, cy, lines = x, cy + 32, lines + 1
        s, bw = tag(cx, cy, l)
        parts.append(s); cx += bw + gap
    return "".join(parts), lines

def svg(width, height, faces, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
            f'width="{width}" height="{height}">{style(faces)}'
            f'<rect width="{width}" height="{height}" fill="{BG}"/>{body}</svg>')

M = 40          # margem (spacing-08/09)
W = 900         # largura nominal ~= largura de render do README no GitHub
CW = W - 2 * M  # largura de conteudo = 820

# ============================ HERO ==========================================
def hero(lang):
    t = {"pt": dict(eyebrow="ENGENHEIRO DE COMPUTAÇÃO",
                    sub="Sistemas de gestão de ponta a ponta — produto, dados e inteligência",
                    tags=["Full stack", "Dados e IA", "Setor público"],
                    loc="DIVINÓPOLIS / MG — BRASIL", avail="DISPONÍVEL PARA OPORTUNIDADES"),
         "en": dict(eyebrow="COMPUTER ENGINEER",
                    sub="End-to-end management systems — product, data and intelligence",
                    tags=["Full stack", "Data & AI", "Public sector"],
                    loc="DIVINÓPOLIS / BRAZIL", avail="AVAILABLE FOR OPPORTUNITIES")}[lang]
    b = []
    # linhas de grade 2x (motivo Carbon), coluna de 56px + medianiz de 16px
    for i in range(1, 16):
        x = M + i * 52
        if x < W - M:
            b.append(f'<rect x="{x}" y="0" width="1" height="312" fill="#1e1e1e"/>')
    b.append(f'<rect x="{M}" y="56" width="32" height="2" fill="{BLUE_60}"/>')
    b.append(txt(M, 84, t["eyebrow"], "PlexMono-400", 12, TEXT_03, 2.4))
    b.append(txt(M, 154, "Thiago Miranda Aboboreira", "PlexSans-300", 54, TEXT_01))
    b.append(f'<rect x="{M}" y="178" width="{CW}" height="1" fill="{LAYER_ACC}"/>')
    b.append(txt(M, 214, t["sub"], "PlexSans-400", 20, TEXT_02))
    row, _ = tagrow(M, 242, t["tags"], maxx=W - M)
    b.append(row)
    b.append(txt(M, 296, t["loc"], "PlexMono-400", 12, TEXT_03, 2.4))
    lx = M + w(t["loc"], "PlexMono-400", 12, 2.4) + 24
    b.append(f'<rect x="{lx:.1f}" y="286" width="8" height="8" fill="{GREEN_40}"/>')
    b.append(txt(round(lx + 20, 1), 296, t["avail"], "PlexMono-400", 12, TEXT_05, 2.4))
    return svg(W, 312, ["PlexSans-300", "PlexSans-400", "PlexMono-400"], "".join(b))

# ===================== ARQUITETURA DE REFERENCIA ============================
def arch(lang):
    t = {"pt": dict(label="ARQUITETURA DE REFERÊNCIA",
                    cols=[("Interface", "Angular · React", "SPA · design system"),
                          ("Aplicação", "Django · DRF · FastAPI", "regras de domínio"),
                          ("Dados", "PostgreSQL · SQL Server", "multitenancy · migrações"),
                          ("Inteligência", "pgvector · LiteLLM", "RAG · avaliação")],
                    cross="TRANSVERSAL",
                    items=[("Identidade", "SSO · OAuth2 · OIDC"), ("Assincronia", "Celery · filas"),
                           ("Empacotamento", "Docker · Compose"), ("Entrega", "GitHub Actions"),
                           ("Garantia", "testes · auditoria")]),
         "en": dict(label="REFERENCE ARCHITECTURE",
                    cols=[("Interface", "Angular · React", "SPA · design system"),
                          ("Application", "Django · DRF · FastAPI", "domain rules"),
                          ("Data", "PostgreSQL · SQL Server", "multitenancy · migrations"),
                          ("Intelligence", "pgvector · LiteLLM", "RAG · evaluation")],
                    cross="CROSS-CUTTING",
                    items=[("Identity", "SSO · OAuth2 · OIDC"), ("Async", "Celery · queues"),
                           ("Packaging", "Docker · Compose"), ("Delivery", "GitHub Actions"),
                           ("Assurance", "testing · audit")])}[lang]
    cw, gap, ch, top = 190, 20, 136, 86
    b = [f'<rect x="{M}" y="40" width="32" height="2" fill="{BLUE_60}"/>',
         txt(M, 68, t["label"], "PlexMono-400", 12, TEXT_03, 2.4)]
    for i, (title, l1, l2) in enumerate(t["cols"]):
        x = M + i * (cw + gap)
        b.append(f'<rect x="{x}" y="{top}" width="{cw}" height="{ch}" fill="{LAYER}" '
                 f'stroke="{LAYER_ACC}" stroke-width="1"/>')
        b.append(txt(x + 16, top + 32, f"0{i+1}", "PlexMono-600", 12, BLUE_40, 1.2))
        b.append(txt(x + 16, top + 66, title, "PlexSans-600", 16, TEXT_01))
        b.append(txt(x + 16, top + 92, l1, "PlexSans-400", 13, TEXT_02))
        b.append(txt(x + 16, top + 112, l2, "PlexSans-400", 13, TEXT_05))
        if i < 3:
            cx = x + cw
            b.append(f'<path d="M{cx+5} {top+ch/2} H{cx+gap-5}" stroke="{BORDER_STR}" stroke-width="1"/>')
            b.append(f'<path d="M{cx+gap-9} {top+ch/2-4} l4 4 l-4 4" fill="none" '
                     f'stroke="{BORDER_STR}" stroke-width="1"/>')
    by = top + ch + 24
    b.append(f'<rect x="{M}" y="{by}" width="{CW}" height="96" fill="{LAYER}" '
             f'stroke="{LAYER_ACC}" stroke-width="1"/>')
    b.append(txt(M + 16, by + 28, t["cross"], "PlexMono-400", 12, TEXT_03, 2.4))
    iw = CW / 5
    for i, (name, sub) in enumerate(t["items"]):
        x = M + i * iw
        if i:
            b.append(f'<rect x="{x}" y="{by+44}" width="1" height="36" fill="{LAYER_ACC}"/>')
        b.append(txt(x + 16, by + 62, name, "PlexSans-600", 13, TEXT_01))
        b.append(txt(x + 16, by + 80, sub, "PlexSans-400", 12, TEXT_05))
    return svg(W, by + 96 + 48,
               ["PlexSans-400", "PlexSans-600", "PlexMono-400", "PlexMono-600"], "".join(b))

# ================================ STACK =====================================
def stack(lang):
    rows = {"pt": [("PRODUTO", ["Angular", "React", "TypeScript", "Tailwind", "ng-zorro", "design system"]),
                   ("BACKEND", ["Django", "DRF", "FastAPI", "Celery", "OAuth2 / OIDC", "REST"]),
                   ("DADOS",   ["PostgreSQL", "SQL Server", "T-SQL", "pgvector", "multitenancy"]),
                   ("IA",      ["RAG", "LiteLLM", "Ollama", "DSPy", "TensorFlow", "Keras"]),
                   ("INFRA",   ["Docker", "Compose", "Oracle Cloud", "GitHub Actions", "nginx"])],
            "en": [("PRODUCT", ["Angular", "React", "TypeScript", "Tailwind", "ng-zorro", "design system"]),
                   ("BACKEND", ["Django", "DRF", "FastAPI", "Celery", "OAuth2 / OIDC", "REST"]),
                   ("DATA",    ["PostgreSQL", "SQL Server", "T-SQL", "pgvector", "multitenancy"]),
                   ("AI",      ["RAG", "LiteLLM", "Ollama", "DSPy", "TensorFlow", "Keras"]),
                   ("INFRA",   ["Docker", "Compose", "Oracle Cloud", "GitHub Actions", "nginx"])]}[lang]
    lx, tx, rh, top = M, M + 132, 56, 44
    b = []
    for i, (label, tags) in enumerate(rows):
        y = top + i * rh
        if i:
            b.append(f'<rect x="{M}" y="{y-16}" width="{CW}" height="1" fill="{LAYER_ACC}"/>')
        b.append(txt(lx, y + 17, label, "PlexMono-600", 12, TEXT_05, 2.4))
        row, lines = tagrow(tx, y, tags, maxx=W - M)
        b.append(row)
        if lines > 1: print(f"  AVISO: linha {label} quebrou em {lines} linhas")
    return svg(W, top + len(rows) * rh - 16 + 32,
               ["PlexSans-400", "PlexMono-600"], "".join(b))

for lang, suf in (("pt", ""), ("en", "-en")):
    for fn, base in ((hero, "hero"), (arch, "arquitetura"), (stack, "stack")):
        p = OUT / f"{base}{suf}.svg"
        p.write_text(fn(lang), encoding="utf-8")
        print(f"{p.name:24s} {p.stat().st_size//1024:4d} KB")
