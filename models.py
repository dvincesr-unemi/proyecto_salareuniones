from datetime import date
from typing import Dict, Any


# CLASE BASE: lo que los tres modelos comparten
class ModeloBase:
    """Padre de todos los modelos. Guarda el id y define el comportamiento comun."""

    def __init__(self, id_registro: int) -> None:
        """
        Inicializa la entidad base con su identificador unico.

        Args:
            id_registro (int): Identificador numerico unico para el registro.

        Returns:
            None
        """
        self.id = int(id_registro)

    # UNICO METODO DE CLASE DEL PROYECTO
    @classmethod
    def desde_diccionario(cls, datos: Dict[str, Any]) -> "ModeloBase":
        """
        Diccionario a objeto. Escrito UNA vez y usado por los tres modelos.
        
        Args:
            datos (Dict[str, Any]): Diccionario con los datos leidos del JSON.

        Returns:
            ModeloBase: Instancia de la clase que hizo la llamada.
        """
        datos_copia = dict(datos)
        id_registro = datos_copia.pop("id")
        return cls(id_registro, **datos_copia)

    # METODOS DE INSTANCIA
    def a_diccionario(self) -> Dict[str, Any]:
        """
        Objeto a diccionario. Cada hijo agrega sus campos.

        Args:
            Ninguno

        Returns:
            Dict[str, Any]: Diccionario base conteniendo solo el id.
        """
        return {"id": self.id}

    def etiqueta(self) -> str:
        """
        Polimorfismo: cada hijo la reescribe a su manera para listados.

        Args:
            Ninguno

        Returns:
            str: Texto generico con el numero de registro.
        """
        return f"registro {self.id}"

    def __str__(self) -> str:
        """
        Representacion visible al imprimir el objeto. Llama a etiqueta().

        Args:
            Ninguno

        Returns:
            str: Representacion final formateada para la consola.
        """
        return f"[{self.id}] {self.etiqueta()}"


# HERENCIA: Persona es la base de Empleado
class Persona(ModeloBase):
    """Todo lo que tiene una persona del sistema."""

    def __init__(self, id_registro: int, nombre: str, apellido: str, email: str) -> None:
        """
        Inicializa una Persona con sus datos civiles basicos.

        Args:
            id_registro (int): Identificador unico numerico.
            nombre (str): Nombre de la persona.
            apellido (str): Apellido de la persona.
            email (str): Correo electronico de contacto.

        Returns:
            None
        """
        super().__init__(id_registro)
        self.nombre = nombre
        self.apellido = apellido
        self.email = email

    def nombre_completo(self) -> str:
        """
        Concatena de forma limpia el nombre y el apellido.

        Args:
            Ninguno

        Returns:
            str: Nombre y apellido unidos por un espacio.
        """
        return f"{self.nombre} {self.apellido}"

    def a_diccionario(self) -> Dict[str, Any]:
        """
        Agrega los atributos de Persona al diccionario del padre.

        Args:
            Ninguno

        Returns:
            Dict[str, Any]: Diccionario con id, nombre, apellido y email.
        """
        datos = super().a_diccionario()
        datos["nombre"] = self.nombre
        datos["apellido"] = self.apellido
        datos["email"] = self.email
        return datos

    def etiqueta(self) -> str:
        """
        Sobrescribe la representacion base para devolver el nombre completo.

        Args:
            Ninguno

        Returns:
            str: Nombre completo.
        """
        return self.nombre_completo()


class Empleado(Persona):
    """Empleado ES UNA Persona, con departamento y cargo (el que hace la reserva)."""

    def __init__(
        self, id_registro: int, nombre: str, apellido: str, email: str,
        departamento: str = "", cargo: str = ""
    ) -> None:
        """
        Inicializa un Empleado integrando sus datos corporativos.

        Args:
            id_registro (int): Identificador unico numerico.
            nombre (str): Nombre del empleado.
            apellido (str): Apellido del empleado.
            email (str): Correo corporativo.
            departamento (str, opcional): Area a la que pertenece. Por defecto "".
            cargo (str, opcional): Puesto del empleado. Por defecto "".

        Returns:
            None
        """
        super().__init__(id_registro, nombre, apellido, email)
        self.departamento = departamento
        self.cargo = cargo

    def a_diccionario(self) -> Dict[str, Any]:
        """
        Extiende el diccionario de Persona con los corporativos.

        Args:
            Ninguno

        Returns:
            Dict[str, Any]: Diccionario completo del Empleado.
        """
        datos = super().a_diccionario()
        datos["departamento"] = self.departamento
        datos["cargo"] = self.cargo
        return datos

    def etiqueta(self) -> str:
        """
        Sobrescribe y extiende la etiqueta de Persona.

        Args:
            Ninguno

        Returns:
            str: Representacion con nombre, departamento y cargo.
        """
        depto_txt = self.departamento or "sin departamento"
        return f"{super().etiqueta()} · {depto_txt} · {self.cargo}"


