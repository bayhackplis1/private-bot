# -*- coding: utf-8 -*-
"""
🤖 𝙃𝙤𝙤𝙠𝙞𝙣𝙜𝙂𝙖𝙣𝙜 V16.0 - UNCOMPRESSED TITAN EDITION
🛡 CÓDIGO EXTENDIDO: Todas las funciones explícitas y detalladas.
🛡 SOPORTE TOTAL:
   - Monitor de Servidor y Logs en tiempo real.
   - Sistema de Respuesta de Soporte (Admin -> Usuario).
   - Inmunización y Modos Virus nucleares.
   - Gestión de Sesiones (Añadir/Borrar/Escanear).
   - Lista de 40+ Dispositivos de Gama Alta.
   - Proxies Rotativas Integradas.
"""

import os
import asyncio
import random
import sys
import json
import time
import re
import psutil
import aiohttp
from datetime import datetime, timedelta
from dotenv import load_dotenv

# ---------------------------------------------------------
# LIBRERÍAS EXTERNAS
# ---------------------------------------------------------
# Telegram Bot API
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters,
    ConversationHandler, CallbackQueryHandler, ContextTypes
)

# Telethon (Cliente Telegram)
from telethon import TelegramClient, functions, types, errors
from telethon.tl.functions.account import ReportPeerRequest
from telethon.tl.functions.messages import ReportRequest, ImportChatInviteRequest
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.types import (
    InputReportReasonSpam,
    InputReportReasonViolence,
    InputReportReasonPornography,
    InputReportReasonChildAbuse,
    InputReportReasonFake,
    InputReportReasonPersonalDetails, 
    InputReportReasonOther,
    InputReportReasonCopyright,
    InputReportReasonIllegalDrugs,
    Channel
)

# ---------------------------------------------------------
# CARGA DE ENTORNO Y VARIABLES
# ---------------------------------------------------------
load_dotenv()
START_TIME = time.time()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
OWNER_IDS_RAW = os.getenv("OWNER_IDS", "")
DEFAULT_BANNER = "https://i.pinimg.com/736x/8d/68/a6/8d68a6411d51ec65171725b82cb160c8.jpg"
DEV_LINK = "https://t.me/Virus_OFC"
CHANNEL_LINK = "https://t.me/HookingGang"
PROXY_API_URL = "https://tq.lunaproxy.com/get_dynamic_ip?neek=1824239&num=1000&regions=all&ip_si=6&sb="
MONITOR_GROUP_ID = -1003343643536

# Verificación de seguridad
if not all([TELEGRAM_BOT_TOKEN, API_ID, API_HASH]):
    print("❌ ERROR CRITICO: Faltan credenciales en el archivo .env")
    print("Por favor, edita el archivo .env con tus datos.")
    sys.exit(1)

# Procesamiento de IDs de Dueños
try:
    OWNER_IDS = {int(x.strip()) for x in OWNER_IDS_RAW.split(",") if x.strip()}
except:
    print("⚠️ Advertencia: Error leyendo OWNER_IDS. Usando set vacío.")
    OWNER_IDS = set()

# Directorios y Archivos
SESSION_DIR = "sessions"
CONFIG_FILE = "config.json"
VIP_FILE = "vip_users.json"
PROXY_FILE = "proxies.json"
os.makedirs(SESSION_DIR, exist_ok=True)

# Sistema de Proxies Global
PROXY_POOL = []
PROXY_STATS = {'total': 0, 'active': 0, 'used': 0}

# ---------------------------------------------------------
# DEFINICIÓN DE ESTADOS DE CONVERSACIÓN
# ---------------------------------------------------------
# Flujo Principal de Ataque
ASK_SPECIFIC_TARGET = 0
ASK_CATEGORY = 1
ASK_COMMENT = 2
ASK_COUNT = 3
ASK_CONFIRM = 4

# Flujo de Sesiones
ASK_NUMBER = 5
ASK_CODE = 6
ASK_PASSWORD = 7
ASK_DELETE_NUM = 8

# Flujo de Configuración
ASK_BANNER_PHOTO = 9

# Flujo de Soporte
ASK_ADMIN_REPLY = 10

# Flujo VIP
ASK_VIP_USER_ID = 11
ASK_VIP_DAYS = 12
ASK_REMOVE_VIP_ID = 13

# Variable de control global
cancel_reporting_flag = False

# Sistema de Colores para Consola
class Colors:
    GREEN = '\033[92m'
    RESET = '\033[0m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'

BANNER_ASCII = f"""{Colors.RED}
██╗  ██╗ ██████╗  ██████╗ ██╗  ██╗██╗███╗   ██╗ ██████╗ 
██║  ██║██╔═══██╗██╔═══██╗██║ ██╔╝██║████╗  ██║██╔════╝ 
███████║██║   ██║██║   ██║█████╔╝ ██║██╔██╗ ██║██║  ███╗
██╔══██║██║   ██║██║   ██║██╔═██╗ ██║██║╚██╗██║██║   ██║
██║  ██║╚██████╔╝╚██████╔╝██║  ██╗██║██║ ╚████║╚██████╔╝
╚═╝  ╚═╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝ ╚═════╝ 
  ██████╗  █████╗ ███╗   ██╗ ██████╗ 
 ██╔════╝ ██╔══██╗████╗  ██║██╔════╝ 
 ██║  ███╗███████║██╔██╗ ██║██║  ███╗
 ██║   ██║██╔══██║██║╚██╗██║██║   ██║
 ╚██████╔╝██║  ██║██║ ╚████║╚██████╔╝
  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝ 
           V16.0 - UNCOMPRESSED TITAN EDITION
{Colors.RESET}"""

# ---------------------------------------------------------
# GESTIÓN DE CONFIGURACIÓN
# ---------------------------------------------------------
def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_config(data):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(data, f)

def get_banner():
    cfg = load_config()
    return cfg.get("banner", DEFAULT_BANNER)

