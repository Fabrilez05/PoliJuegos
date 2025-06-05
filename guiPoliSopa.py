import pygame
import sys
import time
import os
import subprocess
import random
from logicaPoliSopa import PoliSopa, cargar_diccionario, seleccionar_palabras

# --- Configuración de colores, fuentes y tamaños ---
ANCHO_CASILLA = 60
ALTO_CASILLA = 60
MARGEN = 5
ANCHO_BOTON = 120
ALTO_BOTON = 50
FUENTE_SIZE = 32

COLOR_FONDO = (245, 245, 240)
COLOR_TEXTO = (44, 62, 80)
COLOR_BOTON = (212, 175, 55)
COLOR_BOTON2 = (100, 100, 180)
COLOR_BOTON_TEXTO = (44, 62, 80)
COLOR_CASILLA = (255, 255, 255)
COLOR_CASILLA_SELEC = (173, 216, 230)
COLOR_SOMBRA = (220, 210, 180)

# --- Inicialización de pygame y fuentes ---
pygame.init()
FUENTE = pygame.font.Font("augustus/AUGUSTUS.ttf", 32)
FUENTE_TITULO = pygame.font.Font("dalek_pinpoint/DalekPinpointBold.ttf", 48)
FUENTE_BOTON = pygame.font.Font("augustus/AUGUSTUS.ttf", 28)

# --- Obtención de usuario y partida desde argumentos ---
usuario_actual = sys.argv[1] if len(sys.argv) > 1 else "anonimo"
indice_partida = int(sys.argv[2]) if len(sys.argv) > 2 else None
nombre_partida = None

# --- Función para cargar una partida guardada desde archivo ---
def cargar_partida(nombre_archivo="registroSopa.txt", usuario=None, indice=0):
    import os
    if not os.path.exists(nombre_archivo):
        return None
    with open(nombre_archivo, "r", encoding="utf-8") as f:
        contenido = f.read().split("=== PARTIDA ===")
        partidas = []
        for p in contenido:
            lineas = [line.strip() for line in p.strip().splitlines() if line.strip()]
            if lineas and lineas[0].startswith("USUARIO:"):
                user = lineas[0].split(":",1)[1]
                if user == usuario:
                    partidas.append(lineas)
        if not partidas or indice is None or indice >= len(partidas):
            return None
        datos = partidas[indice]
        i = 1
        finalizada = False
        nombre_partida = None
        for line in datos:
            if line.startswith("FINALIZADA:"):
                finalizada = line.split(":",1)[1].strip().upper() == "SI"
            if line.startswith("NOMBRE:"):
                nombre_partida = line.split(":",1)[1].strip()
        while i < len(datos) and (not datos[i] or ',' not in datos[i]):
            i += 1
        if i >= len(datos):
            return None
        filas, columnas = map(int, datos[i].split(","))
        i += 1
        tablero = []
        while i < len(datos) and datos[i] and not datos[i].startswith("PALABRAS:"):
            tablero.append(list(datos[i]))
            i += 1
        while i < len(datos) and not datos[i].startswith("PALABRAS:"):
            i += 1
        i += 1
        palabras_cargar = []
        while i < len(datos) and datos[i] and not datos[i].startswith("ENCONTRADAS:"):
            palabras_cargar.append(datos[i])
            i += 1
        while i < len(datos) and not datos[i].startswith("ENCONTRADAS:"):
            i += 1
        i += 1
        palabras_encontradas_cargar = []
        while i < len(datos) and datos[i] and not datos[i].startswith("TIEMPO:"):
            palabras_encontradas_cargar.append(datos[i])
            i += 1
        while i < len(datos) and not datos[i].startswith("TIEMPO:"):
            i += 1
        tiempo_cargar = 0
        if i < len(datos):
            tiempo_line = datos[i]
            if ":" in tiempo_line:
                try:
                    tiempo_cargar = int(tiempo_line.split(":")[1].strip())
                except ValueError:
                    tiempo_cargar = 0
            elif i+1 < len(datos) and datos[i+1].isdigit():
                tiempo_cargar = int(datos[i+1].strip())
        return filas, columnas, tablero, palabras_cargar, palabras_encontradas_cargar, tiempo_cargar, finalizada, nombre_partida

