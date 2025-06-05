import pygame
import sys
import subprocess
import os

pygame.init()

# --- Configuración de la ventana y colores principales ---
PANTALLA_ANCHO = 1280
PANTALLA_ALTO = 760

COLOR_FONDO = (245, 245, 240)  # Mármol claro
COLOR_TEXTO = (44, 62, 80)     # Gris piedra
COLOR_INPUT = (255, 255, 255)
COLOR_INPUT_ACTIVO = (230, 230, 210)  # Mármol suave
COLOR_BOTON = (212, 175, 55)          # Dorado
COLOR_BOTON_HOVER = (255, 215, 100)   # Dorado claro
COLOR_BOTON_TEXTO = (44, 62, 80)      # Gris piedra
COLOR_LINK = (30, 60, 150)            # Azul clásico

pantalla = pygame.display.set_mode((PANTALLA_ANCHO, PANTALLA_ALTO))
pygame.display.set_caption("Juegos De Letras - Menu Principal")

# --- Fuentes personalizadas ---
fuenteTitulo = pygame.font.Font("dalek_pinpoint/DalekPinpointBold.ttf", 64)
fuenteBoton = pygame.font.Font("augustus/AUGUSTUS.ttf", 44)
fuenteUsuario = pygame.font.Font("augustus/AUGUSTUS.ttf", 28)

usuario_actual = sys.argv[1] if len(sys.argv) > 1 else None

# --- Clase para botones del menú principal ---
class Boton:
    def __init__(self, x, y, ancho, alto, texto, color, colorHover):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.Texto = texto
        self.Color = color
        self.ColorHover = colorHover
        self.estaHover = False

    def dibujar(self, superficie):
        # Dibuja el botón con sombra y texto centrado
        color = self.ColorHover if self.estaHover else self.Color
        shadow_rect = self.rect.move(4, 4)
        pygame.draw.rect(superficie, (220, 210, 180), shadow_rect, border_radius=16)
        pygame.draw.rect(superficie, color, self.rect, border_radius=16)
        pygame.draw.rect(superficie, (180, 150, 40), self.rect, 3, border_radius=16)
        textoSuperficie = fuenteBoton.render(self.Texto, True, COLOR_BOTON_TEXTO)
        textoRect = textoSuperficie.get_rect(center=self.rect.center)
        superficie.blit(textoSuperficie, textoRect)

    def checkHover(self, pos):
        # Cambia el estado hover según la posición del mouse
        self.estaHover = self.rect.collidepoint(pos)
        return self.estaHover

    def estaClickeado(self, pos, evento):
        # Devuelve True si el botón fue clickeado
        return evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1 and self.rect.collidepoint(pos)

# --- Dibuja un degradado vertical en la pantalla ---
def draw_gradient(surface, color1, color2, ancho, alto):
    for y in range(alto):
        ratio = y / alto
        r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
        g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
        b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
        pygame.draw.line(surface, (r, g, b), (0, y), (ancho, y))

