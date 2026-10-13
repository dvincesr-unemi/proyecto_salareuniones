from abc import ABC, abstractmethod

from models import Empleado, Sala, Reserva
from shared.json_manager import GestorJSON
from shared.herramientas import es_email_valido


# CLASE BASE (ABSTRACTA)
# Solo dice QUE metodos debe tener todo controlador.
# COMO se hace cada uno lo escribe cada controlador, de la forma mas simple.
class CrudBase(ABC):

    @abstractmethod
    def leer(self):
        """
        Retorna la lista completa de registros.
        
        Args:
            Ninguno
            
        Returns:
            list: Lista de objetos del modelo.
        """
        pass

    @abstractmethod
    def obtener(self, id_registro):
        """
        Busca un registro por su identificador unico.
        
        Args:
            id_registro (int): Identificador a buscar.
            
        Returns:
            object o None: El objeto encontrado o None si no existe.
        """
        pass

    @abstractmethod
    def buscar(self, texto):
        """
        Filtra registros que coincidan con el texto proporcionado.
        
        Args:
            texto (str): Cadena de busqueda.
            
        Returns:
            list: Lista de objetos que coinciden con el criterio.
        """
        pass

    @abstractmethod
    def siguiente(self):
        """
        Calcula el proximo identificador disponible.
        
        Args:
            Ninguno
            
        Returns:
            int: Siguiente ID numerico.
        """
        pass

    @abstractmethod
    def crear(self, datos):
        """
        Crea un nuevo registro a partir de un diccionario de datos.
        
        Args:
            datos (dict): Diccionario con la informacion del registro.
            
        Returns:
            tuple: (bool: exito, str: mensaje).
        """
        pass

    @abstractmethod
    def actualizar(self, id_registro, datos):
        """
        Modifica un registro existente.
        
        Args:
            id_registro (int): Identificador del registro a modificar.
            datos (dict): Diccionario con los campos a actualizar.
            
        Returns:
            tuple: (bool: exito, str: mensaje).
        """
        pass

    @abstractmethod
    def eliminar(self, id_registro):
        """
        Elimina un registro del sistema.
        
        Args:
            id_registro (int): Identificador del registro a eliminar.
            
        Returns:
            tuple: (bool: exito, str: mensaje).
        """
        pass