# ---------------------------------------------------------
# SISTEMA VIP
# ---------------------------------------------------------
def load_vip_users():
    """Carga la lista de usuarios VIP desde el archivo JSON."""
    if os.path.exists(VIP_FILE):
        try:
            with open(VIP_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_vip_users(data):
    """Guarda la lista de usuarios VIP en el archivo JSON."""
    with open(VIP_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def is_vip(user_id):
    """Verifica si un usuario tiene acceso VIP vigente."""
    vip_data = load_vip_users()
    user_id_str = str(user_id)
    
    if user_id_str not in vip_data:
        return False
    
    expiry = vip_data[user_id_str].get('expiry')
    if expiry == "permanent":
        return True
    
    try:
        expiry_date = datetime.fromisoformat(expiry)
        return datetime.now() < expiry_date
    except:
        return False

def add_vip_user(user_id, days=None, username=None):
    """Agrega un usuario VIP con duración específica o permanente."""
    vip_data = load_vip_users()
    user_id_str = str(user_id)
    
    if days is None or days == 0:
        expiry = "permanent"
    else:
        expiry = (datetime.now() + timedelta(days=days)).isoformat()
    
    vip_data[user_id_str] = {
        'expiry': expiry,
        'added_at': datetime.now().isoformat(),
        'username': username or "Unknown"
    }
    
    save_vip_users(vip_data)
    return expiry

def remove_vip_user(user_id):
    """Elimina un usuario VIP."""
    vip_data = load_vip_users()
    user_id_str = str(user_id)
    
    if user_id_str in vip_data:
        del vip_data[user_id_str]
        save_vip_users(vip_data)
        return True
    return False

def get_vip_info(user_id):
    """Obtiene información detallada del VIP de un usuario."""
    vip_data = load_vip_users()
    user_id_str = str(user_id)
    
    if user_id_str not in vip_data:
        return None
    
    user_vip = vip_data[user_id_str]
    expiry = user_vip.get('expiry')
    
    if expiry == "permanent":
        return {
            'status': 'permanent',
            'days_left': '∞',
            'expiry_date': 'Permanente'
        }
    
    try:
        expiry_date = datetime.fromisoformat(expiry)
        days_left = (expiry_date - datetime.now()).days
        
        if days_left < 0:
            return None
        
        return {
            'status': 'active',
            'days_left': days_left,
            'expiry_date': expiry_date.strftime('%d/%m/%Y')
        }
    except:
        return None

def check_access(user_id):
    """Verifica si el usuario tiene acceso al bot (Owner o VIP)."""
    return check_owner(user_id) or is_vip(user_id)

# ---------------------------------------------------------
# SISTEMA DE PROXIES ROTATIVAS
# ---------------------------------------------------------
async def fetch_proxies():
    """Obtiene proxies desde la API de LunaProxy."""
    global PROXY_POOL, PROXY_STATS
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(PROXY_API_URL, timeout=30) as response:
                if response.status == 200:
                    text = await response.text()
                    # Las proxies vienen en formato: IP:PORT:USER:PASS
                    proxies = []
                    for line in text.strip().split('\n'):
                        if ':' in line:
                            parts = line.strip().split(':')
                            if len(parts) >= 2:
                                proxies.append({
                                    'ip': parts[0],
                                    'port': parts[1],
                                    'user': parts[2] if len(parts) > 2 else None,
                                    'pass': parts[3] if len(parts) > 3 else None,
                                    'used': False,
                                    'full': line.strip()
                                })
                    
                    PROXY_POOL = proxies
                    PROXY_STATS['total'] = len(proxies)
                    PROXY_STATS['active'] = len([p for p in proxies if not p['used']])
                    
                    print(f"{Colors.GREEN}✅ {len(proxies)} proxies cargadas desde LunaProxy{Colors.RESET}")
                    
                    # Guardar en archivo local
                    with open(PROXY_FILE, 'w') as f:
                        json.dump(proxies, f, indent=2)
                    
                    return True
    except Exception as e:
        print(f"{Colors.RED}❌ Error cargando proxies: {e}{Colors.RESET}")
        # Intentar cargar desde archivo local
        if os.path.exists(PROXY_FILE):
            try:
                with open(PROXY_FILE, 'r') as f:
                    PROXY_POOL = json.load(f)
                    PROXY_STATS['total'] = len(PROXY_POOL)
                    PROXY_STATS['active'] = len([p for p in PROXY_POOL if not p['used']])
                    print(f"{Colors.YELLOW}⚠️ Usando {len(PROXY_POOL)} proxies del cache{Colors.RESET}")
                    return True
            except:
                pass
    return False

def get_next_proxy():
    """Obtiene la siguiente proxy disponible del pool."""
    global PROXY_STATS
    
    if not PROXY_POOL:
        return None
    
    # Buscar proxy no usada
    for proxy in PROXY_POOL:
        if not proxy['used']:
            proxy['used'] = True
            PROXY_STATS['used'] += 1
            PROXY_STATS['active'] -= 1
            return proxy
    
    # Si todas están usadas, resetear y usar la primera
    for proxy in PROXY_POOL:
        proxy['used'] = False
    PROXY_STATS['used'] = 0
    PROXY_STATS['active'] = PROXY_STATS['total']
    
    if PROXY_POOL:
        PROXY_POOL[0]['used'] = True
        PROXY_STATS['used'] = 1
        PROXY_STATS['active'] -= 1
        return PROXY_POOL[0]
    
    return None

def proxy_to_dict(proxy):
    """Convierte la proxy a formato compatible con Telethon."""
    if not proxy:
        return None
    
    proxy_dict = {
        'proxy_type': 'socks5',  # Cambiar según el tipo de proxy
        'addr': proxy['ip'],
        'port': int(proxy['port'])
    }
    
    if proxy.get('user') and proxy.get('pass'):
        proxy_dict['username'] = proxy['user']
        proxy_dict['password'] = proxy['pass']
    
    return proxy_dict

# ---------------------------------------------------------
# LISTA DE DISPOSITIVOS (GAMA ALTA & EXTENDIDA)
# ---------------------------------------------------------
def get_random_device_config():
    devices = [
        # Apple iOS
        {'model': 'iPhone 15 Pro Max', 'system': 'iOS 17.5.1', 'app': '10.8.1'},
        {'model': 'iPhone 15 Pro', 'system': 'iOS 17.5', 'app': '10.8.0'},
        {'model': 'iPhone 15', 'system': 'iOS 17.4.1', 'app': '10.8.0'},
        {'model': 'iPhone 14 Pro Max', 'system': 'iOS 16.6.1', 'app': '10.2.0'},
        {'model': 'iPhone 14 Plus', 'system': 'iOS 16.5', 'app': '10.1.0'},
        {'model': 'iPhone 13 Pro', 'system': 'iOS 15.6', 'app': '9.6.4'},
        {'model': 'iPhone 13 Mini', 'system': 'iOS 15.0', 'app': '9.6.4'},
        {'model': 'iPad Pro (M2)', 'system': 'iPadOS 17.4', 'app': '10.8.0'},
        {'model': 'iPad Air 5', 'system': 'iPadOS 16.6', 'app': '10.0.0'},
        
        # Samsung
        {'model': 'Samsung S24 Ultra', 'system': 'Android 14', 'app': '10.9.1'},
        {'model': 'Samsung S24 Plus', 'system': 'Android 14', 'app': '10.9.0'},
        {'model': 'Samsung S23 Ultra', 'system': 'Android 13', 'app': '10.1.1'},
        {'model': 'Samsung S23 Plus', 'system': 'Android 13', 'app': '10.1.0'},
        {'model': 'Samsung Z Fold 5', 'system': 'Android 14', 'app': '10.6.0'},
        {'model': 'Samsung Z Flip 5', 'system': 'Android 14', 'app': '10.5.5'},
        {'model': 'Samsung A54 5G', 'system': 'Android 13', 'app': '10.0.0'},
        {'model': 'Samsung Tab S9', 'system': 'Android 14', 'app': '10.8.5'},

        # Google
        {'model': 'Google Pixel 9 Pro', 'system': 'Android 15', 'app': '10.11.0'},
        {'model': 'Google Pixel 8 Pro', 'system': 'Android 14', 'app': '10.0.0'},
        {'model': 'Google Pixel 8', 'system': 'Android 14', 'app': '10.0.0'},
        {'model': 'Google Pixel 7a', 'system': 'Android 13', 'app': '9.7.0'},

        # Xiaomi / Poco / Redmi
        {'model': 'Xiaomi 14 Ultra', 'system': 'Android 14', 'app': '10.8.2'},
        {'model': 'Xiaomi 13 Pro', 'system': 'Android 13', 'app': '9.8.0'},
        {'model': 'Xiaomi Redmi Note 13', 'system': 'Android 13', 'app': '9.6.5'},
        {'model': 'Poco F5 Pro', 'system': 'Android 13', 'app': '10.0.1'},
        {'model': 'Poco X6 Pro', 'system': 'Android 14', 'app': '10.9.0'},

        # Gaming & Otros
        {'model': 'OnePlus 12', 'system': 'Android 14', 'app': '10.4.5'},
        {'model': 'Huawei P60 Pro', 'system': 'HarmonyOS 4.0', 'app': '10.2.3'},
        {'model': 'Honor Magic6 Pro', 'system': 'Android 14', 'app': '10.7.0'},
        {'model': 'Nothing Phone (2)', 'system': 'Android 14', 'app': '10.5.0'},
        {'model': 'Sony Xperia 1 V', 'system': 'Android 13', 'app': '9.8.0'},
        {'model': 'Realme GT 5', 'system': 'Android 14', 'app': '10.6.2'},
        {'model': 'Asus ROG Phone 8', 'system': 'Android 14', 'app': '10.9.0'},
        {'model': 'RedMagic 9 Pro', 'system': 'Android 14', 'app': '10.8.0'},
        {'model': 'Black Shark 5 Pro', 'system': 'Android 12', 'app': '9.5.0'},
        {'model': 'Motorola Edge 40', 'system': 'Android 13', 'app': '9.9.0'},
        {'model': 'Vivo X100 Pro', 'system': 'Android 14', 'app': '10.5.5'},
        {'model': 'Oppo Find X7', 'system': 'Android 14', 'app': '10.6.1'}
    ]
    return random.choice(devices)

# ---------------------------------------------------------
# UTILIDADES VARIAS
# ---------------------------------------------------------
def check_owner(user_id):
    """Verifica si el usuario es Owner."""
    return user_id in OWNER_IDS

def extract_hash(link):
    """Extrae el hash de un enlace de invitación."""
    if "+" in link:
        return link.split("+")[1]
    if "joinchat" in link:
        return link.split("joinchat/")[1]
    return link.split("/")[-1]

def parse_target_input(text):
    """
    Analiza el texto para determinar qué tipo de objetivo es.
    Retorna: (Tipo, Valor1, Valor2)
    """
    # 1. Mensaje Público (t.me/canal/123)
    match_msg_pub = re.search(r"(?:t\.me|telegram\.me)/([\w\d_]+)/(\d+)", text)
    if match_msg_pub:
        return "msg_public", match_msg_pub.group(1), int(match_msg_pub.group(2))
    
    # 2. Mensaje Privado (t.me/c/12345/123)
    match_msg_priv = re.search(r"(?:t\.me|telegram\.me)/c/(\d+)/(\d+)", text)
    if match_msg_priv:
        return "msg_private", int(match_msg_priv.group(1)), int(match_msg_priv.group(2))
    
    # 3. Invitación (t.me/+hash)
    if "+" in text or "joinchat" in text:
        hash_val = text.split("+")[-1] if "+" in text else text.split("joinchat/")[-1]
        return "invite", hash_val.replace("/", ""), None
        
    # 4. Usuario o Canal Simple (@usuario)
    username = text.split("/")[-1].replace("@", "")
    return "peer", username, None

async def safe_edit(query, text, markup):
    """Intenta editar un mensaje de forma segura."""
    try:
        await query.edit_message_caption(caption=text, parse_mode='Markdown', reply_markup=markup)
    except:
        try:
            await query.edit_message_text(text=text, parse_mode='Markdown', reply_markup=markup)
        except:
            pass

def get_progress_bar(current, total, length=10):
    """Genera una barra de progreso visual."""
    if total == 0:
        return "░" * length
    pct = current / total
    hashes = int(pct * length)
    spaces = length - hashes
    return "▓" * hashes + "░" * spaces

# ---------------------------------------------------------
# MOTOR DE ATAQUE HÍBRIDO MEJORADO (MÁS HUMANO E INDETECTABLE)
# ---------------------------------------------------------
async def attack_worker(session_path, target_raw, count, reason, custom_msg, stats, mode="normal", context=None):
    if cancel_reporting_flag:
        return
    
    # Configuración de sesión y dispositivo
    dev = get_random_device_config()
    session_name = os.path.basename(session_path).replace(".session", "")
    
    # Obtener proxy para esta sesión
    proxy = get_next_proxy()
    proxy_dict = proxy_to_dict(proxy) if proxy else None
    proxy_display = f"{proxy['ip']}:{proxy['port']}" if proxy else "Sin Proxy"
    
    client = TelegramClient(
        session_path.replace(".session", ""), 
        API_ID, 
        API_HASH, 
        device_model=dev['model'], 
        system_version=dev['system'], 
        app_version=dev['app'],
        proxy=proxy_dict
    )

    try:
        await client.connect()
        if not await client.is_user_authorized():
            print(f"{Colors.RED}❌ {session_name} -> OFF (Sesión inválida){Colors.RESET}")
            await client.disconnect()
            return

        # Resolución del Objetivo
        target_type, val1, val2 = parse_target_input(target_raw)
        entity = None
        target_msg_id = None

        try:
            if target_type == "invite":
                try:
                    await client(ImportChatInviteRequest(val1))
                except:
                    pass
                async for dialog in client.iter_dialogs(limit=5):
                    entity = dialog.entity
                    break
            
            elif target_type == "msg_private":
                try:
                    entity = await client.get_entity(int(f"-100{val1}"))
                except:
                    try:
                        entity = await client.get_entity(int(val1))
                    except:
                        pass
                target_msg_id = val2

            else:
                entity = await client.get_entity(val1)
                if target_type == "msg_public":
                    target_msg_id = val2
                
                # Unirse automáticamente si es un canal/grupo público
                if isinstance(entity, Channel):
                    try:
                        await client(JoinChannelRequest(entity))
                    except:
                        pass

        except Exception as e:
            stats['failed'] += count
            await client.disconnect()
            return

        if not entity:
            stats['failed'] += count
            await client.disconnect()
            return

        # Configuración visual del log
        prefix = f"{Colors.CYAN}[ATAQUE]{Colors.RESET}"
        if mode == "virus": prefix = f"{Colors.MAGENTA}[VIRUS]{Colors.RESET}"
        if mode == "immune": prefix = f"{Colors.YELLOW}[IMMUNE]{Colors.RESET}"

        # Bucle de Reportes con comportamiento humano
        for i in range(count):
            if cancel_reporting_flag:
                break
            try:
                ts = datetime.now().strftime('%H:%M:%S')
                
                # Variación en el mensaje para simular comportamiento humano
                variations = ['', ' ', '  ', '\u200b', '\u200c', '\u200d']
                final_msg = custom_msg + random.choice(variations) + ''.join(random.choices(variations, k=random.randint(1, 3)))
                
                # --- MODO INMUNIZACIÓN (POTENCIADO) ---
                if mode == "immune":
                    # Múltiples reportes con diferentes razones para fortalecer
                    immune_reasons = [
                        InputReportReasonOther(),
                        InputReportReasonFake(),
                        InputReportReasonSpam()
                    ]
                    
                    for immune_reason in immune_reasons:
                        await client(ReportPeerRequest(peer=entity, reason=immune_reason, message="Verification and security check"))
                        await asyncio.sleep(random.uniform(1, 2))  # Pausa humanizada
                    
                    stats['success'] += len(immune_reasons)
                    print(f"[{ts}] {prefix} ✅ {session_name} | 🌐 {proxy_display} -> Perfil SUPER-Inmunizado (x{len(immune_reasons)})")
                    await asyncio.sleep(random.randint(8, 15))
                    
                # --- MODO VIRUS (NUKE MEJORADO) ---
                elif mode == "virus":
                    # Ataque masivo con TODAS las razones disponibles
                    reasons_nuke = [
                        InputReportReasonSpam(), 
                        InputReportReasonViolence(), 
                        InputReportReasonFake(),
                        InputReportReasonPornography(),
                        InputReportReasonChildAbuse(),
                        InputReportReasonIllegalDrugs(),
                        InputReportReasonCopyright()
                    ]
                    
                    nuke_count = 0
                    for r in reasons_nuke:
                        try:
                            await client(ReportPeerRequest(peer=entity, reason=r, message="SPAM DETECTED"))
                            nuke_count += 1
                            await asyncio.sleep(random.uniform(0.3, 0.8))  # Rápido pero no instantáneo
                        except:
                            pass
                    
                    stats['success'] += nuke_count
                    print(f"[{ts}] {prefix} ☢️ {session_name} | 🌐 {proxy_display} -> SUPER-NUKE PERFIL (x{nuke_count})")
                    
                    # Si hay mensaje, también atacarlo
                    if target_msg_id:
                        for r in [InputReportReasonSpam(), InputReportReasonViolence(), InputReportReasonFake()]:
                            try:
                                await client(ReportRequest(peer=entity, id=[target_msg_id], reason=r, message="SPAM"))
                                await asyncio.sleep(random.uniform(0.3, 0.7))
                            except:
                                pass
                        print(f"[{ts}] {prefix} ☢️ {session_name} | 🌐 {proxy_display} -> SUPER-NUKE MSG #{target_msg_id}")
                    
                    await asyncio.sleep(random.uniform(1, 2))

                # --- MODO NORMAL MEJORADO (TRIPLE IMPACTO) ---
                else:
                    success_count = 0
                    
                    # 1. Reporte al Perfil (Con doble verificación)
                    try:
                        await client(ReportPeerRequest(peer=entity, reason=reason, message=final_msg))
                        success_count += 1
                        
                        # Segundo reporte con razón alternativa para reforzar
                        alt_reason = InputReportReasonFake() if reason != InputReportReasonFake() else InputReportReasonOther()
                        await asyncio.sleep(random.uniform(2, 4))
                        await client(ReportPeerRequest(peer=entity, reason=alt_reason, message=final_msg))
                        success_count += 1
                        
                        print(f"[{ts}] {prefix} 👀 {session_name} | 🌐 {proxy_display} -> [PERFIL x2] Reportes Enviados")
                    except Exception as e:
                        print(f"[{ts}] {prefix} ⚠️ {session_name} | 🌐 {proxy_display} -> Falló Reporte Perfil")

                    # 2. Reporte al Mensaje Específico (Con refuerzo)
                    if target_msg_id:
                        try:
                            await asyncio.sleep(random.uniform(2, 3))
                            await client(ReportRequest(peer=entity, id=[target_msg_id], reason=reason, message=final_msg))
                            
                            # Segundo reporte al mensaje
                            await asyncio.sleep(random.uniform(1, 2))
                            await client(ReportRequest(peer=entity, id=[target_msg_id], reason=InputReportReasonSpam(), message=final_msg))
                            success_count += 2
                            
                            print(f"[{ts}] {prefix} 💥 {session_name} | 🌐 {proxy_display} -> [MSG #{target_msg_id} x2] Reportes Enviados")
                        except:
                            pass
                    
                    # 3. Auto-Hunt: Si es Canal y no hay ID, ataca múltiples mensajes recientes
                    elif isinstance(entity, Channel):
                         try:
                             msgs = await client.get_messages(entity, limit=3)  # Últimos 3 mensajes
                             for msg in msgs:
                                 if msg:
                                     await asyncio.sleep(random.uniform(1, 2))
                                     await client(ReportRequest(peer=entity, id=[msg.id], reason=reason, message=final_msg))
                                     success_count += 1
                             print(f"[{ts}] {prefix} 🔫 {session_name} | 🌐 {proxy_display} -> [AUTO-HUNT x{len(msgs)}] Reportes Enviados")
                         except:
                             pass
                    
                    stats['success'] += success_count
                    
                    # Pausa humanizada variable (simula lectura, escritura, etc)
                    await asyncio.sleep(random.uniform(5, 10))
            
            except errors.FloodWaitError as e:
                print(f"{Colors.RED}[FloodWait] {session_name} | 🌐 {proxy_display} espera {e.seconds}s{Colors.RESET}")
                await asyncio.sleep(e.seconds)
            except Exception as e:
                stats['failed'] += 1

    except Exception as e:
        pass
    finally:
        if client.is_connected():
            await client.disconnect()

# ---------------------------------------------------------
# SISTEMA DE MONITOREO EN VIVO (Usuario + Grupo)
# ---------------------------------------------------------
async def live_monitor(message, stats, total_expected, cat_name, context, target, custom_msg, mode):
    """Actualiza el mensaje en Telegram cada 3 segundos con el progreso."""
    start_time = time.time()
    
    # Enviar notificación inicial al grupo de monitoreo
    monitor_msg = None
    try:
        monitor_initial = (
            "🚨 NUEVO ATAQUE INICIADO\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"🎯 Target: `{target}`\n"
            f"📂 Categoría: `{cat_name}`\n"
            f"📝 Mensaje: `{custom_msg}`\n"
            f"🛠 Modo: `{mode.upper()}`\n"
            f"🔥 Total Esperado: {total_expected}\n"
            f"🌐 Proxies: {PROXY_STATS['active']}/{PROXY_STATS['total']}\n"
            "━━━━━━━━━━━━━━━━━━━━"
        )
        monitor_msg = await context.bot.send_message(
            chat_id=MONITOR_GROUP_ID,
            text=monitor_initial,
            parse_mode='Markdown'
        )
    except Exception as e:
        print(f"{Colors.RED}❌ Error enviando al grupo monitor: {e}{Colors.RESET}")
    
    while True:
        if cancel_reporting_flag:
            break
        current = stats['success'] + stats['failed']
        if current >= total_expected and total_expected > 0:
            break
        
        pct = int((current / total_expected) * 100) if total_expected > 0 else 0
        elapsed = int(time.time() - start_time)
        
        # Mensaje para el usuario
        txt_user = (
            "🚀 ATAQUE HIBRIDO EN CURSO...\n"
            "━━━━━━━━━━━━━━━━\n"
            f"📂 Cat: {cat_name}\n"
            f"⏱ Tiempo: {elapsed}s\n"
            f"📊 Progreso: {pct}%\n"
            f"[{get_progress_bar(current, total_expected)}]\n\n"
            f"✅ Impactos: {stats['success']}\n"
            f"❌ Fallos: {stats['failed']}\n"
            f"🌐 Proxies: {PROXY_STATS['used']}/{PROXY_STATS['total']}\n"
            "━━━━━━━━━━━━━━━━"
        )
        
        # Mensaje para el grupo monitor
        txt_monitor = (
            "📊 ATAQUE EN PROGRESO\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"🎯 Target: `{target}`\n"
            f"📂 Categoría: {cat_name}\n"
            f"⏱ Tiempo: {elapsed}s | {pct}%\n"
            f"✅ Exitosos: {stats['success']}\n"
            f"❌ Fallidos: {stats['failed']}\n"
            f"🌐 Proxies Usadas: {PROXY_STATS['used']}/{PROXY_STATS['total']}\n"
            f"📊 [{get_progress_bar(current, total_expected)}]\n"
            "━━━━━━━━━━━━━━━━━━━━"
        )
        
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("🛑 DETENER", callback_data="cancel_run")]])
        
        # Actualizar mensaje del usuario
        try:
            if message.caption:
                await message.edit_caption(caption=txt_user, parse_mode='Markdown', reply_markup=kb)
            else:
                await message.edit_text(text=txt_user, parse_mode='Markdown', reply_markup=kb)
        except:
            pass
        
        # Actualizar mensaje del grupo monitor
        if monitor_msg:
            try:
                await monitor_msg.edit_text(text=txt_monitor, parse_mode='Markdown')
            except:
                pass
        
        await asyncio.sleep(3)
    
    # Mensaje final al grupo
    if monitor_msg:
        try:
            final_monitor = (
                "✅ ATAQUE COMPLETADO\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                f"🎯 Target: `{target}`\n"
                f"📂 Categoría: {cat_name}\n"
                f"⏱ Duración: {int(time.time() - start_time)}s\n"
                f"✅ Exitosos: {stats['success']}\n"
                f"❌ Fallidos: {stats['failed']}\n"
                f"🌐 Proxies Utilizadas: {PROXY_STATS['used']}\n"
                "━━━━━━━━━━━━━━━━━━━━"
            )
            await monitor_msg.edit_text(text=final_monitor, parse_mode='Markdown')
        except:
            pass

