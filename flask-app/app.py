import logging
from typing import Dict, Any, List, Tuple
from flask import Flask, jsonify, request, Response

# Configurar el registro de eventos (logging) para auditoría del servidor
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Base de datos simulada en memoria con tipado estático
# Formato: { id_cliente (int): { "id": int, "nombre": str, "saldo": float } }
clientes: Dict[int, Dict[str, Any]] = {
    101: {"id": 101, "nombre": "Carlos Ramos", "saldo": 150.50},
    102: {"id": 102, "nombre": "Glenda Flores", "saldo": 320.00}
}

@app.route("/", methods=["GET"])
def inicio() -> Response:
    """
    Endpoint raíz: Retorna un saludo de bienvenida, la versión y una lista informativa de endpoints.
    """
    logger.info("Consulta al endpoint raíz '/' recibida")
    return jsonify({
        "mensaje": "Bienvenido a la API de clientes",
        "version": "1.0",
        "endpoints": {
            "listar_clientes": "GET /clientes",
            "obtener_cliente": "GET /clientes/<id>",
            "crear_cliente": "POST /clientes"
        }
    })

@app.get("/clientes")
def obtener_clientes() -> Response:
    """
    Retorna el listado completo de clientes ordenados secuencialmente por su ID.
    """
    logger.info("Consulta a GET /clientes - Listando todos los clientes")
    lista_clientes = sorted(list(clientes.values()), key=lambda x: x["id"])
    return jsonify(lista_clientes)

@app.get("/clientes/<int:id>")
def obtener_cliente(id: int) -> Tuple[Response, int]:
    """
    Retorna los datos de un cliente específico según su ID.
    Si el ID no existe en memoria, retorna una respuesta 404 (Not Found).
    """
    logger.info(f"Consulta a GET /clientes/{id} - Buscando cliente")
    cliente = clientes.get(id)
    if cliente:
        return jsonify(cliente), 200
    
    logger.warning(f"Error de consulta: Cliente con ID {id} no encontrado")
    return jsonify({"error": f"Cliente con ID {id} no encontrado"}), 404

@app.post("/clientes")
def agregar_cliente() -> Tuple[Response, int]:
    """
    Crea un nuevo cliente a partir de un cuerpo JSON.
    Valida estrictamente que:
    - La petición envíe contenido de tipo JSON.
    - Se incluya el campo 'nombre' como una cadena de texto no vacía.
    - El campo 'saldo' (opcional) sea numérico y no sea negativo.
    """
    logger.info("Petición POST /clientes - Solicitud de creación de nuevo cliente")
    
    # 1. Validar que la cabecera sea JSON
    if not request.is_json:
        logger.error("Creación rechazada: Content-Type no es application/json")
        return jsonify({"error": "La petición debe incluir cabecera Content-Type: application/json"}), 415

    datos = request.get_json()
    if not datos:
        logger.error("Creación rechazada: Cuerpo JSON vacío")
        return jsonify({"error": "El cuerpo de la petición JSON no puede estar vacío"}), 400

    # 2. Validar y limpiar el campo 'nombre' (obligatorio)
    nombre = datos.get("nombre")
    if not nombre or not isinstance(nombre, str) or not nombre.strip():
        logger.error("Creación rechazada: Nombre ausente, vacío o no es texto")
        return jsonify({"error": "El campo 'nombre' es obligatorio, debe ser un texto y no estar vacío"}), 400

    # 3. Validar el campo 'saldo' (opcional, valor por defecto de 0.0)
    saldo_raw = datos.get("saldo", 0.0)
    
    # Asegurar que sea numérico y descartar booleanos (Python considera a bool como subclase de int)
    if not isinstance(saldo_raw, (int, float)) or isinstance(saldo_raw, bool):
        logger.error("Creación rechazada: El campo 'saldo' no es un número")
        return jsonify({"error": "El campo 'saldo' debe ser un valor numérico"}), 400
        
    saldo = float(saldo_raw)
    if saldo < 0:
        logger.error(f"Creación rechazada: Saldo negativo provisto ({saldo})")
        return jsonify({"error": "El saldo no puede ser un valor negativo"}), 400

    # 4. Auto-generación de ID incremental seguro
    id_cliente = max(clientes.keys(), default=100) + 1

    # 5. Estructurar el nuevo registro limpiando llaves adicionales inesperadas
    nuevo_cliente = {
        "id": id_cliente,
        "nombre": nombre.strip(),
        "saldo": round(saldo, 2)
    }

    clientes[id_cliente] = nuevo_cliente
    logger.info(f"Cliente creado exitosamente: ID={id_cliente}, Nombre='{nuevo_cliente['nombre']}'")
    
    return jsonify(nuevo_cliente), 201

if __name__ == "__main__":
    # Ejecutar en modo desarrollo local en el puerto estándar 5000
    app.run(debug=True, port=5000)
