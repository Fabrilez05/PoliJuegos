import pygame
import sys
import time
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

diccionario = cargar_diccionario("diccPoliSopa.txt")
palabras = seleccionar_palabras(diccionario)
print("Palabras a encontrar:", palabras)
juego = PoliSopa(palabras, filas=8, columnas=10)

# --- Dimensiones ventana ---
ancho = juego.columnas * (ANCHO_CASILLA + MARGEN) + 700
alto = juego.filas * (ALTO_CASILLA + MARGEN) + 200

pantalla = pygame.display.set_mode((ancho, alto))
pygame.display.set_caption("PoliSopa")

# --- Variables de estado ---
seleccionadas = []
palabras_encontradas = []

clock = pygame.time.Clock()
tiempo_inicio = time.time()

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

def guardar_partida(nombre_archivo="registroSopa.txt"):
    with open(nombre_archivo, "w", encoding="utf-8") as f:
        # Guardar dimensiones
        f.write(f"{juego.filas},{juego.columnas}\n")
        # Guardar tablero
        for fila in juego.tablero:
            f.write(''.join(fila) + "\n")
        # Guardar palabras a buscar
        f.write("PALABRAS:\n")
        for palabra in palabras:
            f.write(palabra + "\n")
        # Guardar palabras encontradas
        f.write("ENCONTRADAS:\n")
        for palabra in palabras_encontradas:
            f.write(palabra + "\n")
        # Guardar tiempo transcurrido
        tiempo_actual = int(time.time() - tiempo_inicio)
        f.write(f"TIEMPO:\n{tiempo_actual}\n")

# --- Main loop ---
if __name__ == "__main__":
    while True:
        pantalla.fill((240, 240, 240))
        dibujar_tablero()
        dibujar_bandeja()
        rect_borrar, rect_aplicar = dibujar_botones()
        mostrar_tabla_progreso()

        # Mostrar contador de tiempo (donde antes iba el gif)
        tiempo_actual = int(time.time() - tiempo_inicio)
        minutos = tiempo_actual // 60
        segundos = tiempo_actual % 60
        texto_tiempo = f"Tiempo: {minutos:02d}:{segundos:02d}"
        x_tiempo = juego.columnas * (ANCHO_CASILLA + MARGEN) + 40
        y_tiempo = juego.filas * (ALTO_CASILLA + MARGEN) + 20
        img_tiempo = fuente.render(texto_tiempo, True, (0, 0, 0))
        pantalla.blit(img_tiempo, (x_tiempo, y_tiempo))

        # Botón Guardar a la derecha del timer
        x_guardar = x_tiempo + img_tiempo.get_width() + 30
        y_guardar = y_tiempo - 10
        rect_guardar = dibujar_boton_guardar(x_guardar, y_guardar)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if rect_guardar.collidepoint(event.pos):
                    guardar_partida()
                    print("Partida guardada en registroSopa.txt")
                elif rect_borrar.collidepoint(event.pos):
                    seleccionadas.clear()
                elif rect_aplicar.collidepoint(event.pos):
                    texto = ''.join([juego.tablero[f][c] for (f, c) in seleccionadas])
                    if texto in palabras and texto not in palabras_encontradas:
                        palabras_encontradas.append(texto)
                    seleccionadas.clear()
                else:
                    manejar_click(event.pos)

        pygame.display.flip()
        clock.tick(60)