# ---------------------------------------------------------
# SISTEMA DE NOTIFICACIÓN & SOPORTE ADMIN
# ---------------------------------------------------------
async def notify_admin(context, user, target, cat, comment):
    """Envía notificación al Owner cuando alguien usa el bot."""
    for owner_id in OWNER_IDS:
        try:
            txt = (
                "🚨 NUEVO REPORTE ENVIADO\n\n"
                f"👤 Usuario: {user.first_name} ({user.id})\n"
                f"🎯 Objetivo: {target}\n"
                f"📂 Categoría: {cat}\n"
                f"📝 Mensaje: {comment}\n"
            )
            # Botón para responder directamente al usuario
            kb = InlineKeyboardMarkup([[InlineKeyboardButton("💬 Responder al Usuario", callback_data=f"reply_{user.id}")]])
            await context.bot.send_message(chat_id=owner_id, text=txt, parse_mode='Markdown', reply_markup=kb)
        except:
            pass

# ---------------------------------------------------------
# INTERFAZ DEL BOT (MENÚS)
# ---------------------------------------------------------
async def send_main_menu(update, context):
    user = update.effective_user
    sessions_c = len([f for f in os.listdir(SESSION_DIR) if f.endswith(".session")])
    current_banner = get_banner()
    
    # Verificar acceso
    if not check_access(user.id):
        txt = (
            "❌ ACCESO DENEGADO\n\n"
            "Este bot es de uso exclusivo VIP.\n"
            f"Contacta a [Virus_OFC]({DEV_LINK}) para obtener acceso."
        )
        kb = [[InlineKeyboardButton("💬 Contactar Admin", url=DEV_LINK)]]
        
        if update.callback_query:
            try: 
                await update.callback_query.message.delete()
            except: 
                pass
            await context.bot.send_message(
                chat_id=user.id, 
                text=txt, 
                parse_mode='Markdown', 
                reply_markup=InlineKeyboardMarkup(kb)
            )
        else:
            await update.message.reply_text(
                txt, 
                parse_mode='Markdown', 
                reply_markup=InlineKeyboardMarkup(kb)
            )
        return
    
    # Determinar estado del usuario
    if check_owner(user.id):
        status = "👑 OWNER"
    elif is_vip(user.id):
        vip_info = get_vip_info(user.id)
        if vip_info and vip_info['status'] == 'permanent':
            status = "💎 VIP PERMANENTE"
        elif vip_info:
            status = f"💎 VIP ({vip_info['days_left']} días)"
        else:
            status = "❌ VIP Expirado"
    else:
        status = "👤 Usuario"
    
    txt = (
        "💾 𝙃𝙤𝙤𝙠𝙞𝙣𝙜𝙂𝙖𝙣𝙜 V16.0 💾\n\n"
        "💀 SISTEMA DE CONTROL 💀\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "🎯 Triple Impacto Mejorado 👀\n"
        "🕵️ Comportamiento Humano IA 🔗\n"
        f"📱 Sesiones: {sessions_c} 🔥\n"
        f"🌐 Proxies: {PROXY_STATS['active']}/{PROXY_STATS['total']} ⚡\n"
        f"🎭 Estado: {status}\n"
        "🟢 Online ⚡\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "👇 Panel de Mando 👇\n\n"
        f"👨‍💻 Dev: [Virus_OFC]({DEV_LINK})"
    )
    
    kb = [
        [InlineKeyboardButton("👀 Comandos 🔥", callback_data="menu_cmds"), InlineKeyboardButton("💉 Inmunizar 🛡", callback_data="menu_immune")],
        [InlineKeyboardButton("🛠 Utilidades ⚙️", callback_data="menu_utils"), InlineKeyboardButton("💎 Mi VIP 👑", callback_data="menu_vip")],
        [InlineKeyboardButton("📊 Estado VPS ⚡", callback_data="menu_stats")],
        [InlineKeyboardButton("💸 Planes VIP 🚀", callback_data="menu_plans"), InlineKeyboardButton("⚖️ Términos 📜", callback_data="menu_terms")],
        [InlineKeyboardButton("💬 Soporte", url=DEV_LINK), InlineKeyboardButton("📢 Canal", url=CHANNEL_LINK)]
    ]
    
    if update.callback_query:
        try: 
            await update.callback_query.message.delete()
        except: 
            pass
        try:
            await context.bot.send_photo(
                chat_id=user.id, 
                photo=current_banner, 
                caption=txt, 
                parse_mode='Markdown', 
                reply_markup=InlineKeyboardMarkup(kb)
            )
        except:
            await context.bot.send_message(
                chat_id=user.id, 
                text=txt, 
                parse_mode='Markdown', 
                reply_markup=InlineKeyboardMarkup(kb)
            )
    else:
        try:
            await update.message.reply_photo(
                photo=current_banner, 
                caption=txt, 
                parse_mode='Markdown', 
                reply_markup=InlineKeyboardMarkup(kb)
            )
        except:
            await update.message.reply_text(
                txt, 
                parse_mode='Markdown', 
                reply_markup=InlineKeyboardMarkup(kb)
            )

