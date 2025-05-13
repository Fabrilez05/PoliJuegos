import pygame
import logicaJuego as Juego 
import sys
import math

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
COLOR_LETRA_SELECCIONADA = (180,70,70)

pantalla = pygame.display.set_mode((PANTALLA_ANCHO, PANTALLA_ALTO))
pygame.display.set_caption("PoliPalabras")

fuente = pygame.font.SysFont("Arial", TAMAÑO_FUENTE)
fuentePequeña = pygame.font.SysFont("Arial", TAMAÑO_FUENTE_PEQUEÑO)

class boton:
    def __init__(self, centroX, centroY, letra, estaCentrado=False):
        self.centroX = centroX
        self.centroY = centroY
        self.letra = letra
        self.estaCentrado = estaCentrado
        self.color = COLOR_BOTON
        self.colorSeleccion = COLOR_BOTON_CURSOR if not estaCentrado else COLOR_LETRA_SELECCIONADA
        self.ColorActual = COLOR_BOTON if not estaCentrado else COLOR_LETRA_SELECCIONADA
        self.texto = fuente.render(letra.lower(), True, COLOR_TEXTO_BOTON)

        self.puntos = []
        for i in range(6):
            anguloSex = 60 * i - 30
            anguloRad = math.radians(anguloSex)
            x = centroX + TAMAÑO_BOTON * math.cos(anguloRad)
            y = centroY + TAMAÑO_BOTON * math.sin(anguloRad)
            self.puntos.append((x, y))

    def dibujar(self, superficie):
        pygame.draw.polygon(superficie, self.color, self.puntos)
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
        self.pilaDeEntrada = Juego.pilaEntrada()
        self.textoEntrada = ''
        self.renderTextoEntrada = ''
        self.cajaEntrada = pygame.Rect(50, PANTALLA_ALTO // 2 - ALTURA_CAJA_ENTRADA // 2, 400, ALTURA_CAJA_ENTRADA)
        self.botonAplicar = pygame.Rect(50, PANTALLA_ALTO // 2 + ALTURA_CAJA_ENTRADA // 2 + 20, 400, TAMAÑO_BOTON)
        self.botonBorrar = pygame.Rect(50, PANTALLA_ALTO // 2 + ALTURA_CAJA_ENTRADA // 2 + 20 + TAMAÑO_BOTON + 10, 400, TAMAÑO_BOTON)
        self.mensaje = ''
        self.mensajeTemp = 0

        self.crearBotones()

    def crearBotones(self):
        self.botones = []
        centroX, centroY = PANTALLA_ANCHO // 2 + 200, PANTALLA_ALTO // 2
        letraSeleccionada = self.juego.letraGenerada
        otrasLetras = [letter for letter in self.juego.letrasJugables if letter != letraSeleccionada]

        # Hexágono central
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


    def dibujar(self, superficie):
        superficie.fill(COLOR_FONDO)

        titulo = fuente.render("PoliPalabras", True, COLOR_BOTON)
        instrucciones = fuentePequeña.render(f"La palabra debe contener {self.juego.letraGenerada.upper()}", True, (0, 0, 0))

        superficie.blit(titulo, (PANTALLA_ANCHO // 2 - titulo.get_width() // 2, 50))
        superficie.blit(instrucciones, (PANTALLA_ANCHO // 2 - instrucciones.get_width() // 2, 100))

        pygame.draw.rect(superficie, COLOR_CAJA_ENTRADA, self.cajaEntrada, 10)
        pygame.draw.rect(superficie, (0, 0, 0), self.cajaEntrada, 2, 10)

        if self.pilaDeEntrada.is_empty():
            self.renderTextoEntrada = ''
        else:
            self.renderTextoEntrada = ''.join(self.pilaDeEntrada.pila).upper()
        superficieEntrada = fuente.render(self.renderTextoEntrada  , True, COLOR_TEXTO_CAJA_ENTRADA)
        superficie.blit(superficieEntrada, (self.cajaEntrada.x + 10, self.cajaEntrada.y + 10))

        for boton in self.botones:
            boton.dibujar(superficie)

        pygame.draw.rect(superficie, COLOR_BOTON, self.botonAplicar, 10)
        pygame.draw.rect(superficie, (0, 0, 0), self.botonAplicar, 2, 10)
        aplicarTexto = fuente.render("Aplicar", True, COLOR_TEXTO_BOTON)
        superficie.blit(aplicarTexto, (self.botonAplicar.x + self.botonAplicar.width // 2 - aplicarTexto.get_width() // 2,
                                       self.botonAplicar.y + self.botonAplicar.height // 2 - aplicarTexto.get_height() // 2))

        pygame.draw.rect(superficie, COLOR_BOTON, self.botonBorrar, 10)
        pygame.draw.rect(superficie, (0, 0, 0), self.botonBorrar, 2, 10)
        borrarTexto = fuente.render("Borrar", True, COLOR_TEXTO_BOTON)
        superficie.blit(borrarTexto, (self.botonBorrar.x + self.botonBorrar.width // 2 - borrarTexto.get_width() // 2,
                                      self.botonBorrar.y + self.botonBorrar.height // 2 - borrarTexto.get_height() // 2))

        if self.mensaje and pygame.time.get_ticks() - self.mensajeTemp < 3000:
            mensajeSuperficie = fuentePequeña.render(f"Longitud: {len(self.textoEntrada)}", True, (0, 0, 0))
            superficie.blit(mensajeSuperficie, (PANTALLA_ANCHO // 2 - mensajeSuperficie.get_width() // 2,
                                                PANTALLA_ALTO // 2 + ALTURA_CAJA_ENTRADA // 2 + 20 + TAMAÑO_BOTON + 10 + TAMAÑO_BOTON // 2 - mensajeSuperficie.get_height() // 2))

        longitudTexto = fuente.render(self.textoEntrada.upper(), True, COLOR_TEXTO_CAJA_ENTRADA)
        superficie.blit(longitudTexto, (PANTALLA_ANCHO // 2 - longitudTexto.get_width() // 2, 450))

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
                    self.checkearPalabra()

                if self.botonBorrar.collidepoint(evento.pos):
                    self.pilaDeEntrada.empty()

        elif evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_RETURN:
                self.checkearPalabra()
            elif evento.key == pygame.K_BACKSPACE:
                self.pilaDeEntrada.pop()

    def checkearPalabra(self):
        self.textoEntrada.join(self.pilaDeEntrada.pila)
        if len(self.textoEntrada) < 3:
            self.mensaje = "La palabra es muy corta"
        elif self.juego.letraGenerada not in self.textoEntrada:
            self.mensaje = f"La palabra no contiene la letra generada: {self.juego.letraGenerada}"
        elif self.textoEntrada not in self.juego.palabras:
            self.mensaje = f"La palabra no está en el diccionario: {self.textoEntrada}"
        else:
            self.mensaje = f"La palabra es correcta: {self.textoEntrada}"

        self.pilaDeEntrada.empty()

    def mostrarMensaje(self, mens):
        self.mensajeTemp = mens
        self.mensajeTemporizador = pygame.time.get_ticks()




def main():

    juego = Juego.Juego()
    juego.letraGenerada = juego.generarLetra()
    juego.generarLetrasJugables()
    juego.obtenerPalabras()
    juego.disminuirPalabras()

    UIjuego = juegoUI(juego)

    reloj = pygame.time.Clock()
    ejecutando = True

    while ejecutando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                ejecutando = False
            UIjuego.manejarEventos(evento)

        UIjuego.refrescar()
        UIjuego.dibujar(pantalla)
        pygame.display.flip()
        reloj.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

