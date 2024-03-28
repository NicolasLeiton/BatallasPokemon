#Juego: Batalla pokemon en consola; Realizado por Nicolas Leiton :D
#Nota: en caso de error con el comando macth, usar una version mas actualizada de Python :)

from abc import ABC, abstractmethod
from random import randint
from copy import deepcopy
from time import sleep
# ---------------------- Funciones generales de apoyo ----------------------
def entrada_int(max_num: int) -> int: #Funcion que se encarga de pedir un numero entero al usuario del 1 al max_num
    while True:
        try:
            num = int(input(f"Ingresa un número entero entre 1 y {max_num}: "))
            if 0<num<=max_num:
                return num
            else:
                print("Error número inválido")

        except ValueError:
            print("Error ingresa un número entero")

def entrada_str(max_len: int, salida: str) -> str: #Funcion que se encarga de pedir una cadena de texto al usuario con una longitud maxima
    while True:
        txt = input(salida)
        if 0<len(txt)<max_len:
            return txt
        else:
            print("Error entrada no válida")

# ---------------------- Clase Personaje ----------------------
class Personaje():
    def __init__(self, nombre:str, hp:int, ataque:int, velocidad:int):
        self.nombre = nombre
        self.hp = hp
        self.ataque = ataque
        self.velocidad = velocidad
        self.estado = None #Objeto de IEstados

        self.debilitado = False #Variable de soporte que nos permite saber si un pokemon ya fue debilitado
        self.movimientos = [] #Lista de objetos, de la clase abstracta Movimiento

    def asignar_mvts(self, factory): #Posibilidad de, a futuro, asignar los movimientos de otra forma
        self.movimientos = factory.crear_mvts(self.nombre)

    def atacar(self, mov_num: int, objetivo): #Ataca al objetivo(objeto de clase personaje) usando el movimiento de la lista en la pocision mov_num
        if self.estado == None: #Si no tiene ningun estado acata directamente
            self.movimientos[mov_num].hacer_movimiento(self, objetivo)
        elif self.estado.efecto(self) == True: #Si tiene algun estado lo llama (si devuelve true el estado significa que le permitio moverse)
            self.movimientos[mov_num].hacer_movimiento(self, objetivo)

    def bajar_vida(self, disminucion:int):
        if (self.hp - disminucion)<=0: #Si la vida baja a cero o menos
            self.hp = 0 #Se pone cero para evitar valores negativos
            self.debilitado = True #Y el pokemon pasa a debilitado
            
        else:
            self.hp-=disminucion
            print(f"¡{self.nombre} ha perdido {disminucion} puntos de vida! \n")

    def __str__(self): #Cuando se llama al personaje como un string devuelve sus caracteristicas principales y su lista de movimientos
        msg = f"El pokemon {self.nombre} tiene: {self.hp} PS; {self.ataque} de ataque; {self.velocidad} de velocidad. Y puede usar los siguientes movimientos: \n"
        for i in range(1, len(self.movimientos)+1):
            msg += f"{i}. {self.movimientos[i-1]} \n"
        return msg


#Posibles estados de un personaje-------
'''
Aqui tenemos el primer uso del patron Strategy, creamos una Interface de los estados,
que tiene la funcion efecto(), su comportamiento será definido por los diferentes tipos de estado que se vayan creando.
Por defecto se le pasa el objeto Personaje, el cual que tiene el estado, y devuelve un bool,
que funciona como soporte para varios estados específicos; siempre que devuelva falso, significará que el pokemon no se movera en ese turno.
Por lo anterior, deducimos que podriamos añadir nuevos estados del pokemon, sin modificar el codigo anterior.
'''
class IEstados():
    def efecto(pokemon: Personaje) -> bool:
        pass

class Intoxicado(IEstados): #Estado que reduce un 20% la vida del pokemon
    def efecto(pokemon: Personaje) -> bool:
        disminucion = round(pokemon.hp * 0.2)
        print(f"{pokemon.nombre} está intoxicado...")
        pokemon.bajar_vida(disminucion)
        return not(pokemon.debilitado)

class Paralizado(IEstados): #Estado con una probabilidad de 1/3 de inmovilizar el pokemon en ese turno
    def efecto(pokemon: Personaje) -> bool:
        if randint(1, 3) == 1:
            print(f"{pokemon.nombre} está paralizado y no se ha podido mover :(")
            return False
        else:
            return True

