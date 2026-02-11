# config.py - Configuración de la aplicación

# Configuración del examen
TOTAL_PREGUNTAS_EXAMEN = 100
PORCENTAJE_APROBACION = 80
TIEMPO_EXAMEN_MINUTOS = 120  # 2 horas

# Categorías de preguntas (basado en el syllabus de ANAC)
CATEGORIAS = {
    "motor": "🔧 Motor y Sistemas",
    "aerodinamica": "✈️ Aerodinámica",
    "navegacion": "🧭 Navegación",
    "meteorologia": "🌦️ Meteorología",
    "regulaciones": "📋 Regulaciones (RAAC)",
    "operaciones": "🛫 Operaciones de Vuelo",
    "comunicaciones": "📡 Comunicaciones",
    "performance": "📊 Performance",
    "general": "📚 Conocimientos Generales"
}

# Colores del tema
COLORS = {
    "primary": "#1E3A8A",      # Azul oscuro
    "secondary": "#3B82F6",    # Azul
    "success": "#10B981",      # Verde
    "error": "#EF4444",        # Rojo
    "warning": "#F59E0B",      # Naranja
    "background": "#F9FAFB",   # Gris claro
}

# Textos de la aplicación
TEXTOS = {
    "titulo_app": "✈️ Simulador Examen PPA - ANAC",
    "subtitulo": "Prepárate para el examen de Piloto Privado de Avión",
    "descripcion_home": """
    ### Bienvenido al Simulador Oficial de Examen PPA
    
    Este simulador te prepara para el examen teórico de la ANAC con:
    - ✅ Más de 370 preguntas reales del banco oficial
    - ✅ Simulacro con las mismas condiciones del examen real
    - ✅ Modo práctica por categorías
    - ✅ Explicaciones detalladas de cada respuesta
    - ✅ Estadísticas de tu progreso
    """,
    "aprobado": "🎉 ¡FELICITACIONES! HAS APROBADO",
    "desaprobado": "😔 No alcanzaste el puntaje mínimo",
    "msg_aprobado": "¡Excelente trabajo! Estás listo para el examen real.",
    "msg_desaprobado": "Sigue practicando. Repasa los temas donde tuviste errores."
}