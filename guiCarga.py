import pygame
import sys
import subprocess
import os

pygame.init()

usuario_actual = sys.argv[1]
juego = sys.argv[2]  # "polisopa" o el nombre que uses para el otro juego

if juego == "polisopa":
    pathJuego = os.path.join(os.path.dirname(__file__), "guiPoliSopa.py")
    registro = os.path.join(os.path.dirname(__file__), "registroSopa.txt")
else:
    pathJuego = os.path.join(os.path.dirname(__file__), "guiPoliPalabras.py")
    registro = os.path.join(os.path.dirname(__file__), "registroPoliPalabras.txt")

ANCHO, ALTO = 800, 600  # Más grande para mejor estética y espacio
COLOR_FONDO = (245, 245, 240)  # Mármol claro
COLOR_BOTON = (212, 175, 55)   # Dorado
COLOR_BOTON2 = (100, 100, 180) # Azul clásico
COLOR_TEXTO = (44, 62, 80)     # Gris piedra
COLOR_BOTON_TEXTO = (44, 62, 80)
COLOR_LISTA = (230, 230, 210)  # Mármol suave
COLOR_LISTA_HOVER = (255, 245, 180)
FUENTE = pygame.font.Font("augustus/AUGUSTUS.ttf", 32)
FUENTE_LISTA = pygame.font.Font("augustus/AUGUSTUS.ttf", 24)

pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Selecciona una opción")

def draw_gradient(surface, color1, color2, ancho, alto):
    for y in range(alto):
        ratio = y / alto
        r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
        g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
        b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
        pygame.draw.line(surface, (r, g, b), (0, y), (ancho, y))

def obtener_partidas_usuario(registro, usuario):
    if not os.path.exists(registro):
        return []
    with open(registro, "r", encoding="utf-8") as f:
        contenido = f.read().split("=== PARTIDA ===")
        partidas = []
        for idx, p in enumerate(contenido):
            lineas = [line.strip() for line in p.strip().splitlines() if line.strip()]
            if lineas and lineas[0].startswith(f"USUARIO:{usuario}"):
                # Busca el nombre personalizado
                nombre = None
                for line in lineas:
                    if line.startswith("NOMBRE:"):
                        nombre = line.split(":",1)[1].strip()
                        break
                if not nombre:
                    nombre = f"Partida {idx+1}"
                partidas.append(nombre)
        return partidas