class Dormido(IEstados): #Estado que siempre que este activo inmoviliza al pokemon. Probabilidad de 1/3 de quitarse
    def efecto(pokemon: Personaje) -> bool:
        if randint(1, 3) == 1:
            print(f"{pokemon.nombre} se ha despertado")
            pokemon.estado = None
            return True
        else:
            print(f"{pokemon.nombre} sigue durmiendo...")
            return False

#---------------------- Clases de los movimientos ----------------------
'''
Aquí de nuevo tenemos el uso del patron Strategy, pero esta vez usando una clase abstracta.
Por defecto, tiene los parámetros nombre y precisión, que tienen todos los movimientos del juego.
Además, cuenta con la funcion acierto() que usando la precision y randint() Verdadero o Falso dependiendo si acierta o no.
Y la clave de la clase, la funcion hacer_movimiento() que su funcionamiento sera definido por las clases que la hereden,
por defecto recibe dos Personajes, el que realiza la acción, y el que la recibe.
Esto es realmente útil ya que cada personaje tiene distintos movimientos de las distintas subclases,
pero que siempre se llamaran usando la misma función. Incluye la posibilidad de posteriormente añadir otro tipo de ataque
'''
class Movimiento(ABC):
    def __init__(self, nombre:str, precision:int):
        self.nombre = nombre
        self.precision = precision

    def acierto(self) -> bool: #Funcion que retorna verdadero si acierta
        if randint(0, 100) <= self.precision: #Se da el acierto usando random randint
            return True
        else:
            return False
    def __str__(self):
        return f"{self.nombre}."

    @abstractmethod
    def hacer_movimiento(self, atacante:Personaje, defensor:Personaje): #Funcion que recibe como parametro el pokemon que realiza el movimiento y el que lo recibe
        pass

#Esta clase añada el parametro de potencia y sus objetos son aquellos que unicamente causan daño
class MovAtaque(Movimiento):
    def __init__(self, nombre:str, precision:int, potencia:int):
        super().__init__(nombre, precision)
        self.potencia = potencia

    def hacer_movimiento(self, atacante:Personaje, defensor:Personaje):
        msg = f"{atacante.nombre} ha usado {self.nombre}"
        if self.acierto()==False:
            msg += ", pero ha fallado"
            print(msg)
        else:
            dano = (self.potencia * atacante.ataque) // 100
            msg+="!"
            print(msg)
            defensor.bajar_vida(dano)
        
#Esta clase añade dos parametros, no obligatorios, que solo se usaran en movimientos que cambien el estado
class MovEstado(Movimiento):
    def __init__(self, nombre:str, precision:int, propiedad:IEstados = None, def_propiedad: str = None):
        super().__init__(nombre, precision)
        self.propiedad = propiedad #Objeto que pertenezca a IEstados 
        self.definicion = def_propiedad #Variable de soporte para lo que se mostrará en pantalla

    def hacer_movimiento(self, atacante:Personaje, defensor:Personaje):
        msg = f"{atacante.nombre} ha usado {self.nombre}"
        if self.acierto()==False:
            msg += ", pero ha fallado."
            
        else:
            #Movimientos más específicos que se definen con un if
            #Aunque si se pensara añadir varios movimientos que hicieran exactamente lo mismo podriamos de nuevo usar strategy y crear una nueva interface
            match self.nombre:
                case "Remolino":
                    defensor.velocidad-= round(defensor.velocidad * 0.25)
                    msg+= f", y ha hecho que {defensor.nombre} baje su velocidad a {defensor.velocidad}."
                case "Gruñido":
                    defensor.ataque-= round(defensor.ataque * 0.2)
                    msg+= f", y ha hecho que {defensor.nombre} baje su ataque a {defensor.ataque}."

            if self.propiedad !=None:
                defensor.estado = self.propiedad
                msg += f", y ahora {defensor.nombre} está {self.definicion}" #Aqui se usa la variable definicion

        print(msg)