# CONTROLADOR DE EMPLEADOS
class EmpleadoController(CrudBase):

    def __init__(self, archivo="data/empleados.json"):
        """
        Inicializa el controlador y carga los datos desde el JSON.
        
        Args:
            archivo (str, opcional): Ruta del archivo JSON. Por defecto "data/empleados.json".
            
        Returns:
            None
        """
        self.gestor = GestorJSON(archivo)

        # Leemos el JSON y convertimos cada diccionario en un objeto Empleado
        self.lista = []
        for datos in self.gestor.leer():
            self.lista.append(Empleado.desde_diccionario(datos))

    def guardar(self):
        """
        Guarda la lista actual de empleados en el archivo JSON.
        
        Args:
            Ninguno
            
        Returns:
            None
        """
        datos = []
        for empleado in self.lista:
            datos.append(empleado.a_diccionario())
        self.gestor.guardar(datos)

    def validar(self, datos, id_actual=None):
        """
        Devuelve un mensaje de error, o None si todo esta bien.
        
        Args:
            datos (dict): Diccionario con la informacion a validar.
            id_actual (int, opcional): ID del empleado si se esta actualizando.
            
        Returns:
            str o None: Mensaje de error si falla la validacion, None si todo esta bien.
        """
        # Al crear hay que traer los tres obligatorios; al actualizar, solo lo que cambia
        if id_actual is None:
            for campo in ("nombre", "apellido", "email"):
                if str(datos.get(campo, "")).strip() == "":
                    return f"El campo {campo} es obligatorio"

        if "email" in datos:
            email = str(datos["email"]).strip().lower()
            if not es_email_valido(email):
                return f"Email invalido: '{email}'"
            # CONJUNTO con los emails de los OTROS empleados
            usados = {e.email for e in self.lista if e.id != id_actual}
            if email in usados:
                return "Ese email ya esta registrado"

        return None

    def leer(self):
        """
        Devuelve la lista de empleados.
        
        Args:
            Ninguno
            
        Returns:
            list: Lista de instancias de Empleado.
        """
        return self.lista

    def obtener(self, id_empleado):
        """
        Busca un empleado por ID.
        
        Args:
            id_empleado (int): ID a buscar.
            
        Returns:
            Empleado o None: Empleado encontrado o None.
        """
        for empleado in self.lista:
            if empleado.id == id_empleado:
                return empleado
        return None

    def buscar(self, texto):
        """
        Busca empleados por coincidencia en texto.
        
        Args:
            texto (str): Texto a buscar.
            
        Returns:
            list: Empleados que coinciden.
        """
        texto = texto.strip().lower()
        encontrados = []
        if texto == "":
            return encontrados

        for empleado in self.lista:
            if (texto in empleado.nombre.lower()
                    or texto in empleado.apellido.lower()
                    or texto in empleado.email
                    or texto in empleado.departamento.lower()
                    or texto in empleado.cargo.lower()):
                encontrados.append(empleado)
        return encontrados

    def siguiente(self):
        """
        Obtiene el siguiente ID.
        
        Args:
            Ninguno
            
        Returns:
            int: Siguiente ID.
        """
        mayor = 0
        for empleado in self.lista:
            if empleado.id > mayor:
                mayor = empleado.id
        return mayor + 1

    def crear(self, datos):
        """
        Crea un empleado si los datos son validos.
        
        Args:
            datos (dict): Datos del empleado.
            
        Returns:
            tuple: (exito (bool), mensaje (str)).
        """
        error = self.validar(datos)
        if error:
            return False, error

        empleado = Empleado(self.siguiente(),
                            str(datos["nombre"]).strip().title(),
                            str(datos["apellido"]).strip().title(),
                            str(datos["email"]).strip().lower(),
                            str(datos.get("departamento", "")).strip().title(),
                            str(datos.get("cargo", "")).strip().title())
        self.lista.append(empleado)
        self.guardar()
        return True, f"Empleado creado: {empleado.etiqueta()}"

    def actualizar(self, id_empleado, datos):
        """
        Actualiza los datos de un empleado.
        
        Args:
            id_empleado (int): ID del empleado a actualizar.
            datos (dict): Datos nuevos.
            
        Returns:
            tuple: (exito (bool), mensaje (str)).
        """
        empleado = self.obtener(id_empleado)
        if empleado is None:
            return False, f"No existe un empleado con id {id_empleado}"
        if not datos:
            return False, "No se indico ningun cambio"

        # DIFERENCIA de conjuntos: campos que no existen en un empleado
        permitidos = {"nombre", "apellido", "email", "departamento", "cargo"}
        desconocidos = set(datos) - permitidos
        if desconocidos:
            return False, f"Campos no validos: {', '.join(sorted(desconocidos))}"

        # Se valida ANTES de tocar el objeto: si algo falla, no cambia nada
        error = self.validar(datos, id_empleado)
        if error:
            return False, error

        for campo, valor in datos.items():
            valor = str(valor).strip()
            if campo in ("nombre", "apellido", "departamento", "cargo"):
                valor = valor.title()
            elif campo == "email":
                valor = valor.lower()
            setattr(empleado, campo, valor)

        self.guardar()
        return True, f"Empleado {id_empleado} actualizado"

    def eliminar(self, id_empleado):
        """
        Elimina un empleado por su ID.
        
        Args:
            id_empleado (int): ID del empleado.
            
        Returns:
            tuple: (exito (bool), mensaje (str)).
        """
        empleado = self.obtener(id_empleado)
        if empleado is None:
            return False, f"No existe un empleado con id {id_empleado}"

        self.lista.remove(empleado)
        self.guardar()
        return True, f"Empleado {id_empleado} eliminado"

    # --- propio de empleados ---
    def departamentos(self):
        """
        CONJUNTO de departamentos: sin repetidos. sorted() lo devuelve como lista.
        
        Args:
            Ninguno
            
        Returns:
            list: Lista ordenada de departamentos.
        """
        return sorted({e.departamento for e in self.lista if e.departamento != ""})


