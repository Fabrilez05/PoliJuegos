import pygame
import sys
import os
import subprocess

pygame.init()

# --- Configuración de la ventana y colores principales ---
ANCHO = 800
ALTO = 760
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
pygame.display.set_caption("Registro")

# --- Dibuja un degradado vertical en la pantalla ---
def draw_gradient(surface, color1, color2, ancho, alto):
    for y in range(alto):
        ratio = y / alto
        r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
        g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
        b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
        pygame.draw.line(surface, (r, g, b), (0, y), (ancho, y))

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
                if len(self.text) < 30:
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
        pygame.draw.rect(pantalla, self.color, self.rect, border_radius=14)
        pygame.draw.rect(pantalla, (180, 150, 40), self.rect, 3, border_radius=14)
        txt_surface = FUENTE_BOTON.render(self.texto, True, self.color_texto)
        pantalla.blit(txt_surface, (self.rect.x + self.rect.w//2 - txt_surface.get_width()//2,
                                    self.rect.y + self.rect.h//2 - txt_surface.get_height()//2))

    def estaClickeado(self, pos, evento):
        # Devuelve True si el botón fue clickeado
        return evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1 and self.rect.collidepoint(pos)

# --- Clase para links subrayados (como "Iniciar Sesión") ---
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

# --- Instancias de campos, botones y links ---
CAMPO_X = 80
CAMPO_W = 440
CAMPO_H = 48
ESPACIO_Y = 90

input_usuario = InputBox(CAMPO_X, 170, CAMPO_W, CAMPO_H)
input_email = InputBox(CAMPO_X, 170 + ESPACIO_Y, CAMPO_W, CAMPO_H)
input_password = InputBox(CAMPO_X, 170 + ESPACIO_Y * 2, CAMPO_W, CAMPO_H, password=True)
input_password2 = InputBox(CAMPO_X, 170 + ESPACIO_Y * 3, CAMPO_W, CAMPO_H, password=True)

boton_register_x = (ANCHO - CAMPO_W) // 2
boton_register_y = 170 + ESPACIO_Y * 4 + 10
boton_register = Boton(boton_register_x, boton_register_y, CAMPO_W, 56, "Registrarse", COLOR_BOTON, COLOR_BOTON_TEXTO)
link_login = Link(0, 0, "Iniciar Sesión")

mensaje_error = ""
mostrar_error = False

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

# --- Función para guardar un nuevo usuario en archivo ---
def guardar_usuario(usuario, email, password):
    with open("usuarios.txt", "a", encoding="utf-8") as f:
        f.write(f"{usuario};{email};{password}\n")

# --- Valida el formato del email ---
def validar_email(email):
    return "@" in email and "." in email and len(email) >= 5

# --- Abre la ventana de login tras registro exitoso ---
def abrir_login():
    dirScript = os.path.dirname(os.path.abspath(__file__))
    pathLogin = os.path.join(dirScript, "guiLogIn.py")
    try:
        subprocess.run([sys.executable, pathLogin])
    except Exception as e:
        print("No se pudo abrir la ventana de login:", e)

# --- Bucle principal de la ventana de registro ---
while True:
    draw_gradient(pantalla, (245, 245, 240), (220, 220, 210), ANCHO, ALTO)
    pygame.draw.line(pantalla, COLOR_BOTON, (80, 110), (ANCHO-80, 110), 4)

    # Título principal
    titulo = FUENTE_TITULO.render("Registro de Usuario", True, COLOR_BOTON)
    pantalla.blit(titulo, (ANCHO//2 - titulo.get_width()//2, 40))

    # Subtítulos alineados a la izquierda sobre cada campo
    usuario_lbl = FUENTE.render("Nombre de usuario:", True, COLOR_LINK)
    pantalla.blit(usuario_lbl, (input_usuario.rect.x, input_usuario.rect.y - 32))
    email_lbl = FUENTE.render("Correo electrónico:", True, COLOR_LINK)
    pantalla.blit(email_lbl, (input_email.rect.x, input_email.rect.y - 32))
    password_lbl = FUENTE.render("Contraseña:", True, COLOR_LINK)
    pantalla.blit(password_lbl, (input_password.rect.x, input_password.rect.y - 32))
    password2_lbl = FUENTE.render("Repetir contraseña:", True, COLOR_LINK)
    pantalla.blit(password2_lbl, (input_password2.rect.x, input_password2.rect.y - 32))

    # Dibuja campos y botón de registro
    input_usuario.draw(pantalla)
    input_email.draw(pantalla)
    input_password.draw(pantalla)
    input_password2.draw(pantalla)
    boton_register.draw(pantalla)

    # Texto y link de login centrados debajo del botón
    texto_login = FUENTE.render("¿Ya tienes cuenta?", True, COLOR_TEXTO)
    x_login = ANCHO // 2 - texto_login.get_width() // 2
    y_login = boton_register.rect.y + boton_register.rect.h + 40
    pantalla.blit(texto_login, (x_login, y_login))

    link_login.x = ANCHO // 2 - link_login.txt_surface.get_width() // 2
    link_login.y = y_login + texto_login.get_height() + 16
    link_login.rect.topleft = (link_login.x, link_login.y)
    link_login.draw(pantalla)

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
        input_email.handle_event(event)
        input_password.handle_event(event)
        input_password2.handle_event(event)
        pos = pygame.mouse.get_pos()

        if boton_register.estaClickeado(pos, event):
            mostrar_error = False
            mensaje_error = ""
            usuarios = leer_usuarios()
            # Validar usuario único
            if any(u["usuario"] == input_usuario.text for u in usuarios):
                mensaje_error = "Ya existe este usuario."
                input_usuario.clear()
                mostrar_error = True
                break
            # Validar email formato y único
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
            # Validar contraseña longitud
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