#---------------------- Factories ----------------------
# Pokemon factory -------------
'''
Aqui uso el patron de diseño Factory, que nos permite encapsular la creacion de pokemons en una interface general,
añadiendo la posibilidad de generarlos de diferentes formas.
En este caso hice dos, una factory  que crea los pokemons con entradas del usuario,
y la otra que los crea de forma aleatoria
'''
class IPokemonFactory:
    #Se piden dos parametros, uno que es la cantidad de pokemons que se devuelven, y otro la lista de todos los pokemons existentes
    def crear_pkms(cantidad:int, lista_pokemons:tuple) -> list:
        pass

class Pokemon_Factory(IPokemonFactory):
    def crear_pkms(cantidad:int, lista_pokemons:tuple) -> list:
        lista_pkms = deepcopy(lista_pokemons) #Como localmente quiero alterar la lista, uso deepcopy que duplica la lista en memoria
        pokemons = []
        print("Los pokemons que puedes seleccionar son los siguientes:")
        for i in range(1, len(lista_pkms)+1):
            print(f"{i}. {lista_pkms[i-1][0]}") #Imprimir nombres de todos los pokemon en pantalla

        while len(pokemons)<cantidad: #El bucle se repite hasta que no se hallan elegido la cantidad de pokemons indicada
            num = entrada_int(len(lista_pkms))-1

            if lista_pkms[num][0] != "seleccionado": #Se verifica que no se haya seleccionado por el usuario
                #Se crea el objeto pasandore los parametros definidos en la lista, y se añade a la lista vacia, que se va a retornar
                pokemons.append(Personaje(lista_pkms[num][0], lista_pkms[num][1], lista_pkms[num][2], lista_pkms[num][3]))
                print(f"Has seleccionado a {lista_pkms[num][0]}")
                lista_pkms[num][0] = "seleccionado"
                #Se llama a ese ultimo pokemon añadido y se le pide que se le asignen los movimientos usando en este caso la StandardMovements_Factory
                pokemons[-1].asignar_mvts(StandardMovements_Factory)  
            else:
                print("No puedes elegir dos veces al mismo pokemon :/")
        print("Todos tus pokemons han sido seleccionados :D \n")
        return pokemons

class RandomPokemon_Factory(IPokemonFactory):
    def crear_pkms(cantidad:int, lista_pokemons:tuple) -> list:
        #Cuenta con un funcionamiento casi identico a la Pokemon_Factory, pero ahora num se genera aleatoriamente
        lista_pkms = deepcopy(lista_pokemons)
        pokemons = []
        while len(pokemons)<cantidad:
            num = randint(0, len(lista_pkms)-1)
            if lista_pkms[num][0] != "seleccionado":
                pokemons.append(Personaje(lista_pkms[num][0], lista_pkms[num][1], lista_pkms[num][2], lista_pkms[num][3]))
                print(f"De forma aleatoria se ha seleccionado a {lista_pkms[num][0]}")
                lista_pkms[num][0] = "seleccionado"
                pokemons[-1].asignar_mvts(StandardMovements_Factory)
        print("Todos los pokemons han sido seleccionados :D \n")
        return pokemons

# Movements Factory ---------------
def crear_movimiento(nombre_movimiento: str) -> Movimiento:#Recibe como parametro el nombre del movimiento y lo devuelve como un objeto creado 
#En esta funcion se encuentran todos los movimientos de todos los pokemons almacenados en tuplas (Separados por su tipo de movimiento)

    #Nombre, precision, potencia
    lista_ataques = (
    ["Impactrueno", 100, 40],
    ["Rayo", 90, 90],
    ["Ataque Rapido", 100, 40],
    ["Placaje", 100, 40],
    ["Tacleada", 100, 55],
    ["Picotazo", 100, 35],
    ["Tornado", 100, 60],
    ["Latigo Cepa", 100, 65],
    ["Lanzallamas", 90, 90],
    ["Ascuas", 100, 40],
    ["Arañazo", 100, 50],
    ["Pistola Agua", 100, 60],
    ["Burbuja", 100, 40],
    ["Rayo Burbuja", 95, 80],
    ["Tajo Cruzado", 80, 100],
    ["HiperColmillo", 80, 110],
    ["Golpe Cabeza", 100, 70],
    ["Lodo", 100, 50],
    ["Bomba Lodo", 90, 90],
    ["Infortunio", 100, 80],
    ["HidroPulso", 80, 100]
    )
    #Nombre, precision, propiedad, definicion propiedad
    lista_estados =(
    ["Supersonico", 85, Paralizado, "paralizado"],
    ["Drenadoras", 100, Intoxicado, "intoxicado"],
    ["Ataque Acido", 90, Intoxicado, "envenenado"],
    ["Somnifero", 70, Dormido, "dormido"],
    ["Remolino", 100, None, None],
    ["Gruñido", 100, None, None]
    )
    #Se recorren ambas listas en busqueda del movimiento seleccionado, cuando lo encuentra se retorna
    for i in lista_estados:
        if i[0] == nombre_movimiento:
            return MovEstado(i[0], i[1], i[2], i[3])

    for i in lista_ataques:
        if i[0] == nombre_movimiento:
            return MovAtaque(i[0], i[1], i[2])
    #Error pensado en mostrarse al desarrollador
    print("Error: ataque no encontrado")
    return None
