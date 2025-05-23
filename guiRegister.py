import pygame
import sys
import os
import subprocess

pygame.init()

# --- Configuración ---
ANCHO = 600
ALTO = 500
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
pygame.display.set_caption("Registro")

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
                if len(self.text) < 30:
                    self.text += event.unicode

    def draw(self, pantalla):
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
        pygame.draw.line(pantalla, self.color, (self.x, self.y + self.txt_surface.get_height()),
                         (self.x + self.txt_surface.get_width(), self.y + self.txt_surface.get_height()), 2)

    def estaClickeado(self, pos, evento):
        return evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1 and self.rect.collidepoint(pos)

# --- Instancias ---
input_usuario = InputBox(200, 90, 200, 40)
input_email = InputBox(200, 160, 200, 40)
input_password = InputBox(200, 230, 200, 40, password=True)
input_password2 = InputBox(200, 300, 200, 40, password=True)
boton_register = Boton(250, 370, 100, 45, "Register", COLOR_BOTON, COLOR_BOTON_TEXTO)
link_login = Link(230, 440, "Iniciar Sesión")

mensaje_error = ""
mostrar_error = False
abrir_login_flag = False

def leer_usuarios():
    usuarios = []
    if os.path.exists("usuarios.txt"):
        with open("usuarios.txt", "r", encoding="utf-8") as f:
            for linea in f:
                partes = linea.strip().split(";")
                if len(partes) == 3:
                    usuarios.append({"usuario": partes[0], "email": partes[1], "password": partes[2]})
    return usuarios

def guardar_usuario(usuario, email, password):
    with open("usuarios.txt", "a", encoding="utf-8") as f:
        f.write(f"{usuario};{email};{password}\n")

def validar_email(email):
    return "@" in email and "." in email and len(email) >= 5

def abrir_login():
    dirScript = os.path.dirname(os.path.abspath(__file__))
    pathLogin = os.path.join(dirScript, "guiLogIn.py")
    try:
        subprocess.run([sys.executable, pathLogin])
    except Exception as e:
        print("No se pudo abrir la ventana de login:", e)

# --- Main loop ---
while True:
    pantalla.fill(COLOR_FONDO)

    # Títulos de campos
    titulo = FUENTE_TITULO.render("Registro de Usuario", True, COLOR_TEXTO)
    pantalla.blit(titulo, (ANCHO//2 - titulo.get_width()//2, 30))
    usuario_lbl = FUENTE.render("Nombre de usuario:", True, COLOR_TEXTO)
    pantalla.blit(usuario_lbl, (input_usuario.rect.x, input_usuario.rect.y - 30))
    email_lbl = FUENTE.render("Correo electrónico:", True, COLOR_TEXTO)
    pantalla.blit(email_lbl, (input_email.rect.x, input_email.rect.y - 30))
    password_lbl = FUENTE.render("Contraseña:", True, COLOR_TEXTO)
    pantalla.blit(password_lbl, (input_password.rect.x, input_password.rect.y - 30))
    password2_lbl = FUENTE.render("Repetir contraseña:", True, COLOR_TEXTO)
    pantalla.blit(password2_lbl, (input_password2.rect.x, input_password2.rect.y - 30))

    # Campos y botones
    input_usuario.draw(pantalla)
    input_email.draw(pantalla)
    input_password.draw(pantalla)
    input_password2.draw(pantalla)
    boton_register.draw(pantalla)

    # Texto de login
    texto_login = FUENTE.render("¿Ya tienes cuenta?:", True, COLOR_TEXTO)
    pantalla.blit(texto_login, (input_usuario.rect.x, 420))
    link_login.draw(pantalla)

    # Mensaje de error
    if mostrar_error and mensaje_error:
        error_surface = FUENTE.render(mensaje_error, True, COLOR_ERROR)
        pantalla.blit(error_surface, (ANCHO//2 - error_surface.get_width()//2, 60))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        input_usuario.handle_event(event)
        input_email.handle_event(event)
        input_password.handle_event(event)
        input_password2.handle_event(event)
        pos = pygame.mouse.get_pos()

        if boton_register.estaClickeado(pos, event):
            mostrar_error = False
            mensaje_error = ""
            usuarios = leer_usuarios()
            # Validar usuario
            if any(u["usuario"] == input_usuario.text for u in usuarios):
                mensaje_error = "Ya existe este usuario."
                input_usuario.clear()
                mostrar_error = True
                break
            # Validar email
            if not validar_email(input_email.text):
                mensaje_error = "Correo electrónico inválido."
                input_email.clear()
                mostrar_error = True
                break
            if any(u["email"] == input_email.text for u in usuarios):
                mensaje_error = "Ya existe este correo."
                input_email.clear()
                mostrar_error = True
                break
            # Validar contraseña
            if not (6 <= len(input_password.text) <= 18):
                mensaje_error = "La contraseña debe tener entre 6 y 18 caracteres."
                input_password.clear()
                input_password2.clear()
                mostrar_error = True
                break
            # Validar confirmación de contraseña
            if input_password.text != input_password2.text:
                mensaje_error = "Las contraseñas no coinciden."
                input_password.clear()
                input_password2.clear()
                mostrar_error = True
                break
            # Si todo es válido, guardar usuario y abrir login
            guardar_usuario(input_usuario.text, input_email.text, input_password.text)
            pygame.quit()
            abrir_login()
            sys.exit()

        if link_login.estaClickeado(pos, event):
            pygame.quit()
            abrir_login()
            sys.exit()

    pygame.display.flip()

# --- Fuera del bucle principal ---
if abrir_login_flag:
    abrir_login()