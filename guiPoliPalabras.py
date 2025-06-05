import pygame
import logicaPoliPalabras
import sys
import math
import time
import random
import os

# Inicializa pygame
pygame.init()

# --- Configuración de pantalla y colores ---
PANTALLA_ANCHO = 1280
PANTALLA_ALTO = 720
TAMAÑO_BOTON = 70
ALTURA_CAJA_ENTRADA = 90

COLOR_FONDO = (245, 245, 240)  # Color de fondo principal
COLOR_TEXTO = (44, 62, 80)     # Color del texto principal
COLOR_BOTON = (212, 175, 55)   # Color de los botones dorados
COLOR_BOTON2 = (100, 100, 180) # Color de botones secundarios (azul)
COLOR_BOTON_TEXTO = (44, 62, 80) # Color del texto de los botones
COLOR_CASILLA = (255, 255, 255)  # Color de la caja de entrada
COLOR_CASILLA_SELEC = (173, 216, 230) # Color de selección de casilla
COLOR_SOMBRA = (220, 210, 180)   # Color de sombra para botones y paneles
COLOR_LETRA_SELECCIONADA = (3, 136, 252) # Color de la letra central seleccionada
COLOR_BOTON_APLICAR = (70, 180, 70)  # Color del botón aplicar
COLOR_BOTON_BORRAR = (180, 70, 70)   # Color del botón borrar
COLOR_BORDE_BOTON_APLICAR = (50, 150, 50)  # Borde botón aplicar
COLOR_BORDE_BOTON_BORRAR = (150, 50, 50)   # Borde botón borrar
COLOR_TEXTO_LISTA = (0,0,0) # Color del texto de la lista de palabras
COLOR_FONDO_LISTA = (240,240,240) # Fondo del panel de lista
COLOR_BORDE_LISTA = (200,200,200) # Borde del panel de lista
ANCHO_LISTA = 350  # Ancho del panel de lista
MARGEN_LISTA = 20  # Margen del panel de lista
COLOR_BOTON_MEZCLAR = (227, 214, 93) # Color del botón mezclar
COLOR_BORDE_BOTON_MEZCLAR = (252, 198, 33) # Borde del botón mezclar
ANCHO_BOTON_MEZCLAR = 150
ALTO_BOTON_MEZCLAR = TAMAÑO_BOTON
COLOR_BOTON_GUARDAR = (255, 215, 0)  # Color del botón guardar
COLOR_BORDE_BOTON_GUARDAR = (200, 150, 0)
COLOR_BOTON_VOLVER = (180, 70, 70)  # Color del botón volver
COLOR_BORDE_BOTON_VOLVER = (150, 50, 50)

# Fuentes utilizadas en la interfaz
FUENTE_TITULO = pygame.font.Font("dalek_pinpoint/DalekPinpointBold.ttf", 48)
FUENTE = pygame.font.Font("augustus/AUGUSTUS.ttf", 32)
FUENTE_PEQUEÑA = pygame.font.Font("augustus/AUGUSTUS.ttf", 24)
FUENTE_BOTON = pygame.font.Font("augustus/AUGUSTUS.ttf", 28)

# Obtiene el usuario actual y el índice de partida desde los argumentos
usuario_actual = sys.argv[1] if len(sys.argv) > 1 else "anonimo"
indice_partida = int(sys.argv[2]) if len(sys.argv) > 2 else None

# Crea la ventana principal del juego
pantalla = pygame.display.set_mode((PANTALLA_ANCHO, PANTALLA_ALTO))
pygame.display.set_caption("PoliPalabras")

# Función para dibujar un fondo con gradiente vertical
def draw_gradient(surface, color1, color2, ancho, alto):
    for y in range(alto):
        ratio = y / alto
        r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
        g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
        b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
        pygame.draw.line(surface, (r, g, b), (0, y), (ancho, y))