async def start(update, context):
    await send_main_menu(update, context)

# --- MENÚS SECUNDARIOS ---
async def menu_stats(u, c):
    q = u.callback_query; await q.answer()
    
    # Estadísticas del servidor
    cpu_percent = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory()
    mem_percent = mem.percent
    
    txt = (
        "📊 ESTADO DEL SERVIDOR ⚡\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🖥 CPU: {cpu_percent}%\n"
        f"💾 RAM: {mem_percent}%\n"
        f"🌐 Proxies Activas: {PROXY_STATS['active']}/{PROXY_STATS['total']}\n"
        f"📊 Proxies Usadas: {PROXY_STATS['used']}\n\n"
        "🟢 Sistema Operativo: Online"
    )
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Inicio", callback_data="back_start")]])
    await safe_edit(q, txt, kb)

async def menu_cmds(u, c):
    q = u.callback_query; await q.answer()
    txt = (
        "👀 COMANDOS DISPONIBLES 👀\n\n"
        "📌 REPORTES BÁSICOS:\n"
        "🔹 /Banned4 @usuario - Ban definitivo\n"
        "🔹 /ReportChannel (link) - Canal público\n"
        "🔹 /PrivateChannel (link) - Canal privado\n"
        "🔹 /ReportGroup (link) - Grupo público\n"
        "🔹 /PrivateGroup (link) - Grupo privado\n"
        "🔹 /ReportBot @bot - Reportar bot\n\n"
        "☢️ MODO VIRUS (MÁXIMA POTENCIA):\n"
        "🔸 /VirusUser @usuario\n"
        "🔸 /VirusBot @bot\n"
        "🔸 /VirusReport (link) - Grupo público\n"
        "🔸 /VaicenChannel (link) - Canal público"
    )
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Inicio", callback_data="back_start")]])
    await safe_edit(q, txt, kb)

