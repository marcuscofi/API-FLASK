import sys
import json
import requests
from typing import Dict, Any, Union

BASE_URL = "http://127.0.0.1:5000"

def imprimir_titulo(titulo: str) -> None:
    """Helper para imprimir secciones de pruebas con formato elegante."""
    print("\n" + "=" * 60)
    print(f" {titulo.upper()} ".center(60, "="))
    print("=" * 60)

def mostrar_resultado(nombre_caso: str, response: requests.Response) -> None:
    """Imprime el código de estado y el JSON formateado de la respuesta."""
    print(f"\nCaso: {nombre_caso}")
    print(f"Código HTTP: {response.status_code}")
    try:
        datos = response.json()
        print("Cuerpo JSON:")
        print(json.dumps(datos, indent=4, ensure_ascii=False))
    except ValueError:
        print(f"Cuerpo Plano (No es JSON): {response.text}")

def ejecutar_pruebas() -> None:
    """Ejecuta una serie de peticiones HTTP para verificar todos los endpoints de la API."""
    try:
        # Verificar conexión inicial con el servidor
        response = requests.get(BASE_URL)
    except requests.exceptions.ConnectionError:
        print("ERROR CRÍTICO: No se puede establecer conexión con el servidor Flask.")
        print(f"Asegúrese de ejecutar primero 'app.py' en {BASE_URL} antes de correr este cliente.")
        sys.exit(1)

    # --- PRUEBA 1: Endpoint Raíz ---
    imprimir_titulo("Prueba 1: Obtener Información de la API")
    mostrar_resultado("GET / (Raíz)", response)

    # --- PRUEBA 2: Obtener Clientes Iniciales ---
    imprimir_titulo("Prueba 2: Listar Clientes Iniciales")
    res_listar = requests.get(f"{BASE_URL}/clientes")
    mostrar_resultado("GET /clientes (Iniciales)", res_listar)

    # --- PRUEBA 3: Crear un Nuevo Cliente Exitosamente ---
    imprimir_titulo("Prueba 3: Crear Nuevo Cliente (Petición Válida)")
    nuevo_cliente = {
        "nombre": "Isabel Ortiz",
        "saldo": 450.75
    }
    res_crear = requests.post(
        f"{BASE_URL}/clientes",
        json=nuevo_cliente
    )
    mostrar_resultado("POST /clientes (Válido)", res_crear)
    
    # Extraer el ID generado si se creó con éxito para usarlo en la Prueba 4
    id_nuevo = None
    if res_crear.status_code == 201:
        id_nuevo = res_crear.json().get("id")

    # --- PRUEBA 4: Obtener el Cliente Recién Creado ---
    if id_nuevo:
        imprimir_titulo(f"Prueba 4: Obtener Cliente Creado (ID: {id_nuevo})")
        res_obtener_nuevo = requests.get(f"{BASE_URL}/clientes/{id_nuevo}")
        mostrar_resultado(f"GET /clientes/{id_nuevo}", res_obtener_nuevo)

    # --- PRUEBA 5: Intentar Obtener Cliente Inexistente (Error 404) ---
    imprimir_titulo("Prueba 5: Buscar Cliente Inexistente")
    id_inexistente = 999
    res_inexistente = requests.get(f"{BASE_URL}/clientes/{id_inexistente}")
    mostrar_resultado(f"GET /clientes/{id_inexistente} (Esperado: 404)", res_inexistente)

    # --- PRUEBA 6: Enviar Payload Inválido - Sin Nombre (Error 400) ---
    imprimir_titulo("Prueba 6: Intentar Crear Cliente sin Nombre")
    cliente_sin_nombre = {
        "saldo": 100.00
    }
    res_sin_nombre = requests.post(
        f"{BASE_URL}/clientes",
        json=cliente_sin_nombre
    )
    mostrar_resultado("POST /clientes (Falta Nombre - Esperado: 400)", res_sin_nombre)

    # --- PRUEBA 7: Enviar Payload Inválido - Saldo Negativo (Error 400) ---
    imprimir_titulo("Prueba 7: Intentar Crear Cliente con Saldo Negativo")
    cliente_saldo_negativo = {
        "nombre": "Pedro Páramo",
        "saldo": -10.50
    }
    res_saldo_negativo = requests.post(
        f"{BASE_URL}/clientes",
        json=cliente_saldo_negativo
    )
    mostrar_resultado("POST /clientes (Saldo Negativo - Esperado: 400)", res_saldo_negativo)

    # --- PRUEBA 8: Listado Final de Clientes ---
    imprimir_titulo("Prueba 8: Listado Final Completo")
    res_listar_final = requests.get(f"{BASE_URL}/clientes")
    mostrar_resultado("GET /clientes (Listado Final)", res_listar_final)

if __name__ == "__main__":
    print("Iniciando Suite de Pruebas de la API de Clientes...")
    ejecutar_pruebas()
