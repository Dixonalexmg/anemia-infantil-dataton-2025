from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from datetime import datetime
import os

def generar_pdf_menu(menu, filename=None):
    """Genera PDF de un menú individual"""
    if not filename:
        filename = f"data/pdfs/menu_{menu['id']}_{datetime.now().strftime('%Y%m%d')}.pdf"
    
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    c = canvas.Canvas(filename, pagesize=letter)
    y = 750
    
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, f"MENÚ: {menu['nombre']}")
    y -= 30
    
    c.setFont("Helvetica", 12)
    c.drawString(50, y, f"Tipo: {menu['tipo'].title()} | Plato: {menu['plato_principal']}")
    y -= 40
    
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Ingredientes:")
    y -= 20
    
    c.setFont("Helvetica", 11)
    for ing in menu['ingredientes']:
        c.drawString(70, y, f"• {ing['cantidad_g']}g de {ing['id']}")
        y -= 18
    
    y -= 10
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Preparación:")
    y -= 20
    
    c.setFont("Helvetica", 11)
    texto = menu['preparacion']
    for linea in [texto[i:i+80] for i in range(0, len(texto), 80)]:
        c.drawString(70, y, linea)
        y -= 18
    
    c.save()
    return filename

def generar_pdf_semanal(menus_semana, filename="data/pdfs/menu_semanal.pdf"):
    """Genera PDF del menú semanal"""
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    c = canvas.Canvas(filename, pagesize=letter)
    y = 750
    
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, y, "MENÚ SEMANAL PERSONALIZADO")
    y -= 40
    
    for dia_menu in menus_semana:
        if y < 100:
            c.showPage()
            y = 750
        
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y, dia_menu['dia'])
        y -= 20
        
        c.setFont("Helvetica", 11)
        c.drawString(70, y, f"Desayuno: {dia_menu['desayuno']['nombre']}")
        y -= 18
        c.drawString(70, y, f"Almuerzo: {dia_menu['almuerzo']['nombre']}")
        y -= 18
        c.drawString(70, y, f"Cena: {dia_menu['cena']['nombre']}")
        y -= 30
    
    c.save()
    return filename
