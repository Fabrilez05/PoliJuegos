import pygame
import sys
import os
import subprocess

pygame.init()

# --- Configuración de la ventana y colores principales ---
ANCHO = 600
ALTO = 520
COLOR_FONDO = (245, 245, 240)
COLOR_TEXTO = (44, 62, 80)
COLOR_INPUT = (255, 255, 255)
COLOR_INPUT_ACTIVO = (230, 230, 210)
COLOR_BOTON = (212, 175, 55)
COLOR_BOTON_TEXTO = (44, 62, 80)
COLOR_LINK = (30, 60, 150)
COLOR_ERROR = (200, 60, 60)

# --- Fuentes personalizadas ---
FUENTE = pygame.font.Font("augustus/AUGUSTUS.ttf", 28)
FUENTE_TITULO = pygame.font.Font("dalek_pinpoint/DalekPinpointBold.ttf", 48)
FUENTE_LINK = pygame.font.Font("augustus/AUGUSTUS.ttf", 22)
FUENTE_BOTON = pygame.font.Font("augustus/AUGUSTUS.ttf", 24)

pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Login")

# --- Clase para campos de texto (input) ---
class InputBox:
    def __init__(self, x, y, w, h, password=False):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = COLOR_INPUT
        self.text = ''
        self.active = False
        self.password = password

    def handle_event(self, event):
        # Maneja eventos de teclado y mouse para el input
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                pass
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                if len(self.text) < 20:
                    self.text += event.unicode

    def draw(self, pantalla):
        # Dibuja el campo de texto en pantalla, con asteriscos si es contraseña
        display_text = '*' * len(self.text) if self.password else self.text
        color = COLOR_INPUT_ACTIVO if self.active else COLOR_INPUT
        border_color = COLOR_BOTON if self.active else (180, 180, 160)
        shadow_rect = self.rect.move(3, 3)
        pygame.draw.rect(pantalla, (220, 210, 180), shadow_rect, border_radius=10)
        pygame.draw.rect(pantalla, color, self.rect, border_radius=10)
        pygame.draw.rect(pantalla, border_color, self.rect, 3, border_radius=10)
        txt_surface = FUENTE.render(display_text, True, COLOR_TEXTO)
        # Centrado vertical
        text_y = self.rect.y + (self.rect.h - txt_surface.get_height()) // 2
        pantalla.blit(txt_surface, (self.rect.x+10, text_y))

    def clear(self):
        # Limpia el texto del input
        self.text = ''

