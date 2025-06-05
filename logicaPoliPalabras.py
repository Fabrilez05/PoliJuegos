import random

# Lista de letras del abecedario español
ABECEDARIO:list = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'ñ', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']

# Frecuencia de aparición de cada letra en español
FRECUENCIA_LETRAS: list = {
    'a': 12.53, 'b': 1.42, 'c': 4.68, 'd': 5.86, 'e': 13.68,
    'f': 0.69, 'g': 1.01, 'h': 0.70, 'i': 6.25, 'j': 0.44,
    'k': 0.02, 'l': 4.97, 'm': 3.15, 'n': 6.71, 'ñ': 0.31, 
    'o': 8.68, 'p': 2.51, 'q': 0.88, 'r': 6.87, 's': 7.98,
    't': 4.63, 'u': 3.93, 'v': 0.90, 'w': 0.01, 'x': 0.22,
    'y': 0.90, 'z': 0.52
}

# Valor de cada letra para el cálculo de puntaje
VALORES_LETRAS: list = {
    'a': 1, 'b': 3, 'c': 3, 'd': 2, 'e': 1, 'f': 4, 'g': 2, 'h': 4, 'i': 1, 'j': 8,
    'k': 8, 'l': 1, 'm': 3, 'n': 1, 'ñ': 8, 'o': 1, 'p': 3, 'q': 5, 'r': 1, 's': 1,
    't': 1, 'u': 1, 'v': 4, 'w': 8, 'x': 8, 'y': 4, 'z': 10
}

class Juego:
    def __init__(self):
        self.palabras: list = []  # Lista de palabras válidas para el juego
        self.letrasJugables: list = []  # Letras disponibles para formar palabras
        self.diccionario = 'diccionarioPoliLetras.txt'  # Archivo de diccionario
        self.letraGenerada: str = ''  # Letra central obligatoria
        self.palabrasCorrectas: list = []  # Palabras ya encontradas por el jugador
        self.letrasIniciales: list = {}  # Letras iniciales y cantidad de palabras encontradas por cada una
        self.palabrasPorLetra: list = {}  # Palabras agrupadas por su letra inicial
        self.puntajes_palabras: dict = {}  # Puntaje de cada palabra encontrada

    # Genera una letra central según la frecuencia de uso en español
    def generarLetra(self) -> str:
        letrasPeso = []
        for letra, peso in FRECUENCIA_LETRAS.items():
            letrasPeso.extend([letra] * int(peso * 100))
        return random.choice(letrasPeso)
    
    # Genera las letras jugables (incluyendo la central) según frecuencia
    def generarLetrasJugables(self) -> None:
        self.letrasJugables.clear()
        self.letrasJugables.append(self.letraGenerada)
        letrasSobrantes = [letra for letra in ABECEDARIO if letra != self.letraGenerada]
        letrasSobrantesPeso = []
        for letra in letrasSobrantes:
            letrasSobrantesPeso.extend([letra] * int(FRECUENCIA_LETRAS[letra] * 100))
        while len(self.letrasJugables) < 7:
            nuevaLetra = random.choice(letrasSobrantesPeso)
            if nuevaLetra not in self.letrasJugables:
                self.letrasJugables.append(nuevaLetra)
        random.shuffle(self.letrasJugables)

    # Obtiene las palabras válidas del diccionario según las letras jugables y la letra central
    def obtenerPalabras(self) -> None:
        self.palabras.clear()
        with open(self.diccionario, 'r', encoding="utf-8") as file:
            todasPalabras = [palabra.strip().lower() for palabra in file.readlines()]
            random.shuffle(todasPalabras)
            for palabra in todasPalabras:
                if (self.letraGenerada in palabra and 
                    all(letra in self.letrasJugables for letra in palabra)):
                    self.palabras.append(palabra)
                    if len(self.palabras) >= 100:
                        break
    
    # Reduce la cantidad de palabras válidas a una cantidad específica
    def disminuirPalabras(self,cantPalabras) -> None:
        if len(self.palabras) > cantPalabras:
            self.palabras = random.sample(self.palabras, cantPalabras)
        
    # Verifica si la palabra ingresada es válida y actualiza los datos del juego
    def checkearPalabra(self,entrada:str) ->str:
        stringSalida = ''
        if len(entrada) < 3:
            stringSalida = 'la palabra es muy corta'
        elif self.letraGenerada not in entrada:
            stringSalida = f"la letra {self.letraGenerada}, no se encuentra en la palabra"
        elif entrada not in self.palabras:
            stringSalida = f'la palabra {entrada} no se encuentra en el diccionario'
        elif entrada in self.palabrasCorrectas:
            stringSalida = f'la palabra {entrada} ya fue enviada'
        else:
            stringSalida = f'la palabra es correcta: {entrada} '
            self.palabrasCorrectas.append(entrada)
            inicial = entrada[0]
            if inicial in self.letrasIniciales:
                self.letrasIniciales[inicial] += 1
            # Calcula y guarda el puntaje de la palabra
            puntaje = sum(VALORES_LETRAS.get(letra, 0) for letra in entrada)
            self.puntajes_palabras[entrada] = puntaje
        return stringSalida

    # Agrupa las palabras por su letra inicial y reinicia los contadores
    def guardarLetrasIniciales(self):
        self.letrasIniciales: list = {}
        self.palabrasPorLetra: list = {}
        for palabra in self.palabras:
            if palabra:
                inicial = palabra[0]
                if inicial not in self.letrasIniciales:
                    self.letrasIniciales[inicial] = 0
                    self.palabrasPorLetra[inicial] = []
                self.palabrasPorLetra[inicial].append(palabra)
        for inicial in self.palabrasPorLetra:
            self.letrasIniciales[inicial] =  0

# Clase para manejar la pila de letras ingresadas por el usuario
class pilaEntrada:
    def __init__(self):
        self.pila = []

    # Agrega una letra a la pila
    def push(self, letra):
        self.pila.append(letra)

    # Quita y retorna la última letra de la pila
    def pop(self):
        if not self.is_empty():
            return self.pila.pop()
        else:
            return None

    # Verifica si la pila está vacía
    def is_empty(self):
        return len(self.pila) == 0

    # Retorna el tamaño de la pila
    def size(self):
        return len(self.pila)
    
    # Vacía la pila
    def empty(self):
        self.pila.clear()