'''
Aqui de nuevo uso el patron Factory, pero en este caso para crear los movimientos.
Actualmente no parece muy util ya que unicamente hay una forma de crear los movimientos,
sin embargo, añade la posibilidad de crear otro tipo de factories (se me ocurre una aleatoria, o una elegida por el usuario)
'''
class IMovementsFactory:
    def crear_mvts(nombre_pkm: str) -> list: 
    #Recibe como parametro el nombre del pokemon ya que la creacion se basara en este
    #Devuelve la lista con los 4 movimientos para el pokemon
        pass
class StandardMovements_Factory(IMovementsFactory):
    def crear_mvts(nombre_pkm: str) -> list:
        movimientos = []
        #Por facilidad usé el nombre del pokemon y de los movimientos en la creacion, ya que en este caso me parecia muy engorroso usar el indice de una lista
        match nombre_pkm: 
            case "Pikachu":
                movimientos.append(crear_movimiento("Impactrueno"))
                movimientos.append(crear_movimiento("Rayo"))
                movimientos.append(crear_movimiento("Ataque Rapido"))
                movimientos.append(crear_movimiento("Placaje"))
            case "Caterpie":
                movimientos.append(crear_movimiento("Placaje"))
                movimientos.append(crear_movimiento("Tacleada"))
                movimientos.append(crear_movimiento("Supersonico"))
                movimientos.append(crear_movimiento("Drenadoras"))
            case "Pidgeotto":
                movimientos.append(crear_movimiento("Picotazo"))
                movimientos.append(crear_movimiento("Remolino"))
                movimientos.append(crear_movimiento("Tornado"))
                movimientos.append(crear_movimiento("Ataque Rapido"))
            case "Bulbasaur":
                movimientos.append(crear_movimiento("Latigo Cepa"))
                movimientos.append(crear_movimiento("Drenadoras"))
                movimientos.append(crear_movimiento("Placaje"))
                movimientos.append(crear_movimiento("Somnifero"))
            case "Charmander":
                movimientos.append(crear_movimiento("Lanzallamas"))
                movimientos.append(crear_movimiento("Gruñido"))
                movimientos.append(crear_movimiento("Arañazo"))
                movimientos.append(crear_movimiento("Ascuas"))
            case "Squirtle":
                movimientos.append(crear_movimiento("Pistola Agua"))
                movimientos.append(crear_movimiento("Burbuja"))
                movimientos.append(crear_movimiento("Ataque Rapido"))
                movimientos.append(crear_movimiento("Placaje"))
            case "Krabby":
                movimientos.append(crear_movimiento("Burbuja"))
                movimientos.append(crear_movimiento("Rayo Burbuja"))
                movimientos.append(crear_movimiento("Placaje"))
                movimientos.append(crear_movimiento("Tajo Cruzado"))
            case "Raticate":
                movimientos.append(crear_movimiento("HiperColmillo"))
                movimientos.append(crear_movimiento("Ataque Rapido"))
                movimientos.append(crear_movimiento("Placaje"))
                movimientos.append(crear_movimiento("Golpe Cabeza"))
            case "Muk":
                movimientos.append(crear_movimiento("Lodo"))
                movimientos.append(crear_movimiento("Bomba Lodo"))
                movimientos.append(crear_movimiento("Ataque Acido"))
                movimientos.append(crear_movimiento("Infortunio"))
            case "Kingler":
                movimientos.append(crear_movimiento("HidroPulso"))
                movimientos.append(crear_movimiento("Rayo Burbuja"))
                movimientos.append(crear_movimiento("Rayo"))
                movimientos.append(crear_movimiento("Placaje"))

        return movimientos
            