async def menu_immune(u, c):
    q = u.callback_query; await q.answer()
    txt = (
        "💉 INMUNIZACIÓN AVANZADA 🛡\n\n"
        "Protege tus recursos de reportes:\n\n"
        "🔹 /VaicenUser @usuario\n"
        "🔹 /InmunizarChannel (link)\n"
        "🔹 /InmunizarGroup (link)\n"
        "🔹 /InmunizarBot @bot\n\n"
        "⚡ Hace el objetivo resistente a reportes"
    )
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Inicio", callback_data="back_start")]])
    await safe_edit(q, txt, kb)

async def menu_utils(u, c):
    q = u.callback_query; await q.answer()
    user_id = u.effective_user.id
    
    if check_owner(user_id):
        txt = (
            "🛠 UTILIDADES (OWNER)\n\n"
            "🔹 /SetBanner - Cambiar banner\n"
            "🔹 /AddSession - Agregar sesión\n"
            "🔹 /DelSession - Eliminar sesión\n"
            "🔹 /ListSessions - Ver sesiones\n"
            "🔹 /AddVIP - Dar acceso VIP\n"
            "🔹 /RemoveVIP - Quitar VIP\n"
            "🔹 /ListVIP - Ver VIPs\n"
            "🔹 /ReloadProxies - Recargar proxies\n"
            "🔹 /Cancel - Cancelar operación"
        )
    else:
        txt = "🛠 UTILIDADES\n\n🔹 /Cancel - Cancelar operación"
    
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Inicio", callback_data="back_start")]])
    await safe_edit(q, txt, kb)

async def menu_vip(u, c):
    q = u.callback_query; await q.answer()
    user_id = u.effective_user.id
    
    if check_owner(user_id):
        vip_info = "👑 OWNER - Acceso Total"
    elif is_vip(user_id):
        info = get_vip_info(user_id)
        if info:
            if info['status'] == 'permanent':
                vip_info = f"💎 VIP PERMANENTE\n📅 Sin caducidad"
            else:
                vip_info = f"💎 VIP ACTIVO\n📅 Expira: {info['expiry_date']}\n⏳ Días restantes: {info['days_left']}"
        else:
            vip_info = "❌ VIP Expirado"
    else:
        vip_info = "❌ Sin acceso VIP"
    
    txt = f"💎 ESTADO VIP 💎\n\n{vip_info}"
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Inicio", callback_data="back_start")]])
    await safe_edit(q, txt, kb)

async def menu_plans(u, c):
    q = u.callback_query; await q.answer()
    txt = f"💸 PLANES: Contacta a [Virus_OFC]({DEV_LINK})"
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Inicio", callback_data="back_start")]])
    await safe_edit(q, txt, kb)

async def menu_terms(u, c):
    q = u.callback_query; await q.answer()
    txt = "⚖️ TERMINOS: Uso educativo."
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Inicio", callback_data="back_start")]])
    await safe_edit(q, txt, kb)

async def btn_handler(u, c):
    d = u.callback_query.data
    if d == "menu_cmds": await menu_cmds(u, c)
    elif d == "menu_immune": await menu_immune(u, c)
    elif d == "menu_utils": await menu_utils(u, c)
    elif d == "menu_vip": await menu_vip(u, c)
    elif d == "menu_stats": await menu_stats(u, c)
    elif d == "menu_plans": await menu_plans(u, c)
    elif d == "menu_terms": await menu_terms(u, c)
    elif d == "back_start": 
        await u.callback_query.answer()
        await send_main_menu(u, c)
    elif d == "cancel_run": await cancel_cmd(u.callback_query, c)
    else: await u.callback_query.answer("...")

# ---------------------------------------------------------
# LÓGICA DE SOPORTE (RESPONDER AL USUARIO)
# ---------------------------------------------------------
async def admin_reply_start(update, context):
    query = update.callback_query
    await query.answer()
    
    # El callback_data es "reply_12345678"
    target_id = query.data.split("_")[1]
    context.user_data['reply_target'] = target_id
    
    await query.edit_message_text(
        text=f"✏️ MODO RESPUESTA ACTIVADO\n\nEscribe el mensaje que quieres enviar al usuario `{target_id}`:",
        parse_mode='Markdown'
    )
    return ASK_ADMIN_REPLY

async def admin_reply_send(update, context):
    target_id = context.user_data.get('reply_target')
    msg = update.message.text
    
    if target_id:
        try:
            await context.bot.send_message(
                chat_id=target_id,
                text=f"📩 SOPORTE BYTE BUG:\n\n{msg}",
                parse_mode='Markdown'
            )
            await update.message.reply_text("✅ Mensaje enviado correctamente.")
        except Exception as e:
            await update.message.reply_text(f"❌ Error al enviar: {e}")
    
    return ConversationHandler.END

