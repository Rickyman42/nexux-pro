from pathlib import Path
import importlib.util
import shutil
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
TMP = ROOT / "tmp" / "publicidad"
OUT = ROOT / "output" / "publicidad" / "a4-duplex-3-variantes"
PDF_OUT = ROOT / "output" / "pdf"
OUT.mkdir(parents=True, exist_ok=True)
PDF_OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(TMP / "deps"))

from PIL import Image, ImageDraw, ImageFilter, ImageOps
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader

spec = importlib.util.spec_from_file_location("flyer_base", TMP / "crear_flyer_doble_cara.py")
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)

DPI = 300

# Cada variante lleva su propio QR. Antes las tres apuntaban a /demo a secas, asi que una
# visita desde el papel era indistinguible de cualquier otra y no habia forma de saber que
# octavilla funcionaba. Ahora pasan por nexux.pro/f/<codigo>, que redirige a la demo
# etiquetando la visita. Los codigos son cortos a proposito: cuanto menos texto lleva un QR,
# mas grandes quedan sus cuadros y mejor se lee en la calle y con el papel doblado.
import qrcode as _qrcode

QR_URL = "https://nexux.pro/demo"


def qr_variante(size=205):
    code = _qrcode.QRCode(error_correction=_qrcode.constants.ERROR_CORRECT_H, box_size=14, border=4)
    code.add_data(QR_URL)
    code.make(fit=True)
    img = code.make_image(fill_color="black", back_color="white").convert("RGB")
    return img.resize((size, size), Image.Resampling.NEAREST)


def px(mm):
    return round(mm / 25.4 * DPI)


# A4 4-up profesional para impresoras digitales con margen no imprimible.
# Folleto final: 93 x 136 mm. Sangre individual: 3 mm. Arte: 99 x 142 mm.
PAGE_W, PAGE_H = px(210), px(297)
ART_W, ART_H = px(99), px(142)
BLEED = px(3)
SAFE = px(5)
CONTENT = BLEED + SAFE
MX, MY = px(4), px(4)
GX, GY = px(4), px(5)
POSITIONS = [
    (MX, MY),
    (MX + ART_W + GX, MY),
    (MX, MY + ART_H + GY),
    (MX + ART_W + GX, MY + ART_H + GY),
]

TEAL = "#49CAC3"
TEAL_DARK = "#087E78"
INK = "#111519"
NAVY = "#071116"
CREAM = "#F5F1EA"
WHITE = "#FFFFFF"
GREY = "#656A70"
LINE = "#D8D5CF"


def bold(size):
    return base.bold(size)


def sans(size):
    return base.sans(size)


def serif(size):
    return base.serif(size)


def serif_italic(size):
    return base.serif_italic(size)


def brand(draw, dark=False):
    base.brand(draw, CONTENT, CONTENT - 9, dark=dark, )


def add_atmosphere(image, ellipse, color=(40, 214, 201, 65)):
    layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    ImageDraw.Draw(layer).ellipse(ellipse, fill=color)
    return Image.alpha_composite(image, layer.filter(ImageFilter.GaussianBlur(85)))


def add_shadow(image, box, alpha=40):
    return base.add_shadow(image, box, radius=24, blur=16, alpha=alpha)


# El QR es la unica accion de toda la octavilla y competia en tamano con el logo. En papel
# repartido en mano tiene que ser lo segundo que se ve, despues del titular. El numero vivia
# repetido en la funcion y en cada llamada, asi que agrandarlo descuadraba las posiciones.
QR_SIZE = 258