#---------------------- Clase Jugador----------------------
class Jugador:
    def __init__(self, nombre):
        self.nombre = nombre
        self.equipo = [] #Lista de objetos de la clase Personaje
        self.pkm_actual = None #Pokemon actualmente en batalla (Objeto Personaje)

        if nombre.upper()=="IA": #Usando el nombre se define si el Jugador es una IA o no
            self.esIA = True #Variable de apoyo para las funciones de la clase
            self.factory = RandomPokemon_Factory #Forma en la que se asignaran los pokemons al jugador
        else:   
            self.esIA = False
            self.factory = Pokemon_Factory

    def pokemon_restantes(self): #Funcion de apoyo para saber cuatos pokemons NO debilitados le quedan al usuario
        cantidad = 0
        for i in self.equipo:
            if i.debilitado == False:
                cantidad+=1
        return cantidad

    def asignar_pkms(self, cantidad_pkms: int, lista_pokemons: tuple): 
    #Funcion que asigna los pokemons usando la respectiva factory (Como parametros recibe los mismo que se le pasaran a la factory)
        print("Turno de seleccionar pokemons para ", self.nombre)
        self.equipo = self.factory.crear_pkms(cantidad_pkms, lista_pokemons)
        self.pkm_actual = self.equipo[0] #La primera elección será el pokemon que saldrá a batalla en turno 1

    def cambiar_pkm(self) -> bool: #Funcion que se llama cuando se quiera cambiar de pokemon
        #Retorna True si el cambio fue efectivo, False si se canceló por el usuario
        if self.esIA==True:
            for i in range(3): #Si es una ia intenta en orden uno por uno hasta sacar a uno que si pueda
                if self.pkm_actual==self.equipo[i]:
                    pass
                elif self.equipo[i].debilitado == True: 
                    pass
                     
                else:
                    print(f"{self.nombre} ha cambiado a {self.pkm_actual.nombre}, por {self.equipo[i].nombre}. \n")
                    self.pkm_actual = self.equipo[i]
                    return True

        #En caso de no ser IA entonces:
        print("Tus pokemons disponibles son: ")
        for i in range(len(self.equipo)): #Se muestra la lista de pokemons con su vida actual
            print(f"{i+1}. {self.equipo[i].nombre}; Puntos de vida restantes: {self.equipo[i].hp}")
        #Opcion para camcelar el cambio 
        print(f"O presiona {len(self.equipo) + 1} para volver atras") 

        while True:
            eleccion = entrada_int(len(self.equipo)+1) - 1
            if eleccion == len(self.equipo):
                return False
            elif self.pkm_actual==self.equipo[eleccion]:
                print("El pokemon seleccionado ya esta en batalla...")
            elif self.equipo[eleccion].debilitado == True: 
                print("No puedes cambiar a un pokemon debilitado...")
                 
            else:
                print(f"{self.nombre} ha cambiado a {self.pkm_actual.nombre}, por {self.equipo[eleccion].nombre}. \n")
                self.pkm_actual = self.equipo[eleccion]
                return True

    def hacer_jugada(self, objetivo:Personaje):
        #Se recibe como parametro el objetivo del ataque, para pasarlo a otras funciones (Si es el caso)
        if self.esIA == True: #Siempre que sea una Ia usará un movimiento aleatorio
            self.pkm_actual.atacar(randint(0,3), objetivo)
            return

        print(f"Presiona 1 para atacar con {self.pkm_actual.nombre}, o presiona 2 para cambiar de pokemon.")
        eleccion = entrada_int(2)
        if eleccion == 2:
            cambiado = self.cambiar_pkm()
            if cambiado == False: 
                return self.hacer_jugada(objetivo) #Si cancela el cambio vuelve a llamarse a si misma
        else:
            print(self.pkm_actual)
            eleccion = entrada_int(4)-1
            self.pkm_actual.atacar(eleccion, objetivo)
                        



                

#---------------------- Clase Juego ----------------------

