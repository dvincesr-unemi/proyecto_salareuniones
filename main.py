from shared.herramientas import (
    imprimir_titulo, imprimir_exito, imprimir_error, imprimir_info, confirmar
)
from views import EmpleadoController, SalaController, ReservaController

# Se crea UN solo controlador de cada tipo.
# A reservas se le pasan los MISMOS empleados y salas.
empleados = EmpleadoController()
salas = SalaController()
reservas = ReservaController(empleados, salas)


# AYUDAS DE PANTALLA

def pausa() -> None:
    """
    Detiene la ejecucion hasta que el usuario presione Enter.
    
    Args:
        Ninguno
        
    Returns:
        None
    """
    input("\nPresione Enter para continuar...")


def pedir_entero(etiqueta: str) -> int:
    """
    Devuelve un entero o None si el usuario escribio otra cosa.
    
    Args:
        etiqueta (str): El texto a mostrar para pedir el dato.
        
    Returns:
        int o None: El numero validado, o None si fallo.
    """
    try:
        return int(input(etiqueta))
    except ValueError:
        return None


def mostrar_resultado(exito: bool, mensaje: str) -> None:
    """
    Muestra el resultado de una operacion del controlador.
    
    Args:
        exito (bool): Si la operacion fue exitosa o no.
        mensaje (str): El texto a mostrar.
        
    Returns:
        None
    """
    if exito:
        imprimir_exito(mensaje)
    else:
        imprimir_error(mensaje)


def mostrar_lista(objetos: list, vacio: str = "No hay registros todavia.") -> None:
    """
    Sirve para empleados, salas y reservas: cada modelo sabe mostrarse.
    
    Args:
        objetos (list): Lista de instancias a imprimir.
        vacio (str, opcional): Mensaje a mostrar si la lista esta vacia.
        
    Returns:
        None
    """
    if not objetos:
        imprimir_info(vacio)
        return
    for objeto in objetos:
        print(f"  {objeto}")
    imprimir_info(f"Total: {len(objetos)}")


def mostrar_detalle(objeto: object) -> None:
    """
    Imprime en pantalla los campos internos de un objeto.
    
    Args:
        objeto (object): Instancia del modelo a inspeccionar.
        
    Returns:
        None
    """
    for clave, valor in objeto.a_diccionario().items():
        print(f"  {str(clave).replace('_', ' ').capitalize():<16}: {valor}")


# MENU DE EMPLEADOS

def crear_empleado() -> None:
    """
    Pide datos por consola y envia la peticion para crear un empleado.
    
    Args:
        Ninguno
        
    Returns:
        None
    """
    imprimir_titulo("REGISTRAR EMPLEADO")
    datos = {
        "nombre": input("Nombre: "),
        "apellido": input("Apellido: "),
        "email": input("Email corporativo: "),
        "departamento": input("Departamento: "),
        "cargo": input("Cargo: "),
    }
    mostrar_resultado(*empleados.crear(datos))
    pausa()


def listar_empleados() -> None:
    """
    Muestra la lista de todos los empleados del sistema.
    
    Args:
        Ninguno
        
    Returns:
        None
    """
    imprimir_titulo("EMPLEADOS REGISTRADOS")
    mostrar_lista(empleados.leer(), "Todavia no hay empleados.")
    pausa()


def buscar_empleado() -> None:
    """
    Busca empleados por un termino y muestra los resultados.
    
    Args:
        Ninguno
        
    Returns:
        None
    """
    imprimir_titulo("BUSCAR EMPLEADO")
    termino = input("Nombre, email, depto o cargo: ")
    encontrados = empleados.buscar(termino)
    mostrar_lista(encontrados, f"Ningun empleado coincide con '{termino}'.")
    pausa()


def ver_empleado() -> None:
    """
    Pide un ID y muestra el detalle completo del empleado.
    
    Args:
        Ninguno
        
    Returns:
        None
    """
    imprimir_titulo("VER EMPLEADO POR ID")
    empleado = empleados.obtener(pedir_entero("Id: "))
    if empleado is None:
        imprimir_error("No encontrado")
    else:
        mostrar_detalle(empleado)
    pausa()


def actualizar_empleado() -> None:
    """
    Pide un ID de empleado y permite editar sus campos (dejando en blanco los que no cambian).
    
    Args:
        Ninguno
        
    Returns:
        None
    """
    imprimir_titulo("ACTUALIZAR EMPLEADO")
    id_empleado = pedir_entero("Id: ")
    empleado = empleados.obtener(id_empleado)
    if empleado is None:
        imprimir_error("No encontrado")
        return pausa()

    imprimir_info(f"Editando: {empleado.etiqueta()}")
    print("Deje en blanco lo que no quiera cambiar.\n")

    cambios = {}
    for campo in ("nombre", "apellido", "email", "departamento", "cargo"):
        actual = getattr(empleado, campo)
        nuevo = input(f"{campo.capitalize()} [{actual}]: ").strip()
        if nuevo:
            cambios[campo] = nuevo

    mostrar_resultado(*empleados.actualizar(id_empleado, cambios))
    pausa()


