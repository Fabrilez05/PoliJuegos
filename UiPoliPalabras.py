import pygame
import logicaJuego
import sys
import math
import time
import random

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
        self.pilaDeEntrada = logicaJuego.pilaEntrada()
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
                    textoPalabra = fuentePequeña.render(palabra, True, COLOR_TEXTO_LISTA)
                    superficie.blit(textoPalabra,(self.rectLista.x + 30, self.rectLista.y + contrapesoY))
                    contrapesoY += anchoLinea

        pygame.draw.rect(superficie, COLOR_BOTON_MEZCLAR, self.botonMezclar, border_radius=10)
        pygame.draw.rect(superficie,COLOR_BORDE_BOTON_MEZCLAR,self.botonMezclar,2,border_radius=10)
        mezclarTexto = fuentePequeña.render("Mezclar", True, COLOR_TEXTO_BOTON)
        superficie.blit(mezclarTexto,(self.botonMezclar.x + self.botonMezclar.width // 2 - mezclarTexto.get_width()//2, self.botonMezclar.y + self.botonMezclar.height//2 - mezclarTexto.get_height()//2))


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

        elif evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_RETURN:
                self.textoEntrada = ''.join(self.pilaDeEntrada.pila)
                self.checkearPalabraMensaje()
            elif evento.key == pygame.K_BACKSPACE:
                self.pilaDeEntrada.pop()
            elif evento.key == pygame.K_s:
                self.mezclarBotones()


    def checkearPalabraMensaje(self):
        self.mensaje = self.juego.checkearPalabra(self.textoEntrada)
        self.mensajeTemp = pygame.time.get_ticks()
        self.pilaDeEntrada.empty()

    def mostrarMensaje(self, mens):
        self.mensajeTemp = mens
        self.mensajeTemporizador = pygame.time.get_ticks()

    def actualizarTiempo(self):
        self.tiempoTranscurrido = time.time()-self.tiempoInicio

def main():
    juego = logicaJuego.Juego()
    juego.letraGenerada = juego.generarLetra()
    juego.generarLetrasJugables()
    juego.obtenerPalabras()
    juego.guardarLetrasIniciales()
    print(juego.palabras)
    juego.disminuirPalabras()
    
    UIjuego = juegoUI(juego)

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