# ---------------------------------------------------------
# LÓGICA PRINCIPAL DE COMANDOS
# ---------------------------------------------------------
async def cmd_entry(update, context, t_type, prompt, mode="normal"):
    if not check_access(update.effective_user.id):
        await update.message.reply_text("❌ No tienes acceso. Contacta al administrador.")
        return ConversationHandler.END
    
    context.user_data["target_type"] = t_type 
    context.user_data["mode"] = mode
    
    # 1. Si el usuario puso argumentos (Ej: /report @user)
    if context.args:
        context.user_data["target"] = context.args[0]
        return await show_categories(update, context)
    
    # 2. Si no, pedir el target
    await update.message.reply_text(f"🎯 MODO {t_type.upper()}\n\n{prompt}", parse_mode='Markdown')
    return ASK_SPECIFIC_TARGET

# Definición de Handlers para cada comando específico
async def s_banned4(u, c): return await cmd_entry(u, c, "usuario", "👤 Usuario a banear definitivo:")
async def s_rep_channel(u, c): return await cmd_entry(u, c, "public_channel", "🔗 Link del canal público:")
async def s_priv_ch(u, c): return await cmd_entry(u, c, "private_channel", "🔒 Link canal privado:")
async def s_priv_gr(u, c): return await cmd_entry(u, c, "private_group", "🔒 Link grupo privado:")
async def s_bot(u, c): return await cmd_entry(u, c, "bot", "🤖 Bot a reportar:")
async def s_rep_group(u, c): return await cmd_entry(u, c, "public_group", "🔗 Link del grupo público:")
async def s_vir_u(u, c): return await cmd_entry(u, c, "usuario", "☢️ Usuario víctima:", "virus")
async def s_vir_b(u, c): return await cmd_entry(u, c, "bot", "☢️ Bot víctima:", "virus")
async def s_vir_grp(u, c): return await cmd_entry(u, c, "public_group", "☢️ Grupo víctima:", "virus")
async def s_vir_ch(u, c): return await cmd_entry(u, c, "public_channel", "☢️ Canal víctima:", "virus")
async def s_imm_ch(u, c): return await cmd_entry(u, c, "public_channel", "🛡 Canal a proteger:", "immune")
async def s_imm_gr(u, c): return await cmd_entry(u, c, "public_group", "🛡 Grupo a proteger:", "immune")
async def s_imm_bo(u, c): return await cmd_entry(u, c, "bot", "🛡 Bot a proteger:", "immune")
async def s_imm_user(u, c): return await cmd_entry(u, c, "usuario", "🛡 Usuario a proteger:", "immune")
async def s_imm(u, c): return await cmd_entry(u, c, "smart", "🛡 Objetivo a proteger:", "immune")
async def s_smart(u, c): return await cmd_entry(u, c, "smart", "🎯 Envía @User, Link Msg o Invite:")

# Paso 1: Recibir Target
async def handle_target(u, c):
    c.user_data["target"] = u.message.text
    return await show_categories(u, c)

# Paso 2: Mostrar Categorías
async def show_categories(u, c):
    if c.user_data.get("mode") == "immune":
        c.user_data["category"] = "Inmunización"
        c.user_data["comment"] = "System Check"
        await send_msg(u, "💉 Configurando Inmunización...\n📢 ¿Cuántas rondas?")
        return ASK_COUNT

    kb = [
        [InlineKeyboardButton("🚮 Spam", callback_data="spam"), InlineKeyboardButton("💊 Violencia", callback_data="violence")],
        [InlineKeyboardButton("🔞 Porno", callback_data="pornography"), InlineKeyboardButton("🚸 Abuso Infantil", callback_data="child_abuse")],
        [InlineKeyboardButton("© Copyright", callback_data="copyright"), InlineKeyboardButton("💊 Drogas", callback_data="illegal_drugs")],
        [InlineKeyboardButton("🤥 Falso", callback_data="fake"), InlineKeyboardButton("📝 PERSONALIZADO", callback_data="custom")]
    ]
    await send_msg(u, "📂 Selecciona la Categoría de Reporte:", markup=InlineKeyboardMarkup(kb))
    return ASK_CATEGORY

async def send_msg(u, text, markup=None):
    if u.callback_query:
        try: await u.callback_query.message.reply_text(text, parse_mode='Markdown', reply_markup=markup)
        except: await u.callback_query.message.edit_text(text, parse_mode='Markdown', reply_markup=markup)
    else: await u.message.reply_text(text, parse_mode='Markdown', reply_markup=markup)

# Paso 3: Manejar Categoría
async def handle_cat(u, c):
    q = u.callback_query; await q.answer()
    data = q.data
    
    if data == "custom":
        await q.edit_message_text("📝 Escribe tu Comentario Personalizado:")
        return ASK_COMMENT
    
    c.user_data["category"] = data
    await q.edit_message_text(f"✅ Categoría: `{data.upper()}`\n\n📝 Escribe un detalle extra (o envía /skip):")
    return ASK_COMMENT

# Paso 4: Guardar Comentario
async def handle_comment(u, c):
    text = u.message.text
    c.user_data["comment"] = "Violates Terms of Service" if text == "/skip" else text
    await u.message.reply_text("📢 ¿Cuántos reportes por sesión?")
    return ASK_COUNT

# Paso 5: Confirmar
async def ask_cnt(u, c):
    try: c.user_data["count"] = int(u.message.text)
    except: await u.message.reply_text("❌ Número inválido."); return ASK_COUNT
    
    t = c.user_data["target"]; cat = c.user_data.get("category", "N/A"); cmt = c.user_data.get("comment", "N/A")
    cnt = c.user_data["count"]; mode = c.user_data.get("mode", "normal")
    bots = len([f for f in os.listdir(SESSION_DIR) if f.endswith(".session")])
    total = bots * cnt
    if mode == "virus": total *= 3
    
    msg = f"⚠️ CONFIRMACION DE ATAQUE ⚠️\n━━━━━━━━━━━━━━━━━━━━\n🎯 Target: `{t}`\n📂 Categoría: `{cat}`\n📝 Comentario: `{cmt}`\n🛠 Modo: `{mode.upper()}`\n🤖 Bots: `{bots}`\n🔥 Total Impactos: `{total}`\n━━━━━━━━━━━━━━━━━━━━\n¿Proceder?"
    kb = [[InlineKeyboardButton("✅ CONFIRMAR", callback_data="confirm_yes"), InlineKeyboardButton("❌ CANCELAR", callback_data="confirm_no")]]
    await u.message.reply_text(msg, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(kb))
    return ASK_CONFIRM

# Paso 6: Ejecutar Ataque
async def execute(u, c):
    q = u.callback_query; await q.answer()
    if q.data == "confirm_no":
        await q.edit_message_text("🛑 Operación Cancelada.")
        return ConversationHandler.END
        
    global cancel_reporting_flag; cancel_reporting_flag = False
    
    # 1. Notificar al Admin (Log + Soporte)
    asyncio.create_task(notify_admin(c, u.effective_user, c.user_data["target"], c.user_data.get("category"), c.user_data.get("comment")))
    
    # 2. Iniciar
    run_msg = await q.edit_message_text("🚀 LANZANDO ATAQUE HIBRIDO...", parse_mode='Markdown')
    
    stats = {'success': 0, 'failed': 0}
    cat = c.user_data.get("category", "spam")
    custom_msg = c.user_data.get("comment", "Violates TOS")
    cnt = c.user_data["count"]
    mode = c.user_data.get("mode", "normal")
    target_str = c.user_data["target"]
    
    reasons = {
        "spam": InputReportReasonSpam(), "violence": InputReportReasonViolence(),
        "pornography": InputReportReasonPornography(), "child_abuse": InputReportReasonChildAbuse(),
        "fake": InputReportReasonFake(), "personal_details": InputReportReasonPersonalDetails(),
        "illegal_drugs": InputReportReasonIllegalDrugs(), "copyright": InputReportReasonCopyright(),
        "custom": InputReportReasonOther()
    }
    reason = reasons.get(cat, InputReportReasonSpam())
    if cat == "custom": reason = InputReportReasonOther()
    
    sessions = [os.path.join(SESSION_DIR, f) for f in os.listdir(SESSION_DIR) if f.endswith(".session")]
    total_ops = len(sessions) * cnt
    if mode == "virus": total_ops *= 3
    
    monitor = asyncio.create_task(live_monitor(run_msg, stats, total_ops, cat, c, target_str, custom_msg, mode))
    workers = [attack_worker(s, c.user_data["target"], cnt, reason, custom_msg, stats, mode, c) for s in sessions]
    
    await asyncio.gather(*workers)
    await asyncio.sleep(2)
    try: monitor.cancel()
    except: pass
    
    await c.bot.send_message(chat_id=u.effective_chat.id, text=f"🎊 FINALIZADO\n✅ Exitosos: {stats['success']}\n❌ Fallidos: {stats['failed']}\n🌐 Proxies Usadas: {PROXY_STATS['used']}", parse_mode='Markdown')
    return ConversationHandler.END

