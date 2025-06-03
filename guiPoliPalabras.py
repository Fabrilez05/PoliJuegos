import pygame
import logicaPoliPalabras
import sys
import math
import time
import random
import os

pygame.init()


PANTALLA_ANCHO = 1280
PANTALLA_ALTO = 720
TAMAÑO_BOTON = 70
ALTURA_CAJA_ENTRADA = 90
COLOR_FONDO = (230,230,230)
COLOR_BOTON = (47,60,92)
COLOR_BOTON_CURSOR = (100, 150, 200)
COLOR_TEXTO_BOTON = (245,245,245)
COLOR_CAJA_ENTRADA = (255, 255, 255)
COLOR_TEXTO_CAJA_ENTRADA = (0, 0, 0)
TAMAÑO_FUENTE = 40
TAMAÑO_FUENTE_PEQUEÑO = 30
COLOR_LETRA_SELECCIONADA = (3,136,252)
COLOR_BOTON_APLICAR = (70, 180, 70)  
COLOR_BOTON_BORRAR = (180, 70, 70)   
COLOR_BORDE_BOTON_APLICAR = (50, 150, 50)  
COLOR_BORDE_BOTON_BORRAR = (150, 50, 50) 
COLOR_TEXTO_LISTA = (0,0,0)
COLOR_FONDO_LISTA = (240,240,240) 
COLOR_BORDE_LISTA = (200,200,200)
ANCHO_LISTA = 300
MARGEN_LISTA = 20
COLOR_BOTON_MEZCLAR = (227, 214, 93)
COLOR_BORDE_BOTON_MEZCLAR = (252, 198, 33)
ANCHO_BOTON_MEZCLAR = 150
ALTO_BOTON_MEZCLAR = TAMAÑO_BOTON
COLOR_BOTON_GUARDAR = (255, 215, 0)  # Amarillo
COLOR_BORDE_BOTON_GUARDAR = (200, 150, 0)
COLOR_BOTON_VOLVER = (180, 70, 70)  # Red color for the back button
COLOR_BORDE_BOTON_VOLVER = (150, 50, 50)

usuario_actual = sys.argv[1] if len(sys.argv) > 1 else "anonimo"
indice_partida = int(sys.argv[2]) if len(sys.argv) > 2 else None

pantalla = pygame.display.set_mode((PANTALLA_ANCHO, PANTALLA_ALTO))
pygame.display.set_caption("PoliPalabras")

fuente = pygame.font.SysFont("Arial", TAMAÑO_FUENTE)
fuentePequeña = pygame.font.SysFont("Arial", TAMAÑO_FUENTE_PEQUEÑO)

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
        
        # Extraer datos de la partida
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
                # formato: PALABRAS_POR_LETRA:a:pal1|pal2,b:pal3|pal4
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

def guardar_partida(nombre_archivo="registroPoliPalabras.txt", usuario=None, indice=None, juego=None, tiempo_transcurrido=0,nombre = None):
    # Lee todas las partidas
    if not os.path.exists(nombre_archivo):
        partidas = []
    else:
        with open(nombre_archivo, "r", encoding="utf-8") as f:
            contenido = f.read().split("=== PARTIDA ===")
            partidas = [p for p in contenido if p.strip()]
    
    # Serializar letras_iniciales si existe
    letras_iniciales_str = ""
    if hasattr(juego, "letrasIniciales") and juego.letrasIniciales:
        letras_iniciales_str = ",".join(f"{letra}:{cantidad}" for letra, cantidad in juego.letrasIniciales.items())

    # Serializar palabras_por_letra si existe
    palabras_por_letra_str = ""
    if hasattr(juego, "palabrasPorLetra") and juego.palabrasPorLetra:
        palabras_por_letra_str = ",".join(
            f"{letra}:{'|'.join(juego.palabrasPorLetra[letra])}" for letra in juego.palabrasPorLetra
        )
    
    # Construye el nuevo registro
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
    
    # Guarda todas las partidas
    with open(nombre_archivo, "w", encoding="utf-8") as f:
        for p in partidas:
            f.write("=== PARTIDA ===\n" + p)

