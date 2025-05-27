import pygame
import sys
import time
import os
import subprocess
from logicaPoliSopa import PoliSopa, cargar_diccionario, seleccionar_palabras

# --- Configuración ---
ANCHO_CASILLA = 60
ALTO_CASILLA = 60
MARGEN = 5
ANCHO_BOTON = 120
ALTO_BOTON = 50
FUENTE_SIZE = 32

# --- Inicialización ---
pygame.init()
fuente = pygame.font.SysFont(None, FUENTE_SIZE)

usuario_actual = sys.argv[1] if len(sys.argv) > 1 else "anonimo"
indice_partida = int(sys.argv[2]) if len(sys.argv) > 2 else None
nombre_partida = None

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
        i = 1  # Saltar línea de usuario
        finalizada = False
        nombre_partida = None
        # Buscar si está finalizada y el nombre
        for line in datos:
            if line.startswith("FINALIZADA:"):
                finalizada = line.split(":",1)[1].strip().upper() == "SI"
            if line.startswith("NOMBRE:"):
                nombre_partida = line.split(":",1)[1].strip()
        # Buscar la línea de dimensiones
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

if indice_partida is not None:
    partida = cargar_partida(nombre_archivo="registroSopa.txt", usuario=usuario_actual, indice=indice_partida)
    if partida:
        filas, columnas, tablero, palabras, palabras_encontradas, tiempo_guardado, partida_finalizada, nombre_partida = partida
        juego = PoliSopa(palabras, filas=filas, columnas=columnas)
        juego.tablero = tablero
        palabras_encontradas = palabras_encontradas
        tiempo_inicio = time.time() - tiempo_guardado
    else:
        # Si no se pudo cargar, inicia nueva partida
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

# --- Dimensiones ventana ---
ancho = juego.columnas * (ANCHO_CASILLA + MARGEN) + 700
alto = juego.filas * (ALTO_CASILLA + MARGEN) + 200

pantalla = pygame.display.set_mode((ancho, alto))
pygame.display.set_caption("PoliSopa")

# --- Variables de estado ---
seleccionadas = []

clock = pygame.time.Clock()