# Función para cargar una partida guardada desde archivo
def cargar_partida(nombre_archivo="registroPoliPalabras.txt", usuario=None, indice=0):
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
        
        # Extrae los datos de la partida
        letra_generada = ""
        letras_jugables = []
        palabras_correctas = []
        palabras = []
        tiempo_guardado = 0
        letras_iniciales = {}
        palabras_por_letra = {}

        for linea in datos:
            if linea.startswith("LETRA_GENERADA:"):
                letra_generada = linea.split(":")[1].strip()
            elif linea.startswith("LETRAS_JUGABLES:"):
                letras_jugables = linea.split(":")[1].strip().split(",")
            elif linea.startswith("PALABRAS_CORRECTAS:"):
                palabras_correctas = linea.split(":")[1].strip().split(",") if linea.split(":")[1].strip() else []
            elif linea.startswith("TIEMPO:"):
                tiempo_guardado = int(linea.split(":")[1].strip())
            elif linea.startswith("PALABRAS_DICCIONARIO"):
                palabras = linea.split(':')[1].strip().split(",") if linea.split(':')[1].strip() else []
            elif linea.startswith("LETRAS_INICIALES:"):
                partes = linea.split(":", 1)[1].strip()
                if partes:
                    for par in partes.split(","):
                        if ":" in par:
                            letra, cantidad = par.split(":")
                            letras_iniciales[letra] = int(cantidad)
            elif linea.startswith("PALABRAS_POR_LETRA:"):
                # Formato: PALABRAS_POR_LETRA:a:pal1|pal2,b:pal3|pal4
                partes = linea.split(":", 1)[1].strip()
                if partes:
                    for par in partes.split(","):
                        if ":" in par:
                            letra, pals = par.split(":")
                            palabras_por_letra[letra] = pals.split("|") if pals else []

        # Si no se guardó PALABRAS_POR_LETRA, reconstruirlo desde palabras
        if not palabras_por_letra and palabras:
            for palabra in palabras:
                if palabra:
                    letra = palabra[0]
                    palabras_por_letra.setdefault(letra, []).append(palabra)

        return letra_generada, letras_jugables, palabras_correctas, tiempo_guardado, palabras, letras_iniciales, palabras_por_letra

# Función para guardar una partida en archivo
def guardar_partida(nombre_archivo="registroPoliPalabras.txt", usuario=None, indice=None, juego=None, tiempo_transcurrido=0,nombre = None):
    # Lee todas las partidas existentes
    if not os.path.exists(nombre_archivo):
        partidas = []
    else:
        with open(nombre_archivo, "r", encoding="utf-8") as f:
            contenido = f.read().split("=== PARTIDA ===")
            partidas = [p for p in contenido if p.strip()]
    
    # Serializa letras_iniciales si existe
    letras_iniciales_str = ""
    if hasattr(juego, "letrasIniciales") and juego.letrasIniciales:
        letras_iniciales_str = ",".join(f"{letra}:{cantidad}" for letra, cantidad in juego.letrasIniciales.items())

    # Serializa palabras_por_letra si existe
    palabras_por_letra_str = ""
    if hasattr(juego, "palabrasPorLetra") and juego.palabrasPorLetra:
        palabras_por_letra_str = ",".join(
            f"{letra}:{'|'.join(juego.palabrasPorLetra[letra])}" for letra in juego.palabrasPorLetra
        )
    
    # Construye el nuevo registro de partida
    registro = f"USUARIO:{usuario}\n"
    registro += f"NOMBRE:{nombre}\n"
    registro += f"LETRA_GENERADA:{juego.letraGenerada}\n"
    registro += f"LETRAS_JUGABLES:{','.join(juego.letrasJugables)}\n"
    registro += f"PALABRAS_DICCIONARIO:{','.join(juego.palabras)}\n"
    registro += f"PALABRAS_CORRECTAS:{','.join(juego.palabrasCorrectas)}\n"
    registro += f"TIEMPO:{int(tiempo_transcurrido)}\n"
    if letras_iniciales_str:
        registro += f"LETRAS_INICIALES:{letras_iniciales_str}\n"
    if palabras_por_letra_str:
        registro += f"PALABRAS_POR_LETRA:{palabras_por_letra_str}\n"
    registro += "=== FIN PARTIDA ===\n\n"
    
    # Elimina cualquier partida previa del mismo usuario y nombre
    nuevas_partidas = []
    for p in partidas:
        lineas = [line.strip() for line in p.strip().splitlines() if line.strip()]
        if not lineas:
            continue
        es_misma = False
        if lineas[0].startswith("USUARIO:") and f"NOMBRE:{nombre}" in lineas:
            user = lineas[0].split(":",1)[1]
            if user == usuario:
                es_misma = True
        if not es_misma:
            nuevas_partidas.append(p)
    
    # Guarda todas las partidas en el archivo
    with open(nombre_archivo, "w", encoding="utf-8") as f:
        for p in partidas:
            f.write("=== PARTIDA ===\n" + p)

# Función para pedir el nombre de la partida al usuario
def pedir_nombre_partida(main_size):
    original_display = pygame.display.get_surface()
    ventana = pygame.display.set_mode((400, 180))
    fuente = pygame.font.SysFont("Arial", 32)
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
                done = True
                text = "SinNombre"
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
    
    pygame.display.set_mode(main_size)
    return text if text else "SinNombre"