def eliminar_empleado() -> None:
    """
    Elimina un empleado por su ID previa confirmacion.
    
    Args:
        Ninguno
        
    Returns:
        None
    """
    imprimir_titulo("ELIMINAR EMPLEADO")
    id_empleado = pedir_entero("Id: ")
    empleado = empleados.obtener(id_empleado)
    if empleado is None:
        imprimir_error("No encontrado")
        return pausa()

    imprimir_info(f"Se eliminara: {empleado.etiqueta()}")
    if confirmar("¿Confirma?"):
        mostrar_resultado(*empleados.eliminar(id_empleado))
    else:
        imprimir_info("Operacion cancelada")
    pausa()


# MENU DE SALAS

def crear_sala() -> None:
    """
    Pide datos por consola y envia la peticion para crear una sala.
    
    Args:
        Ninguno
        
    Returns:
        None
    """
    imprimir_titulo("CREAR SALA")
    datos = {
        "nombre": input("Nombre de la sala (ej. Sala A): "),
        "ubicacion": input("Ubicacion (ej. Piso 3): "),
        "capacidad": input("Capacidad maxima de personas: "),
        "tiene_proyector": input("¿Tiene proyector? (si/no): "),
    }
    mostrar_resultado(*salas.crear(datos))
    pausa()


def listar_salas() -> None:
    """
    Muestra la lista de todas las salas disponibles.
    
    Args:
        Ninguno
        
    Returns:
        None
    """
    imprimir_titulo("SALAS DISPONIBLES")
    mostrar_lista(salas.leer(), "Todavia no hay salas registradas.")
    pausa()


def buscar_sala() -> None:
    """
    Busca salas por nombre o ubicacion.
    
    Args:
        Ninguno
        
    Returns:
        None
    """
    imprimir_titulo("BUSCAR SALA")
    termino = input("Nombre o ubicacion: ")
    mostrar_lista(salas.buscar(termino), "Sin coincidencias.")
    pausa()


def ver_sala() -> None:
    """
    Pide un ID y muestra el detalle completo de la sala.
    
    Args:
        Ninguno
        
    Returns:
        None
    """
    imprimir_titulo("VER SALA POR ID")
    sala = salas.obtener(pedir_entero("Id: "))
    if sala is None:
        imprimir_error("No encontrado")
    else:
        mostrar_detalle(sala)
    pausa()


def actualizar_sala() -> None:
    """
    Permite modificar los atributos de una sala existente.
    
    Args:
        Ninguno
        
    Returns:
        None
    """
    imprimir_titulo("ACTUALIZAR SALA")
    id_sala = pedir_entero("Id: ")
    sala = salas.obtener(id_sala)
    if sala is None:
        imprimir_error("No encontrado")
        return pausa()

    imprimir_info(f"Editando: {sala.etiqueta()}")
    print("Deje en blanco lo que no quiera cambiar.\n")

    cambios = {}
    for campo in ("nombre", "ubicacion", "capacidad", "tiene_proyector"):
        actual = getattr(sala, campo)
        nuevo = input(f"{campo.capitalize()} [{actual}]: ").strip()
        if nuevo:
            cambios[campo] = nuevo

    mostrar_resultado(*salas.actualizar(id_sala, cambios))
    pausa()


def eliminar_sala() -> None:
    """
    Elimina una sala del sistema.
    
    Args:
        Ninguno
        
    Returns:
        None
    """
    imprimir_titulo("ELIMINAR SALA")
    id_sala = pedir_entero("Id: ")
    sala = salas.obtener(id_sala)
    if sala is None:
        imprimir_error("No encontrado")
        return pausa()

    imprimir_info(f"Se eliminara: {sala.etiqueta()}")
    if confirmar("¿Confirma?"):
        mostrar_resultado(*salas.eliminar(id_sala))
    else:
        imprimir_info("Operacion cancelada")
    pausa()


# MENU DE RESERVAS

def registrar_reserva() -> None:
    """
    Guia al usuario para reservar una sala comprobando que no haya choques de horario.
    
    Args:
        Ninguno
        
    Returns:
        None
    """
    imprimir_titulo("RESERVAR SALA")
    imprimir_info("Empleados:")
    mostrar_lista(empleados.leer())
    imprimir_info("Salas:")
    mostrar_lista(salas.leer())

    datos = {
        "empleado_id": pedir_entero("\nId del empleado: "),
        "sala_id": pedir_entero("Id de la sala: "),
        "fecha_reserva": input("Fecha de uso (YYYY-MM-DD): "),
        "hora_inicio": pedir_entero("Hora de inicio (0-23): "),
        "duracion_horas": pedir_entero("Duracion en horas: "),
    }
    
    if None in (datos["empleado_id"], datos["sala_id"], datos["hora_inicio"], datos["duracion_horas"]):
        imprimir_error("Los IDs, hora y duracion deben ser numeros enteros")
        return pausa()

    mostrar_resultado(*reservas.crear(datos))
    pausa()


