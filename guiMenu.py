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
fuenteUsuario = pygame.font.SysFont("Arial", 30)

# --- Usuario actual desde argumentos ---
usuario_actual = sys.argv[1] if len(sys.argv) > 1 else None

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

    # Cambia la separación vertical entre los botones para acercarlos
    espacio_vertical = 40  # Antes era 300, ahora es 40 para acercarlos

    botonJugarPolipalabras = Boton(
        botonX,
        PANTALLA_ALTO // 2 - botonAlto - espacio_vertical // 2,
        botonAncho,
        botonAlto,
        "Jugar PoliPalabras",
        COLOR_BOTON,
        COLOR_BOTON_HOVER
    )
    botonPolisopa = Boton(
        botonX,
        PANTALLA_ALTO // 2 + espacio_vertical // 2,
        botonAncho,
        botonAlto,
        "Jugar PoliSopa",
        COLOR_BOTON,
        COLOR_BOTON_HOVER
    )

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

            if botonPolisopa.estaClickeado(posMouse, evento):
                pygame.quit()
                try:
                    dirScript = os.path.dirname(os.path.abspath(__file__))
                    pathJuego = os.path.join(dirScript, "guiPoliSopa.py")
                    pathCarga = os.path.join(dirScript, "guiCarga.py")
                    registro = os.path.join(dirScript, "registroSopa.txt")
                    # Si hay partidas, abre guiCarga.py, si no, abre el juego directamente
                    if hay_partidas_usuario(registro, usuario_actual):
                        subprocess.run([sys.executable, pathCarga, usuario_actual, "polisopa"])
                    else:
                        subprocess.run([sys.executable, pathJuego, usuario_actual])
                except (FileNotFoundError, PermissionError) as e:
                    print(f"Error al ejecutar el juego: {e}")
                return
                
        botonJugarPolipalabras.checkHover(posMouse)
        botonPolisopa.checkHover(posMouse)

        pantalla.fill(COLOR_FONDO)

        textoTitulo = fuenteTitulo.render("Juegos Palabras", True, COLOR_TITULO)
        rectTitulo = textoTitulo.get_rect(center = (PANTALLA_ANCHO // 2, 150))
        pantalla.blit(textoTitulo,rectTitulo)

        botonJugarPolipalabras.dibujar(pantalla)
        botonPolisopa.dibujar(pantalla)

        # Dibuja el texto del usuario si existe
        if usuario_actual:
            texto_usuario = fuenteUsuario.render(f"Usuario: {usuario_actual}", True, (0,0,0))
            pantalla.blit(texto_usuario, (20, 20))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

def abrir_polisopa():
    ruta = os.path.join(os.path.dirname(__file__), "guiPoliSopa.py")
    subprocess.Popen([sys.executable, ruta, usuario_actual])

boton_polisopa = Boton(100, 100, 200, 50, "PoliSopa", COLOR_BOTON, COLOR_BOTON_HOVER)

def hay_partidas_usuario(nombre_archivo, usuario):
    if not os.path.exists(nombre_archivo):
        return False
    with open(nombre_archivo, "r", encoding="utf-8") as f:
        contenido = f.read().split("=== PARTIDA ===\n")
        for p in contenido:
            if p.strip().startswith(f"USUARIO:{usuario}"):
                return True
    return False

if __name__ == "__main__":
    menu_Main()