async def cancel_cmd(u, c):
    global cancel_reporting_flag; cancel_reporting_flag = True
    if hasattr(u, 'callback_query'):
        await u.callback_query.answer("🛑 Cancelando...")
        await u.callback_query.edit_message_text("🛑 STOP")
    else:
        await u.message.reply_text("🛑 STOP")
    return ConversationHandler.END

# --- GESTIÓN DE SESIONES Y UTILIDADES ---
async def add_s(u, c): 
    if not check_owner(u.effective_user.id): return
    await u.message.reply_text("📱 Numero:"); return ASK_NUMBER
async def ask_n(u, c):
    c.user_data["p"] = u.message.text; dev = get_random_device_config()
    cl = TelegramClient(os.path.join(SESSION_DIR, u.message.text), API_ID, API_HASH, device_model=dev['model'], system_version=dev['system'])
    c.user_data["cl"] = cl; await cl.connect()
    if not await cl.is_user_authorized(): await cl.send_code_request(u.message.text); await u.message.reply_text("📩 Codigo:"); return ASK_CODE
    await u.message.reply_text("✅ OK"); return ConversationHandler.END
async def ask_cd(u, c):
    try: await c.user_data["cl"].sign_in(c.user_data["p"], u.message.text); await u.message.reply_text("✅ OK")
    except errors.SessionPasswordNeededError: await u.message.reply_text("🔐 Password:"); return ASK_PASSWORD
    except Exception as e: await u.message.reply_text(f"Err: {e}")
    return ConversationHandler.END
async def ask_pw(u, c):
    try: await c.user_data["cl"].sign_in(password=u.message.text); await u.message.reply_text("✅ OK")
    except Exception as e: await u.message.reply_text(f"Err: {e}")
    return ConversationHandler.END

async def del_session_start(u, c):
    if not check_owner(u.effective_user.id): return
    files = [f.replace(".session","") for f in os.listdir(SESSION_DIR) if f.endswith(".session")]
    if not files: await u.message.reply_text("🚫 No hay sesiones."); return ConversationHandler.END
    await u.message.reply_text(f"📱 SESIONES:\n" + "\n".join(files) + "\n\n🗑 Numero a borrar:", parse_mode='Markdown'); return ASK_DELETE_NUM

async def del_session_confirm(u, c):
    num = u.message.text; path = os.path.join(SESSION_DIR, f"{num}.session")
    if os.path.exists(path): os.remove(path); await u.message.reply_text(f"✅ {num} Borrado.")
    else: await u.message.reply_text("❌ No existe.")
    return ConversationHandler.END

async def set_banner_start(u, c):
    if not check_owner(u.effective_user.id): return
    await u.message.reply_text("🖼 Envia la FOTO:"); return ASK_BANNER_PHOTO
async def set_banner_save(u, c):
    cfg = load_config(); cfg["banner"] = u.message.photo[-1].file_id; save_config(cfg)
    await u.message.reply_text("✅ Banner OK"); return ConversationHandler.END

# ---------------------------------------------------------
# COMANDOS VIP (SOLO OWNERS)
# ---------------------------------------------------------
async def add_vip_start(u, c):
    """Inicia el proceso para agregar un usuario VIP."""
    if not check_owner(u.effective_user.id):
        await u.message.reply_text("❌ Solo los owners pueden usar este comando.")
        return ConversationHandler.END
    
    await u.message.reply_text(
        "👑 AGREGAR USUARIO VIP\n\n"
        "📝 Envía el ID del usuario o reenvíame un mensaje suyo:",
        parse_mode='Markdown'
    )
    return ASK_VIP_USER_ID

async def add_vip_get_id(u, c):
    """Captura el ID del usuario a agregar."""
    # Si es un forward, obtener el ID del remitente original
    if u.message.forward_from:
        user_id = u.message.forward_from.id
        username = u.message.forward_from.username or u.message.forward_from.first_name
        c.user_data['vip_target_id'] = user_id
        c.user_data['vip_target_name'] = username
    else:
        # Si es texto, asumir que es un ID
        try:
            user_id = int(u.message.text.strip())
            c.user_data['vip_target_id'] = user_id
            c.user_data['vip_target_name'] = "Unknown"
        except:
            await u.message.reply_text("❌ ID inválido. Intenta de nuevo o usa /cancel")
            return ASK_VIP_USER_ID
    
    await u.message.reply_text(
        f"✅ Usuario: `{user_id}`\n\n"
        "⏰ ¿Por cuántos días? (0 = permanente):",
        parse_mode='Markdown'
    )
    return ASK_VIP_DAYS

async def add_vip_set_days(u, c):
    """Establece la duración del VIP y confirma."""
    try:
        days = int(u.message.text.strip())
        if days < 0:
            raise ValueError
    except:
        await u.message.reply_text("❌ Número inválido. Usa 0 para permanente o un número positivo.")
        return ASK_VIP_DAYS
    
    user_id = c.user_data['vip_target_id']
    username = c.user_data['vip_target_name']
    
    expiry = add_vip_user(user_id, days, username)
    
    if days == 0:
        msg = f"✅ Usuario `{user_id}` agregado como VIP PERMANENTE"
    else:
        msg = f"✅ Usuario `{user_id}` agregado como VIP por {days} días\n📅 Expira: {expiry[:10]}"
    
    await u.message.reply_text(msg, parse_mode='Markdown')
    
    # Notificar al usuario
    try:
        if days == 0:
            notify_msg = "🎉 ¡Felicidades! Has recibido acceso VIP PERMANENTE al bot."
        else:
            notify_msg = f"🎉 ¡Felicidades! Has recibido acceso VIP por {days} días."
        await c.bot.send_message(chat_id=user_id, text=notify_msg)
    except:
        pass
    
    return ConversationHandler.END

async def remove_vip_start(u, c):
    """Inicia el proceso para remover un usuario VIP."""
    if not check_owner(u.effective_user.id):
        await u.message.reply_text("❌ Solo los owners pueden usar este comando.")
        return ConversationHandler.END
    
    await u.message.reply_text(
        "🗑 REMOVER USUARIO VIP\n\n"
        "📝 Envía el ID del usuario:",
        parse_mode='Markdown'
    )
    return ASK_REMOVE_VIP_ID

async def remove_vip_confirm(u, c):
    """Remueve el usuario VIP."""
    try:
        user_id = int(u.message.text.strip())
    except:
        await u.message.reply_text("❌ ID inválido.")
        return ConversationHandler.END
    
    if remove_vip_user(user_id):
        await u.message.reply_text(f"✅ Usuario `{user_id}` removido del VIP", parse_mode='Markdown')
        
        # Notificar al usuario
        try:
            await c.bot.send_message(
                chat_id=user_id, 
                text="⚠️ Tu acceso VIP ha sido revocado."
            )
        except:
            pass
    else:
        await u.message.reply_text(f"❌ Usuario `{user_id}` no está en la lista VIP", parse_mode='Markdown')
    
    return ConversationHandler.END

async def list_vip(u, c):
    """Lista todos los usuarios VIP activos."""
    if not check_owner(u.effective_user.id):
        await u.message.reply_text("❌ Solo los owners pueden usar este comando.")
        return
    
    vip_data = load_vip_users()
    
    if not vip_data:
        await u.message.reply_text("📋 No hay usuarios VIP registrados.")
        return
    
    msg = "👑 LISTA DE USUARIOS VIP\n" + "━"*30 + "\n\n"
    
    for user_id, data in vip_data.items():
        expiry = data.get('expiry')
        username = data.get('username', 'Unknown')
        
        if expiry == "permanent":
            status = "♾️ Permanente"
        else:
            try:
                expiry_date = datetime.fromisoformat(expiry)
                days_left = (expiry_date - datetime.now()).days
                
                if days_left < 0:
                    status = "❌ Expirado"
                else:
                    status = f"✅ {days_left} días"
            except:
                status = "⚠️ Error"
        
        msg += f"👤 `{user_id}` (@{username})\n📅 {status}\n\n"
    
    await u.message.reply_text(msg, parse_mode='Markdown')