# UNICA CLASE CON ATRIBUTOS Y METODOS ESTATICOS
class Sala(ModeloBase):
    """Sala ES UN ModeloBase. Representa el espacio fisico a reservar."""

    # ATRIBUTOS ESTATICOS: reglas globales de las instalaciones
    CAPACIDAD_MINIMA = 2
    total_creadas = 0

    def __init__(
        self, id_registro: int, nombre: str, ubicacion: str,
        capacidad: int = 2, tiene_proyector: bool = False
    ) -> None:
        """
        Inicializa una sala de reuniones.

        Args:
            id_registro (int): Identificador unico numerico.
            nombre (str): Nombre o identificador de la sala (ej. Sala A).
            ubicacion (str): Piso o bloque (ej. Piso 3).
            capacidad (int, opcional): Numero maximo de personas. Por defecto 2.
            tiene_proyector (bool, opcional): Indica si cuenta con equipo audiovisual. Por defecto False.

        Returns:
            None
        """
        super().__init__(id_registro)
        self.nombre = nombre
        self.ubicacion = ubicacion
        self.capacidad = int(capacidad)
        
        # Manejo de booleanos al deserializar (por si viene texto 'True' o bool True)
        if isinstance(tiene_proyector, str):
            self.tiene_proyector = tiene_proyector.lower() == 'true'
        else:
            self.tiene_proyector = bool(tiene_proyector)
            
        Sala.total_creadas += 1

    # METODOS ESTATICOS
    @staticmethod
    def es_capacidad_valida(valor: Any) -> bool:
        """
        Valida que la capacidad ingresada sea un numero entero igual o mayor al minimo institucional.

        Args:
            valor (Any): Valor a evaluar.

        Returns:
            bool: True si la capacidad es valida.
        """
        try:
            return int(valor) >= Sala.CAPACIDAD_MINIMA
        except (TypeError, ValueError):
            return False

    # METODOS DE INSTANCIA
    def a_diccionario(self) -> Dict[str, Any]:
        """
        Empaqueta los datos de la sala para el JSON.

        Args:
            Ninguno

        Returns:
            Dict[str, Any]: Diccionario con los datos de la sala.
        """
        datos = super().a_diccionario()
        datos["nombre"] = self.nombre
        datos["ubicacion"] = self.ubicacion
        datos["capacidad"] = self.capacidad
        datos["tiene_proyector"] = self.tiene_proyector
        return datos

    def etiqueta(self) -> str:
        """
        Genera la representacion en texto de la sala.

        Args:
            Ninguno

        Returns:
            str: Detalle con nombre, ubicacion, capacidad y proyector.
        """
        proyector_txt = "🎬 Con proyector" if self.tiene_proyector else "Sin equipo"
        return f"[{self.nombre}] {self.ubicacion} · Capacidad: {self.capacidad} pax · {proyector_txt}"


# ENTIDAD TRANSACCIONAL: La Reserva de la sala
class Reserva(ModeloBase):
    """Reserva individual: conecta a un empleado con una sala en una fecha y bloque de horas."""

    def __init__(
        self, id_registro: int, empleado_id: int, sala_id: int,
        fecha_reserva: str, hora_inicio: int, duracion_horas: int
    ) -> None:
        """
        Inicializa la reserva de una sala.

        Args:
            id_registro (int): Identificador unico de la reserva.
            empleado_id (int): Identificador del empleado que solicita.
            sala_id (int): Identificador de la sala requerida.
            fecha_reserva (str): Fecha en la que se usara la sala (YYYY-MM-DD).
            hora_inicio (int): Hora de entrada en formato 24h (ej. 14 para 2:00 PM).
            duracion_horas (int): Cantidad de horas reservadas.

        Returns:
            None
        """
        super().__init__(id_registro)
        self.empleado_id = int(empleado_id)
        self.sala_id = int(sala_id)
        self.fecha_reserva = fecha_reserva
        self.hora_inicio = int(hora_inicio)
        self.duracion_horas = int(duracion_horas)
        self.fecha_creacion = date.today().isoformat()

    def hora_fin(self) -> int:
        """
        Calcula la hora a la que termina la reunion.

        Args:
            Ninguno

        Returns:
            int: Hora de finalizacion en formato 24h.
        """
        return self.hora_inicio + self.duracion_horas

    def a_diccionario(self) -> Dict[str, Any]:
        """
        Genera el diccionario para persistir la reserva.

        Args:
            Ninguno

        Returns:
            Dict[str, Any]: Diccionario con las llaves de la transaccion.
        """
        datos = super().a_diccionario()
        datos["empleado_id"] = self.empleado_id
        datos["sala_id"] = self.sala_id
        datos["fecha_reserva"] = self.fecha_reserva
        datos["hora_inicio"] = self.hora_inicio
        datos["duracion_horas"] = self.duracion_horas
        datos["fecha_creacion"] = self.fecha_creacion
        return datos

    def etiqueta(self) -> str:
        """
        Resume la informacion relevante de la reserva.

        Args:
            Ninguno

        Returns:
            str: Detalle con fecha, horarios y entidades relacionadas.
        """
        return (f"📅 {self.fecha_reserva} | Sala {self.sala_id} | "
                f"{self.hora_inicio}:00 a {self.hora_fin()}:00 hrs | "
                f"Reservada por Emp {self.empleado_id}")