# CONTROLADOR DE SALAS
class SalaController(CrudBase):

    def __init__(self, archivo="data/salas.json"):
        """
        Inicializa el controlador y carga las salas.
        
        Args:
            archivo (str, opcional): Ruta del archivo JSON. Por defecto "data/salas.json".
            
        Returns:
            None
        """
        self.gestor = GestorJSON(archivo)

        self.lista = []
        for datos in self.gestor.leer():
            self.lista.append(Sala.desde_diccionario(datos))

    def guardar(self):
        """
        Guarda las salas en el JSON.
        
        Args:
            Ninguno
            
        Returns:
            None
        """
        datos = []
        for sala in self.lista:
            datos.append(sala.a_diccionario())
        self.gestor.guardar(datos)

    def validar(self, datos, id_actual=None):
        """
        Valida que una sala tenga datos correctos.
        
        Args:
            datos (dict): Datos a evaluar.
            id_actual (int, opcional): ID de la sala si se esta editando.
            
        Returns:
            str o None: Error si lo hay, de lo contrario None.
        """
        if id_actual is None:
            for campo in ("nombre", "ubicacion"):
                if str(datos.get(campo, "")).strip() == "":
                    return f"El campo {campo} es obligatorio"

        # es_capacidad_valida es el metodo ESTATICO de Sala
        if "capacidad" in datos and not Sala.es_capacidad_valida(datos["capacidad"]):
            return f"Capacidad invalida: '{datos['capacidad']}' (minimo {Sala.CAPACIDAD_MINIMA})"

        if "nombre" in datos:
            nombre = str(datos["nombre"]).strip().title()
            for otra in self.lista:
                if otra.nombre == nombre and otra.id != id_actual:
                    return f"Ya existe una sala llamada {nombre}"
        return None

    def leer(self):
        """
        Obtiene la lista de salas.
        
        Args:
            Ninguno
            
        Returns:
            list: Lista de salas.
        """
        return self.lista

    def obtener(self, id_sala):
        """
        Obtiene una sala por ID.
        
        Args:
            id_sala (int): ID de la sala.
            
        Returns:
            Sala o None: Sala si existe, o None.
        """
        for sala in self.lista:
            if sala.id == id_sala:
                return sala
        return None

    def buscar(self, texto):
        """
        Busca salas por nombre o ubicacion.
        
        Args:
            texto (str): Criterio de busqueda.
            
        Returns:
            list: Salas coincidentes.
        """
        texto = texto.strip().lower()
        encontradas = []
        if texto == "":
            return encontradas

        for sala in self.lista:
            if texto in sala.nombre.lower() or texto in sala.ubicacion.lower():
                encontradas.append(sala)
        return encontradas

    def siguiente(self):
        """
        Genera el proximo ID.
        
        Args:
            Ninguno
            
        Returns:
            int: Proximo ID.
        """
        mayor = 0
        for sala in self.lista:
            if sala.id > mayor:
                mayor = sala.id
        return mayor + 1

    def crear(self, datos):
        """
        Crea una nueva sala.
        
        Args:
            datos (dict): Datos de la sala.
            
        Returns:
            tuple: (exito (bool), mensaje (str)).
        """
        error = self.validar(datos)
        if error:
            return False, error

        # Si no escribieron capacidad, usa la minima por defecto
        capacidad = str(datos.get("capacidad", "")).strip()
        cap_final = int(capacidad) if capacidad != "" else Sala.CAPACIDAD_MINIMA
        
        tiene_proy = str(datos.get("tiene_proyector", "")).strip().lower() in ("si", "true", "1")
        
        sala = Sala(self.siguiente(),
                    str(datos["nombre"]).strip().title(),
                    str(datos["ubicacion"]).strip().title(),
                    cap_final,
                    tiene_proy)
        self.lista.append(sala)
        self.guardar()
        return True, f"Sala creada: {sala.etiqueta()}"

    def actualizar(self, id_sala, datos):
        """
        Actualiza una sala existente.
        
        Args:
            id_sala (int): ID de la sala.
            datos (dict): Datos nuevos.
            
        Returns:
            tuple: (exito (bool), mensaje (str)).
        """
        sala = self.obtener(id_sala)
        if sala is None:
            return False, f"No existe una sala con id {id_sala}"
        if not datos:
            return False, "No se indico ningun cambio"

        desconocidos = set(datos) - {"nombre", "ubicacion", "capacidad", "tiene_proyector"}
        if desconocidos:
            return False, f"Campos no validos: {', '.join(sorted(desconocidos))}"

        error = self.validar(datos, id_sala)
        if error:
            return False, error

        if "nombre" in datos:
            sala.nombre = str(datos["nombre"]).strip().title()
        if "ubicacion" in datos:
            sala.ubicacion = str(datos["ubicacion"]).strip().title()
        if "capacidad" in datos:
            sala.capacidad = int(datos["capacidad"])
        if "tiene_proyector" in datos:
            sala.tiene_proyector = str(datos["tiene_proyector"]).strip().lower() in ("si", "true", "1")

        self.guardar()
        return True, f"Sala {id_sala} actualizada"

    def eliminar(self, id_sala):
        """
        Elimina una sala.
        
        Args:
            id_sala (int): ID de la sala.
            
        Returns:
            tuple: (exito (bool), mensaje (str)).
        """
        sala = self.obtener(id_sala)
        if sala is None:
            return False, f"No existe una sala con id {id_sala}"

        self.lista.remove(sala)
        self.guardar()
        return True, f"Sala {id_sala} eliminada"

    # --- propio de salas ---
    def salas_con_proyector(self):
        """
        Devuelve solo las salas que cuentan con proyector.
        
        Args:
            Ninguno
            
        Returns:
            list: Salas equipadas.
        """
        return [s for s in self.lista if s.tiene_proyector]


