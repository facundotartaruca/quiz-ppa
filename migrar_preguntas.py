#!/usr/bin/env python3
"""
Script de migración de preguntas
Agrega categorías automáticas y campo de explicación a las preguntas existentes
"""

import json
import sys

def detectar_categoria(pregunta_texto):
    """Detecta la categoría de una pregunta basándose en palabras clave"""
    pregunta_lower = pregunta_texto.lower()
    
    # Palabras clave por categoría
    keywords = {
        "motor": ["motor", "cilindro", "pistón", "magneto", "carburador", "mezcla", "otto", 
                  "combustión", "rpm", "aceite", "filtro", "válvula", "bujía", "alternador"],
        "navegacion": ["vor", "rumbo", "adf", "gps", "carta", "ruta", "navegación", "posición",
                       "radial", "dme", "estación", "compass", "brújula", "norte magnético"],
        "meteorologia": ["nube", "viento", "presión", "altitud de densidad", "temperatura", "frente",
                        "meteorología", "clima", "precipitación", "visibilidad", "metar", "taf",
                        "niebla", "turbulencia", "altímetro"],
        "regulaciones": ["raac", "licencia", "habilitación", "reglamento", "certificado",
                        "anac", "circular", "normativa", "horas de vuelo", "piloto privado",
                        "readaptado", "instructor", "pasajeros"],
        "aerodinamica": ["ala", "sustentación", "perfil", "ángulo de ataque", "capa límite",
                        "resistencia", "flap", "pérdida", "envergadura", "slat"],
        "operaciones": ["despegue", "aterrizaje", "circuito", "aproximación", "emergencia",
                       "pista", "performance", "peso", "centro de gravedad", "crosswind"],
        "comunicaciones": ["frecuencia", "radio", "comunicación", "torre", "control",
                          "transponder", "atc", "fraseología", "qnh", "squawk"],
        "performance": ["alcance", "autonomía", "velocidad", "distancia", "consumo",
                       "performance", "peso máximo", "techo", "régimen"]
    }
    
    # Contar coincidencias por categoría
    scores = {}
    for cat, words in keywords.items():
        scores[cat] = sum(1 for word in words if word in pregunta_lower)
    
    # Devolver la categoría con más coincidencias, o "general" si no hay coincidencias
    if max(scores.values()) > 0:
        return max(scores, key=scores.get)
    return "general"

def migrar_preguntas(archivo_entrada, archivo_salida):
    """Migra las preguntas agregando categorías y explicaciones"""
    print(f"📖 Leyendo {archivo_entrada}...")
    
    try:
        with open(archivo_entrada, 'r', encoding='utf-8') as f:
            preguntas = json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: No se encontró el archivo {archivo_entrada}")
        return False
    except json.JSONDecodeError:
        print(f"❌ Error: El archivo {archivo_entrada} no es un JSON válido")
        return False
    
    print(f"✅ Cargadas {len(preguntas)} preguntas")
    print("🔄 Procesando preguntas...")
    
    # Estadísticas
    stats = {
        "total": len(preguntas),
        "con_imagen": 0,
        "por_categoria": {}
    }
    
    # Procesar cada pregunta
    for i, pregunta in enumerate(preguntas, 1):
        # Agregar categoría si no existe
        if 'categoria' not in pregunta:
            categoria = detectar_categoria(pregunta['pregunta'])
            pregunta['categoria'] = categoria
        else:
            categoria = pregunta['categoria']
        
        # Contar por categoría
        if categoria not in stats['por_categoria']:
            stats['por_categoria'][categoria] = 0
        stats['por_categoria'][categoria] += 1
        
        # Agregar campo de explicación vacío si no existe
        if 'explicacion' not in pregunta:
            pregunta['explicacion'] = ""
        
        # Contar imágenes
        if 'imagen' in pregunta and pregunta['imagen']:
            stats['con_imagen'] += 1
        
        # Mostrar progreso cada 50 preguntas
        if i % 50 == 0:
            print(f"  Procesadas {i}/{len(preguntas)} preguntas...")
    
    # Guardar archivo migrado
    print(f"\n💾 Guardando en {archivo_salida}...")
    
    try:
        with open(archivo_salida, 'w', encoding='utf-8') as f:
            json.dump(preguntas, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"❌ Error al guardar: {e}")
        return False
    
    # Mostrar estadísticas
    print("\n✅ ¡Migración completada!")
    print(f"\n📊 Estadísticas:")
    print(f"  Total de preguntas: {stats['total']}")
    print(f"  Preguntas con imagen: {stats['con_imagen']}")
    print(f"\n  Distribución por categoría:")
    
    for cat, count in sorted(stats['por_categoria'].items()):
        porcentaje = (count / stats['total']) * 100
        print(f"    {cat:15s}: {count:3d} ({porcentaje:5.1f}%)")
    
    return True

if __name__ == "__main__":
    # Archivos por defecto
    archivo_entrada = "datos_quiz.json"
    archivo_salida = "datos_quiz_migrado.json"
    
    # Permitir argumentos de línea de comandos
    if len(sys.argv) > 1:
        archivo_entrada = sys.argv[1]
    if len(sys.argv) > 2:
        archivo_salida = sys.argv[2]
    
    print("=" * 60)
    print("🚀 MIGRACIÓN DE PREGUNTAS PPA")
    print("=" * 60)
    print(f"Entrada: {archivo_entrada}")
    print(f"Salida:  {archivo_salida}")
    print("=" * 60 + "\n")
    
    exito = migrar_preguntas(archivo_entrada, archivo_salida)
    
    if exito:
        print(f"\n✨ Archivo migrado guardado como: {archivo_salida}")
        print("📝 Puedes reemplazar tu archivo original o usar el nuevo")
        sys.exit(0)
    else:
        print("\n❌ La migración falló")
        sys.exit(1)
