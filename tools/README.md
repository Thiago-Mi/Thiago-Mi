# Geração dos gráficos

Os três SVGs em `../assets/` não são desenhados à mão: são gerados a partir dos tokens
do **IBM Carbon Design System v10**, tema Gray 100, com tipografia **IBM Plex** embutida
como subset WOFF2 em base64 (sem isso o GitHub cairia em fonte de fallback, já que a
renderização de SVG como imagem não carrega fonte externa).

## Regerar

```bash
mkdir -p build/fonts_dl && cd build/fonts_dl
curl -sLO "https://raw.githubusercontent.com/google/fonts/main/ofl/ibmplexsans/IBMPlexSans%5Bwdth,wght%5D.ttf"
curl -sLO "https://raw.githubusercontent.com/google/fonts/main/ofl/ibmplexmono/IBMPlexMono-Regular.ttf"
curl -sLO "https://raw.githubusercontent.com/google/fonts/main/ofl/ibmplexmono/IBMPlexMono-SemiBold.ttf"
cd ../.. && mv build/fonts_dl/IBMPlexSans*.ttf build/fonts_dl/PlexSans-var.ttf
python tools/mkfonts.py build/fonts_dl build/fonts_out
python tools/build_svgs.py build assets
```

`mkfonts.py` instancia a fonte variável nos três pesos do Carbon (Light 300, Regular 400,
SemiBold 600), reduz cada uma ao conjunto de caracteres usado e devolve base64.
`build_svgs.py` mede o texto pelas métricas reais da fonte — é assim que as pílulas de tag
saem com a largura exata — e escreve os seis SVGs (pt + en).

Requer `fonttools` e `brotli`.

## Por que largura nominal de 900px

O GitHub renderiza o README numa coluna de aproximadamente 830px. Desenhar a 1200px faria
o texto de 12px chegar ao leitor com 8px. A 900px a redução é de apenas 8%, e a escala
tipográfica do Carbon chega praticamente intacta.

## Licenças

- IBM Carbon Design System — Apache 2.0
- IBM Plex — SIL Open Font License 1.1 (permite embutir subsets)