# Clase para los botones hexagonales de letras
class boton:
    def __init__(self, centroX, centroY, letra, estaCentrado=False):
        self.centroX = centroX
        self.centroY = centroY
        self.letra = letra
        self.estaCentrado = estaCentrado
        self.color = COLOR_LETRA_SELECCIONADA if estaCentrado else COLOR_BOTON 
        self.colorSeleccion = COLOR_BOTON2 if not estaCentrado else COLOR_LETRA_SELECCIONADA
        self.ColorActual = self.color
        self.texto = FUENTE.render(letra.lower(), True, COLOR_BOTON_TEXTO)

        self.puntos = []
        for i in range(6):
            anguloSex = 60 * i - 30
            anguloRad = math.radians(anguloSex)
            x = centroX + TAMAÑO_BOTON * math.cos(anguloRad)
            y = centroY + TAMAÑO_BOTON * math.sin(anguloRad)
            self.puntos.append((x, y))

    def dibujar(self, superficie):
        # Dibuja sombra
        shadow_points = [(x+3, y+3) for (x,y) in self.puntos]
        pygame.draw.polygon(superficie, COLOR_SOMBRA, shadow_points) 
        
        pygame.draw.polygon(superficie, self.ColorActual, self.puntos) 
        pygame.draw.polygon(superficie, 'black', self.puntos, 2)

        textoRect = self.texto.get_rect(center=(self.centroX, self.centroY))
        superficie.blit(self.texto, textoRect)

    def estaSeleccionado(self, pos):
        distancia = math.sqrt((pos[0] - self.centroX) ** 2 + (pos[1] - self.centroY) ** 2)
        return distancia <= TAMAÑO_BOTON

    def refrescar(self, pos):
        if not self.estaCentrado:
            if self.estaSeleccionado(pos):
                self.ColorActual = self.colorSeleccion
            else:
                self.ColorActual = self.color

