import logging
from abc import ABC, abstractmethod
from datetime import datetime

# Configuración básica de logging para registrar eventos y errores
logging.basicConfig(
    filename='software_fj_logs.txt',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)
logger = logging.getLogger("SoftwareFJ")

# --- 1. Excepciones Personalizadas (Manejo Robusto de Excepciones) ---

class SistemaException(Exception):
    """Excepción base para el sistema Software FJ."""
    pass

class ValidacionError(SistemaException):
    """Excepción lanzada cuando hay errores de validación de datos."""
    pass

class ServicioNoDisponibleError(SistemaException):
    """Excepción lanzada cuando se intenta reservar un servicio no disponible."""
    pass

class OperacionNoPermitidaError(SistemaException):
    """Excepción lanzada para operaciones que violan la lógica de negocio."""
    pass


# --- 2. Clases Abstractas (Abstracción) ---

class EntidadGeneral(ABC):
    """Clase abstracta que representa entidades generales del sistema."""
    
    def __init__(self, id_entidad):
        self._id_entidad = id_entidad
        
    @property
    def id_entidad(self):
        return self._id_entidad
        
    @abstractmethod
    def obtener_detalles(self):
        """Método abstracto que las clases derivadas deben implementar."""
        pass


# --- 3. Clase Cliente (Encapsulación y Validaciones) ---

class Cliente(EntidadGeneral):
    def __init__(self, id_cliente, nombre, correo, telefono):
        super().__init__(id_cliente)
        # Se utilizan los setters para invocar las validaciones inmediatamente
        self.nombre = nombre
        self.correo = correo
        self.telefono = telefono

    @property
    def nombre(self):
        return self.__nombre

    @nombre.setter
    def nombre(self, valor):
        if not valor or len(valor.strip()) < 3:
            raise ValidacionError("El nombre debe tener al menos 3 caracteres.")
        self.__nombre = valor.strip()

    @property
    def correo(self):
        return self.__correo

    @correo.setter
    def correo(self, valor):
        if "@" not in valor or "." not in valor:
            raise ValidacionError("El correo electrónico no tiene un formato válido.")
        self.__correo = valor.strip()

    @property
    def telefono(self):
        return self.__telefono

    @telefono.setter
    def telefono(self, valor):
        if not str(valor).isdigit() or len(str(valor)) < 7:
            raise ValidacionError("El teléfono debe contener solo números y al menos 7 dígitos.")
        self.__telefono = valor

    def obtener_detalles(self):
        return f"Cliente: {self.nombre} (ID: {self.id_entidad}), Correo: {self.correo}, Teléfono: {self.telefono}"


# --- 4. Clases de Servicios (Herencia y Polimorfismo) ---

class Servicio(EntidadGeneral):
    """Clase abstracta Servicio."""
    def __init__(self, id_servicio, nombre, costo_base):
        super().__init__(id_servicio)
        self.nombre = nombre
        self.costo_base = costo_base
        self._disponible = True

    @property
    def disponible(self):
        return self._disponible

    def modificar_disponibilidad(self, estado: bool):
        self._disponible = estado

    @abstractmethod
    def calcular_costo(self, *args, **kwargs):
        """Calcula el costo del servicio. Simula sobrecarga mediante *args y **kwargs."""
        pass
        
    @abstractmethod
    def validar_parametros(self, **kwargs):
        """Valida que los parámetros entregados para el servicio sean correctos."""
        pass


class ReservaDeSala(Servicio):
    def __init__(self, id_servicio, nombre, costo_base, capacidad):
        super().__init__(id_servicio, nombre, costo_base)
        self.capacidad = capacidad

    # Polimorfismo: Implementación específica y Sobrecarga simulada (parámetros por defecto)
    def calcular_costo(self, horas, incluye_proyector=False, descuento=0):
        costo = self.costo_base * horas
        if incluye_proyector:
            costo += 50 * horas  # Costo adicional por proyector
        if descuento > 0:
            costo -= costo * (descuento / 100)
        return costo

    def validar_parametros(self, **kwargs):
        horas = kwargs.get('horas')
        if horas is None or not isinstance(horas, (int, float)) or horas <= 0:
            raise ValidacionError("La duración en horas debe ser un número positivo mayor a 0.")

    def obtener_detalles(self):
        return f"Reserva de Sala: {self.nombre}, Capacidad: {self.capacidad} pax, Costo Base: ${self.costo_base}/h"


