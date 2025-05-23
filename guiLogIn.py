import pygame
import sys
import os
import subprocess

pygame.init()

# --- Configuración ---
ANCHO = 600
ALTO = 400
COLOR_FONDO = (240, 240, 240)
COLOR_TEXTO = (0, 0, 0)
COLOR_INPUT = (255, 255, 255)
COLOR_INPUT_ACTIVO = (200, 220, 255)
COLOR_BOTON = (100, 180, 100)
COLOR_BOTON_TEXTO = (255, 255, 255)
COLOR_LINK = (0, 0, 200)
COLOR_ERROR = (200, 0, 0)

FUENTE = pygame.font.SysFont(None, 32)
FUENTE_TITULO = pygame.font.SysFont(None, 40)
FUENTE_LINK = pygame.font.SysFont(None, 28)

pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Login")

# --- Campos de texto ---
class InputBox:
    def __init__(self, x, y, w, h, password=False):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = COLOR_INPUT
        self.text = ''
        self.active = False
        self.password = password

    def handle_event(self, event):
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
        # Censura si es password
        display_text = '*' * len(self.text) if self.password else self.text
        color = COLOR_INPUT_ACTIVO if self.active else COLOR_INPUT
        pygame.draw.rect(pantalla, color, self.rect)
        pygame.draw.rect(pantalla, COLOR_TEXTO, self.rect, 2)
        txt_surface = FUENTE.render(display_text, True, COLOR_TEXTO)
        pantalla.blit(txt_surface, (self.rect.x+5, self.rect.y+8))

    def clear(self):
        self.text = ''

# --- Botón ---
class Boton:
    def __init__(self, x, y, w, h, texto, color, color_texto):
        self.rect = pygame.Rect(x, y, w, h)
        self.texto = texto
        self.color = color
        self.color_texto = color_texto

    def draw(self, pantalla):
        pygame.draw.rect(pantalla, self.color, self.rect)
        txt_surface = FUENTE.render(self.texto, True, self.color_texto)
        pantalla.blit(txt_surface, (self.rect.x + self.rect.w//2 - txt_surface.get_width()//2,
                                    self.rect.y + self.rect.h//2 - txt_surface.get_height()//2))

    def estaClickeado(self, pos, evento):
        return evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1 and self.rect.collidepoint(pos)

# --- Link subrayado ---
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
        pantalla.blit(self.txt_surface, (self.x, self.y))
        # Subrayado
        pygame.draw.line(pantalla, self.color, (self.x, self.y + self.txt_surface.get_height()),
                         (self.x + self.txt_surface.get_width(), self.y + self.txt_surface.get_height()), 2)

    def estaClickeado(self, pos, evento):
        return evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1 and self.rect.collidepoint(pos)

# --- Funciones auxiliares ---
def leer_usuarios():
    usuarios = []
    if os.path.exists("usuarios.txt"):
        with open("usuarios.txt", "r", encoding="utf-8") as f:
            for linea in f:
                partes = linea.strip().split(";")
                if len(partes) == 3:
                    usuarios.append({"usuario": partes[0], "email": partes[1], "password": partes[2]})
    return usuarios

def abrir_registro():
    dirScript = os.path.dirname(os.path.abspath(__file__))
    pathRegister = os.path.join(dirScript, "guiRegister.py")
    try:
        subprocess.run([sys.executable, pathRegister])
    except Exception as e:
        print("No se pudo abrir la ventana de registro:", e)

def abrir_menu(usuario):
    dirScript = os.path.dirname(os.path.abspath(__file__))
    pathMenu = os.path.join(dirScript, "guiMenu.py")
    try:
        subprocess.run([sys.executable, pathMenu, usuario])
    except Exception as e:
        print("No se pudo abrir la ventana de menú:", e)

# --- Instancias ---
input_usuario = InputBox(200, 110, 200, 40)
input_password = InputBox(200, 190, 200, 40, password=True)
boton_login = Boton(250, 260, 100, 45, "Login", COLOR_BOTON, COLOR_BOTON_TEXTO)
link_registro = Link(230, 330, "Registrarse")

mensaje_error = ""
mostrar_error = False

# --- Main loop ---
while True:
    pantalla.fill(COLOR_FONDO)

    # Títulos de campos
    titulo = FUENTE_TITULO.render("Iniciar Sesión", True, COLOR_TEXTO)
    pantalla.blit(titulo, (ANCHO//2 - titulo.get_width()//2, 30))
    usuario_lbl = FUENTE.render("Usuario:", True, COLOR_TEXTO)
    pantalla.blit(usuario_lbl, (input_usuario.rect.x, input_usuario.rect.y - 30))
    password_lbl = FUENTE.render("Contraseña:", True, COLOR_TEXTO)
    pantalla.blit(password_lbl, (input_password.rect.x, input_password.rect.y - 30))

    # Campos y botones
    input_usuario.draw(pantalla)
    input_password.draw(pantalla)
    boton_login.draw(pantalla)

    # Texto de registro
    texto_registro = FUENTE.render("¿Aún no tienes cuenta?:", True, COLOR_TEXTO)
    pantalla.blit(texto_registro, (input_usuario.rect.x, 300))
    link_registro.draw(pantalla)

    # Mensaje de error
    if mostrar_error and mensaje_error:
        error_surface = FUENTE.render(mensaje_error, True, COLOR_ERROR)
        pantalla.blit(error_surface, (ANCHO//2 - error_surface.get_width()//2, 70))

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
            # Login correcto
            if usuario["password"] == input_password.text:
                pygame.quit()
                abrir_menu(input_usuario.text)
                sys.exit()

        if link_registro.estaClickeado(pos, event):
            pygame.quit()
            abrir_registro()
            sys.exit()

    pygame.display.flip()