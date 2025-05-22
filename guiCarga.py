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
    pathJuego = os.path.join(os.path.dirname(__file__), "UiPoliPalabras.py")
    registro = os.path.join(os.path.dirname(__file__), "registroPalabras.txt")

ANCHO, ALTO = 500, 300
COLOR_FONDO = (240, 240, 240)
COLOR_BOTON = (100, 180, 100)
COLOR_BOTON2 = (100, 100, 180)
COLOR_TEXTO = (0, 0, 0)
COLOR_BOTON_TEXTO = (255, 255, 255)
COLOR_LISTA = (220, 220, 255)
FUENTE = pygame.font.SysFont(None, 36)
FUENTE_LISTA = pygame.font.SysFont(None, 28)

pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Selecciona una opción")

def obtener_partidas_usuario(registro, usuario):
    if not os.path.exists(registro):
        return []
    with open(registro, "r", encoding="utf-8") as f:
        contenido = f.read().split("=== PARTIDA ===\n")
        partidas = []
        for idx, p in enumerate(contenido):
            if p.strip().startswith(f"USUARIO:{usuario}"):
                partidas.append(f"Partida {idx+1}")
        return partidas

def ventana_lista_partidas(partidas):
    seleccion = None
    scroll = 0
    max_visible = 4  # Número de partidas visibles a la vez
    while True:
        pantalla.fill(COLOR_FONDO)
        titulo = FUENTE.render("Selecciona una partida:", True, COLOR_TEXTO)
        pantalla.blit(titulo, (ANCHO//2 - titulo.get_width()//2, 30))
        botones = []
        visible_partidas = partidas[scroll:scroll+max_visible]
        for i, nombre in enumerate(visible_partidas):
            rect = pygame.Rect(100, 80 + i*50, 300, 40)
            botones.append(rect)
            pygame.draw.rect(pantalla, COLOR_LISTA, rect)
            pygame.draw.rect(pantalla, COLOR_TEXTO, rect, 2)
            txt = FUENTE_LISTA.render(nombre, True, COLOR_TEXTO)
            pantalla.blit(txt, (rect.x + 10, rect.y + 8))
        # Flechas de scroll si hay más partidas
        if scroll > 0:
            pygame.draw.polygon(pantalla, (80,80,80), [(250,70),(270,70),(260,55)])
        if scroll + max_visible < len(partidas):
            pygame.draw.polygon(pantalla, (80,80,80), [(250,80+max_visible*50),(270,80+max_visible*50),(260,95+max_visible*50)])
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Solo click izquierdo selecciona
                    for i, rect in enumerate(botones):
                        if rect.collidepoint(event.pos):
                            seleccion = i + scroll
                            break
                elif event.button == 4:  # Scroll up
                    if scroll > 0:
                        scroll -= 1
                elif event.button == 5:  # Scroll down
                    if scroll + max_visible < len(partidas):
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
    boton_nueva = pygame.Rect(70, 180, 160, 60)
    boton_cargar = pygame.Rect(270, 180, 160, 60)
    while True:
        pantalla.fill(COLOR_FONDO)
        titulo = FUENTE.render("¿Qué deseas hacer?", True, COLOR_TEXTO)
        pantalla.blit(titulo, (ANCHO//2 - titulo.get_width()//2, 60))
        pygame.draw.rect(pantalla, COLOR_BOTON, boton_nueva)
        pygame.draw.rect(pantalla, COLOR_BOTON2, boton_cargar)
        txt_nueva = FUENTE.render("Partida Nueva", True, COLOR_BOTON_TEXTO)
        txt_cargar = FUENTE.render("Cargar Partida", True, COLOR_BOTON_TEXTO)
        pantalla.blit(txt_nueva, (boton_nueva.x + boton_nueva.w//2 - txt_nueva.get_width()//2, boton_nueva.y + 15))
        pantalla.blit(txt_cargar, (boton_cargar.x + boton_cargar.w//2 - txt_cargar.get_width()//2, boton_cargar.y + 15))
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
                        pantalla.blit(msg, (ANCHO//2 - msg.get_width()//2, 120))
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