# Clase principal de la interfaz de usuario del juego
class juegoUI:
    def __init__(self, juego):
        self.juego = juego
        self.botones = []
        self.pilaDeEntrada = logicaPoliPalabras.pilaEntrada()
        self.textoEntrada = ''
        self.renderTextoEntrada = ''
        self.cajaEntrada = pygame.Rect(50, PANTALLA_ALTO // 2 - 120, 350, ALTURA_CAJA_ENTRADA)
        self.botonAplicar = pygame.Rect(50, self.cajaEntrada.bottom + 10, 350, TAMAÑO_BOTON)
        self.botonBorrar = pygame.Rect(50, self.botonAplicar.bottom + 20, 350, TAMAÑO_BOTON)
        self.mensaje = ''
        self.mensajeTemp = 0
        self.tiempoInicio = time.time()
        self.tiempoTranscurrido = 0
        self.rectLista = pygame.Rect(PANTALLA_ANCHO - ANCHO_LISTA - MARGEN_LISTA, 160, ANCHO_LISTA, PANTALLA_ALTO - 200)
        self.botonMezclar = pygame.Rect(PANTALLA_ANCHO // 2 - ANCHO_BOTON_MEZCLAR // 2 + 50, (PANTALLA_ALTO // 2)+(3 * TAMAÑO_BOTON),ANCHO_BOTON_MEZCLAR,ALTO_BOTON_MEZCLAR)
        self.poscicionesOriginales = []
        self.botonGuardar = pygame.Rect(PANTALLA_ANCHO - ANCHO_LISTA - MARGEN_LISTA, 50, ANCHO_LISTA, 50)
        self.botonVolver = pygame.Rect(PANTALLA_ANCHO - ANCHO_LISTA - MARGEN_LISTA, 110, ANCHO_LISTA, 44)
        self.botonComoJugar = pygame.Rect(50, self.cajaEntrada.bottom + 300, 350, 50)
        self.botonPista = pygame.Rect(50, self.cajaEntrada.top - 55, 350, 50)
        self.palabra_pista = ""
        self.pista_actual = ""
        self.crearBotones()

    # Crea los botones hexagonales de letras
    def crearBotones(self):
        self.botones = []
        centroX, centroY = PANTALLA_ANCHO // 2 + 50, PANTALLA_ALTO // 2
        letraSeleccionada = self.juego.letraGenerada
        otrasLetras = [letter for letter in self.juego.letrasJugables if letter != letraSeleccionada]
        self.botones.append(boton(centroX, centroY, letraSeleccionada, True))
        posiciones = []
        for i in range(6):
            angle = 60 * i
            x = centroX + 1.8 * TAMAÑO_BOTON * math.cos(math.radians(angle))
            y = centroY + 1.8 * TAMAÑO_BOTON * math.sin(math.radians(angle))
            posiciones.append((x, y))
        for i, (x, y) in enumerate(posiciones):
            if i < len(otrasLetras):
                self.botones.append(boton(x, y, otrasLetras[i]))

    # Mezcla las letras de los botones exteriores
    def mezclarBotones(self):
        botonesExteriores = [boton for boton in self.botones if not boton.estaCentrado]
        letras = [boton.letra for boton in botonesExteriores]
        random.shuffle(letras)
        for boton,letra in zip(botonesExteriores,letras):
            boton.letra = letra
            boton.texto = FUENTE.render(letra.lower(), True, COLOR_BOTON_TEXTO)
        
    # Dibuja toda la interfaz del juego
    def dibujar(self, superficie):
        draw_gradient(superficie, COLOR_FONDO, (220, 220, 210), PANTALLA_ANCHO, PANTALLA_ALTO)
        titulo = FUENTE_TITULO.render("PoliPalabras", True, COLOR_BOTON)
        superficie.blit(titulo, (PANTALLA_ANCHO // 2 - titulo.get_width() // 2, 50))
        pygame.draw.line(superficie, COLOR_BOTON, (40, 120), (PANTALLA_ANCHO-40, 120), 3)
        pygame.draw.rect(superficie, COLOR_BOTON, self.botonComoJugar, border_radius=12)
        txt_como_jugar = FUENTE_BOTON.render("¿Cómo Jugar?", True, COLOR_BOTON_TEXTO)
        superficie.blit(txt_como_jugar, (self.botonComoJugar.x + self.botonComoJugar.width//2 - txt_como_jugar.get_width()//2, 
                                        self.botonComoJugar.y + self.botonComoJugar.height//2 - txt_como_jugar.get_height()//2))
        pygame.draw.rect(superficie, COLOR_BOTON_VOLVER, self.botonVolver, border_radius=12)
        txt_volver = FUENTE_BOTON.render("Volver", True, COLOR_BOTON_TEXTO)
        superficie.blit(txt_volver, (self.botonVolver.x + self.botonVolver.width//2 - txt_volver.get_width()//2, 
                                   self.botonVolver.y + self.botonVolver.height//2 - txt_volver.get_height()//2))
        if self.mensaje and pygame.time.get_ticks() - self.mensajeTemp < 3000:
            mensajeSuperficie = FUENTE_PEQUEÑA.render(self.mensaje, True, (180, 60, 60))
            superficie.blit(mensajeSuperficie, (10, 30))
        shadow_rect = self.cajaEntrada.move(3, 3)
        pygame.draw.rect(superficie, COLOR_SOMBRA, shadow_rect, border_radius=12)
        pygame.draw.rect(superficie, COLOR_CASILLA, self.cajaEntrada, border_radius=12)
        pygame.draw.rect(superficie, COLOR_BOTON, self.cajaEntrada, 2, border_radius=12)
        if self.pilaDeEntrada.is_empty():
            self.renderTextoEntrada = ''
        else:
            self.renderTextoEntrada = ''.join(self.pilaDeEntrada.pila).upper()
        superficieEntrada = FUENTE.render(self.renderTextoEntrada, True, COLOR_TEXTO)
        superficie.blit(superficieEntrada, (self.cajaEntrada.x + 20, self.cajaEntrada.y + 20))
        for boton in self.botones:
            boton.dibujar(superficie)
        shadow_rect = self.botonAplicar.move(3, 3)
        pygame.draw.rect(superficie, (150, 220, 150), shadow_rect, border_radius=12)
        pygame.draw.rect(superficie, COLOR_BOTON_APLICAR, self.botonAplicar, border_radius=12)
        aplicarTexto = FUENTE_BOTON.render("Aplicar", True, (255, 255, 255))
        superficie.blit(aplicarTexto, (self.botonAplicar.x + self.botonAplicar.width // 2 - aplicarTexto.get_width() // 2,
                                     self.botonAplicar.y + self.botonAplicar.height // 2 - aplicarTexto.get_height() // 2))
        shadow_rect = self.botonBorrar.move(3, 3)
        pygame.draw.rect(superficie, (220, 150, 150), shadow_rect, border_radius=12)
        pygame.draw.rect(superficie, COLOR_BOTON_BORRAR, self.botonBorrar, border_radius=12)
        borrarTexto = FUENTE_BOTON.render("Borrar", True, (255, 255, 255))
        superficie.blit(borrarTexto, (self.botonBorrar.x + self.botonBorrar.width // 2 - borrarTexto.get_width() // 2,
                                    self.botonBorrar.y + self.botonBorrar.height // 2 - borrarTexto.get_height() // 2))
        minutos = int(self.tiempoTranscurrido // 60)
        segundos = int(self.tiempoTranscurrido % 60)
        textoTiempo = FUENTE_PEQUEÑA.render(f'{minutos:02d}:{segundos:02d}', True, COLOR_BOTON)
        superficie.blit(textoTiempo, (PANTALLA_ANCHO - textoTiempo.get_width()-170, 20))
        total_puntos = sum(self.juego.puntajes_palabras.get(p, 0) for p in self.juego.palabrasCorrectas)
        texto_total = FUENTE_PEQUEÑA.render(f"Puntos: {total_puntos}", True, (0, 120, 0))
        superficie.blit(texto_total, (PANTALLA_ANCHO - texto_total.get_width()-20, 20))
        shadow_rect = self.rectLista.move(3, 3)
        pygame.draw.rect(superficie, COLOR_SOMBRA, shadow_rect, border_radius=12)
        pygame.draw.rect(superficie, COLOR_FONDO_LISTA, self.rectLista, border_radius=12)
        pygame.draw.rect(superficie, COLOR_BOTON, self.rectLista, 2, border_radius=12)
        tituloLista = FUENTE_PEQUEÑA.render('Palabras por letra:', True, COLOR_BOTON)
        superficie.blit(tituloLista, (self.rectLista.x + self.rectLista.width//2 - tituloLista.get_width()//2, self.rectLista.y + 10))
        contrapesoY = 50
        anchoLinea = 25
        for letra in sorted(self.juego.letrasIniciales.keys()):
            correctas = self.juego.letrasIniciales[letra]
            total = len(self.juego.palabrasPorLetra.get(letra,[]))
            textoLinea = FUENTE_PEQUEÑA.render(f"empiezan por {letra.upper()}: {correctas}/{total}", True, COLOR_TEXTO_LISTA)
            superficie.blit(textoLinea, (self.rectLista.x + 20, self.rectLista.y + contrapesoY))
            contrapesoY += anchoLinea
        if contrapesoY + 50 < self.rectLista.height:
            contrapesoY +=10
            tituloCorrectas = FUENTE_PEQUEÑA.render('Palabras Acertadas: ', True, COLOR_BOTON)
            superficie.blit(tituloCorrectas,(self.rectLista.x+20,self.rectLista.y + contrapesoY))
            contrapesoY +=anchoLinea
            for palabra in self.juego.palabrasCorrectas:
                if contrapesoY + anchoLinea < self.rectLista.height:
                    puntaje = self.juego.puntajes_palabras.get(palabra, 0)
                    textoPalabra = FUENTE_PEQUEÑA.render(f"{palabra} ({puntaje} pts)", True, COLOR_TEXTO_LISTA)
                    if textoPalabra.get_width() > self.rectLista.width - 60:
                        while textoPalabra.get_width() > self.rectLista.width - 60 and len(palabra) > 3:
                            palabra = palabra[:-1]
                            textoPalabra = FUENTE_PEQUEÑA.render(f"{palabra}... ({puntaje} pts)", True, COLOR_TEXTO_LISTA)
                    superficie.blit(textoPalabra, (self.rectLista.x + 30, self.rectLista.y + contrapesoY))
                    contrapesoY += anchoLinea
        shadow_rect = self.botonMezclar.move(3, 3)
        pygame.draw.rect(superficie, COLOR_SOMBRA, shadow_rect, border_radius=12)
        pygame.draw.rect(superficie, COLOR_BOTON_MEZCLAR, self.botonMezclar, border_radius=12)
        mezclarTexto = FUENTE_PEQUEÑA.render("Mezclar", True, COLOR_BOTON_TEXTO)
        superficie.blit(mezclarTexto,(self.botonMezclar.x + self.botonMezclar.width // 2 - mezclarTexto.get_width()//2, 
                                    self.botonMezclar.y + self.botonMezclar.height//2 - mezclarTexto.get_height()//2))
        shadow_rect = self.botonGuardar.move(3, 3)
        pygame.draw.rect(superficie, (255, 235, 120), shadow_rect, border_radius=12)
        pygame.draw.rect(superficie, COLOR_BOTON_GUARDAR, self.botonGuardar, border_radius=12)
        guardarTexto = FUENTE_PEQUEÑA.render("Guardar Partida", True, COLOR_BOTON_TEXTO)
        superficie.blit(guardarTexto, (self.botonGuardar.x + self.botonGuardar.width // 2 - guardarTexto.get_width() // 2,
                                     self.botonGuardar.y + self.botonGuardar.height // 2 - guardarTexto.get_height() // 2))
        pygame.draw.rect(superficie, COLOR_BOTON2, self.botonPista, border_radius=12)
        texto_pista = FUENTE_BOTON.render("Pedir Pista", True, (255, 255, 255))
        superficie.blit(
            texto_pista,
            (
                self.botonPista.x + self.botonPista.width // 2 - texto_pista.get_width() // 2,
                self.botonPista.y + self.botonPista.height // 2 - texto_pista.get_height() // 2
            )
        )
        if self.pista_actual:
            texto_pista_actual = FUENTE_PEQUEÑA.render(f"Pista: {self.pista_actual}", True, (180, 60, 60))
            superficie.blit(texto_pista_actual, (20, 140))

    # Refresca el estado visual de los botones hexagonales
    def refrescar(self):
        posicionMouse = pygame.mouse.get_pos()
        for boton in self.botones:
            boton.refrescar(posicionMouse)

    # Muestra la ventana de instrucciones
    def ventana_como_jugar(self):
        ayuda_texto = [
            "Reglas de PoliPalabras:",
            "",
            "- Forma palabras usando las letras disponibles.",
            "- Cada palabra debe contener la letra central (azul).",
            "- Las palabras deben tener al menos 3 letras.",
            "- Cada palabra válida suma puntos según su longitud.",
            "",
            "Pistas:",
            "- Puedes pedir una pista con el botón correspondiente.",
            "- Cada pista cuesta 5 puntos.",
            "- Si tienes suficientes puntos, podrás ver letras de una palabra.",
            "",
            "¡Diviértete jugando PoliPalabras!"
        ]
        ANCHO, ALTO = 1280, 600 
        ventana = pygame.display.set_mode((ANCHO, ALTO))
        fuente_titulo = pygame.font.Font("dalek_pinpoint/DalekPinpointBold.ttf", 44)
        fuente_texto = pygame.font.Font("augustus/AUGUSTUS.ttf", 28)
        boton_cerrar = pygame.Rect(ANCHO//2 - 100, ALTO - 90, 200, 60)
        while True:
            ventana.fill(COLOR_FONDO)
            titulo = fuente_titulo.render("¿Cómo Jugar?", True, COLOR_BOTON)
            ventana.blit(titulo, (ANCHO//2 - titulo.get_width()//2, 20))
            y = 80
            for linea in ayuda_texto:
                txt = fuente_texto.render(linea, True, COLOR_TEXTO)
                ventana.blit(txt, (40, y))
                y += 30
            pygame.draw.rect(ventana, COLOR_BOTON, boton_cerrar, border_radius=12)
            txt_cerrar = fuente_texto.render("Cerrar", True, COLOR_BOTON_TEXTO)
            ventana.blit(txt_cerrar, (boton_cerrar.x + boton_cerrar.w//2 - txt_cerrar.get_width()//2, 
                                     boton_cerrar.y + boton_cerrar.h//2 - txt_cerrar.get_height()//2))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.display.set_mode((PANTALLA_ANCHO, PANTALLA_ALTO))
                    return
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if boton_cerrar.collidepoint(event.pos):
                        pygame.display.set_mode((PANTALLA_ANCHO, PANTALLA_ALTO))
                        return
            pygame.display.flip()

    # Maneja todos los eventos de la interfaz
    def manejarEventos(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN:
            for boton in self.botones:
                if boton.estaSeleccionado(evento.pos):
                    self.pilaDeEntrada.push(boton.letra)
            if self.botonAplicar.collidepoint(evento.pos):
                self.textoEntrada = ''.join(self.pilaDeEntrada.pila)
                self.checkearPalabraMensaje()
            if self.botonBorrar.collidepoint(evento.pos):
                self.pilaDeEntrada.empty()
            if self.botonMezclar.collidepoint(evento.pos):
                self.mezclarBotones()
            if self.botonGuardar.collidepoint(evento.pos):
                nombre_partida = pedir_nombre_partida(pantalla.get_size())
                guardar_partida(nombre_archivo="registroPoliPalabras.txt", 
                               usuario=usuario_actual, 
                               indice=indice_partida, 
                               juego=self.juego, 
                               tiempo_transcurrido=self.tiempoTranscurrido,
                               nombre=nombre_partida)
                self.mensaje = "Partida guardada!"
                self.mensajeTemp = pygame.time.get_ticks()
            if self.botonVolver.collidepoint(evento.pos):
                pygame.quit()
                os.system("python guiMenu.py " + usuario_actual)
                sys.exit()
            if self.botonComoJugar.collidepoint(evento.pos):
                self.ventana_como_jugar()
        elif evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_RETURN:
                self.textoEntrada = ''.join(self.pilaDeEntrada.pila)
                self.checkearPalabraMensaje()
            elif evento.key == pygame.K_BACKSPACE:
                self.pilaDeEntrada.pop()
            elif evento.key == pygame.K_s:
                self.mezclarBotones()
        # Solo verifica el botón de pista si es un evento de mouse
        if evento.type == pygame.MOUSEBUTTONDOWN:
            if hasattr(self, "botonPista") and self.botonPista.collidepoint(evento.pos):
                total_puntos = sum(self.juego.puntajes_palabras.get(p, 0) for p in self.juego.palabrasCorrectas)
                if total_puntos < 5:
                    self.mensaje = "¡Necesitas al menos 5 puntos para pedir una pista!"
                    self.mensajeTemp = pygame.time.get_ticks()
                else:
                    puntos_a_restar = 5
                    palabras_ordenadas = list(self.juego.palabrasCorrectas)[::-1]
                    for palabra in palabras_ordenadas:
                        puntaje = self.juego.puntajes_palabras.get(palabra, 0)
                        if puntaje > 0:
                            if puntaje >= puntos_a_restar:
                                self.juego.puntajes_palabras[palabra] -= puntos_a_restar
                                puntos_a_restar = 0
                                break
                            else:
                                puntos_a_restar -= puntaje
                                self.juego.puntajes_palabras[palabra] = 0
                    self.mostrar_ventana_moneda()

    # Chequea la palabra ingresada y muestra mensaje
    def checkearPalabraMensaje(self):
        self.mensaje = self.juego.checkearPalabra(self.textoEntrada)
        self.mensajeTemp = pygame.time.get_ticks()
        self.pilaDeEntrada.empty()

    # Muestra un mensaje temporal
    def mostrarMensaje(self, mens):
        self.mensajeTemp = mens
        self.mensajeTemporizador = pygame.time.get_ticks()

    # Actualiza el tiempo transcurrido
    def actualizarTiempo(self):
        self.tiempoTranscurrido = time.time()-self.tiempoInicio

    # Muestra la ventana de moneda (cara o cruz) con estilo coherente
    def mostrar_ventana_moneda(self):
        ANCHO, ALTO = 600, 400
        ventana = pygame.display.set_mode((ANCHO, ALTO))
        fuente_titulo = FUENTE_TITULO
        fuente_boton = FUENTE_BOTON
        fuente_opcion = FUENTE_BOTON
        cara_img = pygame.image.load("CaraMoneda.png")
        cruz_img = pygame.image.load("CruzMoneda.png")
        cara_img = pygame.transform.scale(cara_img, (120, 120))
        cruz_img = pygame.transform.scale(cruz_img, (120, 120))
        seleccion = None
        resultado = None
        animando = False
        frame = 0
        cara_x = 60
        cruz_x = ANCHO - 180
        img_y = 80
        boton_width = 120
        boton_height = 60
        boton_cara = pygame.Rect(cara_x, img_y + 120 + 20, boton_width, boton_height)
        boton_cruz = pygame.Rect(cruz_x, img_y + 120 + 20, boton_width, boton_height)
        while True:
            draw_gradient(ventana, COLOR_FONDO, (220, 220, 210), ANCHO, ALTO)
            pygame.draw.rect(ventana, COLOR_FONDO_LISTA, (20, 20, ANCHO-40, ALTO-40), border_radius=18)
            pygame.draw.rect(ventana, COLOR_BOTON, (20, 20, ANCHO-40, ALTO-40), 2, border_radius=18)
            titulo = fuente_titulo.render("Elige: Cara o Cruz", True, COLOR_BOTON)
            ventana.blit(titulo, (ANCHO//2 - titulo.get_width()//2, 35))
            pygame.draw.rect(ventana, (100,180,100), boton_cara, border_radius=12)
            pygame.draw.rect(ventana, (180,100,100), boton_cruz, border_radius=12)
            txt_cara = fuente_opcion.render("Cara", True, (255,255,255))
            txt_cruz = fuente_opcion.render("Cruz", True, (255,255,255))
            ventana.blit(txt_cara, (boton_cara.x + boton_cara.width//2 - txt_cara.get_width()//2, boton_cara.y + 12))
            ventana.blit(txt_cruz, (boton_cruz.x + boton_cruz.width//2 - txt_cruz.get_width()//2, boton_cruz.y + 12))
            if animando:
                if frame < 20:
                    ventana.blit(cara_img if frame % 2 == 0 else cruz_img, (ANCHO//2 - 60, 80))
                    pygame.display.flip()
                    pygame.time.delay(60)
                    frame += 1
                else:
                    if resultado == "cara":
                        ventana.blit(cara_img, (ANCHO//2 - 60, 80))
                    else:
                        ventana.blit(cruz_img, (ANCHO//2 - 60, 80))
                    pygame.display.flip()
                    pygame.time.delay(1000)
                    break
            else:
                ventana.blit(cara_img, (60, 80))
                ventana.blit(cruz_img, (ANCHO - 180, 80))
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.display.set_mode((PANTALLA_ANCHO, PANTALLA_ALTO))
                    return
                if event.type == pygame.MOUSEBUTTONDOWN and not animando:
                    if boton_cara.collidepoint(event.pos):
                        seleccion = "cara"
                        resultado = random.choice(["cara", "cruz"])
                        animando = True
                        frame = 0
                    elif boton_cruz.collidepoint(event.pos):
                        seleccion = "cruz"
                        resultado = random.choice(["cara", "cruz"])
                        animando = True
                        frame = 0
        pygame.display.set_mode((PANTALLA_ANCHO, PANTALLA_ALTO))
        if seleccion == resultado:
            self.dar_pista()
        else:
            self.mensaje = "¡No acertaste! Intenta de nuevo."
            self.mensajeTemp = pygame.time.get_ticks()

    # Genera y muestra una pista
    def dar_pista(self):
        palabras_disponibles = [p for p in self.juego.palabras if p not in self.juego.palabrasCorrectas]
        if not palabras_disponibles:
            self.mensaje = "¡Ya encontraste todas las palabras!"
            self.mensajeTemp = pygame.time.get_ticks()
            self.palabra_pista = ""
            self.pista_actual = ""
            return
        palabra = random.choice(palabras_disponibles)
        indices = sorted(random.sample(range(len(palabra)), min(3, len(palabra))))
        pista = ""
        for i, letra in enumerate(palabra):
            if i in indices:
                pista += letra.upper()
            else:
                pista += "_"
        self.palabra_pista = palabra
        self.pista_actual = pista
        self.mensaje = f"Pista generada"
        self.mensajeTemp = pygame.time.get_ticks()

    # Muestra la pantalla de victoria con estilo coherente
    def mostrar_ventana_victoria(self):
        ANCHO, ALTO = 700, 480
        ventana = pygame.display.set_mode((ANCHO, ALTO))
        fuente_titulo = pygame.font.Font("dalek_pinpoint/DalekPinpointBold.ttf", 64)
        fuente_puntaje = pygame.font.Font("augustus/AUGUSTUS.ttf", 38)
        fuente_boton = pygame.font.Font("augustus/AUGUSTUS.ttf", 36)
        corona_img = pygame.image.load("coronaganar.png")
        corona_img = pygame.transform.scale(corona_img, (180, 180))
        boton_menu = pygame.Rect(ANCHO//2 - 170, ALTO - 120, 340, 80)
        total_puntos = sum(self.juego.puntajes_palabras.get(p, 0) for p in self.juego.palabrasCorrectas)
        esperando = True
        while esperando:
            draw_gradient(ventana, COLOR_FONDO, (220, 220, 210), ANCHO, ALTO)
            pygame.draw.rect(ventana, COLOR_FONDO_LISTA, (40, 40, ANCHO-80, ALTO-80), border_radius=24)
            pygame.draw.rect(ventana, COLOR_BOTON, (40, 40, ANCHO-80, ALTO-80), 3, border_radius=24)
            ventana.blit(corona_img, (ANCHO//2 - 90, 60))
            texto = fuente_titulo.render("¡Ganaste!", True, COLOR_BOTON)
            ventana.blit(texto, (ANCHO//2 - texto.get_width()//2, 260))
            texto_puntaje = fuente_puntaje.render(f"Puntaje: {total_puntos}", True, (0, 100, 0))
            ventana.blit(texto_puntaje, (ANCHO//2 - texto_puntaje.get_width()//2, 320))
            pygame.draw.rect(ventana, COLOR_BOTON2, boton_menu, border_radius=16)
            pygame.draw.rect(ventana, (40, 80, 120), boton_menu, 3, border_radius=16)
            txt_menu = fuente_boton.render("Menú Principal", True, (255,255,255))
            ventana.blit(txt_menu, (boton_menu.x + boton_menu.width//2 - txt_menu.get_width()//2, boton_menu.y + boton_menu.height//2 - txt_menu.get_height()//2))
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if boton_menu.collidepoint(event.pos):
                        pygame.display.set_mode((PANTALLA_ANCHO, PANTALLA_ALTO))
                        os.system(f"python guiMenu.py {usuario_actual}")
                        pygame.quit()
                        sys.exit()

# Función principal del juego
def main():
    juego = logicaPoliPalabras.Juego()
    if indice_partida is not None:
        partida = cargar_partida(nombre_archivo="registroPoliPalabras.txt",
                                usuario=usuario_actual,
                                indice=indice_partida)
    else:
        partida = False
    if partida:
        letra_generada, letras_jugables, palabras_correctas, tiempo_guardado, palabras, letras_iniciales, palabras_por_letra = partida
        juego.letraGenerada = letra_generada
        juego.letrasJugables = letras_jugables
        juego.palabrasCorrectas = palabras_correctas
        juego.palabras = palabras
        juego.letrasIniciales = letras_iniciales
        juego.palabrasPorLetra = palabras_por_letra
        print(juego.palabras)
        print(len(juego.palabras))
    else:
        juego.letraGenerada = juego.generarLetra()
        juego.generarLetrasJugables()
        juego.obtenerPalabras()
        juego.disminuirPalabras(2)
        juego.guardarLetrasIniciales()
        print(juego.palabras)
    UIjuego = juegoUI(juego)
    if indice_partida is not None and partida:
        UIjuego.tiempoInicio = time.time() - tiempo_guardado
    reloj = pygame.time.Clock()
    ejecutando = True
    while ejecutando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                ejecutando = False
            UIjuego.manejarEventos(evento)
        UIjuego.actualizarTiempo()
        UIjuego.refrescar()
        UIjuego.dibujar(pantalla)
        pygame.display.flip()
        reloj.tick(60)
        if len(UIjuego.juego.palabrasCorrectas) == len(UIjuego.juego.palabras) and len(UIjuego.juego.palabras) > 0:
            UIjuego.mostrar_ventana_victoria()
    pygame.quit()
    sys.exit()

# Ejecuta el juego si este archivo es el principal
if __name__ == "__main__":
    main()


