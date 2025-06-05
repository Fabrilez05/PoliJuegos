import random

# Direcciones posibles para moverse en el tablero: arriba, abajo, izquierda, derecha
DIRS = [(-1, 0), (1, 0), (0, -1), (0, 1)]

def es_adyacente(a, b):
    # Verifica si dos posiciones son adyacentes en el tablero (movimiento ortogonal)
    return abs(a[0] - b[0]) + abs(a[1] - b[1]) == 1

def insertar_palabra(tablero, palabra, camino):
    # Inserta una palabra en el tablero siguiendo el camino especificado
    for letra, (fila, col) in zip(palabra, camino):
        tablero[fila][col] = letra

def colocar_primera_palabra(tablero, palabra, filas, columnas):
    # Intenta colocar la primera palabra en el tablero en posiciones aleatorias y caminos válidos
    for _ in range(500):
        fila, col = random.randint(0, filas - 1), random.randint(0, columnas - 1)
        camino = [(fila, col)]
        visitado = {(fila, col)}
        for _ in range(1, len(palabra)):
            vecinos = [(fila + dr, col + dc) for dr, dc in DIRS
                       if 0 <= fila + dr < filas and 0 <= col + dc < columnas and (fila + dr, col + dc) not in visitado]
            if not vecinos:
                break
            fila, col = random.choice(vecinos)
            camino.append((fila, col))
            visitado.add((fila, col))
        if len(camino) == len(palabra):
            insertar_palabra(tablero, palabra, camino)
            return camino
    return None

def buscar_camino(palabra, tablero, filas, columnas):
    # Busca un camino válido para colocar la palabra en el tablero, permitiendo compartir letras ya existentes
    def backtrack(i, fila, col, visitado):
        if i == len(palabra):
            return []
        if not (0 <= fila < filas and 0 <= col < columnas):
            return None
        if (fila, col) in visitado:
            return None
        if tablero[fila][col] not in ('', palabra[i]):
            return None
        visitado.add((fila, col))
        if i == len(palabra) - 1:
            return [(fila, col)]
        vecinos = [(fila + dr, col + dc) for dr, dc in DIRS
                   if 0 <= fila + dr < filas and 0 <= col + dc < columnas and (fila + dr, col + dc) not in visitado]
        # Prioriza vecinos que ya tengan la siguiente letra de la palabra
        vecinos.sort(key=lambda pos: tablero[pos[0]][pos[1]] == palabra[i+1], reverse=True)
        for nf, nc in vecinos:
            res = backtrack(i + 1, nf, nc, visitado.copy())
            if res is not None:
                return [(fila, col)] + res
        return None

    # Busca posiciones iniciales candidatas para la palabra
    posiciones_candidatas = [(r, c) for r in range(filas) for c in range(columnas) if tablero[r][c] in ('', palabra[0])]
    random.shuffle(posiciones_candidatas)
    for fila, col in posiciones_candidatas[:50]:
        camino = backtrack(0, fila, col, set())
        if camino and len(camino) == len(palabra):
            return camino
    return []

class PoliSopa:
    # Clase principal para la lógica de la sopa de letras
    def __init__(self, palabras, filas=5, columnas=6):
        self.filas = filas
        self.columnas = columnas
        self.palabras = palabras
        self.tablero = [['' for _ in range(columnas)] for _ in range(filas)]
        self.posiciones_palabras = {}  # Guarda las posiciones de cada palabra en el tablero
        self.crear_tablero()
        self.rellenar_tablero()

    def crear_tablero(self):
        # Intenta colocar todas las palabras en el tablero de forma válida
        palabras = sorted(self.palabras, key=len, reverse=True)
        while True:
            tablero = [['' for _ in range(self.columnas)] for _ in range(self.filas)]
            soluciones = {}
            camino = colocar_primera_palabra(tablero, palabras[0], self.filas, self.columnas)
            if not camino:
                continue
            soluciones[palabras[0]] = camino
            exito = True
            for palabra in palabras[1:]:
                camino = buscar_camino(palabra, tablero, self.filas, self.columnas)
                if camino and len(camino) == len(palabra):
                    insertar_palabra(tablero, palabra, camino)
                    soluciones[palabra] = camino
                else:
                    exito = False
                    break
            if exito:
                self.tablero = tablero
                self.posiciones_palabras = soluciones
                return

    def rellenar_tablero(self):
        # Rellena los espacios vacíos del tablero con letras aleatorias
        for i in range(self.filas):
            for j in range(self.columnas):
                if self.tablero[i][j] == '':
                    self.tablero[i][j] = random.choice('ABCDEFGHIJKLMNÑOPQRSTUVWXYZ')

    def mostrar(self):
        # Imprime el tablero en consola (para depuración)
        for fila in self.tablero:
            print(' '.join(fila))

def cargar_diccionario(ruta):
    # Carga el diccionario de palabras desde un archivo de texto, una palabra por línea
    with open(ruta, encoding="utf-8") as f:
        return [linea.strip().upper() for linea in f if linea.strip()]

def seleccionar_palabras(diccionario):
    # Selecciona 7 palabras aleatorias del diccionario con longitudes específicas
    candidatas = [p for p in diccionario if 6 <= len(p) <= 9]
    random.shuffle(candidatas)
    seleccionadas = []
    # Selecciona 3 palabras de 6 letras, 2 de 7, 1 de 8 y 1 de 9 (si hay suficientes)
    seleccionadas += [p for p in candidatas if len(p) == 6][:3]
    seleccionadas += [p for p in candidatas if len(p) == 7][:2]
    seleccionadas += [p for p in candidatas if len(p) == 8][:1]
    seleccionadas += [p for p in candidatas if len(p) == 9][:1]
    return seleccionadas

if __name__ == "__main__":
    # Ejemplo de uso: genera y muestra una sopa de letras aleatoria
    diccionario = cargar_diccionario("diccPoliSopa.txt")
    palabras = seleccionar_palabras(diccionario)
    juego = PoliSopa(palabras, filas=5, columnas=6)
    juego.mostrar()
    print("\nPalabras a buscar:", ', '.join(palabras))