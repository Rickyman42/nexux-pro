from pathlib import Path

from reportlab.graphics import renderPDF
from reportlab.graphics.barcode import qr
from reportlab.graphics.shapes import Drawing
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A6
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "output" / "pdf" / "nexux-recepcionista-ia-flyer-universal-a6.pdf"
OUTPUT.parent.mkdir(parents=True, exist_ok=True)

FONT_DIR = Path("C:/Windows/Fonts")
pdfmetrics.registerFont(TTFont("NexuxSans", FONT_DIR / "arial.ttf"))
pdfmetrics.registerFont(TTFont("NexuxSansBold", FONT_DIR / "arialbd.ttf"))
pdfmetrics.registerFont(TTFont("NexuxSerif", FONT_DIR / "georgia.ttf"))
pdfmetrics.registerFont(TTFont("NexuxSerifItalic", FONT_DIR / "georgiai.ttf"))

TEAL = HexColor("#4CCBC3")
TEAL_DARK = HexColor("#188D86")
INK = HexColor("#17191D")
MUTED = HexColor("#62676F")
FAINT = HexColor("#ECEBE7")
PAPER = HexColor("#F8F7F4")
WHITE = colors.white

W, H = A6
M = 8 * mm
QR_URL = "https://nexux.pro/demo"


def paragraph(c, text, x, y_top, width, style):
    p = Paragraph(text, style)
    _, height = p.wrap(width, H)
    p.drawOn(c, x, y_top - height)
    return height


