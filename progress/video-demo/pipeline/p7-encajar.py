#!/usr/bin/env python3
"""Encaja la conversacion del plano 7 dentro de la pantalla del movil del plano 6.

El movil de la mano se balancea unos 30 px durante los 8 segundos, asi que pegar
la conversacion en un sitio fijo se nota: el pegote resbala sobre la pantalla.
Aqui se busca la pantalla en CADA fotograma y se deforma la conversacion a las
cuatro esquinas que se hayan encontrado.

Como se encuentra la pantalla: es una mancha muy oscura (10-30 de brillo) sobre
un fondo claro (90-190), asi que se recorre fila a fila desde el centro hacia
fuera hasta salirse de lo oscuro. Los bordes izquierdo y derecho se ajustan por
minimos cuadrados -- las esquinas del movil son redondeadas y tomarlas tal cual
daria un cuadrilatero encogido.

  p7-encajar.py --ver 1        dibuja el cuadrilatero sobre ese fotograma
  p7-encajar.py --medir        mide los 192 y escribe /tmp/p7/esquinas.json
  p7-encajar.py --componer     genera el plano 6 con la conversacion dentro
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter

FRAMES_P6 = Path('/tmp/p6f')
FRAMES_P7 = Path('/tmp/p7/frames')
SALIDA = Path('/tmp/p7/compuesto')
ESQUINAS = Path('/tmp/p7/esquinas.json')

N = 192              # fotogramas del plano 6
UMBRAL = 60          # por debajo de esto es pantalla apagada
SEMILLA = (720, 360)  # un punto que cae dentro de la pantalla en el fotograma 1
ANCHO_MIN = 60       # una fila mas estrecha que esto ya no es pantalla


def franjas(px, w, h):
    """De cada fila, el tramo oscuro que contiene el centro de la pantalla."""
    x0, y0 = SEMILLA
    filas = {}
    for direccion in (-1, 1):
        centro = x0
        y = y0
        while 0 <= y < h:
            if px[centro, y] > UMBRAL:
                # el centro se ha salido: se busca lo oscuro mas cercano
                encontrado = None
                for d in range(1, 90):
                    for c in (centro - d, centro + d):
                        if 0 <= c < w and px[c, y] <= UMBRAL:
                            encontrado = c
                            break
                    if encontrado:
                        break
                if encontrado is None:
                    break
                centro = encontrado
            izq = centro
            while izq > 0 and px[izq - 1, y] <= UMBRAL:
                izq -= 1
            der = centro
            while der < w - 1 and px[der + 1, y] <= UMBRAL:
                der += 1
            if der - izq < ANCHO_MIN:
                break
            filas[y] = (izq, der)
            centro = (izq + der) // 2
            y += direccion
    return filas


def recta(puntos):
    """Minimos cuadrados x = a*y + b."""
    n = len(puntos)
    sy = sum(y for y, _ in puntos)
    sx = sum(x for _, x in puntos)
    syy = sum(y * y for y, _ in puntos)
    sxy = sum(y * x for y, x in puntos)
    den = n * syy - sy * sy
    if den == 0:
        return 0.0, sx / n
    a = (n * sxy - sy * sx) / den
    b = (sx - a * sy) / n
    return a, b


def esquinas(ruta):
    """Las cuatro esquinas de la pantalla: arriba-izq, arriba-der, abajo-der, abajo-izq."""
    im = Image.open(ruta).convert('L')
    w, h = im.size
    filas = franjas(im.load(), w, h)
    if len(filas) < 100:
        raise SystemExit('%s: solo %d filas de pantalla, algo va mal' % (ruta.name, len(filas)))

    ys = sorted(filas)
    arriba, abajo = ys[0], ys[-1]
    alto = abajo - arriba
    # Se descarta el 12% de arriba y de abajo: ahi las esquinas redondeadas
    # estrechan la fila y torcerian las rectas.
    centro = [y for y in ys if arriba + alto * 0.12 <= y <= abajo - alto * 0.12]
    ai, bi = recta([(y, filas[y][0]) for y in centro])
    ad, bd = recta([(y, filas[y][1]) for y in centro])

    return [
        (ai * arriba + bi, arriba),
        (ad * arriba + bd, arriba),
        (ad * abajo + bd, abajo),
        (ai * abajo + bi, abajo),
    ]


def coeficientes(destino, origen):
    """Coeficientes de PIL para llevar el rectangulo origen al cuadrilatero destino.

    PIL mapea al reves de lo que uno espera: pide la transformacion que, dado un
    pixel del resultado, dice de donde sacarlo. Por eso destino va primero.
    """
    A, B = [], []
    for (xd, yd), (xo, yo) in zip(destino, origen):
        A.append([xd, yd, 1, 0, 0, 0, -xo * xd, -xo * yd])
        B.append(xo)
        A.append([0, 0, 0, xd, yd, 1, -yo * xd, -yo * yd])
        B.append(yo)

    # Gauss con pivoteo parcial. Ocho ecuaciones: no merece traer numpy.
    n = 8
    for i in range(n):
        p = max(range(i, n), key=lambda r: abs(A[r][i]))
        A[i], A[p] = A[p], A[i]
        B[i], B[p] = B[p], B[i]
        if abs(A[i][i]) < 1e-12:
            raise SystemExit('sistema degenerado: el cuadrilatero no vale')
        for r in range(i + 1, n):
            f = A[r][i] / A[i][i]
            for c in range(i, n):
                A[r][c] -= f * A[i][c]
            B[r] -= f * B[i]
    x = [0.0] * n
    for i in range(n - 1, -1, -1):
        s = sum(A[i][c] * x[c] for c in range(i + 1, n))
        x[i] = (B[i] - s) / A[i][i]
    return x


def ver(indice):
    ruta = FRAMES_P6 / ('f%04d.png' % indice)
    q = esquinas(ruta)
    im = Image.open(ruta).convert('RGB')
    d = ImageDraw.Draw(im)
    # rojo: lo que encuentra el buscador (el movil entero)
    d.polygon([(round(x), round(y)) for x, y in q], outline=(255, 40, 40))
    # verde: donde acaba pegandose la conversacion (el cristal)
    d.polygon([(round(x), round(y)) for x, y in encoger(q)], outline=(60, 255, 120))
    for x, y in q:
        d.ellipse([x - 5, y - 5, x + 5, y + 5], fill=(255, 210, 0))
    destino = Path('/tmp/p7/verificacion-%04d.png' % indice)
    im.save(destino)
    print(destino, [(round(x), round(y)) for x, y in q])


def medir():
    todas = []
    for i in range(1, N + 1):
        todas.append(esquinas(FRAMES_P6 / ('f%04d.png' % i)))
        if i % 48 == 0:
            print('  medidos', i, 'de', N)
    ESQUINAS.write_text(json.dumps(todas), encoding='utf-8')
    alturas = [q[3][1] - q[0][1] for q in todas]
    izqs = [q[0][0] for q in todas]
    print('escrito', ESQUINAS)
    print('alto de la pantalla: %d a %d px' % (min(alturas), max(alturas)))
    print('borde izquierdo: %d a %d px  (recorrido %d)' %
          (min(izqs), max(izqs), max(izqs) - min(izqs)))


# Cuanto hay que meterse hacia dentro desde lo que detecta el buscador de manchas
# oscuras. Ese buscador encuentra el MOVIL, no la pantalla: el marco metalico es
# casi tan oscuro como el cristal apagado. Sin esto, la conversacion se derrama
# por debajo del telefono y cae sobre los dedos.
MARGEN_LADO = 0.045
MARGEN_ARRIBA = 0.028
MARGEN_ABAJO = 0.055

# Las esquinas del movil son muy redondeadas. Con la conversacion en angulo recto
# asomaban cuatro picos de color, que era lo que mas delataba el pegote.
RADIO = 0.085   # del ancho de la pantalla


def encoger(q):
    """Del contorno del movil al rectangulo del cristal."""
    (aix, aiy), (adx, ady), (bdx, bdy), (bix, biy) = q

    def punto(u, v):
        # bilineal: u de izquierda a derecha, v de arriba a abajo
        xa = aix + (adx - aix) * u
        ya = aiy + (ady - aiy) * u
        xb = bix + (bdx - bix) * u
        yb = biy + (bdy - biy) * u
        return (xa + (xb - xa) * v, ya + (yb - ya) * v)

    u0, u1 = MARGEN_LADO, 1 - MARGEN_LADO
    v0, v1 = MARGEN_ARRIBA, 1 - MARGEN_ABAJO
    return [punto(u0, v0), punto(u1, v0), punto(u1, v1), punto(u0, v1)]


# Medido sobre el propio plano 6, no estimado:
#   - el pixel mas brillante de toda la escena es 241, y el percentil 99,5 es 215.
#     El chat trae blancos de 255, o sea que la pantalla brillaba mas que nada de
#     lo que hay en la habitacion. Eso, mas que el borde, es lo que la despegaba.
#   - el grano de la camara es de 1,3 niveles. La captura no tiene ninguno, y una
#     zona perfectamente limpia dentro de una imagen con grano se ve pegada.
TECHO_BLANCO = 232
GRANO = 1.3
SUAVIZADO = 3.2   # en pixeles del chat; la pantalla se ve a un tercio de ese tamano

# El reflejo del cristal. En el plano apagado la pantalla marca 10-30: lo que pasa
# de 14 es luz reflejada de la habitacion, y es lo unico que se suma.
UMBRAL_REFLEJO = 14
FUERZA_REFLEJO = 0.55


def mascara_pantalla(tam):
    """Silueta del cristal: rectangulo de esquinas redondeadas, con el borde suave.

    El borde va bastante difuminado a proposito. Un canto duro delata el montaje
    aunque todo lo demas este bien.
    """
    w, h = tam
    m = Image.new('L', tam, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], radius=int(w * RADIO), fill=255)
    return m.filter(ImageFilter.GaussianBlur(6))


def integrar(pantalla, escena):
    """Que la pantalla parezca encendida ahi, y no una captura pegada encima.

    Antes se mezclaba un 14% de la escena para heredar el reflejo del cristal, y
    salio mal: el reflejo de este plano es una cara entera, y manchaba el fondo
    del chat de gris sucio. Un movil encendido apenas refleja. Se deja un 6%,
    solo para que coja la temperatura calida de la habitacion, y la sensacion de
    pantalla se consigue con la luz propia: mas clara arriba, donde da la ventana.
    """
    # Los blancos del chat no pueden brillar mas que lo mas brillante del plano.
    techo = pantalla.point(lambda v: int(v * TECHO_BLANCO / 255))

    mezcla = Image.blend(techo, escena, 0.04)

    # El reflejo del cristal. Un cristal SUMA luz, nunca oscurece: por eso el
    # primer intento -- mezclar la escena entera al 14% -- salio sucio, metia la
    # cara reflejada como una mancha gris. Aqui se coge solo lo CLARO del reflejo
    # original (la ventana, la piel iluminada) y se suma. Sin esto la pantalla
    # queda mate, y una pantalla mate dentro de una escena con cristales delata
    # el montaje aunque el borde este perfecto.
    brillo = escena.point(lambda v: max(0, int((v - UMBRAL_REFLEJO) * FUERZA_REFLEJO)))
    mezcla = ImageChops.add(mezcla, brillo.filter(ImageFilter.GaussianBlur(3)))

    # Degradado claro arriba, que es de donde entra la luz de la ventana.
    # linear_gradient va de 0 arriba a 255 abajo, asi que se le da la vuelta.
    arriba = Image.linear_gradient('L').transpose(Image.FLIP_TOP_BOTTOM).resize(mezcla.size)
    con_luz = Image.composite(ImageEnhance.Brightness(mezcla).enhance(1.05),
                              ImageEnhance.Brightness(mezcla).enhance(0.94),
                              arriba)

    # Y el grano de la camara, para que la pantalla no sea la unica zona limpia
    # de un plano que lo tiene por todas partes.
    ruido = Image.effect_noise(con_luz.size, GRANO).convert('RGB')
    return ImageChops.add(con_luz, ruido, scale=1, offset=-128)


# Cuanto se suaviza la trayectoria de las esquinas, en fotogramas. La pantalla se
# busca en cada fotograma por separado y la medida tiene un error de uno o dos
# pixeles que cambia en cada uno: la mano se mueve suave, pero el cuadrilatero da
# saltitos y la conversacion tiembla dentro del movil. El movimiento de verdad
# recorre 50-60 px en 8 s, o sea lentisimo, asi que se puede filtrar fuerte sin
# comerse nada real.
SUAVIZADO_TRAYECTORIA = 3.5


def suavizar_trayectoria(todas):
    """Filtro gaussiano en el tiempo sobre las ocho coordenadas del cuadrilatero."""
    n = len(todas)
    radio = int(SUAVIZADO_TRAYECTORIA * 3)
    pesos = [2.718281828 ** (-(d * d) / (2 * SUAVIZADO_TRAYECTORIA ** 2))
             for d in range(-radio, radio + 1)]
    total = sum(pesos)

    suave = []
    for i in range(n):
        esquinas_i = []
        for e in range(4):
            punto = []
            for eje in (0, 1):
                acum = 0.0
                for k, p in enumerate(pesos):
                    j = min(max(i + k - radio, 0), n - 1)   # se replica en los extremos
                    acum += todas[j][e][eje] * p
                punto.append(acum / total)
            esquinas_i.append(tuple(punto))
        suave.append(esquinas_i)
    return suave


def vaiven(cuantos):
    """Indices del plano 6 para durar lo que dure la conversacion.

    El plano 6 son 8 s y la conversacion 11, asi que el fondo se queda corto
    justo antes de la confirmacion, que es lo unico que el plano tiene que
    contar. Se va y se vuelve: como la camara esta quieta y lo unico que pasa es
    el balanceo de la mano, la vuelta no se distingue de la ida. Alargar el clip
    ralentizandolo si se habria notado.
    """
    ciclo = list(range(1, N + 1)) + list(range(N - 1, 1, -1))
    seq = []
    while len(seq) < cuantos:
        seq += ciclo
    return seq[:cuantos]


def componer():
    todas = suavizar_trayectoria(json.loads(ESQUINAS.read_text(encoding='utf-8')))
    SALIDA.mkdir(parents=True, exist_ok=True)
    chats = sorted(FRAMES_P7.glob('f*.png'))
    if not chats:
        raise SystemExit('no hay fotogramas del plano 7 en %s' % FRAMES_P7)

    indices = vaiven(len(chats))
    for k, i in enumerate(indices):
        fondo = Image.open(FRAMES_P6 / ('f%04d.png' % i)).convert('RGB')
        # El suavizado va antes de deformar: hecho despues, el desenfoque
        # arrastraria el negro de fuera de la pantalla y dejaria un halo oscuro
        # justo en el borde, que es lo que se quiere evitar.
        chat = Image.open(chats[k]).convert('RGB').filter(
            ImageFilter.GaussianBlur(SUAVIZADO))

        q = encoger(todas[i - 1])
        w, hgt = chat.size
        origen = [(0, 0), (w, 0), (w, hgt), (0, hgt)]
        c = coeficientes(q, origen)

        deformado = chat.transform(fondo.size, Image.PERSPECTIVE, c, Image.BICUBIC)
        mascara = mascara_pantalla(chat.size).transform(
            fondo.size, Image.PERSPECTIVE, c, Image.BICUBIC)
        fondo.paste(integrar(deformado, fondo), (0, 0), mascara)
        fondo.save(SALIDA / ('f%04d.png' % (k + 1)))
        if (k + 1) % 48 == 0:
            print('  compuestos', k + 1, 'de', len(indices))
    print('compuestos', len(indices), 'fotogramas en', SALIDA)


if __name__ == '__main__':
    if '--ver' in sys.argv:
        ver(int(sys.argv[sys.argv.index('--ver') + 1]))
    elif '--medir' in sys.argv:
        medir()
    elif '--componer' in sys.argv:
        componer()
    else:
        print(__doc__)
