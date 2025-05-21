import random


ABECEDARIO:list = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'ñ', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']

FRECUENCIA_LETRAS: list = {
    'a': 12.53, 'b': 1.42, 'c': 4.68, 'd': 5.86, 'e': 13.68,
    'f': 0.69, 'g': 1.01, 'h': 0.70, 'i': 6.25, 'j': 0.44,
    'k': 0.02, 'l': 4.97, 'm': 3.15, 'n': 6.71, 'ñ': 0.31, 
    'o': 8.68, 'p': 2.51, 'q': 0.88, 'r': 6.87, 's': 7.98,
    't': 4.63, 'u': 3.93, 'v': 0.90, 'w': 0.01, 'x': 0.22,
    'y': 0.90, 'z': 0.52
}

class Juego:
    def __init__(self):
        self.palabras: list = []
        self.letrasJugables: list = []
        self.diccionario = 'diccionario.txt'
        self.letraGenerada: str = ''
        self.palabrasCorrectas: list = []
        self.letrasIniciales: list = {}
        self.palabrasPorLetra: list = {}

        
    
    def generarLetra(self) -> str:
        letrasPeso = []
        for letra, peso in FRECUENCIA_LETRAS.items():
            letrasPeso.extend([letra] * int(peso * 100))
        return random.choice(letrasPeso)
    
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
    
    def disminuirPalabras(self) -> None:
        if len(self.palabras) > 100:
            self.palabras = random.sample(self.palabras, 100)

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
                

        return stringSalida

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





class pilaEntrada:
    def __init__(self):
        self.pila = []

    def push(self, letra):
        self.pila.append(letra)

    def pop(self):
        if not self.is_empty():
            return self.pila.pop()
        else:
            return None

    def is_empty(self):
        return len(self.pila) == 0

    def size(self):
        return len(self.pila)
    
    def empty(self):
        self.pila.clear()




'''
def main() -> None:
    juego = Juego()
    juego.letraGenerada = juego.generarLetra()
    juego.generarLetrasJugables()
    juego.obtenerPalabras()
    juego.disminuirPalabras()



    pilaDeEntrada = pilaEntrada()




    while True:

        print(juego.palabras)

        print(f"ingrese una letra de : {juego.letrasJugables}, la palabra debe contener la letra generada: {juego.letraGenerada}")
        entrada: str = input()

        while entrada not in juego.letrasJugables or len(entrada) > 1:
            print(f"ingrese una letra de : {juego.letrasJugables}, la palabra debe contener la letra generada: {juego.letraGenerada}")
            entrada = input()

        pilaDeEntrada.push(entrada)

        print ("desea evaluar la palabra? (si/no)")
        evaluar: str = input()

        if evaluar.lower() == "si":
            entrada = "".join(pilaEntrada.pila)
            while not pilaEntrada.is_empty():
                if pilaDeEntrada.size() < 3:
                    print("la palabra es muy corta")
                    pilaEntrada.empty()
                elif juego.letraGenerada not in pilaEntrada.pila:
                    print("la palabra no contiene la letra generada")
                    pilaDeEntrada.empty()
                elif entrada not in juego.palabras:
                    print("la palabra no existe")
                    pilaDeEntrada.empty()
                else:
                    print("la palabra es correcta")
                    pilaDeEntrada.empty()

'''