class AlquilerDeEquipo(Servicio):
    def __init__(self, id_servicio, nombre, costo_base, requiere_deposito=True):
        super().__init__(id_servicio, nombre, costo_base)
        self.requiere_deposito = requiere_deposito

    def calcular_costo(self, dias, seguro_adicional=False):
        costo = self.costo_base * dias
        if seguro_adicional:
            costo += 20 * dias # Costo del seguro diario
        return costo

    def validar_parametros(self, **kwargs):
        dias = kwargs.get('dias')
        if dias is None or not isinstance(dias, int) or dias <= 0:
            raise ValidacionError("El alquiler debe ser por al menos 1 día entero (número entero positivo).")

    def obtener_detalles(self):
        return f"Alquiler Equipo: {self.nombre}, Depósito: {'Sí' if self.requiere_deposito else 'No'}, Costo: ${self.costo_base}/día"


class AsesoriaEspecializada(Servicio):
    def __init__(self, id_servicio, nombre, costo_base, area_experiencia):
        super().__init__(id_servicio, nombre, costo_base)
        self.area_experiencia = area_experiencia

    def calcular_costo(self, sesiones, modalidad_urgente=False):
        costo = self.costo_base * sesiones
        if modalidad_urgente:
            costo *= 1.5  # Recargo del 50% por urgencia
        return costo

    def validar_parametros(self, **kwargs):
        sesiones = kwargs.get('sesiones')
        if sesiones is None or not isinstance(sesiones, int) or sesiones <= 0:
            raise ValidacionError("La cantidad de sesiones debe ser un entero positivo.")

    def obtener_detalles(self):
        return f"Asesoría: {self.area_experiencia}, Costo Base: ${self.costo_base}/sesión"


# --- 5. Clase Reserva (Asociación e Integración) ---

class Reserva:
    def __init__(self, id_reserva, cliente, servicio, parametros_servicio):
        self.id_reserva = id_reserva
        self.cliente = cliente
        self.servicio = servicio
        self.parametros_servicio = parametros_servicio
        self.estado = "Pendiente"
        self.costo_total = 0.0

    def procesar_reserva(self):
        logger.info(f"Iniciando procesamiento de reserva {self.id_reserva} para cliente {self.cliente.nombre}.")
        
        # Estructura try/except/else/finally completa
        try:
            # 1. Validar disponibilidad del servicio
            if not self.servicio.disponible:
                raise ServicioNoDisponibleError(f"El servicio '{self.servicio.nombre}' se encuentra temporalmente inactivo.")
            
            # 2. Validar parámetros específicos del servicio
            self.servicio.validar_parametros(**self.parametros_servicio)
            
            # 3. Calcular costo (Polimorfismo en acción)
            self.costo_total = self.servicio.calcular_costo(**self.parametros_servicio)
            
        except ValidacionError as e:
            self.estado = "Fallida (Datos Inválidos)"
            logger.error(f"ValidacionError en reserva {self.id_reserva}: {e}")
            # Encadenamiento de excepciones
            raise ValidacionError(f"Datos inválidos al procesar la reserva {self.id_reserva}.") from e
            
        except ServicioNoDisponibleError as e:
            self.estado = "Cancelada (No Disponible)"
            logger.warning(f"ServicioNoDisponibleError en reserva {self.id_reserva}: {e}")
            raise
            
        except TypeError as e:
            self.estado = "Fallida (Error de Tipos/Cálculo)"
            logger.critical(f"Error de tipos/inconsistencia en reserva {self.id_reserva}. Probable parámetro incorrecto: {e}")
            raise SistemaException(f"Error interno de cálculo en la reserva {self.id_reserva}.") from e
            
        except Exception as e:
            self.estado = "Error Crítico"
            logger.critical(f"Excepción general capturada en reserva {self.id_reserva}: {e}")
            raise SistemaException("Falla crítica y desconocida al procesar la reserva.") from e
            
        else:
            # Se ejecuta si el bloque try termina sin levantar ninguna excepción
            self.estado = "Confirmada"
            mensaje_exito = f"Reserva {self.id_reserva} confirmada con éxito. Costo total: ${self.costo_total}"
            logger.info(mensaje_exito)
            print(f"[ÉXITO] {mensaje_exito}")
            
        finally:
            # Se ejecuta siempre, haya ocurrido un error o no
            print(f"[FINALLY] Finalizando ciclo de la reserva {self.id_reserva}. Estado actual: {self.estado}")

    def cancelar_reserva(self):
        try:
            if self.estado == "Cancelada":
                raise OperacionNoPermitidaError("La reserva ya fue cancelada previamente.")
            self.estado = "Cancelada"
            logger.info(f"La reserva {self.id_reserva} fue cancelada exitosamente.")
            print(f"[INFO] Reserva {self.id_reserva} cancelada.")
        except OperacionNoPermitidaError as e:
            logger.error(f"Error al intentar cancelar reserva {self.id_reserva}: {e}")
            raise


# --- 6. Simulación del Sistema ---