def listar_reservas() -> None:
    """
    Muestra la agenda de reservas del sistema.
    
    Args:
        Ninguno
        
    Returns:
        None
    """
    imprimir_titulo("AGENDA DE RESERVAS")
    mostrar_lista(reservas.leer(), "Todavia no hay reservas.")
    pausa()


def ver_comprobante() -> None:
    """
    Imprime el ticket o confirmacion de la reserva.
    
    Args:
        Ninguno
        
    Returns:
        None
    """
    imprimir_titulo("CONFIRMACION DE RESERVA")
    texto = reservas.comprobante(pedir_entero("Id de la reserva: "))
    if texto is None:
        imprimir_error("No existe esa reserva")
    else:
        print(texto)
    pausa()


def anular_reserva() -> None:
    """
    Elimina una reserva y libera el espacio de la sala.
    
    Args:
        Ninguno
        
    Returns:
        None
    """
    imprimir_titulo("ANULAR RESERVA")
    id_reserva = pedir_entero("Id de la reserva: ")
    if id_reserva and confirmar("Se liberara el espacio de la sala. ¿Confirma?"):
        mostrar_resultado(*reservas.eliminar(id_reserva))
    else:
        imprimir_info("Operacion cancelada")
    pausa()


def resumen() -> None:
    """
    Muestra un tablero con metricas generales del sistema.
    
    Args:
        Ninguno
        
    Returns:
        None
    """
    imprimir_titulo("RESUMEN DEL SISTEMA")
    print(f"  Empleados registrados: {len(empleados.leer())}")
    print(f"  Departamentos activos: {', '.join(empleados.departamentos()) or '-'}")
    print(f"  Salas totales        : {len(salas.leer())}")
    
    con_proyector = salas.salas_con_proyector()
    print(f"  Salas con proyector  : {len(con_proyector)}")
    
    print(f"  Reservas vigentes    : {len(reservas.leer())}")
    pausa()


# MENUS: DICCIONARIOS tecla -> (texto, funcion)

MENU_EMPLEADOS = {
    "1": ("Registrar empleado", crear_empleado),
    "2": ("Ver todos", listar_empleados),
    "3": ("Buscar", buscar_empleado),
    "4": ("Ver por id", ver_empleado),
    "5": ("Actualizar", actualizar_empleado),
    "6": ("Eliminar", eliminar_empleado),
    "0": ("Volver", None),
}

MENU_SALAS = {
    "1": ("Crear sala", crear_sala),
    "2": ("Ver todas", listar_salas),
    "3": ("Buscar", buscar_sala),
    "4": ("Ver por id", ver_sala),
    "5": ("Actualizar", actualizar_sala),
    "6": ("Eliminar", eliminar_sala),
    "0": ("Volver", None),
}

MENU_RESERVAS = {
    "1": ("Reservar sala", registrar_reserva),
    "2": ("Ver agenda completa", listar_reservas),
    "3": ("Ver ticket confirmacion", ver_comprobante),
    "4": ("Anular reserva", anular_reserva),
    "0": ("Volver", None),
}


def ejecutar_menu(titulo: str, opciones: dict) -> None:
    """
    Un solo bucle para los tres submenus.
    
    Args:
        titulo (str): Titulo del menu.
        opciones (dict): Opciones y funciones mapeadas.
        
    Returns:
        None
    """
    while True:
        imprimir_titulo(titulo)
        for tecla, (texto, _funcion) in opciones.items():
            print(f"  {tecla}. {texto}")
        print()

        tecla = input("Opcion: ").strip()
        if tecla not in opciones:               # busqueda por clave: instantanea
            imprimir_error("Opcion no valida")
            pausa()
            continue

        _texto, funcion = opciones[tecla]
        if funcion is None:                     # la opcion "Volver"
            break
        funcion()


def main() -> None:
    """
    Punto de entrada principal del sistema de reservas.
    
    Args:
        Ninguno
        
    Returns:
        None
    """
    while True:
        imprimir_titulo("SISTEMA DE RESERVAS DE SALAS")
        print("  1. Empleados")
        print("  2. Salas de Reuniones")
        print("  3. Agenda / Reservas")
        print("  4. Resumen")
        print("  0. Salir\n")

        tecla = input("Opcion: ").strip()
        if tecla == "1":
            ejecutar_menu("EMPLEADOS", MENU_EMPLEADOS)
        elif tecla == "2":
            ejecutar_menu("SALAS", MENU_SALAS)
        elif tecla == "3":
            ejecutar_menu("RESERVAS", MENU_RESERVAS)
        elif tecla == "4":
            resumen()
        elif tecla == "0":
            imprimir_info("¡Hasta luego! 👋")
            break
        else:
            imprimir_error("Opcion no valida")
            pausa()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nPrograma interrumpido por el usuario.")