def dibujar_tablero():
    for i in range(juego.filas):
        for j in range(juego.columnas):
            x = MARGEN + j * (ANCHO_CASILLA + MARGEN)
            y = MARGEN + i * (ALTO_CASILLA + MARGEN)
            rect = pygame.Rect(x, y, ANCHO_CASILLA, ALTO_CASILLA)
            color = (173, 216, 230) if (i, j) in seleccionadas else (255, 255, 255)
            pygame.draw.rect(pantalla, color, rect)
            pygame.draw.rect(pantalla, (0, 0, 0), rect, 2)
            letra = juego.tablero[i][j]
            img = fuente.render(letra, True, (0, 0, 0))
            pantalla.blit(img, (x + ANCHO_CASILLA//2 - img.get_width()//2, y + ALTO_CASILLA//2 - img.get_height()//2))

def dibujar_bandeja():
    texto = ''.join([juego.tablero[f][c] for (f, c) in seleccionadas])
    img = fuente.render(texto, True, (0, 0, 0))
    x = MARGEN
    y = juego.filas * (ALTO_CASILLA + MARGEN) + MARGEN
    pantalla.blit(img, (x, y))

def dibujar_botones():
    # Botón Borrar
    x1 = MARGEN
    y1 = juego.filas * (ALTO_CASILLA + MARGEN) + 60
    rect_borrar = pygame.Rect(x1, y1, ANCHO_BOTON, ALTO_BOTON)
    pygame.draw.rect(pantalla, (220, 100, 100), rect_borrar)
    img_borrar = fuente.render("Borrar", True, (255, 255, 255))
    pantalla.blit(img_borrar, (x1 + ANCHO_BOTON//2 - img_borrar.get_width()//2, y1 + ALTO_BOTON//2 - img_borrar.get_height()//2))

    # Botón Aplicar
    x2 = x1 + ANCHO_BOTON + 20
    rect_aplicar = pygame.Rect(x2, y1, ANCHO_BOTON, ALTO_BOTON)
    pygame.draw.rect(pantalla, (100, 180, 100), rect_aplicar)
    img_aplicar = fuente.render("Aplicar", True, (255, 255, 255))
    pantalla.blit(img_aplicar, (x2 + ANCHO_BOTON//2 - img_aplicar.get_width()//2, y1 + ALTO_BOTON//2 - img_aplicar.get_height()//2))

    return rect_borrar, rect_aplicar

def dibujar_boton_guardar(x, y):
    ANCHO_GUARDAR = 120
    ALTO_GUARDAR = 50
    rect_guardar = pygame.Rect(x, y, ANCHO_GUARDAR, ALTO_GUARDAR)
    pygame.draw.rect(pantalla, (255, 215, 0), rect_guardar)  # Amarillo
    img_guardar = fuente.render("Guardar", True, (0, 0, 0))
    pantalla.blit(img_guardar, (x + ANCHO_GUARDAR//2 - img_guardar.get_width()//2, y + ALTO_GUARDAR//2 - img_guardar.get_height()//2))
    return rect_guardar

def es_adyacente(c1, c2):
    return abs(c1[0] - c2[0]) + abs(c1[1] - c2[1]) == 1

def manejar_click(pos):
    # Tablero
    for i in range(juego.filas):
        for j in range(juego.columnas):
            x = MARGEN + j * (ANCHO_CASILLA + MARGEN)
            y = MARGEN + i * (ALTO_CASILLA + MARGEN)
            rect = pygame.Rect(x, y, ANCHO_CASILLA, ALTO_CASILLA)
            if rect.collidepoint(pos):
                if seleccionadas and (i, j) == seleccionadas[-1]:
                    seleccionadas.pop()  # Permite deshacer la última selección
                    return
                if (i, j) in seleccionadas:
                    return  # Ya seleccionada (no permite seleccionar dos veces)
                # Limita la cantidad máxima de letras seleccionadas a 9
                if len(seleccionadas) >= 9:
                    return
                if not seleccionadas or es_adyacente(seleccionadas[-1], (i, j)):
                    seleccionadas.append((i, j))
                return

def mostrar_tabla_progreso():
    x0 = juego.columnas * (ANCHO_CASILLA + MARGEN) + 40
    y0 = MARGEN
    tam_celda = 40
    espacio_y = 10

    for palabra in palabras:
        for idx, letra in enumerate(palabra):
            x = x0 + idx * (tam_celda + 2)
            y = y0
            if palabra in palabras_encontradas:
                color = (100, 200, 100)  # Verde si encontrada
                texto = letra
            else:
                if idx == 0:
                    color = (255, 255, 255)  # Blanco para la primera letra
                    texto = letra
                else:
                    color = (200, 200, 200)  # Gris para las no encontradas
                    texto = "_"
            rect = pygame.Rect(x, y, tam_celda, tam_celda)
            pygame.draw.rect(pantalla, color, rect)
            pygame.draw.rect(pantalla, (0, 0, 0), rect, 2)
            img = fuente.render(texto, True, (0, 0, 0))
            pantalla.blit(img, (x + tam_celda//2 - img.get_width()//2, y + tam_celda//2 - img.get_height()//2))
        y0 += tam_celda + espacio_y

def guardar_partida(nombre_archivo="registroSopa.txt", usuario=None, indice=None, nombre_partida=None, finalizada=False, tiempo_final=None):
    # Lee todas las partidas
    if not os.path.exists(nombre_archivo):
        partidas = []
    else:
        with open(nombre_archivo, "r", encoding="utf-8") as f:
            contenido = f.read().split("=== PARTIDA ===")
            partidas = [p for p in contenido if p.strip()]

    # Construye el nuevo registro
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

    # Elimina cualquier partida previa del mismo usuario y nombre
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

    # Guarda todas las partidas
    with open(nombre_archivo, "w", encoding="utf-8") as f:
        for p in nuevas_partidas:
            f.write("=== PARTIDA ===\n" + p)

def pedir_nombre_partida(main_size):
    import pygame
    ventana = pygame.display.set_mode((400, 180))
    fuente = pygame.font.SysFont(None, 32)
    input_box = pygame.Rect(50, 60, 300, 40)
    boton_guardar = pygame.Rect(150, 120, 100, 40)
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = color_inactive
    active = False
    text = ''
    done = False
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
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
        ventana.fill((240,240,240))
        txt_surface = fuente.render("Nombre de la partida:", True, (0,0,0))
        ventana.blit(txt_surface, (50, 20))
        pygame.draw.rect(ventana, color, input_box, 2)
        txt_surface2 = fuente.render(text, True, (0,0,0))
        ventana.blit(txt_surface2, (input_box.x+5, input_box.y+8))
        pygame.draw.rect(ventana, (100,180,100), boton_guardar)
        txt_guardar = fuente.render("Guardar", True, (255,255,255))
        ventana.blit(txt_guardar, (boton_guardar.x + boton_guardar.w//2 - txt_guardar.get_width()//2, boton_guardar.y + 8))
        pygame.display.flip()
    # Restaura la ventana principal
    pygame.display.set_mode(main_size)
    return text if text else "SinNombre"

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

    # Botones
    boton_menu = pygame.Rect(80, 320, 150, 50)
    boton_salir = pygame.Rect(270, 320, 150, 50)

    while True:
        pantalla_victoria.fill((240, 240, 240))
        # Título
        titulo = fuente_titulo.render("¡GANASTE!", True, (0, 120, 0))
        pantalla_victoria.blit(titulo, (ANCHO//2 - titulo.get_width()//2, 30))

        # Palabras encontradas
        subtitulo = fuente.render("Palabras encontradas:", True, (0,0,0))
        pantalla_victoria.blit(subtitulo, (40, 100))
        for i, palabra in enumerate(palabras_encontradas):
            txt = fuente.render(palabra, True, (0,0,0))
            pantalla_victoria.blit(txt, (60, 130 + i*30))

        # Tiempo de juego
        minutos = tiempo_total // 60
        segundos = tiempo_total % 60
        tiempo_txt = fuente.render(f"Tiempo de juego: {minutos:02d}:{segundos:02d}", True, (0,0,0))
        pantalla_victoria.blit(tiempo_txt, (40, 130 + len(palabras_encontradas)*30 + 20))

        # Botones
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

# --- Main loop ---
if __name__ == "__main__":
    # Al inicio, después de crear la ventana principal
    BOTON_VOLVER = pygame.Rect(ancho - 140, 20, 120, 40)  # 20px de margen derecho

    while True:
        pantalla.fill((240, 240, 240))
        dibujar_tablero()
        dibujar_bandeja()
        rect_borrar, rect_aplicar = dibujar_botones()
        mostrar_tabla_progreso()

        # Mostrar contador de tiempo
        if not partida_finalizada:
            tiempo_actual = int(time.time() - tiempo_inicio)
        else:
            tiempo_actual = tiempo_guardado
        minutos = tiempo_actual // 60
        segundos = tiempo_actual % 60
        texto_tiempo = f"Tiempo: {minutos:02d}:{segundos:02d}"
        x_tiempo = juego.columnas * (ANCHO_CASILLA + MARGEN) + 40
        y_tiempo = juego.filas * (ALTO_CASILLA + MARGEN) + 20
        img_tiempo = fuente.render(texto_tiempo, True, (0, 0, 0))
        pantalla.blit(img_tiempo, (x_tiempo, y_tiempo))

        # Botón Guardar
        x_guardar = x_tiempo + img_tiempo.get_width() + 30
        y_guardar = y_tiempo - 10
        rect_guardar = dibujar_boton_guardar(x_guardar, y_guardar)

        pygame.draw.rect(pantalla, (180, 100, 100), BOTON_VOLVER)
        fuente_boton = pygame.font.SysFont(None, 28)
        txt_volver = fuente_boton.render("Volver", True, (255,255,255))
        pantalla.blit(txt_volver, (BOTON_VOLVER.x + BOTON_VOLVER.w//2 - txt_volver.get_width()//2,
                                   BOTON_VOLVER.y + BOTON_VOLVER.h//2 - txt_volver.get_height()//2))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
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
                            # Buscar el índice de la nueva partida
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
                                # Después de ventana_victoria, termina el bucle principal
                                break
                        else:
                            seleccionadas.clear()
                    else:
                        manejar_click(event.pos)

        pygame.display.flip()
        clock.tick(60)