# --- Menú principal: muestra los botones principales y maneja navegación ---
def menu_Main():
    botonAncho = 600
    botonAlto = 80
    botonX = PANTALLA_ANCHO // 2 - botonAncho // 2
    espacio_vertical = 60

    # Botones principales
    botonJugarPolipalabras = Boton(
        botonX,
        260,
        botonAncho,
        botonAlto,
        "Jugar Polipalabras",
        COLOR_BOTON,
        COLOR_BOTON_HOVER
    )
    botonPolisopa = Boton(
        botonX,
        260 + botonAlto + espacio_vertical,
        botonAncho,
        botonAlto,
        "Jugar PoliSopa",
        COLOR_BOTON,
        COLOR_BOTON_HOVER
    )
    botonMejores = Boton(
        botonX,
        260 + 2 * (botonAlto + espacio_vertical),
        botonAncho,
        botonAlto,
        "Mejores Jugadores",
        COLOR_BOTON,
        COLOR_BOTON_HOVER
    )

    # Botón para cerrar sesión
    boton_cerrar = pygame.Rect(PANTALLA_ANCHO // 2 - 120, 260 + 3 * (botonAlto + espacio_vertical), 240, 60)

    ejecutar = True

    while ejecutar:
        posMouse = pygame.mouse.get_pos()
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                ejecutar = False

            # Acciones de los botones principales
            if botonJugarPolipalabras.estaClickeado(posMouse, evento):
                pygame.quit()
                try:
                    dirScript = os.path.dirname(os.path.abspath(__file__))
                    pathJuego = os.path.join(dirScript, "guiPoliPalabras.py")
                    pathCarga = os.path.join(dirScript, "guiCarga.py")
                    registro = os.path.join(dirScript, "registroPoliPalabras.txt")
                    if hay_partidas_usuario(registro, usuario_actual):
                        subprocess.run([sys.executable, pathCarga, usuario_actual, "polipalabras"])
                    else:
                        subprocess.run([sys.executable, pathJuego, usuario_actual])
                except (FileNotFoundError, PermissionError) as e:
                    print(f"Error al ejecutar el juego: {e}")
                return

            if botonPolisopa.estaClickeado(posMouse, evento):
                pygame.quit()
                try:
                    dirScript = os.path.dirname(os.path.abspath(__file__))
                    pathJuego = os.path.join(dirScript, "guiPoliSopa.py")
                    pathCarga = os.path.join(dirScript, "guiCarga.py")
                    registro = os.path.join(dirScript, "registroSopa.txt")
                    if hay_partidas_usuario(registro, usuario_actual):
                        subprocess.run([sys.executable, pathCarga, usuario_actual, "polisopa"])
                    else:
                        subprocess.run([sys.executable, pathJuego, usuario_actual])
                except (FileNotFoundError, PermissionError) as e:
                    print(f"Error al ejecutar el juego: {e}")
                return

            if botonMejores.estaClickeado(posMouse, evento):
                ventana_elegir_juego_mejores()
                pygame.display.set_mode((PANTALLA_ANCHO, PANTALLA_ALTO))

            # Botón cerrar sesión
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if boton_cerrar.collidepoint(evento.pos):
                    pygame.quit()
                    dirScript = os.path.dirname(os.path.abspath(__file__))
                    pathLogin = os.path.join(dirScript, "guiLogIn.py")
                    subprocess.run([sys.executable, pathLogin])
                    sys.exit()

        # Actualiza el estado hover de los botones
        botonJugarPolipalabras.checkHover(posMouse)
        botonPolisopa.checkHover(posMouse)
        botonMejores.checkHover(posMouse)

        # Fondo degradado mármol y línea decorativa
        draw_gradient(pantalla, (245, 245, 240), (220, 220, 210), PANTALLA_ANCHO, PANTALLA_ALTO)
        pygame.draw.line(pantalla, COLOR_BOTON, (120, 160), (PANTALLA_ANCHO-120, 160), 5)

        # Título centrado
        textoTitulo = fuenteTitulo.render("Poli Juegos", True, COLOR_BOTON)
        pantalla.blit(textoTitulo, (PANTALLA_ANCHO // 2 - textoTitulo.get_width() // 2, 70))

        # Dibuja los botones principales con sombra
        for boton in [botonJugarPolipalabras, botonPolisopa, botonMejores]:
            shadow_rect = boton.rect.move(4, 4)
            pygame.draw.rect(pantalla, (220, 210, 180), shadow_rect, border_radius=16)
            boton.dibujar(pantalla)

        # Botón cerrar sesión centrado, con sombra y bordes redondeados
        shadow_cerrar = boton_cerrar.move(3, 3)
        pygame.draw.rect(pantalla, (160, 80, 80), shadow_cerrar, border_radius=14)
        pygame.draw.rect(pantalla, (180, 100, 100), boton_cerrar, border_radius=14)
        fuente_boton = pygame.font.Font("augustus/AUGUSTUS.ttf", 28)
        txt_cerrar = fuente_boton.render("Cerrar sesión", True, (255, 255, 255))
        pantalla.blit(txt_cerrar, (boton_cerrar.x + boton_cerrar.w // 2 - txt_cerrar.get_width() // 2,
                                   boton_cerrar.y + boton_cerrar.h // 2 - txt_cerrar.get_height() // 2))

        # Dibuja el texto del usuario si existe
        if usuario_actual:
            texto_usuario = fuenteUsuario.render(f"Usuario: {usuario_actual}", True, (0, 0, 0))
            pantalla.blit(texto_usuario, (30, 20))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

# --- Verifica si el usuario tiene partidas guardadas ---
def hay_partidas_usuario(nombre_archivo, usuario):
    if not os.path.exists(nombre_archivo):
        return False
    with open(nombre_archivo, "r", encoding="utf-8") as f:
        contenido = f.read().split("=== PARTIDA ===\n")
        for p in contenido:
            if p.strip().startswith(f"USUARIO:{usuario}"):
                return True
    return False

# --- Ventana para elegir el juego del ranking de mejores jugadores ---
def ventana_elegir_juego_mejores():
    ANCHO, ALTO = 600, 340
    ventana = pygame.display.set_mode((ANCHO, ALTO))
    fuente_titulo = pygame.font.Font("dalek_pinpoint/DalekPinpointBold.ttf", 38)
    fuente_boton = pygame.font.Font("augustus/AUGUSTUS.ttf", 22)
    boton_palabras = pygame.Rect(80, 120, 200, 70)
    boton_sopa = pygame.Rect(320, 120, 200, 70)
    boton_cerrar = pygame.Rect(ANCHO//2 - 80, ALTO - 70, 160, 48)
    while True:
        ventana.fill(COLOR_FONDO)
        titulo = fuente_titulo.render("Mejores Jugadores", True, COLOR_BOTON)
        ventana.blit(titulo, (ANCHO//2 - titulo.get_width()//2, 40))
        pygame.draw.rect(ventana, COLOR_BOTON, boton_palabras, border_radius=14)
        pygame.draw.rect(ventana, COLOR_BOTON, boton_sopa, border_radius=14)
        txt_palabras = fuente_boton.render("PoliPalabras", True, COLOR_BOTON_TEXTO)
        txt_sopa = fuente_boton.render("PoliSopa", True, COLOR_BOTON_TEXTO)
        ventana.blit(txt_palabras, (boton_palabras.x + boton_palabras.w//2 - txt_palabras.get_width()//2,
                                    boton_palabras.y + boton_palabras.h//2 - txt_palabras.get_height()//2))
        ventana.blit(txt_sopa, (boton_sopa.x + boton_sopa.w//2 - txt_sopa.get_width()//2,
                                boton_sopa.y + boton_sopa.h//2 - txt_sopa.get_height()//2))
        pygame.draw.rect(ventana, COLOR_BOTON, boton_cerrar, border_radius=12)
        txt_cerrar = fuente_boton.render("Cerrar", True, COLOR_BOTON_TEXTO)
        ventana.blit(txt_cerrar, (boton_cerrar.x + boton_cerrar.w//2 - txt_cerrar.get_width()//2, boton_cerrar.y + 8))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.display.set_mode((PANTALLA_ANCHO, PANTALLA_ALTO))
                return
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if boton_palabras.collidepoint(event.pos):
                    ventana_mejores_jugadores("polipalabras")
                    return
                if boton_sopa.collidepoint(event.pos):
                    ventana_mejores_jugadores("polisopa")
                    return
                if boton_cerrar.collidepoint(event.pos):
                    pygame.display.set_mode((PANTALLA_ANCHO, PANTALLA_ALTO))
                    return
        pygame.display.flip()

# --- Ventana que muestra el ranking de mejores jugadores para cada juego ---
def ventana_mejores_jugadores(juego):
    ANCHO, ALTO = 700, 600
    ventana = pygame.display.set_mode((ANCHO, ALTO))
    fuente_titulo = pygame.font.Font("dalek_pinpoint/DalekPinpointBold.ttf", 36)
    fuente = pygame.font.Font("augustus/AUGUSTUS.ttf", 28)
    fuente_small = pygame.font.Font("augustus/AUGUSTUS.ttf", 22)
    boton_cerrar = pygame.Rect(ANCHO//2 - 80, ALTO - 70, 160, 48)

    x_pos = [80, 320, 540]

    # Leer mejores jugadores de archivo según el juego
    if juego == "polipalabras":
        archivo = "registroPoliPalabras.txt"
        mejores = []
        if os.path.exists(archivo):
            with open(archivo, "r", encoding="utf-8") as f:
                contenido = f.read().split("=== PARTIDA ===")
                puntajes = []
                for p in contenido:
                    lineas = [line.strip() for line in p.strip().splitlines() if line.strip()]
                    if not lineas:
                        continue
                    usuario = None
                    puntaje = None
                    finalizada = False
                    for line in lineas:
                        if line.startswith("USUARIO:"):
                            usuario = line.split(":",1)[1].strip()
                        if line.startswith("PUNTAJE:"):
                            try:
                                puntaje = int(line.split(":",1)[1].strip())
                            except:
                                puntaje = None
                        if line.startswith("FINALIZADA:"):
                            finalizada = "SI" in line.upper()
                    if usuario and puntaje is not None and finalizada:
                        puntajes.append((usuario, puntaje))
                mejores_dict = {}
                for usuario, puntaje in puntajes:
                    if usuario not in mejores_dict or puntaje > mejores_dict[usuario]:
                        mejores_dict[usuario] = puntaje
                mejores = sorted(mejores_dict.items(), key=lambda x: x[1], reverse=True)[:10]
    else:  # polisopa
        archivo = "registroSopa.txt"
        mejores = []
        if os.path.exists(archivo):
            with open(archivo, "r", encoding="utf-8") as f:
                contenido = f.read().split("=== PARTIDA ===")
                tiempos = []
                for p in contenido:
                    lineas = [line.strip() for line in p.strip().splitlines() if line.strip()]
                    if not lineas:
                        continue
                    usuario = None
                    tiempo = None
                    finalizada = False
                    for line in lineas:
                        if line.startswith("USUARIO:"):
                            usuario = line.split(":",1)[1].strip()
                        if line.startswith("FINALIZADA:"):
                            finalizada = "SI" in line.upper()
                        if line.startswith("TIEMPO:"):
                            try:
                                tiempo = int(line.split(":",1)[1].strip())
                            except:
                                tiempo = None
                    if usuario and tiempo is not None and finalizada:
                        tiempos.append((usuario, tiempo))
                mejores_dict = {}
                for usuario, tiempo in tiempos:
                    if usuario not in mejores_dict or tiempo < mejores_dict[usuario]:
                        mejores_dict[usuario] = tiempo
                mejores = sorted(mejores_dict.items(), key=lambda x: x[1])[:10]

    while True:
        ventana.fill(COLOR_FONDO)
        titulo = fuente_titulo.render("Top 10 - " + ("PoliPalabras" if juego=="polipalabras" else "PoliSopa"), True, COLOR_BOTON)
        ventana.blit(titulo, (ANCHO//2 - titulo.get_width()//2, 30))

        # Encabezados alineados por la parte superior (top)
        encabezados = ["POSICION", "USUARIO", "PUNTAJE" if juego=="polipalabras" else "TIEMPO"]
        enc_surfs = [fuente.render(enc, True, COLOR_TEXTO) for enc in encabezados]
        enc_y = 100
        for i, surf in enumerate(enc_surfs):
            ventana.blit(surf, (x_pos[i] + 60 - surf.get_width()//2, enc_y))

        y = 150
        for idx, (usuario, valor) in enumerate(mejores, 1):
            if juego == "polisopa":
                minutos = valor // 60
                segundos = valor % 60
                valor_str = f"{minutos:02d}:{segundos:02d}"
            else:
                valor_str = str(valor)
            pos_surf = fuente_small.render(f"{idx}", True, COLOR_TEXTO)
            user_surf = fuente_small.render(usuario, True, COLOR_TEXTO)
            val_surf = fuente_small.render(valor_str, True, COLOR_TEXTO)
            ventana.blit(pos_surf, (x_pos[0] + 60 - pos_surf.get_width()//2, y))
            ventana.blit(user_surf, (x_pos[1] + 60 - user_surf.get_width()//2, y))
            ventana.blit(val_surf, (x_pos[2] + 60 - val_surf.get_width()//2, y))
            y += 38

        pygame.draw.rect(ventana, COLOR_BOTON, boton_cerrar, border_radius=12)
        txt_cerrar = fuente.render("Cerrar", True, COLOR_BOTON_TEXTO)
        ventana.blit(txt_cerrar, (boton_cerrar.x + boton_cerrar.w//2 - txt_cerrar.get_width()//2, boton_cerrar.y + 8))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.display.set_mode((PANTALLA_ANCHO, PANTALLA_ALTO))
                return
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if boton_cerrar.collidepoint(event.pos):
                    pygame.display.set_mode((PANTALLA_ANCHO, PANTALLA_ALTO))
                    return
        pygame.display.flip()

if __name__ == "__main__":
    menu_Main()