# --- Inicialización de partida: carga o nueva ---
if indice_partida is not None:
    partida = cargar_partida(nombre_archivo="registroSopa.txt", usuario=usuario_actual, indice=indice_partida)
    if partida:
        filas, columnas, tablero, palabras, palabras_encontradas, tiempo_guardado, partida_finalizada, nombre_partida = partida
        juego = PoliSopa(palabras, filas=filas, columnas=columnas)
        juego.tablero = tablero
        palabras_encontradas = palabras_encontradas
        tiempo_inicio = time.time() - tiempo_guardado
    else:
        diccionario = cargar_diccionario("diccPoliSopa.txt")
        palabras = seleccionar_palabras(diccionario)
        print("Palabras a encontrar:", palabras)
        juego = PoliSopa(palabras, filas=5, columnas=6)
        palabras_encontradas = []
        tiempo_inicio = time.time()
        partida_finalizada = False
        nombre_partida = None
else:
    diccionario = cargar_diccionario("diccPoliSopa.txt")
    palabras = seleccionar_palabras(diccionario)
    print("Palabras a encontrar:", palabras)
    juego = PoliSopa(palabras, filas=8, columnas=10)
    palabras_encontradas = []
    tiempo_inicio = time.time()
    partida_finalizada = False
    nombre_partida = None

# --- Cálculo de dimensiones de la ventana principal ---
PANEL_LATERAL_ANCHO = 340
MARGEN_IZQ = 60
MARGEN_SUP = 120
ancho = juego.columnas * (ANCHO_CASILLA + MARGEN) + PANEL_LATERAL_ANCHO + MARGEN_IZQ * 2 + 80
alto = max(juego.filas * (ALTO_CASILLA + MARGEN) + 220, 700)
pantalla = pygame.display.set_mode((ancho, alto))
pygame.display.set_caption("PoliSopa")

# --- Variables de estado del juego ---
seleccionadas = []
usos_pista = 0
penalizacion_total = 0
pistas_reveladas = {}  # palabra: [índices de letras reveladas]
clock = pygame.time.Clock()
mensaje_pista = ""
mensaje_pista_tiempo = 0

# --- Función para mostrar mensajes temporales de pista ---
def mostrar_mensaje_pista(texto):
    global mensaje_pista, mensaje_pista_tiempo
    mensaje_pista = texto
    mensaje_pista_tiempo = pygame.time.get_ticks()

