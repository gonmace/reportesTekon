#!/usr/bin/env python3
"""
Script simple para probar la API de login
"""

import requests
import json

# URL de la API (usando el puerto 8001 como en tu main.rest)
BASE_URL = "http://localhost:8001"
LOGIN_URL = f"{BASE_URL}/api/v1/mobile/login/"


def test_login():
    """Prueba el login con las credenciales del main.rest"""

    # Datos de prueba (probando con el usuario 'maick' primero)
    data = {
        "username": "maick",
        "password": "djmaickxd"
    }

    headers = {
        "Content-Type": "application/json"
    }

    print("=== Probando API de Login ===")
    print(f"URL: {LOGIN_URL}")
    print(f"Datos: {json.dumps(data, indent=2)}")
    print(f"Headers: {headers}")
    print("-" * 50)

    try:
        response = requests.post(LOGIN_URL, json=data, headers=headers)

        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")

        if response.status_code == 200:
            print("✅ Login exitoso!")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        else:
            print("❌ Login falló")
            print(f"Response: {response.text}")

    except requests.exceptions.ConnectionError:
        print("❌ Error de conexión. Asegúrate de que el servidor esté corriendo en el puerto 8001")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")


if __name__ == "__main__":
    test_login()
