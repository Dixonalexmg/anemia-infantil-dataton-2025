import requests
from datetime import datetime

def enviar_menu_whatsapp(telefono, menu, es_semanal=False):
    """Envía menú por WhatsApp (simulado o real con API)"""
    try:
        # OPCIÓN 1: WhatsApp Business API (requiere configuración)
        # url = "https://graph.facebook.com/v18.0/YOUR_PHONE_ID/messages"
        # headers = {"Authorization": "Bearer YOUR_TOKEN"}
        
        # OPCIÓN 2: Twilio WhatsApp
        # from twilio.rest import Client
        # client = Client(account_sid, auth_token)
        
        # SIMULACIÓN PARA MVP
        mensaje = _generar_mensaje_whatsapp(menu, es_semanal)
        
        # Log del envío
        with open("data/logs/whatsapp_envios.txt", "a", encoding="utf-8") as f:
            f.write(f"{datetime.now()} | {telefono} | {mensaje[:50]}...\n")
        
        return {"exito": True, "mensaje": "Enviado (simulado)"}
    
    except Exception as e:
        return {"exito": False, "mensaje": str(e)}

def _generar_mensaje_whatsapp(menu, es_semanal):
    """Genera texto del mensaje"""
    if es_semanal:
        texto = "🗓️ *MENÚ SEMANAL NUTRISENSEIA*\n\n"
        for dia in menu:
            texto += f"*{dia['dia']}*\n"
            texto += f"🍳 {dia['desayuno']['nombre']}\n"
            texto += f"🍲 {dia['almuerzo']['nombre']}\n"
            texto += f"🌙 {dia['cena']['nombre']}\n\n"
    else:
        texto = f"🍽️ *{menu['nombre']}*\n\n"
        texto += f"📋 *Ingredientes:*\n"
        for ing in menu['ingredientes']:
            texto += f"• {ing['cantidad_g']}g {ing['id']}\n"
        texto += f"\n🍳 *Preparación:*\n{menu['preparacion']}"
    
    return texto