def ventana_lista_partidas(partidas):
    seleccion = None
    scroll = 0
    max_visible = 4
    lista_ancho = 600  # Más ancho, casi toda la ventana
    lista_x = (ANCHO - lista_ancho) // 2
    item_alto = 64
    espacio_y = 24
    while True:
        draw_gradient(pantalla, (245, 245, 240), (220, 220, 210), ANCHO, ALTO)
        titulo = FUENTE.render("Selecciona una partida:", True, COLOR_BOTON)
        pantalla.blit(titulo, (ANCHO//2 - titulo.get_width()//2, 30))
        botones = []
        visible_partidas = partidas[scroll:scroll+max_visible]
        mouse_pos = pygame.mouse.get_pos()
        for i, nombre in enumerate(visible_partidas):
            rect = pygame.Rect(lista_x, 100 + i*(item_alto + espacio_y), lista_ancho, item_alto)
            botones.append(rect)
            is_hover = rect.collidepoint(mouse_pos)
            color = COLOR_LISTA_HOVER if is_hover else COLOR_LISTA
            shadow_rect = rect.move(3, 3)
            pygame.draw.rect(pantalla, (220, 210, 180), shadow_rect, border_radius=14)
            pygame.draw.rect(pantalla, color, rect, border_radius=14)
            pygame.draw.rect(pantalla, COLOR_BOTON, rect, 2, border_radius=14)
            txt = FUENTE_LISTA.render(nombre, True, COLOR_TEXTO)
            pantalla.blit(
                txt,
                (rect.x + rect.w // 2 - txt.get_width() // 2, rect.y + rect.h // 2 - txt.get_height() // 2)
            )
        # Flechas de scroll si hay más partidas
        if scroll > 0:
            pygame.draw.polygon(
                pantalla, COLOR_BOTON,
                [(ANCHO//2 - 20, 90), (ANCHO//2 + 20, 90), (ANCHO//2, 60)]
            )
        if scroll + max_visible < len(partidas):
            y_arrow = 100 + max_visible * (item_alto + espacio_y) - espacio_y // 2
            pygame.draw.polygon(
                pantalla, COLOR_BOTON,
                [(ANCHO//2 - 20, y_arrow), (ANCHO//2 + 20, y_arrow), (ANCHO//2, y_arrow + 30)]
            )
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for i, rect in enumerate(botones):
                        if rect.collidepoint(event.pos):
                            seleccion = i + scroll
                            break
                elif event.button == 4 and scroll > 0:
                    scroll -= 1
                elif event.button == 5 and scroll + max_visible < len(partidas):
                    scroll += 1
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and scroll > 0:
                    scroll -= 1
                if event.key == pygame.K_DOWN and scroll + max_visible < len(partidas):
                    scroll += 1
        if seleccion is not None:
            break
        pygame.display.flip()
    return seleccion

def main():
    boton_ancho = 340   # Más ancho
    boton_alto = 100    # Más alto
    boton_nueva = pygame.Rect(ANCHO//2 - boton_ancho - 40, 320, boton_ancho, boton_alto)
    boton_cargar = pygame.Rect(ANCHO//2 + 40, 320, boton_ancho, boton_alto)
    while True:
        draw_gradient(pantalla, (245, 245, 240), (220, 220, 210), ANCHO, ALTO)
        pygame.draw.line(pantalla, COLOR_BOTON, (100, 120), (ANCHO-100, 120), 5)
        titulo = FUENTE.render("¿Qué deseas hacer?", True, COLOR_BOTON)
        pantalla.blit(titulo, (ANCHO//2 - titulo.get_width()//2, 70))
        # Botón Nueva Partida
        shadow_nueva = boton_nueva.move(4, 4)
        pygame.draw.rect(pantalla, (220, 210, 180), shadow_nueva, border_radius=18)
        pygame.draw.rect(pantalla, COLOR_BOTON, boton_nueva, border_radius=18)
        pygame.draw.rect(pantalla, (180, 150, 40), boton_nueva, 4, border_radius=18)
        txt_nueva = FUENTE.render("Partida Nueva", True, COLOR_BOTON_TEXTO)
        pantalla.blit(txt_nueva, (boton_nueva.x + boton_nueva.w//2 - txt_nueva.get_width()//2, boton_nueva.y + boton_nueva.h//2 - txt_nueva.get_height()//2))
        # Botón Cargar Partida
        shadow_cargar = boton_cargar.move(4, 4)
        pygame.draw.rect(pantalla, (220, 210, 180), shadow_cargar, border_radius=18)
        pygame.draw.rect(pantalla, COLOR_BOTON2, boton_cargar, border_radius=18)
        pygame.draw.rect(pantalla, (80, 80, 180), boton_cargar, 4, border_radius=18)
        txt_cargar = FUENTE.render("Cargar Partida", True, COLOR_BOTON_TEXTO)
        pantalla.blit(txt_cargar, (boton_cargar.x + boton_cargar.w//2 - txt_cargar.get_width()//2, boton_cargar.y + boton_cargar.h//2 - txt_cargar.get_height()//2))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if boton_nueva.collidepoint(event.pos):
                    pygame.quit()
                    subprocess.run([sys.executable, pathJuego, usuario_actual])
                    sys.exit()
                if boton_cargar.collidepoint(event.pos):
                    partidas = obtener_partidas_usuario(registro, usuario_actual)
                    if not partidas:
                        msg = FUENTE.render("No hay partidas guardadas.", True, (200,0,0))
                        pantalla.blit(msg, (ANCHO//2 - msg.get_width()//2, 180))
                        pygame.display.flip()
                        pygame.time.wait(1500)
                        continue
                    seleccion = ventana_lista_partidas(partidas)
                    if seleccion is not None:
                        pygame.quit()
                        subprocess.run([sys.executable, pathJuego, usuario_actual, str(seleccion)])
                        sys.exit()
        pygame.display.flip()

if __name__ == "__main__":
    main()