# utils.py - Funciones auxiliares

import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import streamlit as st

def cargar_preguntas(archivo: str = "datos_quiz.json") -> List[Dict]:
    """Carga las preguntas desde el archivo JSON"""
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error(f"❌ No se encontró el archivo {archivo}")
        return []
    except json.JSONDecodeError:
        st.error(f"❌ Error al leer el archivo {archivo}")
        return []

def seleccionar_preguntas(
    todas_preguntas: List[Dict], 
    cantidad: int = 100, 
    categoria: str = None,
    modo: str = "examen"
) -> List[Dict]:
    """
    Selecciona preguntas según el modo y categoría
    """
    preguntas_filtradas = todas_preguntas.copy()
    
    # Filtrar por categoría si se especifica
    if categoria and categoria != "todas":
        preguntas_filtradas = [
            p for p in preguntas_filtradas 
            if p.get("categoria", "general") == categoria
        ]
    
    # Si no hay suficientes preguntas, usar todas las disponibles
    cantidad_final = min(cantidad, len(preguntas_filtradas))
    
    # Randomizar
    return random.sample(preguntas_filtradas, cantidad_final)

def calcular_estadisticas(respuestas: List[Dict]) -> Dict:
    """
    Calcula estadísticas detalladas del simulacro
    """
    total = len(respuestas)
    if total == 0:
        return {}
    
    correctas = sum(1 for r in respuestas if r['correcta'])
    incorrectas = total - correctas
    porcentaje = (correctas / total) * 100
    
    # Estadísticas por categoría
    stats_categoria = {}
    for r in respuestas:
        cat = r.get('categoria', 'general')
        if cat not in stats_categoria:
            stats_categoria[cat] = {'total': 0, 'correctas': 0}
        stats_categoria[cat]['total'] += 1
        if r['correcta']:
            stats_categoria[cat]['correctas'] += 1
    
    # Calcular porcentaje por categoría
    for cat in stats_categoria:
        total_cat = stats_categoria[cat]['total']
        correctas_cat = stats_categoria[cat]['correctas']
        stats_categoria[cat]['porcentaje'] = (correctas_cat / total_cat) * 100
    
    return {
        'total': total,
        'correctas': correctas,
        'incorrectas': incorrectas,
        'porcentaje': porcentaje,
        'aprobado': porcentaje >= 80,
        'por_categoria': stats_categoria
    }

def formatear_tiempo(segundos: int) -> str:
    """Formatea segundos en formato HH:MM:SS"""
    horas = segundos // 3600
    minutos = (segundos % 3600) // 60
    segs = segundos % 60
    
    if horas > 0:
        return f"{horas:02d}:{minutos:02d}:{segs:02d}"
    else:
        return f"{minutos:02d}:{segs:02d}"

def generar_reporte_texto(stats: Dict, respuestas: List[Dict]) -> str:
    """Genera un reporte en texto plano para descargar"""
    reporte = f"""
========================================
REPORTE DE SIMULACRO PPA - ANAC
========================================
Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}

RESULTADO GENERAL
-----------------
Total de preguntas: {stats['total']}
Respuestas correctas: {stats['correctas']}
Respuestas incorrectas: {stats['incorrectas']}
Porcentaje: {stats['porcentaje']:.1f}%
Estado: {'✅ APROBADO' if stats['aprobado'] else '❌ DESAPROBADO'}

RESULTADOS POR CATEGORÍA
--------------------------
"""
    
    for cat, data in stats['por_categoria'].items():
        reporte += f"\n{cat.upper()}\n"
        reporte += f"  Correctas: {data['correctas']}/{data['total']} ({data['porcentaje']:.1f}%)\n"
    
    reporte += "\n\nPREGUNTAS INCORRECTAS\n"
    reporte += "=====================\n\n"
    
    for idx, r in enumerate(respuestas):
        if not r['correcta']:
            reporte += f"Pregunta {idx + 1}:\n"
            reporte += f"  {r['pregunta']}\n"
            reporte += f"  Tu respuesta: {r['respuesta_usuario']}\n"
            reporte += f"  Respuesta correcta: {r['respuesta_correcta']}\n"
            if r.get('explicacion'):
                reporte += f"  Explicación: {r['explicacion']}\n"
            reporte += "\n"
    
    return reporte

def detectar_categoria_automatica(pregunta_texto: str) -> str:
    """
    Intenta detectar la categoría de una pregunta basándose en palabras clave
    """
    pregunta_lower = pregunta_texto.lower()
    
    # Palabras clave por categoría
    keywords = {
        "motor": ["motor", "cilindro", "pistón", "magneto", "carburador", "mezcla", "otto", 
                  "combustión", "rpm", "aceite", "filtro", "válvula"],
        "navegacion": ["vor", "rumbo", "adf", "gps", "carta", "ruta", "navegación", "posición",
                       "radial", "dme", "estación", "compass"],
        "meteorologia": ["nube", "viento", "presión", "altitud", "temperatura", "frente",
                        "meteorología", "clima", "precipitación", "visibilidad", "metar", "taf"],
        "regulaciones": ["raac", "licencia", "habilitación", "reglamento", "certificado",
                        "anac", "circular", "normativa", "horas de vuelo"],
        "aerodinamica": ["ala", "sustentación", "perfil", "ángulo de ataque", "capa límite",
                        "resistencia", "sustentación", "flap", "pérdida"],
        "operaciones": ["despegue", "aterrizaje", "circuito", "aproximación", "emergencia",
                       "pista", "performance", "peso", "centro de gravedad"],
        "comunicaciones": ["frecuencia", "radio", "comunicación", "torre", "control",
                          "transponder", "atc", "fraseología"],
        "performance": ["alcance", "autonomía", "velocidad", "distancia", "consumo",
                       "performance", "peso máximo", "techo"]
    }
    
    # Contar coincidencias por categoría
    scores = {}
    for cat, words in keywords.items():
        scores[cat] = sum(1 for word in words if word in pregunta_lower)
    
    # Devolver la categoría con más coincidencias, o "general" si no hay coincidencias
    if max(scores.values()) > 0:
        return max(scores, key=scores.get)
    return "general"

def migrar_preguntas_con_categorias(archivo_entrada: str, archivo_salida: str):
    """
    Migra el archivo de preguntas antiguo agregando categorías automáticamente
    """
    preguntas = cargar_preguntas(archivo_entrada)
    
    for pregunta in preguntas:
        if 'categoria' not in pregunta:
            pregunta['categoria'] = detectar_categoria_automatica(pregunta['pregunta'])
        
        # Agregar campo de explicación vacío si no existe
        if 'explicacion' not in pregunta:
            pregunta['explicacion'] = ""
    
    with open(archivo_salida, 'w', encoding='utf-8') as f:
        json.dump(preguntas, f, ensure_ascii=False, indent=2)
    
    return preguntas
