#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cliente de API para el Bot de Reportes
Demuestra cómo enviar reportes programáticamente
"""

import requests
import json
import time
import os # Importar os para usar variables de entorno

# ----------------
# CONFIGURACIÓN
# ----------------
# Se recomienda usar variables de entorno para la clave y URL,
# pero si no se usan, se usa el valor predeterminado del archivo.
API_URL = os.getenv("REPORT_BOT_API_URL", "http://localhost:5000")
# ¡IMPORTANTE! Reemplaza "tu_clave_secreta_aqui" con la clave real de tu bot.py
API_KEY = os.getenv("REPORT_BOT_API_KEY", "tu_clave_secreta_aqui") 

# Headers con autenticación
HEADERS = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}


def check_health():
    """Verifica si el bot está en línea"""
    try:
        response = requests.get(f"{API_URL}/api/health")
        data = response.json()
        print("✅ Bot Status:")
        print(f"   Estado: {data['status']}")
        print(f"   Sesiones activas: {data['sessions']}")
        print(f"   Reporte en curso: {data['reporting_in_progress']}")
        return data['status'] == 'online'
    except Exception as e:
        print(f"❌ Error conectando al bot: {e}")
        return False


def list_sessions():
    """Lista las sesiones disponibles"""
    try:
        response = requests.get(f"{API_URL}/api/sessions", headers=HEADERS)
        if response.status_code == 401:
            print("❌ Error: API Key incorrecta")
            return None
        
        data = response.json()
        print(f"\n📱 Sesiones Activas ({data['count']}):")
        for session in data['sessions']:
            print(f"   • {session['phone']}")
        return data['sessions']
    except Exception as e:
        print(f"❌ Error obteniendo sesiones: {e}")
        return None


def send_report(target, category="spam", comment="", count=1, message_links=None):
    """
    Envía un reporte a través de la API
    
    Args:
        target: Usuario, grupo o canal a reportar (@username o ID)
        category: Categoría del reporte (spam, violence, etc.)
        comment: Comentario adicional
        count: Número de veces a reportar el perfil
        message_links: Lista de enlaces de mensajes específicos (soporta múltiples links)
    """
    if message_links is None:
        message_links = []
    
    payload = {
        "target": target,
        "category": category,
        "comment": comment,
        "count": count,
        "message_links": message_links
    }
    
    print(f"\n📤 Enviando reporte...")
    print(f"   Objetivo: {target}")
    print(f"   Categoría: {category}")
    print(f"   Mensajes: {len(message_links)}")
    print(f"   Repeticiones: {count}")
    
    try:
        response = requests.post(
            f"{API_URL}/api/report",
            headers=HEADERS,
            json=payload
        )
        
        if response.status_code == 401:
            print("❌ Error: API Key incorrecta")
            return None
        
        if response.status_code == 429:
            print("⚠️ Ya hay un reporte en curso. Espera a que termine.")
            return None
        
        if response.status_code == 400:
            print(f"❌ Error en los datos: {response.json()}")
            return None
        
        data = response.json()
        
        if data.get('status') == 'completed':
            print("\n✅ Reporte completado!")
            results = data['results']
            
            msg_reports = results['message_reports']
            profile_reports = results['profile_reports']
            
            print(f"\n📊 Resultados:")
            print(f"   Reportes de Mensajes: {msg_reports['successful']} ✅ / {msg_reports['failed']} ❌")
            print(f"   Reportes de Perfil: {profile_reports['successful']} ✅ / {profile_reports['failed']} ❌")
            
            total_success = msg_reports['successful'] + profile_reports['successful']
            total_fail = msg_reports['failed'] + profile_reports['failed']
            print(f"\n   Total: {total_success} exitosos, {total_fail} fallidos")
            
            return data
        else:
            print(f"⚠️ Respuesta inesperada: {data}")
            return data
            
    except Exception as e:
        print(f"❌ Error enviando reporte: {e}")
        return None


def main():
    """Función principal con ejemplos de uso"""
    print("=" * 60)
    print("🤖 Cliente de API - Bot de Reportes")
    print("=" * 60)
    
    # 1. Verificar estado del bot
    print("\n1️⃣ Verificando estado del bot...")
    if not check_health():
        print("\n❌ El bot no está en línea. Inicia bot.py primero.")
        return
    
    time.sleep(1)
    
    # 2. Listar sesiones
    print("\n2️⃣ Obteniendo sesiones activas...")
    sessions = list_sessions()
    if not sessions or len(sessions) == 0:
        print("\n⚠️ No hay sesiones activas. Agrega sesiones primero con /addsession en Telegram")
        return
    
    time.sleep(1)
    
    # 3. Ejemplos de reportes
    print("\n" + "=" * 60)
    print("📋 EJEMPLOS DE REPORTES")
    print("=" * 60)
    
    # Ejemplo 1: Reportar usuario simple
    print("\n📌 Ejemplo 1: Reportar usuario por spam")
    send_report(
        target="@usuario_spam",
        category="spam",
        comment="Enviando publicidad no solicitada",
        count=3
    )
    
    time.sleep(2)
    
    # Ejemplo 2: Reportar mensajes específicos (con múltiples links)
    print("\n📌 Ejemplo 2: Reportar mensajes específicos")
    send_report(
        target="@canal_problematico",
        category="violence",
        comment="Contenido violento",
        count=2,
        message_links=[
            "https://t.me/canal_problematico/123",
            "https://t.me/canal_problematico/124",
            "https://t.me/canal_problematico/125" # ¡Múltiples links soportados!
        ]
    )
    
    time.sleep(2)
    
    # Ejemplo 3: Reportar canal privado (soporta links de invitación)
    print("\n📌 Ejemplo 3: Reportar canal privado (link de invitación)")
    send_report(
        target="https://t.me/c/1234567890/1", # Link de un mensaje en el canal privado
        category="pornography",
        comment="Contenido explícito no apropiado",
        count=5
    )
    
    print("\n" + "=" * 60)
    print("✅ Ejemplos completados")
    print("=" * 60)


# Función para uso interactivo
def interactive_mode():
    """Modo interactivo para enviar reportes"""
    print("\n🎮 MODO INTERACTIVO")
    print("=" * 60)
    
    if not check_health():
        print("\n❌ El bot no está en línea.")
        return
    
    sessions = list_sessions()
    if not sessions or len(sessions) == 0:
        print("\n⚠️ No hay sesiones activas.")
        return
    
    print("\nIngresa los datos del reporte:")
    
    target = input("  📍 Objetivo (@usuario, link, etc): ").strip()
    if not target:
        print("❌ Objetivo requerido")
        return
    
    print("\n  Categorías disponibles:")
    print("    1. spam")
    print("    2. violence")
    print("    3. pornography")
    print("    4. child_abuse")
    print("    5. copyright")
    print("    6. fake")
    print("    7. personal_details")
    print("    8. other")
    
    category = input("\n  🏷️ Categoría (1-8 o nombre): ").strip()
    categories = ["spam", "violence", "pornography", "child_abuse", 
                  "copyright", "fake", "personal_details", "other"]
    
    # Intenta convertir el número a categoría, si no, usa el texto
    try:
        category = categories[int(category) - 1]
    except:
        # Usa el texto ingresado por el usuario, si es válido. Si no, usa "spam"
        if category not in categories:
            category = "spam"
            print(f"  ⚠️ Usando categoría por defecto: {category}")
        else:
            print(f"  ✅ Categoría seleccionada: {category}")

    
    comment = input("  💬 Comentario (Enter para omitir): ").strip()
    
    count_str = input("  🔢 Repeticiones (1-50, default 1): ").strip()
    try:
        count = int(count_str) if count_str else 1
        count = max(1, min(50, count))
    except:
        count = 1
    
    print("\n  Enlaces de mensajes (uno por línea, Enter vacío para terminar):")
    message_links = []
    while True:
        link = input("    🔗 ").strip()
        if not link:
            break
        message_links.append(link)
    
    print("\n" + "=" * 60)
    send_report(target, category, comment, count, message_links)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_mode()
    else:
        main()
        
        # Preguntar si quiere modo interactivo
        print("\n¿Deseas usar el modo interactivo? (s/n): ", end="")
        choice = input().strip().lower()
        if choice == 's':
            interactive_mode()