# --- Dibuja el tablero de letras en pantalla ---
def dibujar_tablero():
    for i in range(juego.filas):
        for j in range(juego.columnas):
            x = MARGEN_IZQ + j * (ANCHO_CASILLA + MARGEN)
            y = MARGEN_SUP + i * (ALTO_CASILLA + MARGEN)
            rect = pygame.Rect(x, y, ANCHO_CASILLA, ALTO_CASILLA)
            shadow_rect = rect.move(3, 3)
            pygame.draw.rect(pantalla, COLOR_SOMBRA, shadow_rect, border_radius=10)
            color = COLOR_CASILLA_SELEC if (i, j) in seleccionadas else COLOR_CASILLA
            pygame.draw.rect(pantalla, color, rect, border_radius=10)
            pygame.draw.rect(pantalla, COLOR_BOTON, rect, 2, border_radius=10)
            letra = juego.tablero[i][j]
            img = FUENTE.render(letra, True, COLOR_TEXTO)
            pantalla.blit(img, (x + ANCHO_CASILLA//2 - img.get_width()//2, y + ALTO_CASILLA//2 - img.get_height()//2))

# --- Dibuja la bandeja con la palabra seleccionada actualmente ---
def dibujar_bandeja():
    texto = ''.join([juego.tablero[f][c] for (f, c) in seleccionadas])
    img = FUENTE.render(texto, True, (0, 0, 0))
    x = MARGEN_IZQ
    y = MARGEN_SUP + juego.filas * (ALTO_CASILLA + MARGEN) + 18
    pygame.draw.rect(pantalla, (230,230,210), (x, y, juego.columnas * (ANCHO_CASILLA + MARGEN) - MARGEN, 48), border_radius=10)
    pantalla.blit(img, (x + 12, y + 8))

# --- Dibuja los botones de Borrar y Aplicar debajo del tablero ---
def dibujar_botones():
    total_ancho = 2 * ANCHO_BOTON + 20
    x1 = MARGEN_IZQ + (juego.columnas * (ANCHO_CASILLA + MARGEN) - total_ancho) // 2
    y1 = MARGEN_SUP + juego.filas * (ALTO_CASILLA + MARGEN) + 80
    rect_borrar = pygame.Rect(x1, y1, ANCHO_BOTON, ALTO_BOTON)
    shadow_rect_borrar = rect_borrar.move(3, 3)
    pygame.draw.rect(pantalla, (220, 150, 150), shadow_rect_borrar, border_radius=12)
    pygame.draw.rect(pantalla, (220, 100, 100), rect_borrar, border_radius=12)
    img_borrar = FUENTE_BOTON.render("Borrar", True, (255, 255, 255))
    pantalla.blit(img_borrar, (x1 + ANCHO_BOTON//2 - img_borrar.get_width()//2, y1 + ALTO_BOTON//2 - img_borrar.get_height()//2))
    x2 = x1 + ANCHO_BOTON + 20
    rect_aplicar = pygame.Rect(x2, y1, ANCHO_BOTON, ALTO_BOTON)
    shadow_rect_aplicar = rect_aplicar.move(3, 3)
    pygame.draw.rect(pantalla, (150, 220, 150), shadow_rect_aplicar, border_radius=12)
    pygame.draw.rect(pantalla, (100, 180, 100), rect_aplicar, border_radius=12)
    img_aplicar = FUENTE_BOTON.render("Aplicar", True, (255, 255, 255))
    pantalla.blit(img_aplicar, (x2 + ANCHO_BOTON//2 - img_aplicar.get_width()//2, y1 + ALTO_BOTON//2 - img_aplicar.get_height()//2))
    return rect_borrar, rect_aplicar

# --- Dibuja el botón de guardar partida ---
def dibujar_boton_guardar(x, y):
    ANCHO_GUARDAR = 140
    ALTO_GUARDAR = 54
    rect_guardar = pygame.Rect(x, y, ANCHO_GUARDAR, ALTO_GUARDAR)
    shadow_rect_guardar = rect_guardar.move(3, 3)
    pygame.draw.rect(pantalla, (255, 235, 120), shadow_rect_guardar, border_radius=12)
    pygame.draw.rect(pantalla, COLOR_BOTON, rect_guardar, border_radius=12)
    img_guardar = FUENTE_BOTON.render("Guardar", True, COLOR_BOTON_TEXTO)
    pantalla.blit(img_guardar, (x + ANCHO_GUARDAR//2 - img_guardar.get_width()//2, y + ALTO_GUARDAR//2 - img_guardar.get_height()//2))
    return rect_guardar

# --- Verifica si dos celdas son adyacentes ---
def es_adyacente(c1, c2):
    return abs(c1[0] - c2[0]) + abs(c1[1] - c2[1]) == 1

# --- Maneja el click del usuario sobre el tablero ---
def manejar_click(pos):
    for i in range(juego.filas):
        for j in range(juego.columnas):
            x = MARGEN_IZQ + j * (ANCHO_CASILLA + MARGEN)
            y = MARGEN_SUP + i * (ALTO_CASILLA + MARGEN)
            rect = pygame.Rect(x, y, ANCHO_CASILLA, ALTO_CASILLA)
            if rect.collidepoint(pos):
                if seleccionadas and (i, j) == seleccionadas[-1]:
                    seleccionadas.pop()
                    return
                if (i, j) in seleccionadas:
                    return
                if len(seleccionadas) >= 9:
                    return
                if not seleccionadas or es_adyacente(seleccionadas[-1], (i, j)):
                    seleccionadas.append((i, j))
                return

# --- Dibuja la tabla de progreso de palabras encontradas y pistas ---
def mostrar_tabla_progreso():
    x0 = MARGEN_IZQ + juego.columnas * (ANCHO_CASILLA + MARGEN) + 40
    y0 = MARGEN_SUP + 10
    tam_celda = 40
    espacio_y = 10
    for palabra in palabras:
        indices_pista = pistas_reveladas.get(palabra, [])
        for idx, letra in enumerate(palabra):
            x = x0 + idx * (tam_celda + 2)
            y = y0
            rect = pygame.Rect(x, y, tam_celda, tam_celda)
            shadow_rect = rect.move(2, 2)
            if palabra in palabras_encontradas:
                color = (100, 200, 100)
                texto = letra
            elif idx == 0 or idx in indices_pista:
                color = (255, 255, 255)
                texto = letra
            else:
                color = (200, 200, 200)
                texto = "_"
            pygame.draw.rect(pantalla, (200, 200, 220), shadow_rect, border_radius=8)
            pygame.draw.rect(pantalla, color, rect, border_radius=8)
            pygame.draw.rect(pantalla, (0, 0, 0), rect, 2, border_radius=8)
            img = FUENTE.render(texto, True, (0, 0, 0))
            pantalla.blit(img, (x + tam_celda//2 - img.get_width()//2, y + tam_celda//2 - img.get_height()//2))
        y0 += tam_celda + espacio_y

# --- Guarda el estado de la partida en archivo ---
def guardar_partida(nombre_archivo="registroSopa.txt", usuario=None, indice=None, nombre_partida=None, finalizada=False, tiempo_final=None):
    if not os.path.exists(nombre_archivo):
        partidas = []
    else:
        with open(nombre_archivo, "r", encoding="utf-8") as f:
            contenido = f.read().split("=== PARTIDA ===")
            partidas = [p for p in contenido if p.strip()]
    registro = "USUARIO:{}\n".format(usuario)
    if nombre_partida:
        registro += "NOMBRE:{}\n".format(nombre_partida)
    if finalizada:
        registro += "FINALIZADA:SI\n"
    registro += f"{juego.filas},{juego.columnas}\n"
    for fila in juego.tablero:
        registro += ''.join(fila) + "\n"
    registro += "PALABRAS:\n"
    for palabra in palabras:
        registro += palabra + "\n"
    registro += "ENCONTRADAS:\n"
    for palabra in palabras_encontradas:
        registro += palabra + "\n"
    if tiempo_final is not None:
        registro += f"TIEMPO:{tiempo_final}\n"
    else:
        tiempo_actual = int(time.time() - tiempo_inicio)
        registro += f"TIEMPO:{tiempo_actual}\n"
    registro += "=== FIN PARTIDA ===\n\n"
    nuevas_partidas = []
    for p in partidas:
        lineas = [line.strip() for line in p.strip().splitlines() if line.strip()]
        if not lineas:
            continue
        es_misma = False
        if lineas[0].startswith("USUARIO:") and f"NOMBRE:{nombre_partida}" in lineas:
            user = lineas[0].split(":",1)[1]
            if user == usuario:
                es_misma = True
        if not es_misma:
            nuevas_partidas.append(p)
    nuevas_partidas.append(registro)
    with open(nombre_archivo, "w", encoding="utf-8") as f:
        for p in nuevas_partidas:
            f.write("=== PARTIDA ===\n" + p)

# --- Solicita al usuario el nombre de la partida mediante una ventana ---
def pedir_nombre_partida(main_size):
    ANCHO_VENTANA = 700
    ALTO_VENTANA = 320
    ventana = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA))
    fuente = pygame.font.Font("augustus/AUGUSTUS.ttf", 30)
    input_box = pygame.Rect(80, 110, 540, 60)
    boton_guardar = pygame.Rect(140, 210, 420, 60)
    color_inactive = (220, 210, 180)
    color_active = (100, 180, 100)
    color = color_inactive
    active = False
    text = ''
    done = False

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.display.set_mode(main_size)
                return "SinNombre"
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = True
                else:
                    active = False
                color = color_active if active else color_inactive
                if boton_guardar.collidepoint(event.pos):
                    done = True
            if event.type == pygame.KEYDOWN and active:
                if event.key == pygame.K_RETURN:
                    done = True
                elif event.key == pygame.K_BACKSPACE:
                    text = text[:-1]
                else:
                    if len(text) < 20:
                        text += event.unicode

        ventana.fill((245, 245, 240))
        txt_surface = fuente.render("NOMBRE DE LA PARTIDA:", True, (44, 62, 80))
        ventana.blit(txt_surface, (ANCHO_VENTANA//2 - txt_surface.get_width()//2, 10))
        pygame.draw.rect(ventana, color, input_box, 2, border_radius=14)
        txt_surface2 = fuente.render(text, True, (44, 62, 80))
        ventana.blit(txt_surface2, (input_box.x+16, input_box.y+14))
        pygame.draw.rect(ventana, (212, 175, 55), boton_guardar, border_radius=18)
        txt_guardar = fuente.render("GUARDAR PARTIDA", True, (44, 62, 80))
        ventana.blit(txt_guardar, (boton_guardar.x + boton_guardar.w//2 - txt_guardar.get_width()//2, boton_guardar.y + 10))
        pygame.display.flip()

    pygame.display.set_mode(main_size)
    return text if text else "SinNombre"

# --- Muestra la ventana de victoria al finalizar la partida ---
def ventana_victoria(palabras_encontradas, tiempo_total, usuario_actual, indice_partida, nombre_partida):
    import pygame
    import sys
    import os
    import subprocess
    ANCHO, ALTO = 500, 400
    pantalla_victoria = pygame.display.set_mode((ANCHO, ALTO))
    fuente_titulo = pygame.font.SysFont(None, 48)
    fuente = pygame.font.SysFont(None, 32)
    fuente_btn = pygame.font.SysFont(None, 28)
    boton_menu = pygame.Rect(80, 320, 150, 50)
    boton_salir = pygame.Rect(270, 320, 150, 50)
    while True:
        pantalla_victoria.fill((240, 240, 240))
        titulo = fuente_titulo.render("¡GANASTE!", True, (0, 120, 0))
        pantalla_victoria.blit(titulo, (ANCHO//2 - titulo.get_width()//2, 30))
        subtitulo = fuente.render("Palabras encontradas:", True, (0,0,0))
        pantalla_victoria.blit(subtitulo, (40, 100))
        for i, palabra in enumerate(palabras_encontradas):
            txt = fuente.render(palabra, True, (0,0,0))
            pantalla_victoria.blit(txt, (60, 130 + i*30))
        minutos = tiempo_total // 60
        segundos = tiempo_total % 60
        tiempo_txt = fuente.render(f"Tiempo de juego: {minutos:02d}:{segundos:02d}", True, (0,0,0))
        pantalla_victoria.blit(tiempo_txt, (40, 130 + len(palabras_encontradas)*30 + 20))
        pygame.draw.rect(pantalla_victoria, (100,180,100), boton_menu)
        pygame.draw.rect(pantalla_victoria, (180,100,100), boton_salir)
        txt_menu = fuente_btn.render("Ir al menú", True, (255,255,255))
        txt_salir = fuente_btn.render("Salir", True, (255,255,255))
        pantalla_victoria.blit(txt_menu, (boton_menu.x + boton_menu.w//2 - txt_menu.get_width()//2, boton_menu.y + 12))
        pantalla_victoria.blit(txt_salir, (boton_salir.x + boton_salir.w//2 - txt_salir.get_width()//2, boton_salir.y + 12))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                guardar_partida(nombre_archivo="registroSopa.txt", usuario=usuario_actual, indice=indice_partida, nombre_partida=nombre_partida, finalizada=True, tiempo_final=tiempo_total)
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if boton_menu.collidepoint(event.pos):
                    guardar_partida(nombre_archivo="registroSopa.txt", usuario=usuario_actual, indice=indice_partida, nombre_partida=nombre_partida, finalizada=True, tiempo_final=tiempo_total)
                    pygame.quit()
                    dirScript = os.path.dirname(os.path.abspath(__file__))
                    pathMenu = os.path.join(dirScript, "guiMenu.py")
                    subprocess.run([sys.executable, pathMenu, usuario_actual])
                    sys.exit()
                if boton_salir.collidepoint(event.pos):
                    guardar_partida(nombre_archivo="registroSopa.txt", usuario=usuario_actual, indice=indice_partida, nombre_partida=nombre_partida, finalizada=True, tiempo_final=tiempo_total)
                    pygame.quit()
                    sys.exit()
        pygame.display.flip()

# --- Busca el índice de una partida guardada por usuario y nombre ---
def obtener_indice_partida(usuario, nombre_partida, nombre_archivo="registroSopa.txt"):
    if not os.path.exists(nombre_archivo):
        return None
    with open(nombre_archivo, "r", encoding="utf-8") as f:
        contenido = f.read().split("=== PARTIDA ===")
        for idx, p in enumerate(contenido):
            lineas = [line.strip() for line in p.strip().splitlines() if line.strip()]
            if not lineas:
                continue
            if lineas[0].startswith("USUARIO:") and f"NOMBRE:{nombre_partida}" in lineas:
                user = lineas[0].split(":",1)[1]
                if user == usuario:
                    return idx
    return None

# --- Dibuja un degradado vertical en la superficie dada ---
def draw_gradient(surface, color1, color2, ancho, alto):
    for y in range(alto):
        ratio = y / alto
        r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
        g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
        b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
        pygame.draw.line(surface, (r, g, b), (0, y), (ancho, y))

# --- Calcula la posición Y final de la tabla de progreso ---
def obtener_y_final_tabla_progreso():
    tam_celda = 40
    espacio_y = 10
    y0 = MARGEN_SUP + 10
    return y0 + len(palabras) * (tam_celda + espacio_y)

# --- Ventana para el minijuego de cara o cruz para obtener pista ---
def ventana_cara_cruz():
    ANCHO, ALTO = 400, 320
    ventana = pygame.display.set_mode((ANCHO, ALTO))
    fuente = pygame.font.Font("augustus/AUGUSTUS.ttf", 32)
    fuente_btn = pygame.font.Font("augustus/AUGUSTUS.ttf", 28)
    boton_cara = pygame.Rect(60, 220, 120, 50)
    boton_cruz = pygame.Rect(220, 220, 120, 50)
    eleccion = None
    resultado = None
    animando = False
    frame = 0
    img_cara = pygame.transform.scale(pygame.image.load("caramoneda.png"), (120, 120))
    img_cruz = pygame.transform.scale(pygame.image.load("cruzmoneda.png"), (120, 120))
    moneda_imgs = [img_cara, img_cruz]
    while True:
        ventana.fill((245, 245, 240))
        txt = fuente.render("Elige: Cara o Cruz", True, COLOR_BOTON)
        ventana.blit(txt, (ANCHO//2 - txt.get_width()//2, 40))
        pygame.draw.rect(ventana, (220, 210, 180), boton_cara.move(3,3), border_radius=12)
        pygame.draw.rect(ventana, COLOR_BOTON, boton_cara, border_radius=12)
        txt_cara = fuente_btn.render("CARA", True, COLOR_BOTON_TEXTO)
        ventana.blit(txt_cara, (boton_cara.x + boton_cara.w//2 - txt_cara.get_width()//2, boton_cara.y + boton_cara.h//2 - txt_cara.get_height()//2))
        pygame.draw.rect(ventana, (220, 210, 180), boton_cruz.move(3,3), border_radius=12)
        pygame.draw.rect(ventana, COLOR_BOTON2, boton_cruz, border_radius=12)
        txt_cruz = fuente_btn.render("CRUZ", True, (255,255,255))
        ventana.blit(txt_cruz, (boton_cruz.x + boton_cruz.w//2 - txt_cruz.get_width()//2, boton_cruz.y + boton_cruz.h//2 - txt_cruz.get_height()//2))
        if animando:
            img = moneda_imgs[frame % 2]
            ventana.blit(img, (ANCHO//2 - 60, 80))
            pygame.display.flip()
            pygame.time.wait(120)
            frame += 1
            if frame > 12:
                resultado = random.choice(["cara", "cruz"])
                img = img_cara if resultado == "cara" else img_cruz
                ventana.blit(img, (ANCHO//2 - 60, 80))
                pygame.display.flip()
                pygame.time.wait(800)
                pygame.display.set_mode((ancho, alto))
                return eleccion == resultado
            continue
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.display.set_mode((ancho, alto))
                return False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if boton_cara.collidepoint(event.pos):
                    eleccion = "cara"
                    animando = True
                if boton_cruz.collidepoint(event.pos):
                    eleccion = "cruz"
                    animando = True
        pygame.display.flip()

# --- Aplica una pista a una palabra aleatoria no encontrada ---
def dar_pista():
    global usos_pista
    palabras_restantes = [p for p in palabras if p not in palabras_encontradas and p not in pistas_reveladas]
    if not palabras_restantes:
        return
    palabra = random.choice(palabras_restantes)
    letras = list(palabra)
    random.shuffle(letras)
    mitad = max(1, len(letras)//2)
    indices_revelar = sorted(random.sample(range(len(letras)), mitad))
    pistas_reveladas[palabra] = indices_revelar
    mostrar_mensaje_pista(f"Pista aplicada a: {palabra.upper()}")

# --- Ventana de ayuda con las reglas del juego ---
def ventana_como_jugar():
    ayuda_texto = [
        "Reglas de PoliSopa:",
        "",
        "- Encuentra las 7 palabras ocultas en la sopa de letras.",
        "- Selecciona letras adyacentes para formar palabras.",
        "- Haz clic en 'Aplicar' para validar tu selección.",
        "- Si la palabra es correcta, se marcará como encontrada.",
        "",
        "Pistas y penalizaciones:",
        "- Puedes pedir una pista con el botón 'PISTA'.",
        "- Para obtenerla, debes ganar un cara o cruz.",
        "- Cada vez que pides una pista, se suma una penalización de tiempo.",
        "- La penalización aumenta cada vez que usas una pista.",
        "- Si ganas, se revelan letras de una palabra no encontrada.",
        "- Si pierdes, solo se suma la penalización.",
        "",
        "¡Diviértete jugando PoliSopa!"
    ]
    ANCHO, ALTO = 920, 670
    ventana = pygame.display.set_mode((ANCHO, ALTO))
    fuente = pygame.font.Font("augustus/AUGUSTUS.ttf", 20)
    fuente_titulo = pygame.font.Font("dalek_pinpoint/DalekPinpointBold.ttf", 30)
    boton_cerrar = pygame.Rect(ANCHO//2 - 80, ALTO - 70, 160, 48)
    while True:
        ventana.fill((245, 245, 240))
        titulo = fuente_titulo.render("¿Cómo Jugar?", True, COLOR_BOTON)
        ventana.blit(titulo, (ANCHO//2 - titulo.get_width()//2, 24))
        y = 80
        for linea in ayuda_texto:
            txt = fuente.render(linea, True, COLOR_TEXTO)
            ventana.blit(txt, (40, y))
            y += 32
        pygame.draw.rect(ventana, COLOR_BOTON, boton_cerrar, border_radius=12)
        txt_cerrar = fuente.render("Cerrar", True, COLOR_BOTON_TEXTO)
        ventana.blit(txt_cerrar, (boton_cerrar.x + boton_cerrar.w//2 - txt_cerrar.get_width()//2, boton_cerrar.y + 8))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.display.set_mode((ancho, alto))
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                if boton_cerrar.collidepoint(event.pos):
                    pygame.display.set_mode((ancho, alto))
                    return
        pygame.display.flip()

# --- Bucle principal del juego ---
if __name__ == "__main__":
    # Define los botones superiores
    boton_como_jugar = pygame.Rect(40, 30, 230, 44)
    BOTON_VOLVER = pygame.Rect(boton_como_jugar.right + 20, 30, 140, 44)

    while True:
        pantalla.fill((240, 240, 240))
        draw_gradient(pantalla, COLOR_FONDO, (220, 220, 210), ancho, alto)

        # Dibuja botón ¿Cómo Jugar?
        pygame.draw.rect(pantalla, COLOR_BOTON, boton_como_jugar, border_radius=12)
        fuente_boton_como_jugar = pygame.font.Font("augustus/AUGUSTUS.ttf", 22)
        txt_como_jugar = fuente_boton_como_jugar.render("¿Cómo Jugar?", True, COLOR_BOTON_TEXTO)
        pantalla.blit(txt_como_jugar, (boton_como_jugar.x + boton_como_jugar.w//2 - txt_como_jugar.get_width()//2, boton_como_jugar.y + 8))

        # Dibuja botón Volver
        pygame.draw.rect(pantalla, COLOR_BOTON, BOTON_VOLVER, border_radius=12)
        fuente_volver = pygame.font.Font("augustus/AUGUSTUS.ttf", 22)
        txt_volver = fuente_volver.render("Volver", True, COLOR_BOTON_TEXTO)
        pantalla.blit(txt_volver, (BOTON_VOLVER.x + BOTON_VOLVER.w//2 - txt_volver.get_width()//2, BOTON_VOLVER.y + BOTON_VOLVER.h//2 - txt_volver.get_height()//2))

        # Dibuja título y línea decorativa
        titulo = FUENTE_TITULO.render("PoliSopa", True, COLOR_BOTON)
        pantalla.blit(titulo, (ancho // 2 - titulo.get_width() // 2, 30))
        pygame.draw.line(pantalla, COLOR_BOTON, (40, MARGEN_SUP - 10), (ancho-40, MARGEN_SUP - 10), 5)

        dibujar_tablero()
        dibujar_bandeja()
        mostrar_tabla_progreso()

        # Calcula posición de panel lateral y botones de acción
        x_panel = MARGEN_IZQ + juego.columnas * (ANCHO_CASILLA + MARGEN) + 60
        y_panel = obtener_y_final_tabla_progreso() + 10

        # Muestra el tiempo de juego
        if not partida_finalizada:
            tiempo_actual = int(time.time() - tiempo_inicio)
        else:
            tiempo_actual = tiempo_guardado
        minutos = tiempo_actual // 60
        segundos = tiempo_actual % 60
        texto_tiempo = f"Tiempo: {minutos:02d}:{segundos:02d}"
        img_tiempo = FUENTE.render(texto_tiempo, True, (0, 0, 0))
        pantalla.blit(img_tiempo, (x_panel, y_panel))

        # Dibuja botón Guardar
        ANCHO_GUARDAR = 180
        ALTO_GUARDAR = 60
        y_guardar = y_panel + img_tiempo.get_height() + 18
        rect_guardar = pygame.Rect(x_panel, y_guardar, ANCHO_GUARDAR, ALTO_GUARDAR)
        shadow_rect_guardar = rect_guardar.move(3, 3)
        pygame.draw.rect(pantalla, (255, 235, 120), shadow_rect_guardar, border_radius=14)
        pygame.draw.rect(pantalla, COLOR_BOTON, rect_guardar, border_radius=14)
        img_guardar = FUENTE_BOTON.render("GUARDAR", True, COLOR_BOTON_TEXTO)
        pantalla.blit(img_guardar, (rect_guardar.x + rect_guardar.w//2 - img_guardar.get_width()//2, y_guardar + ALTO_GUARDAR//2 - img_guardar.get_height()//2))

        # Dibuja botón Pista
        ANCHO_PISTA = 180
        ALTO_PISTA = 60
        x_pista = x_panel + ANCHO_GUARDAR + 30
        y_pista = y_guardar
        rect_pista = pygame.Rect(x_pista, y_pista, ANCHO_PISTA, ALTO_PISTA)
        shadow_rect_pista = rect_pista.move(3, 3)
        pygame.draw.rect(pantalla, (200, 200, 255), shadow_rect_pista, border_radius=14)
        pygame.draw.rect(pantalla, COLOR_BOTON2, rect_pista, border_radius=14)
        img_pista = FUENTE_BOTON.render("PISTA", True, (255, 255, 255))
        pantalla.blit(img_pista, (rect_pista.x + rect_pista.w//2 - img_pista.get_width()//2, rect_pista.y + rect_pista.h//2 - img_pista.get_height()//2))

        # Dibuja botones de acción (Borrar y Aplicar)
        ANCHO_ACCION = 180
        ALTO_ACCION = 60
        espacio_btn = 30
        y_accion = y_pista + ALTO_PISTA + 24
        rect_borrar = pygame.Rect(x_panel, y_accion, ANCHO_ACCION, ALTO_ACCION)
        rect_aplicar = pygame.Rect(x_panel + ANCHO_ACCION + espacio_btn, y_accion, ANCHO_ACCION, ALTO_ACCION)
        for rect, color, texto_btn in [
            (rect_borrar, (220, 100, 100), "BORRAR"),
            (rect_aplicar, (100, 180, 100), "APLICAR")
        ]:
            shadow_rect = rect.move(3, 3)
            pygame.draw.rect(pantalla, (220, 210, 180), shadow_rect, border_radius=14)
            pygame.draw.rect(pantalla, color, rect, border_radius=14)
            img_btn = FUENTE_BOTON.render(texto_btn, True, (255, 255, 255))
            pantalla.blit(img_btn, (rect.x + rect.w//2 - img_btn.get_width()//2, rect.y + rect.h//2 - img_btn.get_height()//2))

        # Muestra mensaje de pista si corresponde
        if mensaje_pista and pygame.time.get_ticks() - mensaje_pista_tiempo < 4000:
            img = FUENTE_BOTON.render(mensaje_pista, True, (100, 60, 180))
            x_msg = ancho // 2 + titulo.get_width() // 2 + 30
            y_msg = 40
            pantalla.blit(img, (x_msg, y_msg))

        # --- Manejo de eventos del usuario ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if boton_como_jugar.collidepoint(event.pos):
                    ventana_como_jugar()
                    continue
                if BOTON_VOLVER.collidepoint(event.pos):
                    pygame.quit()
                    dirScript = os.path.dirname(os.path.abspath(__file__))
                    pathMenu = os.path.join(dirScript, "guiMenu.py")
                    subprocess.run([sys.executable, pathMenu, usuario_actual])
                    sys.exit()
                if not partida_finalizada:
                    if rect_guardar.collidepoint(event.pos):
                        if indice_partida is None:
                            main_size = pantalla.get_size()
                            nombre_partida = pedir_nombre_partida(main_size)
                            guardar_partida(nombre_archivo="registroSopa.txt", usuario=usuario_actual, indice=None, nombre_partida=nombre_partida)
                            indice_partida = obtener_indice_partida(usuario_actual, nombre_partida)
                        else:
                            guardar_partida(nombre_archivo="registroSopa.txt", usuario=usuario_actual, indice=indice_partida, nombre_partida=nombre_partida)
                        print("Partida guardada en registroSopa.txt")
                    elif rect_borrar.collidepoint(event.pos):
                        seleccionadas.clear()
                    elif rect_aplicar.collidepoint(event.pos):
                        texto = ''.join([juego.tablero[f][c] for (f, c) in seleccionadas])
                        if texto in palabras and texto not in palabras_encontradas:
                            palabras_encontradas.append(texto)
                            seleccionadas.clear()
                            # --- CHEQUEO DE VICTORIA ---
                            if len(palabras_encontradas) == 7:
                                tiempo_total = int(time.time() - tiempo_inicio)
                                ventana_victoria(
                                    palabras_encontradas,
                                    tiempo_total,
                                    usuario_actual,
                                    indice_partida,
                                    nombre_partida
                                )
                                break
                        else:
                            seleccionadas.clear()
                    elif rect_pista.collidepoint(event.pos):
                        penalizacion = 30 * (2 ** usos_pista)
                        tiempo_inicio -= penalizacion
                        if ventana_cara_cruz():
                            dar_pista()
                            mostrar_mensaje_pista("¡Has ganado la pista!")
                        else:
                            mostrar_mensaje_pista("¡No has ganado la pista!")
                        usos_pista += 1
                    else:
                        manejar_click(event.pos)

        pygame.display.flip()
        clock.tick(60)