def paste_qr(image, x, y, dark=False):
    draw = ImageDraw.Draw(image)
    size = QR_SIZE
    draw.rounded_rectangle((x - 11, y - 11, x + size + 11, y + size + 11), radius=17, fill=WHITE, outline=LINE, width=2)
    image.paste(qr_variante(size), (x, y))
    draw.text((x + size // 2, y + size + 31), "HABLA CON LARA AHORA", font=bold(15), fill=WHITE if dark else INK, anchor="mm")
    draw.text((x + size // 2, y + size + 56), "Tarda 30 segundos · nexux.pro", font=bold(12), fill=TEAL if dark else TEAL_DARK, anchor="mm")


def footer(image, dark, y=1390):
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((CONTENT, y, CONTENT + 250, y + 72), radius=36, fill=TEAL if dark else INK)
    draw.text((CONTENT + 125, y + 36), "29 €/mes", font=bold(26), fill=INK if dark else WHITE, anchor="mm")
    draw.text((CONTENT, y + 98), "WhatsApp · Telegram · Web", font=bold(16), fill=WHITE if dark else INK)
    draw.text((CONTENT, y + 128), "Sin comisiones por cita", font=sans(14), fill="#D7E0E2" if dark else GREY)
    paste_qr(image, ART_W - CONTENT - QR_SIZE, y - 5, dark=dark)


def chat_card(image, box):
    x1, y1, x2, y2 = box
    image = add_shadow(image, box, 55)
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle(box, radius=27, fill="#FBFAF8")
    draw.rounded_rectangle((x1, y1, x2, y1 + 63), radius=27, fill="#0C867E")
    draw.rectangle((x1, y1 + 38, x2, y1 + 63), fill="#0C867E")
    draw.ellipse((x1 + 24, y1 + 11, x1 + 66, y1 + 53), fill=TEAL)
    draw.text((x1 + 45, y1 + 32), "L", font=bold(17), fill=INK, anchor="mm")
    draw.text((x1 + 82, y1 + 12), "Lara · Recepcionista IA", font=bold(15), fill=WHITE)
    draw.text((x1 + 82, y1 + 36), "Responde mientras trabajas", font=sans(11), fill="#D3F5F2")
    incoming = (x1 + 28, y1 + 100, x2 - 110, y1 + 185)
    draw.rounded_rectangle(incoming, radius=18, fill="#ECE9E4")
    draw.text((incoming[0] + 20, incoming[1] + 14), "Cliente", font=bold(11), fill=GREY)
    draw.text((incoming[0] + 20, incoming[1] + 42), "Hola, ¿tenéis cita mañana?", font=bold(17), fill=INK)
    outgoing = (x1 + 105, y1 + 220, x2 - 28, y2 - 30)
    draw.rounded_rectangle(outgoing, radius=18, fill="#D9F7F3")
    draw.text((outgoing[0] + 20, outgoing[1] + 14), "Lara", font=bold(11), fill=TEAL_DARK)
    draw.text((outgoing[0] + 20, outgoing[1] + 43), "Sí. Tengo libre a las 17:30.", font=sans(16), fill=INK)
    draw.text((outgoing[0] + 20, outgoing[1] + 72), "¿Te la reservo?", font=sans(16), fill=INK)
    return image


def agenda_panel(image, box):
    x1, y1, x2, y2 = box
    image = add_shadow(image, box, 52)
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle(box, radius=24, fill=WHITE)
    draw.text((x1 + 25, y1 + 26), "AGENDA", font=bold(12), fill=TEAL_DARK)
    draw.text((x1 + 25, y1 + 56), "Miércoles 26", font=bold(19), fill=INK)
    draw.line((x1 + 23, y1 + 96, x2 - 23, y1 + 96), fill=LINE, width=2)
    draw.text((x1 + 25, y1 + 132), "16:30", font=bold(14), fill=GREY)
    apt = (x1 + 23, y1 + 172, x2 - 23, y1 + 300)
    draw.rounded_rectangle(apt, radius=16, fill="#DDF7F4", outline=TEAL, width=3)
    draw.text((apt[0] + 20, apt[1] + 20), "17:30", font=bold(16), fill=TEAL_DARK)
    draw.text((apt[0] + 20, apt[1] + 52), "Nueva cita", font=bold(19), fill=INK)
    draw.text((apt[0] + 20, apt[1] + 85), "Confirmada por Lara", font=sans(12), fill=GREY)
    draw.text((x1 + 25, y1 + 338), "18:00", font=bold(14), fill=GREY)
    return image


def agenda_real(image, box, caption):
    x1, y1, x2, y2 = box
    image = add_shadow(image, box, 28)
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle(box, radius=21, fill=WHITE, outline=LINE, width=2)
    source = Image.open(ROOT / "public" / "img" / "crm-agenda-real.webp").convert("RGB")
    source = source.crop((850, 480, 2600, 1130))
    target = (x2 - x1 - 32, y2 - y1 - 54)
    source = ImageOps.fit(source, target, Image.Resampling.LANCZOS)
    source = source.convert("RGBA")
    source.putalpha(base.rounded_mask(source.size, 13))
    image.paste(source, (x1 + 16, y1 + 16), source)
    ImageDraw.Draw(image).text((x1 + 17, y2 - 29), caption, font=bold(11), fill=GREY)
    return image


def variant_1_front():
    image = add_atmosphere(Image.new("RGBA", (ART_W, ART_H), NAVY), (500, -210, 1300, 590))
    draw = ImageDraw.Draw(image)
    brand(draw, True)
    draw.text((CONTENT, 180), "TU CLIENTE NO SABE", font=bold(48), fill=WHITE)
    draw.text((CONTENT, 238), "QUE ESTÁS TRABAJANDO.", font=bold(48), fill=WHITE)
    draw.text((CONTENT, 314), "Solo sabe que", font=serif(39), fill=WHITE)
    draw.text((330, 304), "nadie le contestó.", font=serif_italic(41), fill=TEAL)
    draw.text((CONTENT, 382), "Lara responde y convierte el mensaje en una cita.", font=sans(20), fill="#D8E1E3")
    image = chat_card(image, (CONTENT, 475, 675, 930))
    draw = ImageDraw.Draw(image)
    draw.line((695, 715, 765, 715), fill=TEAL, width=7)
    draw.polygon([(765, 700), (795, 715), (765, 730)], fill=TEAL)
    image = agenda_panel(image, (785, 545, ART_W - CONTENT, 1008))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((745, 975, ART_W - CONTENT, 1045), radius=35, fill=TEAL)
    draw.text((910, 1010), "CITA CONFIRMADA", font=bold(16), fill=INK, anchor="mm")
    draw.text((CONTENT, 1138), "Mientras tú sigues", font=serif(35), fill=WHITE)
    draw.text((CONTENT, 1181), "con tu trabajo.", font=serif_italic(38), fill=TEAL)
    footer(image, True, 1375)
    return image.convert("RGB")


def variant_1_back():
    image = Image.new("RGBA", (ART_W, ART_H), CREAM)
    draw = ImageDraw.Draw(image)
    brand(draw, False)
    draw.text((CONTENT, 180), "Esto ocurre mientras", font=serif(37), fill=INK)
    draw.text((CONTENT, 224), "tú sigues trabajando.", font=serif_italic(40), fill=TEAL_DARK)
    steps = [
        ("1", "TE ESCRIBEN", "¿Tenéis cita mañana?"),
        ("2", "LARA RESPONDE", "Consulta tus huecos disponibles."),
        ("3", "CITA CONFIRMADA", "Queda guardada en tu agenda."),
    ]
    y = 306
    for number, title, body in steps:
        draw.ellipse((CONTENT, y, CONTENT + 42, y + 42), fill=INK if number == "3" else TEAL)
        draw.text((CONTENT + 21, y + 21), number, font=bold(15), fill=WHITE if number == "3" else INK, anchor="mm")
        draw.text((CONTENT + 60, y - 2), title, font=bold(12), fill=TEAL_DARK)
        draw.text((CONTENT + 60, y + 21), body, font=sans(16), fill=INK)
        y += 65
    image = agenda_real(image, (CONTENT, 520, ART_W - CONTENT, 875), "La agenda real que recibe el negocio.")
    draw = ImageDraw.Draw(image)
    box = (CONTENT, 935, ART_W - CONTENT, 1168)
    draw.rounded_rectangle(box, radius=22, fill=WHITE, outline=LINE, width=2)
    draw.text((CONTENT + 25, 965), "UNA CITA PUEDE CAMBIAR LA CUENTA", font=bold(12), fill=TEAL_DARK)
    draw.text((CONTENT + 25, 1008), "Si una cita vale 42 €...", font=bold(24), fill=INK)
    draw.text((CONTENT + 25, 1048), "Lara cuesta 29 € al mes", font=bold(24), fill=INK)
    draw.line((CONTENT + 25, 1094, 720, 1094), fill=LINE, width=2)
    draw.text((CONTENT + 25, 1115), "Con una cita así, el mes ya está cubierto.", font=bold(17), fill=TEAL_DARK)
    draw.text((ART_W - CONTENT - 125, 987), "+13 €", font=bold(38), fill=INK, anchor="mm")
    draw.text((ART_W - CONTENT - 125, 1032), "después de cubrir", font=sans(11), fill=GREY, anchor="mm")
    draw.text((ART_W - CONTENT - 125, 1051), "la mensualidad", font=sans(11), fill=GREY, anchor="mm")
    draw.text((CONTENT, 1235), "¿Quieres verla responder?", font=serif(31), fill=INK)
    draw.text((CONTENT, 1275), "Escanea y prueba la conversación.", font=sans(16), fill=GREY)
    draw.rounded_rectangle((CONTENT, 1335, 675, 1404), radius=34, fill=INK)
    draw.text((385, 1369), "MIRAR LA DEMO", font=bold(17), fill=WHITE, anchor="mm")
    paste_qr(image, ART_W - CONTENT - QR_SIZE, 1225, False)
    return image.convert("RGB")


def variant_2_front():
    image = Image.new("RGBA", (ART_W, ART_H), CREAM)
    draw = ImageDraw.Draw(image)
    brand(draw, False)
    draw.text((CONTENT, 180), "CADA MENSAJE", font=bold(50), fill=INK)
    draw.text((CONTENT, 239), "SIN RESPUESTA", font=bold(50), fill=INK)
    draw.text((CONTENT, 307), "puede ser una cita", font=serif_italic(42), fill=TEAL_DARK)
    draw.text((CONTENT, 357), "que no vuelve.", font=serif_italic(42), fill=TEAL_DARK)
    draw.text((CONTENT, 430), "Mientras terminas un trabajo, otro cliente", font=sans(19), fill=GREY)
    draw.text((CONTENT, 459), "ya está buscando quién le responda.", font=sans(19), fill=GREY)
    box = (CONTENT, 535, ART_W - CONTENT, 900)
    image = add_shadow(image, box, 34)
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle(box, radius=26, fill=WHITE)
    draw.text((CONTENT + 30, 570), "MENSAJE RECIBIDO", font=bold(13), fill=TEAL_DARK)
    draw.rounded_rectangle((CONTENT + 28, 615, ART_W - CONTENT - 160, 706), radius=18, fill="#ECE9E4")
    draw.text((CONTENT + 52, 644), "¿Tenéis hueco esta tarde?", font=bold(18), fill=INK)
    draw.line((CONTENT + 145, 758, ART_W - CONTENT - 215, 758), fill=TEAL, width=7)
    draw.polygon([(ART_W - CONTENT - 215, 743), (ART_W - CONTENT - 184, 758), (ART_W - CONTENT - 215, 773)], fill=TEAL)
    draw.rounded_rectangle((CONTENT + 240, 801, ART_W - CONTENT - 28, 870), radius=17, fill="#D9F7F3")
    draw.text((CONTENT + 265, 824), "17:30 · Cita confirmada", font=bold(17), fill=INK)
    draw.ellipse((ART_W - CONTENT - 135, 587, ART_W - CONTENT - 48, 674), fill=TEAL)
    draw.text((ART_W - CONTENT - 91, 630), "1", font=bold(36), fill=INK, anchor="mm")
    draw.text((CONTENT, 970), "Lara contesta.", font=serif(34), fill=INK)
    draw.text((CONTENT, 1012), "Mira tu agenda.", font=serif(34), fill=INK)
    draw.text((CONTENT, 1054), "Deja la cita puesta.", font=serif_italic(36), fill=TEAL_DARK)
    draw.rounded_rectangle((CONTENT, 1145, ART_W - CONTENT, 1260), radius=24, fill=INK)
    draw.text((CONTENT + 28, 1169), "SI UNA CITA VALE 42 €...", font=bold(13), fill=TEAL)
    draw.text((CONTENT + 28, 1202), "una sola ya cubre los 29 € del mes.", font=bold(19), fill=WHITE)
    footer(image, False, 1375)
    return image.convert("RGB")


def variant_2_back():
    image = add_atmosphere(Image.new("RGBA", (ART_W, ART_H), "#083E3C"), (400, -180, 1280, 650))
    draw = ImageDraw.Draw(image)
    brand(draw, True)
    draw.text((CONTENT, 180), "No necesitas contestar", font=serif(36), fill=WHITE)
    draw.text((CONTENT, 224), "para no perder la cita.", font=serif_italic(39), fill=TEAL)
    image = chat_card(image, (CONTENT, 305, ART_W - CONTENT, 740))
    draw = ImageDraw.Draw(image)
    draw.text((CONTENT, 820), "UNA CUENTA SENCILLA", font=bold(13), fill=TEAL)
    draw.text((CONTENT, 862), "Si una cita vale 42 €", font=bold(26), fill=WHITE)
    draw.text((CONTENT, 902), "Lara cuesta 29 € al mes", font=bold(26), fill=WHITE)
    draw.line((CONTENT, 950, 730, 950), fill="#5E8986", width=2)
    draw.text((CONTENT, 976), "Con una cita así, el mes ya está cubierto.", font=bold(18), fill=TEAL)
    draw.text((CONTENT, 1016), "Ejemplo, no promesa de ingresos.", font=sans(12), fill="#C9D7D6")
    draw.text((CONTENT, 1098), "¿Cuánto vale una cita en tu negocio?", font=serif(29), fill=WHITE)
    draw.text((CONTENT, 1140), "Escanea y mira cómo responde Lara.", font=sans(16), fill="#D7E1E1")
    draw.rounded_rectangle((CONTENT, 1205, 675, 1274), radius=34, fill=TEAL)
    draw.text((385, 1239), "PROBAR LA DEMO", font=bold(17), fill=INK, anchor="mm")
    paste_qr(image, ART_W - CONTENT - QR_SIZE, 1118, True)
    draw.text((CONTENT, 1410), "WhatsApp · Telegram · Web", font=bold(16), fill=WHITE)
    draw.text((CONTENT, 1442), "29 €/mes · Sin comisiones", font=sans(15), fill="#D7E1E1")
    return image.convert("RGB")


def variant_3_front():
    image = add_atmosphere(Image.new("RGBA", (ART_W, ART_H), NAVY), (-280, 500, 720, 1510), (40, 214, 201, 52))
    draw = ImageDraw.Draw(image)
    brand(draw, True)
    draw.text((CONTENT, 180), "TE ESCRIBEN.", font=bold(51), fill=WHITE)
    draw.text((CONTENT, 240), "LARA RESPONDE.", font=bold(51), fill=TEAL)
    draw.text((CONTENT, 300), "LA CITA ENTRA", font=bold(51), fill=WHITE)
    draw.text((CONTENT, 360), "EN TU AGENDA.", font=bold(51), fill=WHITE)
    draw.text((CONTENT, 432), "Eso es Nexux Recepcionista IA.", font=serif_italic(27), fill="#D8E1E3")
    steps = [
        ("1", "MENSAJE", "¿Tenéis cita?"),
        ("2", "LARA", "A las 17:30"),
        ("3", "AGENDA", "Confirmada"),
    ]
    y = 535
    for i, (number, title, body) in enumerate(steps):
        x = CONTENT + i * 330
        draw.rounded_rectangle((x, y, x + 278, y + 285), radius=24, fill="#FBFAF8")
        draw.ellipse((x + 22, y + 20, x + 68, y + 66), fill=INK if i == 2 else TEAL)
        draw.text((x + 45, y + 43), number, font=bold(16), fill=WHITE if i == 2 else INK, anchor="mm")
        draw.text((x + 22, y + 91), title, font=bold(13), fill=TEAL_DARK)
        draw.text((x + 22, y + 139), body, font=bold(17), fill=INK)
        if i < 2:
            draw.line((x + 278, y + 144, x + 314, y + 144), fill=TEAL, width=6)
            draw.polygon([(x + 314, y + 132), (x + 337, y + 144), (x + 314, y + 156)], fill=TEAL)
    draw.rounded_rectangle((CONTENT, 900, ART_W - CONTENT, 1027), radius=26, fill="#0C867E")
    draw.text((CONTENT + 28, 927), "MIENTRAS TÚ SIGUES TRABAJANDO", font=bold(13), fill="#D1F6F2")
    draw.text((CONTENT + 28, 961), "Lara responde, organiza y reserva.", font=bold(22), fill=WHITE)
    draw.text((CONTENT, 1100), "No es otro calendario.", font=serif(34), fill=WHITE)
    draw.text((CONTENT, 1143), "Es quien ayuda a llenarlo.", font=serif_italic(36), fill=TEAL)
    footer(image, True, 1375)
    return image.convert("RGB")


def variant_3_back():
    image = Image.new("RGBA", (ART_W, ART_H), CREAM)
    draw = ImageDraw.Draw(image)
    brand(draw, False)
    draw.text((CONTENT, 180), "Lo que recibe tu negocio", font=serif(37), fill=INK)
    draw.text((CONTENT, 224), "desde el primer día.", font=serif_italic(40), fill=TEAL_DARK)
    features = [
        ("R", "RESPUESTAS", "Lara atiende los mensajes mientras trabajas."),
        ("A", "AGENDA", "Consulta tus huecos y propone una hora."),
        ("C", "CITAS", "La reserva queda guardada en tu agenda."),
    ]
    y = 305
    for letter, title, body in features:
        draw.rounded_rectangle((CONTENT, y, ART_W - CONTENT, y + 96), radius=19, fill=WHITE, outline=LINE, width=2)
        draw.ellipse((CONTENT + 18, y + 23, CONTENT + 66, y + 71), fill=TEAL)
        draw.text((CONTENT + 42, y + 47), letter, font=bold(16), fill=INK, anchor="mm")
        draw.text((CONTENT + 84, y + 16), title, font=bold(12), fill=TEAL_DARK)
        draw.text((CONTENT + 84, y + 45), body, font=sans(14), fill=INK)
        y += 113
    image = agenda_real(image, (CONTENT, 690, ART_W - CONTENT, 1030), "Tu agenda, tus clientes y tus citas.")
    draw = ImageDraw.Draw(image)
    draw.text((CONTENT, 1107), "29 € al mes.", font=bold(30), fill=INK)
    draw.text((CONTENT, 1150), "Sin comisiones por cita.", font=serif_italic(26), fill=TEAL_DARK)
    draw.text((CONTENT, 1210), "¿Quieres verla funcionando?", font=serif(27), fill=INK)
    draw.rounded_rectangle((CONTENT, 1270, 675, 1339), radius=34, fill=INK)
    draw.text((385, 1304), "MIRAR LA DEMO", font=bold(17), fill=WHITE, anchor="mm")
    paste_qr(image, ART_W - CONTENT - QR_SIZE, 1145, False)
    draw.text((CONTENT, 1430), "WhatsApp · Telegram · Web", font=bold(15), fill=GREY)
    return image.convert("RGB")


# Revision visual: el producto se entiende de un vistazo. El movil queda en
# primer plano con el mensaje y el profesional sigue trabajando al fondo.
PHOTO_DIR = TMP / "personajes-v2"


def photo_background(filename):
    source = Image.open(PHOTO_DIR / filename).convert("RGBA")
    return ImageOps.fit(source, (ART_W, ART_H), Image.Resampling.LANCZOS)


def darken_photo(image):
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    for y in range(0, 720):
        alpha = max(0, 202 - int(y * 0.19))
        od.rectangle((0, y, ART_W, y + 2), fill=(2, 11, 15, alpha))
    for y in range(1190, ART_H):
        alpha = min(210, 72 + int((y - 1190) * 0.32))
        od.rectangle((0, y, ART_W, y + 2), fill=(2, 11, 15, alpha))
    return Image.alpha_composite(image, overlay)


def notification(image, box, time="Ahora"):
    x1, y1, x2, y2 = box
    image = add_shadow(image, box, 78)
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle(box, radius=27, fill=(250, 250, 248, 246), outline="#D7DDDC", width=2)
    draw.ellipse((x1 + 22, y1 + 23, x1 + 70, y1 + 71), fill=TEAL)
    draw.text((x1 + 46, y1 + 47), "N", font=bold(17), fill=INK, anchor="mm")
    draw.text((x1 + 87, y1 + 18), "Nuevo mensaje", font=bold(14), fill=INK)
    draw.text((x2 - 24, y1 + 20), time, font=sans(11), fill=GREY, anchor="ra")
    draw.text((x1 + 87, y1 + 48), "¿Tenéis cita mañana?", font=bold(17), fill=INK)
    return image


def photo_front(filename, headline, accent, notification_box, qr_side, supporting):
    image = darken_photo(photo_background(filename))
    draw = ImageDraw.Draw(image)
    brand(draw, True)
    y = 176
    for line in headline:
        draw.text((CONTENT, y), line, font=bold(47), fill=WHITE)
        y += 56
    draw.text((CONTENT, y + 14), accent, font=serif_italic(35), fill=TEAL)
    draw.text((CONTENT, y + 66), supporting, font=sans(16), fill="#E1E8E9")
    image = notification(image, notification_box)
    draw = ImageDraw.Draw(image)
    qr_x = ART_W - CONTENT - QR_SIZE if qr_side == "right" else CONTENT
    price_x = qr_x - 270 if qr_side == "right" else qr_x + 245
    draw.rounded_rectangle((price_x, 1420, price_x + 240, 1492), radius=36, fill=TEAL)
    draw.text((price_x + 120, 1456), "29 €/mes", font=bold(24), fill=INK, anchor="mm")
    draw.text((price_x, 1510), "WhatsApp · Telegram · Web", font=bold(13), fill=WHITE)
    draw.text((price_x, 1538), "Sin comisiones por cita", font=sans(12), fill="#DDE7E8")
    paste_qr(image, qr_x, 1332, True)
    return image.convert("RGB")


def phone_conversation(image, box):
    x1, y1, x2, y2 = box
    image = add_shadow(image, box, 55)
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle(box, radius=62, fill="#11161A", outline="#30373C", width=4)
    sx1, sy1, sx2, sy2 = x1 + 22, y1 + 25, x2 - 22, y2 - 28
    draw.rounded_rectangle((sx1, sy1, sx2, sy2), radius=43, fill="#F4F1EC")
    draw.rounded_rectangle((x1 + 250, y1 + 10, x2 - 250, y1 + 32), radius=11, fill="#050708")
    draw.rounded_rectangle((sx1, sy1, sx2, sy1 + 92), radius=43, fill="#087E78")
    draw.rectangle((sx1, sy1 + 48, sx2, sy1 + 92), fill="#087E78")
    draw.ellipse((sx1 + 26, sy1 + 22, sx1 + 82, sy1 + 78), fill=TEAL)
    draw.text((sx1 + 54, sy1 + 50), "L", font=bold(21), fill=INK, anchor="mm")
    draw.text((sx1 + 102, sy1 + 18), "Lara · Recepcionista IA", font=bold(18), fill=WHITE)
    draw.text((sx1 + 102, sy1 + 51), "En línea · atendiendo por ti", font=sans(13), fill="#D8F5F2")
    incoming = (sx1 + 28, sy1 + 140, sx2 - 188, sy1 + 244)
    draw.rounded_rectangle(incoming, radius=20, fill="#E3DFD9")
    draw.text((incoming[0] + 21, incoming[1] + 18), "CLIENTE", font=bold(10), fill=GREY)
    draw.text((incoming[0] + 21, incoming[1] + 51), "Hola, ¿tenéis cita mañana?", font=bold(17), fill=INK)
    outgoing = (sx1 + 155, sy1 + 285, sx2 - 28, sy1 + 424)
    draw.rounded_rectangle(outgoing, radius=20, fill="#D4F5F1")
    draw.text((outgoing[0] + 21, outgoing[1] + 17), "LARA", font=bold(10), fill=TEAL_DARK)
    draw.text((outgoing[0] + 21, outgoing[1] + 50), "Sí. Tengo libre a las 17:30.", font=sans(16), fill=INK)
    draw.text((outgoing[0] + 21, outgoing[1] + 82), "¿Te la reservo?", font=bold(17), fill=INK)
    confirmed = (sx1 + 82, sy1 + 476, sx2 - 82, sy1 + 577)
    draw.rounded_rectangle(confirmed, radius=22, fill=WHITE, outline=TEAL, width=3)
    draw.ellipse((confirmed[0] + 24, confirmed[1] + 27, confirmed[0] + 70, confirmed[1] + 73), fill=TEAL)
    draw.line((confirmed[0] + 36, confirmed[1] + 50, confirmed[0] + 44, confirmed[1] + 59), fill=INK, width=4)
    draw.line((confirmed[0] + 44, confirmed[1] + 59, confirmed[0] + 61, confirmed[1] + 40), fill=INK, width=4)
    draw.text((confirmed[0] + 91, confirmed[1] + 20), "17:30 · CITA CONFIRMADA", font=bold(15), fill=INK)
    draw.text((confirmed[0] + 91, confirmed[1] + 51), "Guardada en tu agenda", font=sans(13), fill=GREY)
    draw.rounded_rectangle((sx1 + 28, sy2 - 70, sx2 - 28, sy2 - 22), radius=24, fill=WHITE, outline=LINE, width=2)
    draw.text((sx1 + 53, sy2 - 57), "Escribe un mensaje...", font=sans(13), fill="#92979A")
    return image


def conversation_back(title, accent, proof_title, proof_body):
    image = Image.new("RGBA", (ART_W, ART_H), CREAM)
    draw = ImageDraw.Draw(image)
    brand(draw, False)
    draw.text((CONTENT, 177), title, font=serif(34), fill=INK)
    draw.text((CONTENT, 219), accent, font=serif_italic(37), fill=TEAL_DARK)
    image = phone_conversation(image, (CONTENT + 75, 300, ART_W - CONTENT - 75, 1035))
    draw = ImageDraw.Draw(image)
    draw.text((CONTENT, 1092), proof_title, font=bold(19), fill=INK)
    draw.text((CONTENT, 1129), proof_body, font=sans(15), fill=GREY)

    # Secuencia compacta: explica el producto antes de pedir el escaneo.
    flow_top, flow_bottom = 1182, 1262
    draw.rounded_rectangle(
        (CONTENT, flow_top, ART_W - CONTENT, flow_bottom),
        radius=22,
        fill="#E6F7F5",
        outline="#B9E6E2",
        width=2,
    )
    flow = (("1", "RESPONDE"), ("2", "CONSULTA"), ("3", "RESERVA"))
    usable = ART_W - 2 * CONTENT
    col = usable / 3
    for index, (number, label) in enumerate(flow):
        cx = CONTENT + col * index + col / 2
        draw.ellipse((cx - 23, flow_top + 17, cx + 23, flow_top + 63), fill=TEAL)
        draw.text((cx, flow_top + 40), number, font=bold(15), fill=INK, anchor="mm")
        draw.text((cx + 48, flow_top + 40), label, font=bold(14), fill=INK, anchor="lm")

    draw.text((CONTENT, 1300), "29 €/mes", font=bold(24), fill=TEAL_DARK)
    draw.text((CONTENT + 142, 1303), "Sin comisiones por cita", font=bold(14), fill=INK)
    draw.rounded_rectangle((CONTENT, 1365, 710, 1443), radius=39, fill=INK)
    draw.text((410, 1404), "QUIERO VERLA RESERVAR", font=bold(16), fill=WHITE, anchor="mm")
    paste_qr(image, ART_W - CONTENT - QR_SIZE, 1292, False)
    draw.text((CONTENT, 1510), "nexux.pro", font=bold(15), fill=INK)
    draw.text((CONTENT + 125, 1510), "WhatsApp · Telegram · Web", font=bold(13), fill=GREY)
    return image.convert("RGB")


def variant_1_front():
    return photo_front(
        "01-hombre-movil-primer-plano.png",
        ("TU CLIENTE NO SABE", "QUE ESTÁS TRABAJANDO."),
        "Solo sabe que nadie le contestó.",
        (105, 1045, 540, 1150),
        "right",
        "Lara responde y deja la cita puesta por ti.",
    )


def variant_1_back():
    return conversation_back(
        "El mensaje llega.",
        "Lara responde. La cita queda puesta.",
        "MIENTRAS TÚ SIGUES TRABAJANDO",
        "El cliente recibe respuesta sin esperar a que acabes.",
    )


def variant_2_front():
    return photo_front(
        "02-mujer-movil-primer-plano.png",
        ("CADA MENSAJE", "SIN RESPUESTA"),
        "puede ser una cita que no vuelve.",
        (625, 1035, 1090, 1140),
        "left",
        "Lara responde aunque tú estés atendiendo.",
    )


def variant_2_back():
    return conversation_back(
        "No necesitas contestar",
        "para no perder la cita.",
        "SI UNA CITA VALE 42 €...",
        "una sola ya cubre los 29 € del mes. Ejemplo, no promesa.",
    )


def variant_3_front():
    return photo_front(
        "03-mayor-movil-primer-plano.png",
        ("TE ESCRIBEN. LARA RESPONDE.", "LA CITA ENTRA EN TU AGENDA."),
        "Eso es Nexux Recepcionista IA.",
        (105, 1040, 540, 1145),
        "right",
        "Sin parar el trabajo. Sin perder la oportunidad.",
    )


def variant_3_back():
    return conversation_back(
        "Te escriben. Lara responde.",
        "La cita entra en tu agenda.",
        "WHATSAPP · TELEGRAM · WEB",
        "Responde, consulta tus huecos y confirma la reserva.",
    )


# Revision clara: cuatro mensajes dentro del telefono, cita creada en una
# segunda pantalla y el profesional ocupado al fondo.
PHOTO_DIR_V3 = TMP / "personajes-v4"


def light_photo(filename):
    source = Image.open(PHOTO_DIR_V3 / filename).convert("RGBA")
    image = ImageOps.fit(source, (ART_W, ART_H), Image.Resampling.LANCZOS)
    veil = Image.new("RGBA", image.size, (255, 255, 255, 0))
    vd = ImageDraw.Draw(veil)
    for y in range(0, 650):
        alpha = max(0, 178 - int(y * 0.20))
        vd.rectangle((0, y, ART_W, y + 2), fill=(255, 255, 255, alpha))
    return Image.alpha_composite(image, veil)


def perspective_coefficients(destination, source):
    matrix, vector = [], []
    for (x, y), (u, v) in zip(destination, source):
        matrix.append([x, y, 1, 0, 0, 0, -u * x, -u * y])
        matrix.append([0, 0, 0, x, y, 1, -v * x, -v * y])
        vector.extend([u, v])
    return tuple(np.linalg.solve(np.asarray(matrix, dtype=float), np.asarray(vector, dtype=float)))


def warp_to_screen(ui, destination, opacity=216, corner_radius=0):
    # Conserva parte del cristal fotografiado para que la interfaz parezca
    # encendida dentro del dispositivo, no una pegatina opaca superpuesta.
    ui = ui.copy()
    alpha = ui.getchannel("A")
    if corner_radius:
        rounded = Image.new("L", ui.size, 0)
        ImageDraw.Draw(rounded).rounded_rectangle(
            (0, 0, ui.width - 1, ui.height - 1), radius=corner_radius, fill=255
        )
        alpha = Image.composite(alpha, Image.new("L", ui.size, 0), rounded)
    alpha = alpha.point(lambda value: value * opacity // 255)
    ui.putalpha(alpha)
    source = [(0, 0), (ui.width - 1, 0), (ui.width - 1, ui.height - 1), (0, ui.height - 1)]
    coeffs = perspective_coefficients(destination, source)
    return ui.transform(
        (ART_W, ART_H),
        Image.Transform.PERSPECTIVE,
        coeffs,
        resample=Image.Resampling.BICUBIC,
        fillcolor=(0, 0, 0, 0),
    )


def phone_messages_ui():
    ui = Image.new("RGBA", (420, 760), "#162126")
    draw = ImageDraw.Draw(ui)
    draw.text((210, 34), "10:14", font=bold(34), fill=WHITE, anchor="mm")
    draw.text((210, 78), "4 notificaciones nuevas", font=bold(17), fill="#D5E2E3", anchor="mm")
    notifications = [
        ("ahora", "¿Tenéis cita mañana?"),
        ("1 min", "Quiero reservar a las 17:30"),
        ("2 min", "¿Hay hueco esta tarde?"),
        ("3 min", "¿Cuál es el precio?"),
    ]
    y = 116
    for when, message in notifications:
        draw.rounded_rectangle((18, y, 402, y + 118), radius=24, fill="#F7F9F8", outline="#D5DDDC", width=2)
        draw.ellipse((34, y + 27, 94, y + 87), fill="#25D366")
        draw.text((64, y + 57), "W", font=bold(22), fill=WHITE, anchor="mm")
        draw.text((112, y + 20), "WhatsApp", font=bold(16), fill=INK)
        draw.text((380, y + 21), when, font=sans(12), fill=GREY, anchor="ra")
        draw.text((112, y + 58), message, font=bold(17), fill=INK)
        y += 130
    draw.rounded_rectangle((76, 660, 344, 720), radius=30, fill="#087E78")
    draw.text((210, 690), "Lara los está atendiendo", font=bold(16), fill=WHITE, anchor="mm")
    return ui


def appointment_ui():
    source = Image.open(ROOT / "public" / "img" / "demo-crm.png").convert("RGBA")
    source = source.crop((175, 80, 1005, 1005))
    ui = ImageOps.fit(source, (760, 430), Image.Resampling.LANCZOS)
    draw = ImageDraw.Draw(ui)
    draw.rounded_rectangle((300, 202, 742, 414), radius=24, fill=(255, 255, 255, 247), outline=TEAL, width=6)
    draw.rounded_rectangle((322, 226, 445, 390), radius=20, fill="#D8F6F2")
    draw.text((383, 267), "17:30", font=bold(28), fill=TEAL_DARK, anchor="mm")
    draw.text((383, 326), "HOY", font=bold(17), fill=INK, anchor="mm")
    draw.text((470, 225), "NUEVA CITA", font=bold(18), fill=TEAL_DARK)
    draw.text((470, 263), "CONFIRMADA", font=bold(24), fill=INK)
    draw.text((470, 311), "Marta G.", font=bold(19), fill=INK)
    draw.text((470, 350), "Reservada por Lara", font=bold(16), fill=TEAL_DARK)
    draw.rounded_rectangle((25, 18, 245, 68), radius=25, fill="#101619")
    draw.text((135, 43), "CRM NEXUX · EN VIVO", font=bold(14), fill=WHITE, anchor="mm")
    return ui


SCREEN_LAYOUTS = {
    "01-autonomia-clara.png": {
        "phone": [(172, 1156), (374, 1136), (675, 1411), (406, 1486)],
        "appointment": [(508, 826), (1024, 835), (1017, 1190), (467, 1156)],
    },
    "02-autonomia-clara.png": {
        "phone": [(90, 1289), (254, 1269), (424, 1459), (236, 1515)],
        "appointment": [(512, 989), (1094, 1028), (1035, 1435), (426, 1339)],
    },
    "03-autonomia-clara.png": {
        "phone": [(172, 1219), (353, 1193), (594, 1465), (363, 1528)],
        "appointment": [(568, 953), (1050, 955), (1050, 1311), (541, 1289)],
    },
}


def paste_qr_compact(image, x, y):
    draw = ImageDraw.Draw(image)
    size = 224
    # El rotulo va DENTRO de la tarjeta blanca. Al agrandar el QR, el texto suelto subia
    # hasta cruzarse con la tablet de la foto y quedaba ilegible sobre el mueble.
    draw.rounded_rectangle((x - 12, y - 52, x + size + 12, y + size + 12), radius=16, fill=WHITE, outline=LINE, width=2)
    draw.text((x + size // 2, y - 28), "HABLA CON LARA AHORA", font=bold(14), fill=INK, anchor="mm")
    image.paste(qr_variante(size), (x, y))


def autonomous_front(filename, headline, accent, supporting):
    image = light_photo(filename)
    layout = SCREEN_LAYOUTS[filename]
    image = Image.alpha_composite(
        image, warp_to_screen(phone_messages_ui(), layout["phone"], corner_radius=38)
    )
    image = Image.alpha_composite(
        image, warp_to_screen(appointment_ui(), layout["appointment"], corner_radius=22)
    )
    draw = ImageDraw.Draw(image)
    brand(draw, False)
    y = 176
    for line in headline:
        draw.text((CONTENT, y), line, font=bold(45), fill=INK)
        y += 55
    draw.text((CONTENT, y + 12), accent, font=serif_italic(34), fill=TEAL_DARK)
    draw.text((CONTENT, y + 63), supporting, font=sans(16), fill="#43494D")

    # Una sola lectura visual: mensaje -> Lara -> cita. Sustituye el antiguo
    # boton flotante por una explicacion que conecta los dos dispositivos.
    flow_box = (CONTENT, 610, ART_W - CONTENT, 724)
    draw.rounded_rectangle(flow_box, radius=28, fill=(255, 255, 255, 238), outline="#C9DDDB", width=2)
    labels = (("1", "MENSAJES", "entran"), ("2", "LARA", "responde"), ("3", "CITA", "confirmada"))
    usable = ART_W - 2 * CONTENT
    col = usable / 3
    for index, (number, title, detail) in enumerate(labels):
        left = CONTENT + index * col
        cx = left + col / 2
        draw.ellipse((left + 25, 635, left + 75, 685), fill=TEAL)
        draw.text((left + 50, 660), number, font=bold(16), fill=INK, anchor="mm")
        draw.text((left + 91, 640), title, font=bold(14), fill=INK)
        draw.text((left + 91, 668), detail, font=sans(13), fill=GREY)
        if index < 2:
            ax = left + col - 20
            draw.line((ax - 22, 660, ax + 12, 660), fill=TEAL_DARK, width=4)
            draw.polygon([(ax + 12, 652), (ax + 28, 660), (ax + 12, 668)], fill=TEAL_DARK)

    # El cierre comercial funciona como un unico bloque, no como piezas sueltas.
    footer = (CONTENT - 12, 1490, ART_W - CONTENT + 12, ART_H - CONTENT)
    draw.rounded_rectangle(footer, radius=30, fill=(255, 255, 255, 244), outline="#D7E0DF", width=2)
    draw.rounded_rectangle((CONTENT + 12, 1500, CONTENT + 262, 1574), radius=37, fill=TEAL)
    draw.text((CONTENT + 137, 1537), "29 €/mes", font=bold(24), fill=INK, anchor="mm")
    draw.text((CONTENT + 292, 1508), "SIN COMISIONES", font=bold(14), fill=INK)
    draw.text((CONTENT + 292, 1539), "WhatsApp · Telegram · Web", font=bold(13), fill=INK)
    draw.text((CONTENT + 292, 1567), "La cita sigue siendo tuya · nexux.pro", font=sans(12), fill=GREY)
    paste_qr_compact(image, ART_W - CONTENT - 224, 1398)
    return image.convert("RGB")


def variant_1_front():
    return autonomous_front(
        "01-autonomia-clara.png",
        ("CADA MENSAJE QUE", "NO CONTESTAS ES..."),
        "una cita que no vuelve.",
        "Lara responde, mira tu agenda y reserva mientras tú trabajas.",
    )


def variant_1_back():
    return conversation_back(
        "El mensaje entra.",
        "Lara lo convierte en una cita.",
        "LA CITA QUE IBAS A PERDER, CONFIRMADA.",
        "El cliente escribe. Lara propone las 17:30 y la deja en tu agenda.",
    )


def variant_2_front():
    return autonomous_front(
        "02-autonomia-clara.png",
        ("TE ESCRIBEN MIENTRAS", "ESTÁS TRABAJANDO."),
        "Lara contesta por ti.",
        "Y cuando quieren cita, la deja confirmada en tu agenda.",
    )


def variant_2_back():
    return conversation_back(
        "Tú atiendes tu negocio.",
        "Lara atiende los mensajes.",
        "NO DEJES AL CLIENTE ESPERANDO.",
        "Responde, consulta tus huecos y confirma la cita sin interrumpirte.",
    )


def variant_3_front():
    return autonomous_front(
        "03-autonomia-clara.png",
        ("NO NECESITAS VIVIR", "MIRANDO EL MÓVIL."),
        "Necesitas que alguien conteste.",
        "Lara responde y reserva por WhatsApp, Telegram y web.",
    )


def variant_3_back():
    return conversation_back(
        "No es otro chatbot.",
        "Es la recepción de tu negocio.",
        "29 € AL MES. TUS CITAS SIGUEN SIENDO TUYAS.",
        "Sin comisión por reserva y sin pagar por cada empleado.",
    )


def crop_marks(sheet):
    draw = ImageDraw.Draw(sheet)
    mark, gap, width = px(2.4), px(0.6), max(2, px(0.18))
    for ox, oy in POSITIONS:
        left, right = ox + BLEED, ox + ART_W - BLEED
        top, bottom = oy + BLEED, oy + ART_H - BLEED
        for x in (left, right):
            draw.line((x, top - gap - mark, x, top - gap), fill=INK, width=width)
            draw.line((x, bottom + gap, x, bottom + gap + mark), fill=INK, width=width)
        for y in (top, bottom):
            draw.line((left - gap - mark, y, left - gap, y), fill=INK, width=width)
            draw.line((right + gap, y, right + gap + mark, y), fill=INK, width=width)
    cx, cy, r = PAGE_W // 2, PAGE_H // 2, px(1.4)
    for x, y in ((cx, px(2)), (cx, PAGE_H - px(2)), (px(2), cy), (PAGE_W - px(2), cy)):
        draw.line((x - r, y, x + r, y), fill=INK, width=width)
        draw.line((x, y - r, x, y + r), fill=INK, width=width)


def impose(card):
    sheet = Image.new("RGB", (PAGE_W, PAGE_H), WHITE)
    for x, y in POSITIONS:
        sheet.paste(card, (x, y))
    crop_marks(sheet)
    return sheet


def impose_cards(cards):
    if len(cards) != 4:
        raise ValueError("El pliego mixto necesita exactamente cuatro artes")
    sheet = Image.new("RGB", (PAGE_W, PAGE_H), WHITE)
    for (x, y), card in zip(POSITIONS, cards):
        sheet.paste(card, (x, y))
    crop_marks(sheet)
    return sheet


def make_pdf(front, back, path, title):
    temp_front = path.with_name(path.stem + "-front-cmyk.jpg")
    temp_back = path.with_name(path.stem + "-back-cmyk.jpg")
    front.convert("CMYK").save(temp_front, quality=95, subsampling=0, dpi=(DPI, DPI))
    back.convert("CMYK").save(temp_back, quality=95, subsampling=0, dpi=(DPI, DPI))
    c = canvas.Canvas(str(path), pagesize=A4, pageCompression=1)
    c.setTitle(title)
    c.setAuthor("Nexux Pro")
    c.setSubject("A4 duplex, 4-up, CMYK 300 dpi, 3 mm bleed, crop marks")
    for image_path in (temp_front, temp_back):
        c.drawImage(ImageReader(str(image_path)), 0, 0, width=A4[0], height=A4[1], preserveAspectRatio=False)
        c.showPage()
    c.save()
    temp_front.unlink()
    temp_back.unlink()


def instructions(path):
    path.write_text(
        "NEXUX PRO - IMPRESION A4 DOBLE CARA\n\n"
        "Hoja: A4 vertical 210 x 297 mm\n"
        "Imposicion: 4 folletos por hoja\n"
        "Folleto final: 93 x 136 mm\n"
        "Sangre individual: 3 mm\n"
        "Zona segura: 5 mm\n"
        "Resolucion: 300 ppp\n"
        "Color: CMYK\n\n"
        "IMPRESORA\n"
        "- Doble cara y voltear por el borde largo.\n"
        "- Tamano real / escala 100 %.\n"
        "- No usar Ajustar, Encoger ni Ampliar.\n"
        "- Centrar la pagina. No activar impresion sin bordes.\n\n"
        "GUILLOTINA\n"
        "- Usa las marcas negras de la cara 1.\n"
        "- Retira primero margenes exteriores y despues calles centrales.\n"
        "- Haz una prueba antes del lote completo.\n\n"
        "Las dos caras usan coordenadas identicas. La sangre tolera pequenas desviaciones, "
        "pero si la prueba duplex se desplaza mas de 1 mm hay que ajustar el registro mecanico "
        "en la impresora o su controlador.\n",
        encoding="utf-8",
    )


def main():
    variants = [
        ("01-dolor-directo", variant_1_front, variant_1_back, "Nexux Pro - Dolor directo"),
        ("02-cita-que-no-vuelve", variant_2_front, variant_2_back, "Nexux Pro - Cita que no vuelve"),
        ("03-producto-explicito", variant_3_front, variant_3_back, "Nexux Pro - Producto explicito"),
    ]
    # Solo se copia al escritorio de Windows si se ejecuta alli; en el servidor no existe.
    desktop = Path("C:/Users/Nexux/Desktop/Publicidad Nexux Pro/A4 doble cara - 3 variantes")
    try:
        desktop.mkdir(parents=True, exist_ok=True)
    except OSError:
        desktop = OUT / "_copia"
        desktop.mkdir(parents=True, exist_ok=True)
    instructions(OUT / "INSTRUCCIONES-IMPRESION.txt")
    shutil.copy2(OUT / "INSTRUCCIONES-IMPRESION.txt", desktop / "INSTRUCCIONES-IMPRESION.txt")

    # Un codigo por variante: sin esto las tres llevan el mismo QR y el reparto no dice
    # cual funciona, que es justo lo que se quiere medir.
    codigos = {
        "01-dolor-directo": "d1",
        "02-cita-que-no-vuelve": "d2",
        "03-producto-explicito": "d3",
    }

    rendered = []
    for slug, make_front, make_back, title in variants:
        globals()["QR_URL"] = "https://nexux.pro/f/" + codigos[slug]
        print("  " + slug + " -> " + QR_URL)
        folder = OUT / slug
        folder.mkdir(parents=True, exist_ok=True)
        front, back = make_front(), make_back()
        front_path, back_path = folder / "folleto-anverso.png", folder / "folleto-reverso.png"
        front.save(front_path, dpi=(DPI, DPI), optimize=True)
        back.save(back_path, dpi=(DPI, DPI), optimize=True)
        front_sheet, back_sheet = impose(front), impose(back)
        front_sheet.save(folder / "a4-anverso-4up.png", dpi=(DPI, DPI), optimize=True)
        back_sheet.save(folder / "a4-reverso-4up.png", dpi=(DPI, DPI), optimize=True)
        pdf_path = PDF_OUT / f"nexux-pro-{slug}-a4-duplex-4up.pdf"
        make_pdf(front_sheet, back_sheet, pdf_path, title)
        shutil.copy2(pdf_path, desktop / pdf_path.name)
        shutil.copy2(front_path, desktop / f"{slug}-anverso.png")
        shutil.copy2(back_path, desktop / f"{slug}-reverso.png")
        rendered.append((front, back))
        print(f"{pdf_path}\t{pdf_path.stat().st_size}")

    # Pliego de prueba comercial: una unidad de cada variante y una segunda
    # unidad de la variante 1, que es la principal. En la cara trasera se
    # intercambian izquierda/derecha para que cada reverso quede detrás de su
    # anverso al imprimir a doble cara y voltear por el borde largo.
    mixed_front = impose_cards([
        rendered[0][0], rendered[1][0],
        rendered[2][0], rendered[0][0],
    ])
    mixed_back = impose_cards([
        rendered[1][1], rendered[0][1],
        rendered[0][1], rendered[2][1],
    ])
    mixed_pdf = PDF_OUT / "nexux-pro-variantes-mixtas-a4-duplex-4up.pdf"
    make_pdf(mixed_front, mixed_back, mixed_pdf, "Nexux Pro - Variantes mixtas")
    mixed_front.save(OUT / "pliego-mixto-anverso.png", dpi=(DPI, DPI), optimize=True)
    mixed_back.save(OUT / "pliego-mixto-reverso.png", dpi=(DPI, DPI), optimize=True)
    shutil.copy2(mixed_pdf, desktop / mixed_pdf.name)
    shutil.copy2(OUT / "pliego-mixto-anverso.png", desktop / "pliego-mixto-anverso.png")
    shutil.copy2(OUT / "pliego-mixto-reverso.png", desktop / "pliego-mixto-reverso.png")
    print(f"{mixed_pdf}\t{mixed_pdf.stat().st_size}")


if __name__ == "__main__":
    main()
