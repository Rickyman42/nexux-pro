"""
Plano 14 — el cierre del anuncio. 5 segundos.

v2: el bloque se centra como grupo. En la v1 el QR y el texto quedaban pegados a
la izquierda y sobraba un tercio de pantalla a la derecha.

Paleta y tipografias de la web de nexux.pro. El QR apunta a nexux.pro/demo, el
mismo del flyer, y se lee con un lector real antes de dar nada por bueno.
"""
import segno
import zxingcpp
from PIL import Image, ImageDraw, ImageFont

W, H = 1280, 720
FONDO = (247, 246, 243)
TINTA = (20, 22, 26)
TEAL = (42, 139, 132)
SUAVE = (122, 128, 125)
LINEA = (223, 222, 215)

URL = "https://nexux.pro/demo"
F = "/home/nexux/.local/share/fonts/"
SERIF, GEIST, GEIST_SB = F + "InstrumentSerif-Regular.ttf", F + "Geist-1.ttf", F + "Geist-2.ttf"
fn = lambda r, t: ImageFont.truetype(r, t)

# --- QR ---
segno.make(URL, error="h").save("/tmp/qr.png", scale=14, border=2,
                                dark="#14161A", light="#FFFFFF")
LADO, AIRE = 300, 18
qr_img = Image.open("/tmp/qr.png").convert("RGB").resize((LADO, LADO), Image.LANCZOS)

# --- medir el texto para poder centrar el grupo ---
card = Image.new("RGB", (W, H), FONDO)
d = ImageDraw.Draw(card)

lineas = [
    ("nexux.pro", fn(SERIF, 92), TINTA, 108),
    ("Recepcionista IA", fn(GEIST_SB, 30), TINTA, 42),
    ("29 € al mes · sin comisiones · sin permanencia", fn(GEIST, 25), SUAVE, 52),
    ("Escanea y pruébala sin registrarte", fn(GEIST_SB, 26), TEAL, 0),
]
ancho_texto = max(d.textlength(t, font=f) for t, f, _, _ in lineas)

CAJA = LADO + AIRE * 2          # el marco blanco del QR
SEPAR = 92                      # aire entre QR y texto
total = CAJA + SEPAR + ancho_texto
x0 = (W - total) / 2            # <- el grupo, centrado

QX, QY = x0 + AIRE, (H - LADO) // 2
d.rounded_rectangle([QX - AIRE, QY - AIRE, QX + LADO + AIRE, QY + LADO + AIRE],
                    radius=10, fill=(255, 255, 255))
card.paste(qr_img, (int(QX), int(QY)))

TX = x0 + CAJA + SEPAR
d.line([(TX - 46, QY + 14), (TX - 46, QY + LADO - 14)], fill=LINEA, width=1)

y = QY + 24
for texto, f, color, salto in lineas:
    d.text((TX, y), texto, font=f, fill=color)
    y += salto

card.save("/tmp/cierre.png")
print("tarjeta v2 compuesta, bloque centrado")

leidos = zxingcpp.read_barcodes(Image.open("/tmp/cierre.png"))
if not leidos:
    raise SystemExit("FALLO: el QR no se puede leer")
for r in leidos:
    print("QR leido:", r.text)
    if r.text != URL:
        raise SystemExit("FALLO: apunta a %r" % r.text)
print("QR verificado con lector real")