def pedir_nombre_partida(main_size):
    # Store the original display surface
    original_display = pygame.display.get_surface()
    
    # Create a new temporary window
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
    
    # Restore the original display surface
    pygame.display.set_mode(main_size)
    return text if text else "SinNombre"

class boton:
    def __init__(self, centroX, centroY, letra, estaCentrado=False):
        self.centroX = centroX
        self.centroY = centroY
        self.letra = letra
        self.estaCentrado = estaCentrado
        self.color = COLOR_LETRA_SELECCIONADA if estaCentrado else COLOR_BOTON 
        self.colorSeleccion = COLOR_BOTON_CURSOR if not estaCentrado else COLOR_LETRA_SELECCIONADA
        self.ColorActual = self.color
        self.texto = fuente.render(letra.lower(), True, COLOR_TEXTO_BOTON)

        self.puntos = []
        for i in range(6):
            anguloSex = 60 * i - 30
            anguloRad = math.radians(anguloSex)
            x = centroX + TAMAÑO_BOTON * math.cos(anguloRad)
            y = centroY + TAMAÑO_BOTON * math.sin(anguloRad)
            self.puntos.append((x, y))

    def dibujar(self, superficie):
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


class juegoUI:
    def __init__(self, juego):
        self.juego = juego
        self.botones = []
        self.pilaDeEntrada = logicaPoliPalabras.pilaEntrada()
        self.textoEntrada = ''
        self.renderTextoEntrada = ''
        self.cajaEntrada = pygame.Rect(50, PANTALLA_ALTO // 2 - ALTURA_CAJA_ENTRADA // 2, 350, ALTURA_CAJA_ENTRADA)
        self.botonAplicar = pygame.Rect(50, PANTALLA_ALTO // 2 + ALTURA_CAJA_ENTRADA // 2 + 20, 350, TAMAÑO_BOTON)
        self.botonBorrar = pygame.Rect(50, PANTALLA_ALTO // 2 + ALTURA_CAJA_ENTRADA // 2 + 20 + TAMAÑO_BOTON + 10, 350, TAMAÑO_BOTON)
        self.mensaje = ''
        self.mensajeTemp = 0
        self.tiempoInicio = time.time()
        self.tiempoTranscurrido = 0
        self.rectLista = pygame.Rect(PANTALLA_ANCHO - ANCHO_LISTA - MARGEN_LISTA, 150, ANCHO_LISTA, PANTALLA_ALTO -20)
        self.botonMezclar = pygame.Rect(PANTALLA_ANCHO // 2 - ANCHO_BOTON_MEZCLAR // 2 + 50, (PANTALLA_ALTO // 2)+(3 * TAMAÑO_BOTON),ANCHO_BOTON_MEZCLAR,ALTO_BOTON_MEZCLAR)
        self.poscicionesOriginales = []
        self.botonGuardar = pygame.Rect(PANTALLA_ANCHO - ANCHO_LISTA - MARGEN_LISTA, 100, ANCHO_LISTA, 40)
        self.botonVolver = pygame.Rect(PANTALLA_ANCHO - ANCHO_LISTA - MARGEN_LISTA, 60, ANCHO_LISTA, 40)

        self.palabra_pista = ""
        self.pista_actual = ""
  
        self.crearBotones()

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

    def mezclarBotones(self):
        botonesExteriores = [boton for boton in self.botones if not boton.estaCentrado]

        letras = [boton.letra for boton in botonesExteriores]

        random.shuffle(letras)

        for boton,letra in zip(botonesExteriores,letras):
            boton.letra = letra
            boton.texto = fuente.render(letra.lower(), True, COLOR_TEXTO_BOTON)
        

    def dibujar(self, superficie):
        superficie.fill(COLOR_FONDO)

        titulo = fuente.render("PoliPalabras", True, COLOR_BOTON)
        instrucciones = fuentePequeña.render(f"La palabra debe contener {self.juego.letraGenerada.upper()}", True, (0, 0, 0))
        superficie.blit(titulo, (PANTALLA_ANCHO // 2 - titulo.get_width() // 2, 50))
        superficie.blit(instrucciones, (PANTALLA_ANCHO // 2 - instrucciones.get_width() // 2, 100))

        if self.mensaje and pygame.time.get_ticks() - self.mensajeTemp < 3000:
            mensajeSuperficie = fuentePequeña.render(self.mensaje, True, (0, 0, 0))
            superficie.blit(mensajeSuperficie, (self.cajaEntrada.x + self.cajaEntrada.width // 2 - mensajeSuperficie.get_width() // 2,
                                              self.cajaEntrada.y - mensajeSuperficie.get_height() - 10))

        pygame.draw.rect(superficie, COLOR_CAJA_ENTRADA, self.cajaEntrada, 10)
        pygame.draw.rect(superficie, (0, 0, 0), self.cajaEntrada, 2, 10)

        if self.pilaDeEntrada.is_empty():
            self.renderTextoEntrada = ''
        else:
            self.renderTextoEntrada = ''.join(self.pilaDeEntrada.pila).upper()
        superficieEntrada = fuente.render(self.renderTextoEntrada, True, COLOR_TEXTO_CAJA_ENTRADA)
        superficie.blit(superficieEntrada, (self.cajaEntrada.x + 10, self.cajaEntrada.y + 10))

        for boton in self.botones:
            boton.dibujar(superficie)

        pygame.draw.rect(superficie, COLOR_BOTON_APLICAR, self.botonAplicar, border_radius=10)
        pygame.draw.rect(superficie, COLOR_BORDE_BOTON_APLICAR, self.botonAplicar, 2, border_radius=10)
        aplicarTexto = fuente.render("Aplicar", True, COLOR_TEXTO_BOTON)
        superficie.blit(aplicarTexto, (self.botonAplicar.x + self.botonAplicar.width // 2 - aplicarTexto.get_width() // 2,
                                       self.botonAplicar.y + self.botonAplicar.height // 2 - aplicarTexto.get_height() // 2))

        pygame.draw.rect(superficie, COLOR_BOTON_BORRAR, self.botonBorrar, border_radius=10)
        pygame.draw.rect(superficie, COLOR_BORDE_BOTON_BORRAR, self.botonBorrar, 2, border_radius=10)
        borrarTexto = fuente.render("Borrar", True, COLOR_TEXTO_BOTON)
        superficie.blit(borrarTexto, (self.botonBorrar.x + self.botonBorrar.width // 2 - borrarTexto.get_width() // 2,
                                      self.botonBorrar.y + self.botonBorrar.height // 2 - borrarTexto.get_height() // 2))

        minutos = int(self.tiempoTranscurrido // 60)
        segundos = int(self.tiempoTranscurrido % 60)
        textoTiempo = fuentePequeña.render(f'{minutos:02d}:{segundos:02d}',True,COLOR_BOTON)
        superficie.blit(textoTiempo, (PANTALLA_ANCHO - textoTiempo.get_width()-20,20))

        pygame.draw.rect(superficie, COLOR_FONDO_LISTA, self.rectLista, 0 ,10)
        pygame.draw.rect(superficie, COLOR_BORDE_LISTA, self.rectLista, 2, 10)

        tituloLista = fuentePequeña.render('Las palabras inician por: ', True, COLOR_BOTON)
        superficie.blit(tituloLista, (self.rectLista.x + self.rectLista.width//2 - tituloLista.get_width()//2, self.rectLista.y + 10))
        contrapesoY = 50
        anchoLinea = 25
        for letra in sorted(self.juego.letrasIniciales.keys()):
            correctas = self.juego.letrasIniciales[letra]
            total = len(self.juego.palabrasPorLetra.get(letra,[]))
            textoLinea = fuentePequeña.render(f"empiezan por {letra.upper()}: {correctas}/{total}", True, COLOR_TEXTO_LISTA)
            superficie.blit(textoLinea, (self.rectLista.x + 20, self.rectLista.y + contrapesoY))
            contrapesoY += anchoLinea
        if contrapesoY + 50 < self.rectLista.height:
            contrapesoY +=10
            tituloCorrectas = fuentePequeña.render('Palabras Acertadas: ', True, COLOR_BOTON)
            superficie.blit(tituloCorrectas,(self.rectLista.x+20,self.rectLista.y + contrapesoY))
            contrapesoY +=anchoLinea

            for palabra in self.juego.palabrasCorrectas:
                if contrapesoY + anchoLinea < self.rectLista.height:
                    puntaje = self.juego.puntajes_palabras.get(palabra, 0)
                    textoPalabra = fuentePequeña.render(f"{palabra} ({puntaje} pts)", True, COLOR_TEXTO_LISTA)
                    superficie.blit(textoPalabra, (self.rectLista.x + 30, self.rectLista.y + contrapesoY))
                    contrapesoY += anchoLinea

        pygame.draw.rect(superficie, COLOR_BOTON_MEZCLAR, self.botonMezclar, border_radius=10)
        pygame.draw.rect(superficie,COLOR_BORDE_BOTON_MEZCLAR,self.botonMezclar,2,border_radius=10)
        mezclarTexto = fuentePequeña.render("Mezclar", True, COLOR_TEXTO_BOTON)
        superficie.blit(mezclarTexto,(self.botonMezclar.x + self.botonMezclar.width // 2 - mezclarTexto.get_width()//2, self.botonMezclar.y + self.botonMezclar.height//2 - mezclarTexto.get_height()//2))

        pygame.draw.rect(superficie, COLOR_BOTON_GUARDAR, self.botonGuardar, border_radius=10)
        pygame.draw.rect(superficie, COLOR_BORDE_BOTON_GUARDAR, self.botonGuardar, 2, border_radius=10)
        guardarTexto = fuentePequeña.render("Guardar Partida", True, (0, 0, 0))
        superficie.blit(guardarTexto, (self.botonGuardar.x + self.botonGuardar.width // 2 - guardarTexto.get_width() // 2,
                                     self.botonGuardar.y + self.botonGuardar.height // 2 - guardarTexto.get_height() // 2))
        
        # Draw the back to menu button
        pygame.draw.rect(superficie, COLOR_BOTON_VOLVER, self.botonVolver, border_radius=10)
        pygame.draw.rect(superficie, COLOR_BORDE_BOTON_VOLVER, self.botonVolver, 2, border_radius=10)
        volverTexto = fuentePequeña.render("Volver al Menú", True, COLOR_TEXTO_BOTON)
        superficie.blit(volverTexto, (self.botonVolver.x + self.botonVolver.width // 2 - volverTexto.get_width() // 2,
                                    self.botonVolver.y + self.botonVolver.height // 2 - volverTexto.get_height() // 2))

        # Mostrar total de puntos en la esquina superior izquierda
        total_puntos = sum(self.juego.puntajes_palabras.get(p, 0) for p in self.juego.palabrasCorrectas)
        texto_total = fuentePequeña.render(f"Total puntos: {total_puntos}", True, (0, 120, 0))
        superficie.blit(texto_total, (20, 20))

        # Botón de pista debajo del puntaje
        self.botonPista = pygame.Rect(20, 60, 140, 40)
        pygame.draw.rect(superficie, (70, 130, 180), self.botonPista, border_radius=8)
        pygame.draw.rect(superficie, (40, 80, 120), self.botonPista, 2, border_radius=8)
        texto_pista = fuentePequeña.render("Pedir Pista", True, (255,255,255))
        superficie.blit(texto_pista, (self.botonPista.x + self.botonPista.width//2 - texto_pista.get_width()//2,
                                      self.botonPista.y + self.botonPista.height//2 - texto_pista.get_height()//2))

        # Mostrar la pista actual debajo del botón de pista
        if self.pista_actual:
            texto_pista_actual = fuentePequeña.render(f"Pista: {self.pista_actual}", True, (180, 60, 60))
            superficie.blit(texto_pista_actual, (20, 110))


    def refrescar(self):
        posicionMouse = pygame.mouse.get_pos()
        for boton in self.botones:
            boton.refrescar(posicionMouse)

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
                # Chequea puntos antes de abrir la ventana
                total_puntos = sum(self.juego.puntajes_palabras.get(p, 0) for p in self.juego.palabrasCorrectas)
                if total_puntos < 5:
                    self.mensaje = "¡Necesitas al menos 5 puntos para pedir una pista!"
                    self.mensajeTemp = pygame.time.get_ticks()
                else:
                    # Restar 5 puntos aquí, de las palabras acertadas (de atrás hacia adelante)
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
                    # Ahora sí, abrir la ventana de moneda
                    self.mostrar_ventana_moneda()

    def checkearPalabraMensaje(self):
        self.mensaje = self.juego.checkearPalabra(self.textoEntrada)
        self.mensajeTemp = pygame.time.get_ticks()
        self.pilaDeEntrada.empty()

    def mostrarMensaje(self, mens):
        self.mensajeTemp = mens
        self.mensajeTemporizador = pygame.time.get_ticks()

    def actualizarTiempo(self):
        self.tiempoTranscurrido = time.time()-self.tiempoInicio

    def mostrar_ventana_moneda(self):
        # Cargar imágenes (asegúrate de tener CaraMoneda.png y CruzMoneda.png en tu carpeta)
        cara_img = pygame.image.load("CaraMoneda.png")
        cruz_img = pygame.image.load("CruzMoneda.png")
        cara_img = pygame.transform.scale(cara_img, (120, 120))
        cruz_img = pygame.transform.scale(cruz_img, (120, 120))

        ventana = pygame.display.set_mode((400, 300))
        fuente_local = pygame.font.SysFont("Arial", 28)
        seleccion = None
        resultado = None
        animando = False
        frame = 0

        boton_cara = pygame.Rect(60, 200, 100, 50)
        boton_cruz = pygame.Rect(240, 200, 100, 50)

        while True:
            ventana.fill((230, 230, 230))
            titulo = fuente_local.render("Elige: Cara o Cruz", True, (0, 0, 0))
            ventana.blit(titulo, (200 - titulo.get_width()//2, 30))

            pygame.draw.rect(ventana, (100,180,100), boton_cara)
            pygame.draw.rect(ventana, (180,100,100), boton_cruz)
            txt_cara = fuente_local.render("Cara", True, (255,255,255))
            txt_cruz = fuente_local.render("Cruz", True, (255,255,255))
            ventana.blit(txt_cara, (boton_cara.x + boton_cara.width//2 - txt_cara.get_width()//2, boton_cara.y + 10))
            ventana.blit(txt_cruz, (boton_cruz.x + boton_cruz.width//2 - txt_cruz.get_width()//2, boton_cruz.y + 10))

            if animando:
                # Animación simple de moneda girando
                if frame < 20:
                    ventana.blit(cara_img if frame % 2 == 0 else cruz_img, (140, 70))
                    pygame.display.flip()
                    pygame.time.delay(60)
                    frame += 1
                else:
                    # Mostrar resultado final
                    if resultado == "cara":
                        ventana.blit(cara_img, (140, 70))
                    else:
                        ventana.blit(cruz_img, (140, 70))
                    pygame.display.flip()
                    pygame.time.delay(1000)
                    break
            else:
                ventana.blit(cara_img, (60, 70))
                ventana.blit(cruz_img, (220, 70))

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

        # Después de la animación, mostrar pista si acertó
        pygame.display.set_mode((PANTALLA_ANCHO, PANTALLA_ALTO))
        if seleccion == resultado:
            self.dar_pista()
        else:
            self.mensaje = "¡No acertaste! Intenta de nuevo."
            self.mensajeTemp = pygame.time.get_ticks()

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
        juego.disminuirPalabras()
        juego.guardarLetrasIniciales()
        print(juego.palabras)
        print(len(juego.palabras))

    # Initialize UI with the game state
    UIjuego = juegoUI(juego)
    # Adjust time if loaded from save
    if indice_partida is not None and partida:
        UIjuego.tiempoInicio = time.time() - tiempo_guardado

    # Main game loop
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
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
