import sys, base64, json, pathlib
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools import subset

SRC = pathlib.Path(sys.argv[1])
OUT = pathlib.Path(sys.argv[2])
OUT.mkdir(parents=True, exist_ok=True)

CHARS = (
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "abcdefghijklmnopqrstuvwxyz"
    "0123456789"
    " .,:;!?'\"/\\|()[]{}<>-_=+*&@#%$"
    "·—–°ºª"
    "ÀÁÂÃÇÉÊÍÓÔÕÚÜ"
    "àáâãçéêíóôõúü"
    "→▸•"
)

def make(font, name):
    opts = subset.Options()
    opts.layout_features = ["kern", "liga"]
    opts.desubroutinize = True
    opts.notdef_outline = False
    opts.recalc_bounds = True
    opts.drop_tables += ["DSIG"]
    s = subset.Subsetter(options=opts)
    s.populate(text=CHARS)
    s.subset(font)
    font.flavor = "woff2"
    p = OUT / f"{name}.woff2"
    font.save(str(p))
    b = base64.b64encode(p.read_bytes()).decode()
    print(f"{name:22s} {p.stat().st_size:6d} bytes  ->  b64 {len(b)}")
    return b

res = {}
for weight, label in ((300, "PlexSans-300"), (400, "PlexSans-400"), (600, "PlexSans-600")):
    f = TTFont(str(SRC / "PlexSans-var.ttf"))
    f = instancer.instantiateVariableFont(f, {"wght": weight, "wdth": 100}, inplace=True)
    res[label] = make(f, label)

for fn, label in (("PlexMono-Regular.ttf", "PlexMono-400"), ("PlexMono-SemiBold.ttf", "PlexMono-600")):
    res[label] = make(TTFont(str(SRC / fn)), label)

(OUT / "fonts.json").write_text(json.dumps(res), encoding="utf-8")
print("\ntotal base64:", sum(len(v) for v in res.values()), "chars")