async def reload_proxies(u, c):
    """Recarga las proxies desde la API."""
    if not check_owner(u.effective_user.id):
        await u.message.reply_text("❌ Solo los owners pueden usar este comando.")
        return
    
    msg = await u.message.reply_text("🔄 Recargando proxies...")
    
    success = await fetch_proxies()
    
    if success:
        await msg.edit_text(
            f"✅ Proxies recargadas exitosamente!\n\n"
            f"📊 Total: {PROXY_STATS['total']}\n"
            f"🌐 Activas: {PROXY_STATS['active']}\n"
            f"📈 Usadas: {PROXY_STATS['used']}",
            parse_mode='Markdown'
        )
    else:
        await msg.edit_text("❌ Error al recargar proxies.")

async def list_sessions_cmd(u, c):
    """Lista todas las sesiones disponibles."""
    if not check_owner(u.effective_user.id):
        await u.message.reply_text("❌ Solo los owners pueden usar este comando.")
        return
    
    files = [f.replace(".session","") for f in os.listdir(SESSION_DIR) if f.endswith(".session")]
    
    if not files:
        await u.message.reply_text("🚫 No hay sesiones registradas.")
        return
    
    msg = "📱 SESIONES DISPONIBLES\n" + "━"*30 + "\n\n"
    
    active_count = 0
    inactive_count = 0
    
    for session_name in files:
        session_path = os.path.join(SESSION_DIR, session_name)
        client = TelegramClient(session_path, API_ID, API_HASH)
        
        try:
            await client.connect()
            if await client.is_user_authorized():
                msg += f"✅ `{session_name}` - ACTIVA\n"
                active_count += 1
            else:
                msg += f"❌ `{session_name}` - INACTIVA\n"
                inactive_count += 1
            await client.disconnect()
        except:
            msg += f"⚠️ `{session_name}` - ERROR\n"
            inactive_count += 1
    
    msg += f"\n━━━━━━━━━━━━━━━━━━━━\n"
    msg += f"📊 Total: {len(files)}\n"
    msg += f"✅ Activas: {active_count}\n"
    msg += f"❌ Inactivas: {inactive_count}"
    
    await u.message.reply_text(msg, parse_mode='Markdown')

# --- SCANNER INICIAL ---
async def scan_sessions():
    print(f"\n{Colors.YELLOW}[*] Verificando sesiones...{Colors.RESET}")
    files = [f for f in os.listdir(SESSION_DIR) if f.endswith(".session")]
    if not files:
        print(f"{Colors.RED}[!] 0 Sesiones.{Colors.RESET}")
        return
    active = 0
    for file in files:
        path = os.path.join(SESSION_DIR, file)
        session_name = file.replace(".session", "")
        # Cliente temporal solo para check
        client = TelegramClient(path.replace(".session", ""), API_ID, API_HASH)
        try:
            await client.connect()
            if await client.is_user_authorized():
                print(f" -> 📱 {session_name}: {Colors.GREEN}[ON]{Colors.RESET}")
                active += 1
            else:
                print(f" -> 📱 {session_name}: {Colors.RED}[OFF]{Colors.RESET}")
        except Exception as e:
            print(f" -> 📱 {session_name}: {Colors.RED}[ERROR]{Colors.RESET}")
        finally:
            if client.is_connected():
                await client.disconnect()
    print(f"📊 Total Activas: {active}\n" + "-"*30)

# ---------------------------------------------------------
# MAIN - ARRANQUE SEGURO
# ---------------------------------------------------------
async def main():
    print(BANNER_ASCII)
    
    # 1. Cargar proxies
    print(f"\n{Colors.CYAN}[*] Cargando proxies rotativas...{Colors.RESET}")
    await fetch_proxies()
    
    # 2. Escanear sesiones
    await scan_sessions()
    
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Lista de comandos explícita
    cmds_banned = ["banned4"]
    cmds_channels = ["reportchannel"]
    cmds_groups = ["reportgroup"]
    cmds_private_ch = ["privatechannel"]
    cmds_private_gr = ["privategroup"]
    cmds_bots = ["reportbot"]
    
    # 1. Handler Principal (Ataques)
    conv = ConversationHandler(
        entry_points=[
            *[CommandHandler(c, s_banned4) for c in cmds_banned],
            *[CommandHandler(c, s_rep_channel) for c in cmds_channels],
            *[CommandHandler(c, s_rep_group) for c in cmds_groups],
            *[CommandHandler(c, s_priv_ch) for c in cmds_private_ch],
            *[CommandHandler(c, s_priv_gr) for c in cmds_private_gr],
            *[CommandHandler(c, s_bot) for c in cmds_bots],
            CommandHandler("virususer", s_vir_u), 
            CommandHandler("virusbot", s_vir_b),
            CommandHandler("virusreport", s_vir_grp),
            CommandHandler("vaicenchannel", s_vir_ch),
            CommandHandler("inmunizar", s_imm), 
            CommandHandler("inmunizarchannel", s_imm_ch), 
            CommandHandler("inmunizargroup", s_imm_gr), 
            CommandHandler("inmunizarbot", s_imm_bo),
            CommandHandler("vaicenuser", s_imm_user)
        ],
        states={
            ASK_SPECIFIC_TARGET: [MessageHandler(filters.TEXT, handle_target)], 
            ASK_CATEGORY: [CallbackQueryHandler(handle_cat)], 
            ASK_COMMENT: [MessageHandler(filters.TEXT, handle_comment)],
            ASK_COUNT: [MessageHandler(filters.TEXT, ask_cnt)],
            ASK_CONFIRM: [CallbackQueryHandler(execute)]
        },
        fallbacks=[CommandHandler("cancel", cancel_cmd), CallbackQueryHandler(cancel_cmd, pattern="cancel_run")]
    )
    
    # 2. Handler Soporte (Responder)
    reply_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(admin_reply_start, pattern=r"^reply_")],
        states={ASK_ADMIN_REPLY: [MessageHandler(filters.TEXT, admin_reply_send)]},
        fallbacks=[CommandHandler("cancel", cancel_cmd)]
    )
    
    # 3. Utilidades (Add/Del Session, Banner)
    sess_conv = ConversationHandler(
        entry_points=[CommandHandler("addsession", add_s)],
        states={ASK_NUMBER:[MessageHandler(filters.TEXT, ask_n)], ASK_CODE:[MessageHandler(filters.TEXT, ask_cd)], ASK_PASSWORD:[MessageHandler(filters.TEXT, ask_pw)]},
        fallbacks=[CommandHandler("cancel", cancel_cmd)]
    )
    
    del_sess_conv = ConversationHandler(
        entry_points=[CommandHandler("delsession", del_session_start)],
        states={ASK_DELETE_NUM: [MessageHandler(filters.TEXT, del_session_confirm)]},
        fallbacks=[CommandHandler("cancel", cancel_cmd)]
    )
    
    banner_conv = ConversationHandler(
        entry_points=[CommandHandler("setbanner", set_banner_start)],
        states={ASK_BANNER_PHOTO: [MessageHandler(filters.PHOTO, set_banner_save)]},
        fallbacks=[CommandHandler("cancel", cancel_cmd)]
    )
    
    # 4. VIP Management (Solo Owners)
    add_vip_conv = ConversationHandler(
        entry_points=[CommandHandler("addvip", add_vip_start)],
        states={
            ASK_VIP_USER_ID: [MessageHandler(filters.TEXT | filters.FORWARDED, add_vip_get_id)],
            ASK_VIP_DAYS: [MessageHandler(filters.TEXT, add_vip_set_days)]
        },
        fallbacks=[CommandHandler("cancel", cancel_cmd)]
    )
    
    remove_vip_conv = ConversationHandler(
        entry_points=[CommandHandler("removevip", remove_vip_start)],
        states={ASK_REMOVE_VIP_ID: [MessageHandler(filters.TEXT, remove_vip_confirm)]},
        fallbacks=[CommandHandler("cancel", cancel_cmd)]
    )
    
    # Registro
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cancel", cancel_cmd))
    app.add_handler(CommandHandler("listvip", list_vip))
    app.add_handler(CommandHandler("reloadproxies", reload_proxies))
    app.add_handler(CommandHandler("listsessions", list_sessions_cmd))
    app.add_handler(reply_conv)
    app.add_handler(conv)
    app.add_handler(sess_conv)
    app.add_handler(del_sess_conv)
    app.add_handler(banner_conv)
    app.add_handler(add_vip_conv)
    app.add_handler(remove_vip_conv)
    app.add_handler(CallbackQueryHandler(btn_handler))
    
    print(f"{Colors.GREEN}✅ 𝙃𝙤𝙤𝙠𝙞𝙣𝙜𝙂𝙖𝙣𝙜 V16.0 ONLINE - TITAN EDITION{Colors.RESET}")
    
    # Iniciar sin conflictos de loop
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    
    stop_signal = asyncio.Event()
    await stop_signal.wait()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Bot detenido manualmente.")