# CONTROLADOR DE RESERVAS
class ReservaController(CrudBase):

    def __init__(self, empleados, salas, archivo="data/reservas.json"):
        """
        Inicializa el controlador vinculando Empleados y Salas.
        
        Args:
            empleados (EmpleadoController): Instancia del controlador de empleados.
            salas (SalaController): Instancia del controlador de salas.
            archivo (str, opcional): Ruta del JSON. Por defecto "data/reservas.json".
            
        Returns:
            None
        """
        # La reserva USA a los otros dos controladores.
        # Hay que pasarle los MISMOS que usa main.py.
        self.empleados = empleados
        self.salas = salas
        self.gestor = GestorJSON(archivo)

        self.lista = []
        for datos in self.gestor.leer():
            self.lista.append(Reserva.desde_diccionario(datos))

    def guardar(self):
        """
        Guarda las reservas en el JSON.
        
        Args:
            Ninguno
            
        Returns:
            None
        """
        datos = []
        for reserva in self.lista:
            datos.append(reserva.a_diccionario())
        self.gestor.guardar(datos)

    def validar(self, datos):
        """
        Valida tipos de datos, existencias y CRUCE DE HORARIOS.
        
        Args:
            datos (dict): Datos de la reserva.
            
        Returns:
            str o None: Error si existe, si no None.
        """
        try:
            empleado_id = int(datos.get("empleado_id", 0))
            sala_id = int(datos.get("sala_id", 0))
            hora_inicio = int(datos.get("hora_inicio", 0))
            duracion_horas = int(datos.get("duracion_horas", 0))
        except (TypeError, ValueError):
            return "empleado_id, sala_id, hora_inicio y duracion deben ser numeros enteros"

        fecha_reserva = str(datos.get("fecha_reserva", "")).strip()
        if not fecha_reserva:
            return "La fecha de reserva es obligatoria"

        if duracion_horas <= 0:
            return "La duracion debe ser de al menos 1 hora"
            
        if not (0 <= hora_inicio <= 23):
            return "La hora de inicio debe estar entre 0 y 23"

        if self.empleados.obtener(empleado_id) is None:
            return f"No existe un empleado con id {empleado_id}"

        sala = self.salas.obtener(sala_id)
        if sala is None:
            return f"No existe una sala con id {sala_id}"

        # REGLA DE NEGOCIO ESTRELLA: Validar cruce de horarios (Overlap)
        hora_fin_nueva = hora_inicio + duracion_horas
        
        for r in self.lista:
            if r.sala_id == sala_id and r.fecha_reserva == fecha_reserva:
                # Comprobar si el bloque de horas choca con otro
                if hora_inicio < r.hora_fin() and hora_fin_nueva > r.hora_inicio:
                    return (f"Cruce de horarios: La {sala.nombre} ya esta reservada "
                            f"de {r.hora_inicio}:00 a {r.hora_fin()}:00 por el empleado {r.empleado_id}")

        return None

    def leer(self):
        """
        Obtiene todas las reservas.
        
        Args:
            Ninguno
            
        Returns:
            list: Lista de reservas.
        """
        return self.lista

    def obtener(self, id_reserva):
        """
        Busca una reserva por ID.
        
        Args:
            id_reserva (int): ID de la reserva.
            
        Returns:
            Reserva o None: Objeto si se encuentra, o None.
        """
        for reserva in self.lista:
            if reserva.id == id_reserva:
                return reserva
        return None

    def buscar(self, texto):
        """
        Busca reservas por fecha, ej: "2026-10-15".
        
        Args:
            texto (str): Fecha a buscar.
            
        Returns:
            list: Reservas coincidentes.
        """
        texto = texto.strip()
        encontradas = []
        if texto == "":
            return encontradas

        for reserva in self.lista:
            if texto in reserva.fecha_reserva:
                encontradas.append(reserva)
        return encontradas

    def siguiente(self):
        """
        Genera el siguiente ID disponible para reservas.
        
        Args:
            Ninguno
            
        Returns:
            int: Proximo ID.
        """
        mayor = 0
        for reserva in self.lista:
            if reserva.id > mayor:
                mayor = reserva.id
        return mayor + 1

    def crear(self, datos):
        """
        Registra una nueva reserva si no hay cruce de horarios.
        
        Args:
            datos (dict): Datos para la reserva.
            
        Returns:
            tuple: (exito (bool), mensaje (str)).
        """
        error = self.validar(datos)
        if error:
            return False, error

        reserva = Reserva(self.siguiente(),
                          int(datos["empleado_id"]),
                          int(datos["sala_id"]),
                          str(datos["fecha_reserva"]).strip(),
                          int(datos["hora_inicio"]),
                          int(datos["duracion_horas"]))

        self.lista.append(reserva)
        self.guardar()
        return True, f"Reserva {reserva.id} confirmada para el {reserva.fecha_reserva}"

    def actualizar(self, id_reserva, datos):
        """
        Bloquea la modificacion de reservas.
        
        Args:
            id_reserva (int): ID de la reserva.
            datos (dict): Datos nuevos.
            
        Returns:
            tuple: (exito (bool), mensaje (str)).
        """
        # Una reserva no se modifica: se anula y se vuelve a reservar
        return False, "Las reservas no se pueden modificar: anulela y reserve de nuevo"

    def eliminar(self, id_reserva):
        """
        Anula una reserva liberando el espacio.
        
        Args:
            id_reserva (int): ID de la reserva a eliminar.
            
        Returns:
            tuple: (exito (bool), mensaje (str)).
        """
        reserva = self.obtener(id_reserva)
        if reserva is None:
            return False, f"No existe la reserva {id_reserva}"

        self.lista.remove(reserva)
        self.guardar()
        return True, f"Reserva {id_reserva} anulada exitosamente"

    # --- propio de reservas ---
    def comprobante(self, id_reserva):
        """
        Genera el ticket o confirmacion de la reserva en texto.
        
        Args:
            id_reserva (int): ID de la reserva.
            
        Returns:
            str o None: Texto formateado del comprobante o None si no existe.
        """
        reserva = self.obtener(id_reserva)
        if reserva is None:
            return None

        empleado = self.empleados.obtener(reserva.empleado_id)
        sala = self.salas.obtener(reserva.sala_id)

        texto = f"CONFIRMACION DE RESERVA #{reserva.id}\n"
        texto += f"Generada el : {reserva.fecha_creacion}\n"
        texto += "-" * 42 + "\n"
        texto += f"Solicitante : {empleado.nombre_completo() if empleado else 'eliminado'}\n"
        texto += f"Sala        : {sala.nombre if sala else 'eliminado'} ({sala.ubicacion if sala else ''})\n"
        texto += f"Fecha de uso: {reserva.fecha_reserva}\n"
        texto += f"Horario     : {reserva.hora_inicio}:00 a {reserva.hora_fin()}:00 hrs\n"
        texto += "-" * 42 + "\n"
        texto += f"Duracion total: {reserva.duracion_horas} hora(s)"
        return texto