class Juego:
    def __init__(self, lista_pokemons: tuple, pkmsPorJugador: int):
        self.turno = 0
        self.jugadores =[]
        self.lista_pokemons = lista_pokemons
        self.cantidad_pkms = pkmsPorJugador

    def iniciar(self):
        print('Bienvenido a Pokémon... \n Para empezar ingresa el nombre de los jugadores: (En caso de que quieras que alguno sea controlado por la maquina, llamalo "IA")')
        #Se crean los jugadores y se les asignan los pokemons
        self.jugadores.append(Jugador(entrada_str(15, "Nombre del primer jugador: ")))
        self.jugadores.append(Jugador(entrada_str(15, "Nombre del segundo jugador: ")))
        self.jugadores[0].asignar_pkms(self.cantidad_pkms, self.lista_pokemons)
        self.jugadores[1].asignar_pkms(self.cantidad_pkms, self.lista_pokemons)

        self.bucle()

    def bucle(self):
        while True:
            self.turno+=1
            print(f"--------------- Empieza el turno numero {self.turno} ---------------\n")
            
            if self.jugadores[0].pkm_actual.velocidad < self.jugadores[1].pkm_actual.velocidad: 
            #Segun la velocidad de los pokemons se determina quien hara las cosas primero
                self.jugadores[0], self.jugadores[1] = self.jugadores[1], self.jugadores[0]

            elif self.jugadores[0].pkm_actual.velocidad == self.jugadores[1].pkm_actual.velocidad:
                #Si las velocidades son iguales se determina al azar
                if randint(1,2) == 2:
                    self.jugadores[0], self.jugadores[1] = self.jugadores[1], self.jugadores[0]
            
            #El primer jugador hace su jugada
            print(f"Turno de {self.jugadores[0].nombre} ........")
            self.jugadores[0].hacer_jugada(self.jugadores[1].pkm_actual)
            

            if self.jugadores[1].pkm_actual.debilitado == False: 
            #Se verifica que despues del ataque el pokemon del segundo jugador siga vivo
                sleep(1.5) #Pequeña pausa para que no salga demasiado texto seguido
                print(f"Ahora es turno de {self.jugadores[1].nombre} ........")
                self.jugadores[1].hacer_jugada(self.jugadores[0].pkm_actual) #El segundo jugador hace su jugada


                if self.jugadores[0].pkm_actual.debilitado == True: #Se verifica que el pokemon del primer jugador siga vivo
                    print(f"¡{self.jugadores[0].pkm_actual.nombre} de {self.jugadores[0].nombre} se ha debilitado! \n")

                    if self.jugadores[0].pokemon_restantes() == 0: 
                    #Si no tiene mas pokemons vivos se acaba el juego
                        print(self.jugadores[1].nombre, "ha ganado la batalla!!!")
                        return
                    else:
                        while self.jugadores[0].cambiar_pkm() == False: #Pide al jugador que cambie su pokemon
                            print("No puedes volver atras, tienes que elegir un pokemon...")

            else: #Si no esta vivo el pokemon, no puede atacar
                print(f"¡{self.jugadores[1].pkm_actual.nombre} de {self.jugadores[1].nombre} se ha debilitado! \n")
                if self.jugadores[1].pokemon_restantes() == 0:
                    #Si no tiene mas pokemons vivos se acaba el juego
                    print(self.jugadores[0].nombre, "ha ganado la batalla!!!")
                    return
                else:
                    while self.jugadores[1].cambiar_pkm() == False: #Pide al jugador que cambie su pokemon
                        print("No puedes volver atras, tienes que elegir un pokemon...")

            sleep(2) #Pequeña pausa intermedia antes del siguiente turno



#---------------------- Ejecucion ----------------------
#Definicion pokemons existentes ----------------------
#Nombre, vida, ataque, velocidad
lista_pokemons = (
["Pikachu", 80, 95, 90],
["Caterpie", 70, 70, 45],
["Pidgeotto", 100, 95, 70],
["Bulbasaur", 110, 90, 45],
["Charmander", 90, 100, 65],
["Squirtle", 110, 90, 42],
["Krabby", 78, 105, 50],
["Raticate", 80, 100, 97],
["Muk", 100, 110, 40],
["Kingler", 90, 120, 50]
)
#Crear la clase Juego e iniciar
juego = Juego(lista_pokemons, 3)
juego.iniciar()