def simular_sistema():
    print("=========================================================")
    print(" INICIANDO SIMULACIÓN - SISTEMA SOFTWARE FJ")
    print("=========================================================")
    
    # Listas internas
    clientes = []
    servicios = []
    
    # Preparar algunos servicios válidos
    sala = ReservaDeSala("S01", "Sala Conferencias A", 100, capacidad=50)
    equipo = AlquilerDeEquipo("E01", "Laptop Dell XPS", 50, requiere_deposito=True)
    asesoria = AsesoriaEspecializada("A01", "Migración a la Nube", 300, "Arquitectura Cloud")
    servicios.extend([sala, equipo, asesoria])

    # OPERACIÓN 1: Registro Válido de Cliente
    print("\n--- 1. Registro Válido de Cliente ---")
    try:
        c1 = Cliente("C01", "Carlos Perez", "carlos@empresa.com", "3001234567")
        clientes.append(c1)
        print(f"Cliente registrado: {c1.obtener_detalles()}")
    except Exception as e:
        print(f"Error inesperado: {e}")

    # OPERACIÓN 2: Registro Inválido de Cliente (Correo incorrecto)
    print("\n--- 2. Registro Inválido de Cliente (Correo Invalido) ---")
    try:
        c2 = Cliente("C02", "Ana Martinez", "correo-sin-arroba", "3007654321")
    except ValidacionError as e:
        print(f"[CAPTURADO] {e}")

    # OPERACIÓN 3: Registro Inválido de Cliente (Teléfono con letras)
    print("\n--- 3. Registro Inválido de Cliente (Teléfono Invalido) ---")
    try:
        c3 = Cliente("C03", "Luis Gomez", "luis@mail.com", "123ABC89")
    except ValidacionError as e:
        print(f"[CAPTURADO] {e}")

    # OPERACIÓN 4: Reserva Exitosa con Sobrecarga (Sala con proyector y descuento)
    print("\n--- 4. Reserva Exitosa (Reserva de Sala) ---")
    try:
        r1 = Reserva("R001", c1, sala, {'horas': 5, 'incluye_proyector': True, 'descuento': 10})
        r1.procesar_reserva()
    except SistemaException as e:
        print(f"[ERROR] {e}")

    # OPERACIÓN 5: Reserva Exitosa con distintos parámetros (Asesoría urgente)
    print("\n--- 5. Reserva Exitosa (Asesoría Urgente) ---")
    try:
        r2 = Reserva("R002", c1, asesoria, {'sesiones': 2, 'modalidad_urgente': True})
        r2.procesar_reserva()
    except SistemaException as e:
        print(f"[ERROR] {e}")

    # OPERACIÓN 6: Reserva Fallida (Parámetros faltantes/inválidos - horas negativas)
    print("\n--- 6. Reserva Fallida (Datos Inválidos) ---")
    try:
        r3 = Reserva("R003", c1, sala, {'horas': -3})
        r3.procesar_reserva()
    except SistemaException as e:
        # Se captura el encadenamiento de excepciones (from e)
        print(f"[CAPTURADO] {type(e).__name__}: {e}")
        print(f"Causa original: {e.__cause__}")

    # OPERACIÓN 7: Reserva Fallida (Servicio no disponible)
    print("\n--- 7. Reserva Fallida (Servicio Indisponible) ---")
    try:
        equipo.modificar_disponibilidad(False) # Inactivar servicio
        r4 = Reserva("R004", c1, equipo, {'dias': 3})
        r4.procesar_reserva()
    except SistemaException as e:
        print(f"[CAPTURADO] {type(e).__name__}: {e}")

    # OPERACIÓN 8: Cálculo Inconsistente / Tipo Inválido (Letras en lugar de números)
    print("\n--- 8. Reserva Fallida (Cálculo Inconsistente / Tipos incorrectos) ---")
    try:
        # Pasa un string "cinco" en el parámetro 'dias' en lugar de un número. Esto fallará en validación o cálculo.
        r5 = Reserva("R005", c1, equipo, {'dias': "cinco"})
        r5.procesar_reserva()
    except SistemaException as e:
        print(f"[CAPTURADO] {type(e).__name__}: {e}")

    # OPERACIÓN 9: Cancelación Exitosa
    print("\n--- 9. Cancelación de Reserva Existente ---")
    try:
        r1.cancelar_reserva()
    except SistemaException as e:
        print(f"[ERROR] {e}")

    # OPERACIÓN 10: Cancelación Fallida (Operación no permitida: Ya estaba cancelada)
    print("\n--- 10. Operación No Permitida (Cancelar algo cancelado) ---")
    try:
        r1.cancelar_reserva()
    except SistemaException as e:
        print(f"[CAPTURADO] {type(e).__name__}: {e}")

    print("\n=========================================================")
    print(" SIMULACIÓN FINALIZADA. LOS EVENTOS FUERON REGISTRADOS EN 'software_fj_logs.txt'")
    print("=========================================================")

if __name__ == "__main__":
    simular_sistema()