# --- Clase para botones ---
class Boton:
    def __init__(self, x, y, w, h, texto, color, color_texto):
        self.rect = pygame.Rect(x, y, w, h)
        self.texto = texto
        self.color = color
        self.color_texto = color_texto

    def draw(self, pantalla):
        # Dibuja el botón con sombra y texto centrado
        shadow_rect = self.rect.move(3, 3)
        pygame.draw.rect(pantalla, (200, 180, 100), shadow_rect, border_radius=14)
        pygame.draw.rect(pantalla, COLOR_BOTON, self.rect, border_radius=14)
        pygame.draw.rect(pantalla, (180, 150, 40), self.rect, 3, border_radius=14)
        txt_surface = FUENTE_BOTON.render(self.texto, True, COLOR_BOTON_TEXTO)
        pantalla.blit(txt_surface, (self.rect.x + self.rect.w//2 - txt_surface.get_width()//2,
                                    self.rect.y + self.rect.h//2 - txt_surface.get_height()//2))

    def estaClickeado(self, pos, evento):
        # Devuelve True si el botón fue clickeado
        return evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1 and self.rect.collidepoint(pos)

# --- Clase para links subrayados (como "Registrarse") ---
class Link:
    def __init__(self, x, y, texto):
        self.texto = texto
        self.x = x
        self.y = y
        self.font = FUENTE_LINK
        self.color = COLOR_LINK
        self.txt_surface = self.font.render(self.texto, True, self.color)
        self.rect = self.txt_surface.get_rect(topleft=(x, y))

    def draw(self, pantalla):
        # Dibuja el link subrayado
        pantalla.blit(self.txt_surface, (self.x, self.y))
        pygame.draw.line(pantalla, self.color, (self.x, self.y + self.txt_surface.get_height()),
                         (self.x + self.txt_surface.get_width(), self.y + self.txt_surface.get_height()), 2)

    def estaClickeado(self, pos, evento):
        # Devuelve True si el link fue clickeado
        return evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1 and self.rect.collidepoint(pos)

# --- Función para leer usuarios desde archivo ---
def leer_usuarios():
    usuarios = []
    if os.path.exists("usuarios.txt"):
        with open("usuarios.txt", "r", encoding="utf-8") as f:
            for linea in f:
                partes = linea.strip().split(";")
                if len(partes) == 3:
                    usuarios.append({"usuario": partes[0], "email": partes[1], "password": partes[2]})
    return usuarios

# --- Función para abrir la ventana de registro ---
def abrir_registro():
    dirScript = os.path.dirname(os.path.abspath(__file__))
    pathRegister = os.path.join(dirScript, "guiRegister.py")
    try:
        subprocess.run([sys.executable, pathRegister])
    except Exception as e:
        print("No se pudo abrir la ventana de registro:", e)

# --- Función para abrir el menú principal tras login exitoso ---
def abrir_menu(usuario):
    dirScript = os.path.dirname(os.path.abspath(__file__))
    pathMenu = os.path.join(dirScript, "guiMenu.py")
    try:
        subprocess.run([sys.executable, pathMenu, usuario])
    except Exception as e:
        print("No se pudo abrir la ventana de menú:", e)

# --- Dibuja un degradado vertical en la pantalla ---
def draw_gradient(surface, color1, color2, ancho, alto):
    for y in range(alto):
        ratio = y / alto
        r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
        g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
        b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
        pygame.draw.line(surface, (r, g, b), (0, y), (ancho, y))

# --- Instancias de campos, botones y links ---
input_usuario = InputBox(200, 170, 200, 44)
input_password = InputBox(200, 250, 200, 44, password=True)
boton_login = Boton(250, 330, 100, 50, "Login", COLOR_BOTON, COLOR_BOTON_TEXTO)
link_registro = Link(0, 0, "Registrarse")  # Posición se ajusta dinámicamente

mensaje_error = ""
mostrar_error = False

# --- Bucle principal de la ventana de login ---
while True:
    draw_gradient(pantalla, (245, 245, 240), (220, 220, 210), ANCHO, ALTO)

    # Dibuja el título principal
    titulo = FUENTE_TITULO.render("Iniciar Sesión", True, COLOR_BOTON)
    pantalla.blit(titulo, (ANCHO//2 - titulo.get_width()//2, 30))

    # Línea decorativa bajo el título
    pygame.draw.line(pantalla, COLOR_BOTON, (80, 110), (ANCHO-80, 110), 4)

    # Etiquetas de usuario y contraseña
    usuario_lbl = FUENTE.render("Usuario:", True, COLOR_LINK)
    pantalla.blit(usuario_lbl, (input_usuario.rect.x, input_usuario.rect.y - 32))
    password_lbl = FUENTE.render("Contraseña:", True, COLOR_LINK)
    pantalla.blit(password_lbl, (input_password.rect.x, input_password.rect.y - 32))

    # Dibuja campos de texto y botón de login
    input_usuario.draw(pantalla)
    input_password.draw(pantalla)
    boton_login.draw(pantalla)

    # Texto y link de registro centrados debajo del botón
    texto_registro = FUENTE.render("¿Aún no tienes cuenta?", True, COLOR_TEXTO)
    x_registro = ANCHO//2 - texto_registro.get_width()//2
    y_registro = boton_login.rect.y + boton_login.rect.h + 40
    pantalla.blit(texto_registro, (x_registro, y_registro))

    link_registro.x = ANCHO//2 - link_registro.txt_surface.get_width()//2
    link_registro.y = y_registro + texto_registro.get_height() + 12
    link_registro.rect.topleft = (link_registro.x, link_registro.y)
    link_registro.draw(pantalla)

    # Muestra mensaje de error si corresponde
    if mostrar_error and mensaje_error:
        error_surface = FUENTE.render(mensaje_error, True, COLOR_ERROR)
        pantalla.blit(error_surface, (ANCHO//2 - error_surface.get_width()//2, 90))

    # --- Manejo de eventos del usuario ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        input_usuario.handle_event(event)
        input_password.handle_event(event)
        pos = pygame.mouse.get_pos()
        if boton_login.estaClickeado(pos, event):
            mostrar_error = False
            mensaje_error = ""
            usuarios = leer_usuarios()
            usuario = next((u for u in usuarios if u["usuario"] == input_usuario.text), None)
            if not usuario:
                mensaje_error = "El usuario no existe"
                mostrar_error = True
                input_usuario.clear()
                input_password.clear()
                break
            if usuario["password"] != input_password.text:
                mensaje_error = "Contraseña incorrecta"
                mostrar_error = True
                input_password.clear()
                break
            if usuario["password"] == input_password.text:
                pygame.quit()
                abrir_menu(input_usuario.text)
                sys.exit()

        if link_registro.estaClickeado(pos, event):
            pygame.quit()
            abrir_registro()
            sys.exit()

    pygame.display.flip()