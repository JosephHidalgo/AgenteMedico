"""
Script para probar los endpoints del API
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def print_response(title, response):
    """Imprimir respuesta formateada"""
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        try:
            data = response.json()
            print(f"Response:\n{json.dumps(data, indent=2, ensure_ascii=False)}")
        except:
            print(f"Response: {response.text}")
    else:
        print(f"Error: {response.text}")

def test_endpoints():
    """Probar todos los endpoints del API"""
    
    # 1. Listar médicos
    print("\n" + "="*60)
    print("TEST 1: Listar médicos")
    print("="*60)
    response = requests.get(f"{BASE_URL}/api/medicos/")
    print_response("GET /api/medicos/", response)
    
    if response.status_code == 200:
        data = response.json()
        if data.get('medicos'):
            medico_id = data['medicos'][0]['id']
            
            # 2. Obtener horarios de un médico
            print("\n" + "="*60)
            print(f"TEST 2: Horarios del médico ID {medico_id}")
            print("="*60)
            response = requests.get(f"{BASE_URL}/api/medicos/{medico_id}/horarios/")
            print_response(f"GET /api/medicos/{medico_id}/horarios/", response)
    
    # 3. Listar citas
    print("\n" + "="*60)
    print("TEST 3: Listar todas las citas")
    print("="*60)
    response = requests.get(f"{BASE_URL}/api/citas/")
    print_response("GET /api/citas/", response)
    
    # 4. Filtrar citas por estado
    print("\n" + "="*60)
    print("TEST 4: Filtrar citas AGENDADAS")
    print("="*60)
    response = requests.get(f"{BASE_URL}/api/citas/?estado=AGENDADA")
    print_response("GET /api/citas/?estado=AGENDADA", response)
    
    # 5. Iniciar conversación con el asistente
    print("\n" + "="*60)
    print("TEST 5: Iniciar conversación con asistente")
    print("="*60)
    response = requests.post(f"{BASE_URL}/api/asistente/iniciar/")
    print_response("POST /api/asistente/iniciar/", response)
    
    if response.status_code == 200:
        data = response.json()
        conversacion_id = data.get('conversacion_id')
        
        # 6. Enviar mensaje al asistente (requiere OpenAI API key)
        print("\n" + "="*60)
        print("TEST 6: Enviar mensaje al asistente")
        print("="*60)
        print("⚠️  Este test requiere que tengas configurada tu OpenAI API Key en .env")
        mensaje_data = {
            "conversacion_id": conversacion_id,
            "mensaje": "Hola, tengo dolor de cabeza desde hace 2 días"
        }
        response = requests.post(
            f"{BASE_URL}/api/asistente/mensaje/",
            json=mensaje_data
        )
        print_response("POST /api/asistente/mensaje/", response)
    
    # 7. Crear una cita
    print("\n" + "="*60)
    print("TEST 7: Crear una cita")
    print("="*60)
    
    # Primero obtener un médico disponible
    response_medicos = requests.get(f"{BASE_URL}/api/medicos/")
    if response_medicos.status_code == 200:
        data = response_medicos.json()
        if data.get('medicos'):
            medico_id = data['medicos'][0]['id']
            
            cita_data = {
                "medico": medico_id,
                "fecha": "2025-11-15",
                "hora": "10:00:00",
                "motivo": "Consulta general de prueba",
                "sintomas_iniciales": "Dolor de cabeza",
                "paciente_nombre": "Test",
                "paciente_apellido_paterno": "Usuario",
                "paciente_apellido_materno": "Prueba",
                "paciente_email": "test@example.com",
                "paciente_telefono": "999888777",
                "paciente_fecha_nacimiento": "1990-01-01",
                "paciente_sexo": "M"
            }
            
            response = requests.post(
                f"{BASE_URL}/api/citas/",
                json=cita_data
            )
            print_response("POST /api/citas/", response)
            
            if response.status_code == 201:
                cita = response.json()
                cita_id = cita['id']
                
                # 8. Obtener PDF de la cita
                print("\n" + "="*60)
                print(f"TEST 8: Descargar PDF de cita ID {cita_id}")
                print("="*60)
                response = requests.get(f"{BASE_URL}/api/citas/{cita_id}/pdf/")
                if response.status_code == 200:
                    print(f"✅ PDF descargado exitosamente ({len(response.content)} bytes)")
                    # Guardar el PDF
                    with open(f"cita_{cita_id}.pdf", "wb") as f:
                        f.write(response.content)
                    print(f"📄 PDF guardado como: cita_{cita_id}.pdf")
                else:
                    print(f"❌ Error al descargar PDF: {response.status_code}")
    
    print("\n" + "="*60)
    print("✅ PRUEBAS COMPLETADAS")
    print("="*60)

if __name__ == "__main__":
    try:
        test_endpoints()
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se pudo conectar al servidor.")
        print("   Asegúrate de que el servidor esté corriendo en http://localhost:8000")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
