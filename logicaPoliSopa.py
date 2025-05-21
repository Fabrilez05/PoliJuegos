import random

def seleccionar_palabras(diccionario):
    palabras6 = [p for p in diccionario if len(p) == 6]
    palabras7 = [p for p in diccionario if len(p) == 7]
    palabras8 = [p for p in diccionario if len(p) == 8]
    palabras9 = [p for p in diccionario if len(p) == 9]
    seleccionadas = (
        random.sample(palabras6, 3) +
        random.sample(palabras7, 2) +
        random.sample(palabras8, 1) +
        random.sample(palabras9, 1)
    )
    random.shuffle(seleccionadas)
    return [p.upper() for p in seleccionadas]

def cargar_diccionario(ruta):
    with open(ruta, encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

class PoliSopa:
    def __init__(self, palabras, filas=5, columnas=6):  # Cambiado a 5x6
        self.filas = filas
        self.columnas = columnas
        self.palabras = palabras
        self.tablero = [['' for _ in range(columnas)] for _ in range(filas)]
        self.posiciones_palabras = {}  # {palabra: [(fila, col), ...]}
        self.colocar_palabras()
        self.rellenar_tablero()

    def colocar_palabras(self):
        # Ordena las palabras de mayor a menor longitud
        palabras_ordenadas = sorted(self.palabras, key=len, reverse=True)
        while True:  # Sin límite de intentos
            self.tablero = [['' for _ in range(self.columnas)] for _ in range(self.filas)]
            self.posiciones_palabras = {}
            exito = True
            for palabra in palabras_ordenadas:
                for _ in range(300):  # Más intentos por palabra
                    camino = self.buscar_camino_para_palabra(palabra)
                    if camino:
                        for (f, c), letra in zip(camino, palabra):
                            self.tablero[f][c] = letra
                        self.posiciones_palabras[palabra] = camino
                        break
                else:
                    exito = False
                    break
            if exito:
                break

    def buscar_camino_para_palabra(self, palabra):
        # Busca un camino ortogonal aleatorio para la palabra
        for _ in range(100):
            f = random.randint(0, self.filas-1)
            c = random.randint(0, self.columnas-1)
            if self.tablero[f][c] not in ('', palabra[0]):
                continue
            camino = [(f, c)]
            if self._camino_recursivo(f, c, palabra, 1, set([(f, c)]), camino):
                return camino
        return None

    def _camino_recursivo(self, f, c, palabra, idx, visitados, camino):
        if idx == len(palabra):
            return True
        vecinos = self.vecinos_ortogonales(f, c)
        random.shuffle(vecinos)
        for nf, nc in vecinos:
            if (nf, nc) in visitados:
                continue
            if self.tablero[nf][nc] not in ('', palabra[idx]):
                continue
            visitados.add((nf, nc))
            camino.append((nf, nc))
            if self._camino_recursivo(nf, nc, palabra, idx+1, visitados, camino):
                return True
            camino.pop()
            visitados.remove((nf, nc))
        return False

    def vecinos_ortogonales(self, f, c):
        vecinos = []
        for df, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
            nf, nc = f+df, c+dc
            if 0 <= nf < self.filas and 0 <= nc < self.columnas:
                vecinos.append((nf, nc))
        return vecinos

    def rellenar_tablero(self):
        for i in range(self.filas):
            for j in range(self.columnas):
                if self.tablero[i][j] == '':
                    self.tablero[i][j] = random.choice('ABCDEFGHIJKLMNÑOPQRSTUVWXYZ')

    def mostrar(self):
        for fila in self.tablero:
            print(' '.join(fila))

if __name__ == "__main__":
    diccionario = cargar_diccionario("diccPoliSopa.txt")
    palabras = seleccionar_palabras(diccionario)
    juego = PoliSopa(palabras, filas=5, columnas=6)  # Cambiado a 5x6
    juego.mostrar()
    print("\nPalabras a buscar:", ', '.join(palabras))