def logo(c, y):
    c.setFillColor(TEAL)
    c.roundRect(M, y - 8 * mm, 8 * mm, 8 * mm, 1.5 * mm, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont("NexuxSerifItalic", 12)
    c.drawCentredString(M + 4 * mm, y - 5.9 * mm, "N")
    c.setFillColor(INK)
    c.setFont("NexuxSansBold", 10)
    c.drawString(M + 11 * mm, y - 5.1 * mm, "nexux")
    c.setFillColor(TEAL)
    c.drawString(M + 25.5 * mm, y - 5.1 * mm, ".pro")
    c.setFillColor(MUTED)
    c.setFont("NexuxSansBold", 4.9)
    c.drawString(M + 11 * mm, y - 7.5 * mm, "RECEPCIONISTA IA")


def pill(c, x, y, w, h, text, fill, text_color, font_size=6.5):
    c.setFillColor(fill)
    c.roundRect(x, y, w, h, h / 2, fill=1, stroke=0)
    c.setFillColor(text_color)
    c.setFont("NexuxSansBold", font_size)
    c.drawCentredString(x + w / 2, y + h / 2 - font_size * 0.34, text)


def qr_code(c, x, y, size):
    c.setFillColor(WHITE)
    c.roundRect(x - 2.3 * mm, y - 2.3 * mm, size + 4.6 * mm, size + 4.6 * mm, 2 * mm, fill=1, stroke=0)
    widget = qr.QrCodeWidget(QR_URL)
    bounds = widget.getBounds()
    drawing = Drawing(size, size, transform=[size / (bounds[2] - bounds[0]), 0, 0, size / (bounds[3] - bounds[1]), 0, 0])
    drawing.add(widget)
    renderPDF.draw(drawing, c, x, y)


def message_flow(c, y_top):
    left = M
    width = W - 2 * M
    bubble_h = 14 * mm

    c.setFillColor(WHITE)
    c.setStrokeColor(HexColor("#D9D8D4"))
    c.setLineWidth(0.5)
    c.roundRect(left, y_top - bubble_h, width * 0.73, bubble_h, 3 * mm, fill=1, stroke=1)
    c.setFillColor(MUTED)
    c.setFont("NexuxSans", 6)
    c.drawString(left + 4 * mm, y_top - 4.8 * mm, "CLIENTE")
    c.setFillColor(INK)
    c.setFont("NexuxSansBold", 8.4)
    c.drawString(left + 4 * mm, y_top - 10.1 * mm, "¿Tenéis hueco mañana?")

    second_y = y_top - 18 * mm
    second_x = left + width * 0.23
    c.setFillColor(TEAL)
    c.setStrokeColor(TEAL_DARK)
    c.roundRect(second_x, second_y - bubble_h, width * 0.77, bubble_h, 3 * mm, fill=1, stroke=0)
    c.setFillColor(HexColor("#0D5C57"))
    c.setFont("NexuxSansBold", 6)
    c.drawString(second_x + 4 * mm, second_y - 4.8 * mm, "LARA")
    c.setFillColor(INK)
    c.setFont("NexuxSansBold", 8.4)
    c.drawString(second_x + 4 * mm, second_y - 10.1 * mm, "Sí. Te reservo a las 17:30.")

    card_y = second_y - 18 * mm
    c.setFillColor(INK)
    c.roundRect(left, card_y - 17 * mm, width, 17 * mm, 3 * mm, fill=1, stroke=0)
    c.setFillColor(TEAL)
    c.roundRect(left + 4 * mm, card_y - 13 * mm, 10 * mm, 10 * mm, 2 * mm, fill=1, stroke=0)
    c.setStrokeColor(INK)
    c.setLineWidth(1.4)
    c.setLineCap(1)
    c.line(left + 6.4 * mm, card_y - 8.1 * mm, left + 8.2 * mm, card_y - 10 * mm)
    c.line(left + 8.2 * mm, card_y - 10 * mm, left + 11.7 * mm, card_y - 6.4 * mm)
    c.setFillColor(TEAL)
    c.setFont("NexuxSansBold", 5.7)
    c.drawString(left + 18 * mm, card_y - 5.8 * mm, "CITA CONFIRMADA")
    c.setFillColor(WHITE)
    c.setFont("NexuxSansBold", 9.2)
    c.drawString(left + 18 * mm, card_y - 11.4 * mm, "Mañana · 17:30")


def front(c):
    c.setFillColor(PAPER)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setFillColor(TEAL)
    c.rect(0, H - 2.3 * mm, W, 2.3 * mm, fill=1, stroke=0)
    logo(c, H - 7 * mm)

    headline = ParagraphStyle(
        "headline",
        fontName="NexuxSerif",
        fontSize=19.2,
        leading=19.6,
        textColor=INK,
        alignment=TA_LEFT,
    )
    paragraph(
        c,
        'Cada mensaje que no contestas es <font name="NexuxSerifItalic" color="#188D86">una cita que no vuelve.</font>',
        M,
        H - 24 * mm,
        W - 2 * M,
        headline,
    )

    message_flow(c, H - 57 * mm)

    c.setFillColor(MUTED)
    c.setFont("NexuxSans", 7)
    c.drawString(M, 30.5 * mm, "Lara responde, mira tu agenda y deja la cita puesta.")
    c.setFillColor(INK)
    c.setFont("NexuxSansBold", 7.2)
    c.drawString(M, 26.7 * mm, "Tú sigues trabajando.")

    pill(c, M, 16.5 * mm, 32 * mm, 7 * mm, "29 €/mes", INK, WHITE, 7.2)
    c.setFillColor(MUTED)
    c.setFont("NexuxSans", 5.4)
    c.drawString(M, 12.4 * mm, "Sin comisiones · Sin permanencia")

    qr_size = 24 * mm
    qr_x = W - M - qr_size
    qr_y = 7.5 * mm
    qr_code(c, qr_x, qr_y, qr_size)
    c.setFillColor(INK)
    c.setFont("NexuxSansBold", 5.6)
    c.drawRightString(qr_x - 3.5 * mm, 15.5 * mm, "Escanea y mira")
    c.drawRightString(qr_x - 3.5 * mm, 12.4 * mm, "cómo responde")
    c.setFillColor(TEAL_DARK)
    c.setFont("NexuxSansBold", 5.2)
    c.drawRightString(qr_x - 3.5 * mm, 8.9 * mm, "nexux.pro")
    c.showPage()


def step(c, number, title, text, y):
    c.setFillColor(TEAL)
    c.circle(M + 5 * mm, y, 5 * mm, fill=1, stroke=0)
    c.setFillColor(INK)
    c.setFont("NexuxSansBold", 8)
    c.drawCentredString(M + 5 * mm, y - 2.7, str(number))
    c.setFillColor(WHITE)
    c.setFont("NexuxSansBold", 8)
    c.drawString(M + 14 * mm, y + 1.2 * mm, title)
    c.setFillColor(HexColor("#B8BBC1"))
    c.setFont("NexuxSans", 6.3)
    c.drawString(M + 14 * mm, y - 2.7 * mm, text)


def back(c):
    c.setFillColor(INK)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    logo_y = H - 7 * mm
    c.setFillColor(TEAL)
    c.roundRect(M, logo_y - 8 * mm, 8 * mm, 8 * mm, 1.5 * mm, fill=1, stroke=0)
    c.setFillColor(INK)
    c.setFont("NexuxSerifItalic", 12)
    c.drawCentredString(M + 4 * mm, logo_y - 5.9 * mm, "N")
    c.setFillColor(WHITE)
    c.setFont("NexuxSansBold", 10)
    c.drawString(M + 11 * mm, logo_y - 5.1 * mm, "nexux")
    c.setFillColor(TEAL)
    c.drawString(M + 25.5 * mm, logo_y - 5.1 * mm, ".pro")

    headline = ParagraphStyle(
        "back-headline",
        fontName="NexuxSerif",
        fontSize=18.5,
        leading=19.2,
        textColor=WHITE,
        alignment=TA_LEFT,
    )
    paragraph(
        c,
        'No importa a qué te dedicas. <font name="NexuxSerifItalic" color="#4CCBC3">Importa cómo te piden hora.</font>',
        M,
        H - 25 * mm,
        W - 2 * M,
        headline,
    )

    c.setFillColor(HexColor("#272A30"))
    c.roundRect(M, H - 79 * mm, W - 2 * M, 39 * mm, 4 * mm, fill=1, stroke=0)
    step(c, 1, "Recibe el mensaje", "WhatsApp, Telegram o web.", H - 49 * mm)
    step(c, 2, "Comprueba tu agenda", "Ofrece solo huecos reales.", H - 61 * mm)
    step(c, 3, "Confirma la cita", "Queda registrada automáticamente.", H - 73 * mm)

    c.setFillColor(WHITE)
    c.setFont("NexuxSansBold", 9)
    c.drawString(M, H - 88 * mm, "Una recepcionista IA por 29 €/mes")
    c.setFillColor(HexColor("#B8BBC1"))
    c.setFont("NexuxSans", 6.5)
    c.drawString(M, H - 93 * mm, "Para cualquier negocio que trabaja con citas.")
    c.drawString(M, H - 97 * mm, "Sin comisión por reserva. Sin pagar por empleado.")

    qr_size = 26 * mm
    qr_x = W - M - qr_size
    qr_y = 8 * mm
    qr_code(c, qr_x, qr_y, qr_size)
    c.setFillColor(TEAL)
    c.setFont("NexuxSansBold", 7.3)
    c.drawString(M, 27 * mm, "Mira una demo real")
    c.setFillColor(WHITE)
    c.setFont("NexuxSans", 6.3)
    c.drawString(M, 22.4 * mm, "Escanea el QR y comprueba")
    c.drawString(M, 18.7 * mm, "cómo responde y reserva Lara.")
    c.setFillColor(TEAL)
    c.setFont("NexuxSansBold", 6)
    c.drawString(M, 12 * mm, "nexux.pro")
    c.showPage()


def main():
    c = canvas.Canvas(str(OUTPUT), pagesize=A6, pageCompression=1)
    c.setTitle("Nexux Recepcionista IA - Flyer universal A6")
    c.setAuthor("Nexux Innovación Digital S.L.")
    c.setSubject("Publicidad impresa para negocios que trabajan con citas")
    front(c)
    back(c)
    c.save()
    print(OUTPUT)


if __name__ == "__main__":
    main()
