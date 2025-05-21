import pygame
import sys
import subprocess
import os

pygame.init()

PANTALLA_ANCHO = 1280
PANTALLA_ALTO = 720
COLOR_FONDO = (230,230,230)
COLOR_BOTON = (47, 60, 92)
COLOR_BOTON_HOVER = (100, 150, 200)
COLOR_TEXTO = (245, 245, 245)
COLOR_TITULO = (47, 60, 92)

pantalla = pygame.display.set_mode((PANTALLA_ANCHO,PANTALLA_ALTO))
pygame.display.set_caption("Juegos De Letras - Menu Principal")

fuenteTitulo = pygame.font.SysFont("Comic Sans", 60 )
fuenteBoton = pygame.font.SysFont("Arial", 60 )

class Boton:
    def __init__(self, x, y, ancho, alto, texto, color, colorHover):
        self.rect = pygame.Rect(x,y,ancho,alto)
        self.Texto = texto
        self.Color = color
        self.ColorHover = colorHover
        self.estaHover = False

    def dibujar (self,superficie):
        color = self.ColorHover if self.estaHover else self.Color
        pygame.draw.rect(superficie,color,self.rect,border_radius=10)
        pygame.draw.rect(superficie,(0,0,0),self.rect,2,border_radius=10)   

        textoSuperficie = fuenteBoton.render(self.Texto,True, COLOR_TEXTO)
        textoRect = textoSuperficie.get_rect(center = self.rect.center)
        superficie.blit(textoSuperficie,textoRect)

    def checkHover(self, pos):
        self.estaHover = self.rect.collidepoint(pos)
        return self.estaHover   
    
    def estaClickeado (self,pos,evento):
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            return self.rect.collidepoint(pos)
        else:
            return False
        
def menu_Main():
    botonAncho = 1000
    botonAlto = 80
    botonX = PANTALLA_ANCHO // 2 - botonAncho //2 

    botonJugarPolipalabras = Boton(botonX,PANTALLA_ALTO // 2 - 100, botonAncho, botonAlto, "Jugar PoliPalabras", COLOR_BOTON, COLOR_BOTON_HOVER)
    botonJugarPorti = Boton(botonX,PANTALLA_ALTO // 2 + 50, botonAncho, botonAlto, "Jugar Porti", COLOR_BOTON, COLOR_BOTON_HOVER)

    ejecutar = True

    while ejecutar:
        posMouse = pygame.mouse.get_pos()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                ejecutar = False

            if  botonJugarPolipalabras.estaClickeado(posMouse, evento):
                pygame.quit()
                try:
                    dirScript = os.path.dirname(os.path.abspath(__file__))
                    pathJuego = os.path.join(dirScript,"UiPoliPalabras.py")
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    subprocess.Popen('cmd /c echo Starting game... && timeout 5', startupinfo=startupinfo)
                    subprocess.run([sys.executable, pathJuego])
                except (FileNotFoundError,PermissionError) as e:
                    print(f"Error al ejecutar {pathJuego}: {e}")
                return

            if botonJugarPorti.estaClickeado(posMouse, evento):
                pass
                '''
                pygame.quit()
                try:
                    dirScript = os.path.dirname(os.path.abspath(__file__))
                    pathJuego = os.path.join(dirScript,"elPortiJuego.py")
                    subprocess.run([sys.executable, pathJuego])
                except (FileNotFoundError,PermissionError) as e:
                    print(f"Error al ejecutar {pathJuego}: {e}")
                return
                ''' 
        botonJugarPolipalabras.checkHover(posMouse)
        botonJugarPorti.checkHover(posMouse)

        pantalla.fill(COLOR_FONDO)

        textoTitulo = fuenteTitulo.render("Juegos Palabras", True, COLOR_TITULO)
        rectTitulo = textoTitulo.get_rect(center = (PANTALLA_ANCHO // 2, 150))
        pantalla.blit(textoTitulo,rectTitulo)

        botonJugarPolipalabras.dibujar(pantalla)
        botonJugarPorti.dibujar(pantalla)

        pygame.display.flip()

    pygame.quit
    sys.exit()

if __name__ == "__main__":
    menu_Main()