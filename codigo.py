from abc import ABC, abstractmethod
from functools import reduce
import math
import random
import time
from datetime import datetime


class Gestor:
    _unicaInstancia = None
    def __init__(self):
        pass

    @classmethod
    def obtener_instancia(cls):
        if not cls._unicaInstancia:
            cls._unicaInstancia = cls
        return cls._unicaInstancia
    
    def iniciar_proceso():
        sensor = Sensor('Invernadero')
        observer = Operator('Observer')
        sensor.register_observer(observer)
        crecimiento = Crecimiento()
        umbral = Umbral(crecimiento)
        estadistico = Estadisticos(umbral)
        simular_sensor(sensor)
# Definición de la clase Observable (Sujeto)
class Observable:
    def __init__(self):
        self._observers = []

    def register_observer(self, observer):
        if  isinstance(observer, Observer):
            self._observers.append(observer)
        else:
            raise Exception('No se puede registrar un objeto que no es un Observer.')

    def remove_observer(self, observer):
        if  isinstance(observer, Observer):
            self._observers.remove(observer)
        else:
            raise Exception('No se puede eliminar un objeto que no es un Observer.')

    def notify_observers(self, data):
        for observer in self._observers:
            observer.update(data)

# Definición de la clase Observer
class Observer(ABC):
    @abstractmethod
    def update(self, data):
        pass

# Definición de la clase Sensor (Sujeto observable)
class Sensor(Observable):
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.value = 0

    def set_value(self, value):
        self.value = value
        self.notify_observers(self.value)

# Definición de la clase Operador (Observador)
class Operator(Observer):
    def __init__(self, name):
        self.name = name
        self.historico = []
        self._crecimiento = Crecimiento()
        self._umbral = Umbral(self._crecimiento)
        self._estadistico = Estadisticos(self._umbral)

    def update(self, data):
        self.historico.append(data)
        temperaturas = list(map(lambda x: x[1], self.historico))
        self._estadistico.handle_request(temperaturas)
### Chain of responsability
class Handler:
    def __init__(self, succesor=None):
        self.succesor=succesor
    def handle_request(self,requiest):
        pass
    
class Estadisticos(Handler):
    def handle_request(self,request):
        if len(request) < 12:
            data = request
        else:
            data = request[-12:]
        contexto = ContextoCalculoEstadisticos(data)
        media = Media('media')
        mediana = Mediana('mediana')
        maximo = Maximo('maximo')
        contexto.establecerEstrategia(media)
        contexto.calculoEstadisticos()
        if isinstance(self.succesor, Handler):
            self.succesor.handle_request(request)
        else:
            raise Exception('El siguiente elemento en la cadena de de responsabilidad debe de ser un Handler')

class Umbral(Handler):
    def handle_request(self, request):
        if request[-1] > 32:
            print('¡ALERTA! La temperatura ha sobrepasado los 32 grados. ¡ALERTA!')
        self.succesor.handle_request(request)

class Crecimiento(Handler):
    def handle_request(self, request):
        if len(request) >= 6:
            if request[-1] - request[-6] >= 10:
                print('¡ALERTA! La temperatura ha ascendido más de diez grados en los últimos 30 segundos. ¡ALERTA!')
        if self.succesor:
            self.succesor.handle_request(request)

### Strategy
class ContextoCalculoEstadisticos:
    def __init__(self, datos, estrategia = None):
        self.datos = datos
        self.estrategia = estrategia

    def establecerEstrategia(self, estrategiaNueva):
        if isinstance(estrategiaNueva, Estrategia):
            self.estrategia = estrategiaNueva
        else: 
            raise Exception('La estrategia nueva debe de ser un objeto Estrategia')

    def calculoEstadisticos(self):
        self.estrategia.calculo(self.datos)

class Estrategia(ABC):
    @abstractmethod
    def calculo(datos):
        pass


class Media(Estrategia):
    def __init__(self, nombre):
        self.nombre = nombre

    def calculo(self, datos):
        media = reduce(lambda x, y: x + y, datos) / len(datos)
        desviaciones = list(map(lambda x: (x - media) ** 2, datos))
        # Calcular la suma de los cuadrados de las desviaciones
        suma_cuadrados_desviaciones = reduce(lambda x, y: x + y, desviaciones)
        # Calcular la desviación estándar
        desviacion_estandar = math.sqrt(suma_cuadrados_desviaciones / len(datos))
        print(f"La temperatura media de los ultimos 60 segundos es: {round(media, 2)}\nLa desviación estandar es: {round(desviacion_estandar, 2)}")


class Mediana(Estrategia):
    def __init__(self, nombre):
        self.nombre = nombre
    
    def calculo(self, datos):
        lista_ordenada = sorted(datos)
        longitud = len(lista_ordenada)
    
        if longitud % 2 == 0:
            # Si la longitud de la lista es par, calcular el promedio de los dos valores centrales
            medio_1, medio_2 = list(map(lambda x: lista_ordenada[x], [(longitud // 2) - 1, (longitud // 2)]))
            return (medio_1 + medio_2) / 2
        else:
            # Si la longitud de la lista es impar, la mediana es el valor central
            return lista_ordenada[longitud // 2]

class Maximo(Estrategia):
    def __init__(self, nombre):
        self.nombre = nombre
    
    def calculo(self, datos):
        maximo = max(datos)
        minimo = min(datos)
        print(f"La temperatura máxima de los ultimos 60 segundos es {maximo} y la mínima es {minimo}")


def simular_sensor(sensor):
    while True:
        temperatura = round(random.uniform(10, 35), 2)
        tiempo = datetime.now()
        sensor.set_value((tiempo, temperatura))
        time.sleep(5)


if __name__ == '__main__':
    g = Gestor.obtener_instancia()
    Gestor.iniciar_proceso()