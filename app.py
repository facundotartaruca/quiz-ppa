import streamlit as st
import json
import os
import random
from datetime import datetime, timedelta
import time

# Importar configuración y utilidades
from config import *
from utils import *

# ==========================================
# CONFIGURACIÓN DE PÁGINA
# ==========================================
st.set_page_config(
    page_title="Simulador PPA - ANAC",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# CSS PERSONALIZADO
# ==========================================
st.markdown(f"""
<style>
    /* Títulos - adaptar al tema */
    h1, h2, h3 {{
        font-weight: 700;
    }}
    
    /* Botones personalizados */
    .stButton>button {{
        background-color: {COLORS['secondary']};
        color: white;
        font-weight: 600;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        border: none;
        transition: all 0.3s;
    }}
    
    .stButton>button:hover {{
        background-color: {COLORS['primary']};
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }}
    
    /* Tarjetas de estadísticas - adaptables al tema */
    .stat-card {{
        background: rgba(59, 130, 246, 0.1);
        border: 1px solid rgba(59, 130, 246, 0.2);
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
    }}
    
    /* Pregunta destacada - adaptable al tema */
    .pregunta-box {{
        background: rgba(59, 130, 246, 0.05);
        border: 1px solid rgba(59, 130, 246, 0.2);
        padding: 2rem;
        border-radius: 12px;
        border-left: 4px solid {COLORS['secondary']};
        margin: 1.5rem 0;
    }}
    
    /* Timer */
    .timer-box {{
        background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['secondary']} 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        font-size: 1.5rem;
        font-weight: 700;
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }}
    
    /* Categoría badge */
    .categoria-badge {{
        background: {COLORS['secondary']};
        color: white;
        padding: 0.3rem 1rem;
        border-radius: 20px;
        font-size: 0.9rem;
        display: inline-block;
        margin: 0.5rem 0;
    }}
    
    /* Mejorar contraste de radio buttons en modo oscuro */
    .stRadio > label {{
        background: rgba(59, 130, 246, 0.05);
        padding: 0.75rem;
        border-radius: 8px;
        margin: 0.25rem 0;
        border: 1px solid rgba(59, 130, 246, 0.2);
        transition: all 0.2s;
    }}
    
    .stRadio > label:hover {{
        background: rgba(59, 130, 246, 0.1);
        border-color: rgba(59, 130, 246, 0.4);
    }}

</style>
""", unsafe_allow_html=True)

# ==========================================
# INICIALIZACIÓN DE ESTADOS
# ==========================================
def inicializar_estados():
    """Inicializa todos los estados de la sesión"""
    if 'pagina_actual' not in st.session_state:
        st.session_state.pagina_actual = 'home'
    
    if 'preguntas' not in st.session_state:
        st.session_state.preguntas = []
    
    if 'indice' not in st.session_state:
        st.session_state.indice = 0
    
    if 'respuestas' not in st.session_state:
        st.session_state.respuestas = []
    
    if 'respondido' not in st.session_state:
        st.session_state.respondido = False
    
    if 'modo' not in st.session_state:
        st.session_state.modo = 'examen'
    
    if 'tiempo_inicio' not in st.session_state:
        st.session_state.tiempo_inicio = None
    
    if 'con_timer' not in st.session_state:
        st.session_state.con_timer = False

inicializar_estados()

# ==========================================
# SIDEBAR - NAVEGACIÓN Y CONFIGURACIÓN
# ==========================================
with st.sidebar:
    st.image("imagenes/logo.png", use_container_width=True)
    st.markdown("---")
    
    # Navegación
    st.subheader("📍 Navegación")
    
    if st.button("🏠 Inicio", use_container_width=True):
        st.session_state.pagina_actual = 'home'
        st.rerun()
    
    if st.button("📝 Nuevo Simulacro", use_container_width=True):
        st.session_state.pagina_actual = 'configurar'
        st.rerun()
    
    if st.button("📊 Mis Estadísticas", use_container_width=True):
        st.session_state.pagina_actual = 'estadisticas'
        st.rerun()
    
    if st.button("❓ Ayuda", use_container_width=True):
        st.session_state.pagina_actual = 'ayuda'
        st.rerun()
    
    st.markdown("---")
    
    # Información durante el examen
    if st.session_state.pagina_actual == 'examen' and st.session_state.preguntas:
        st.subheader("📌 Progreso")
        progreso = min(1.0, (st.session_state.indice + 1) / len(st.session_state.preguntas))
        st.progress(progreso)
        pregunta_actual = min(st.session_state.indice + 1, len(st.session_state.preguntas))
        st.write(f"Pregunta {pregunta_actual} de {len(st.session_state.preguntas)}")
        
        # Contador de respuestas
        total_respondidas = len(st.session_state.respuestas)
        st.metric("Respondidas", f"{total_respondidas}/{len(st.session_state.preguntas)}")
        
        # Timer si está activado
        if st.session_state.con_timer and st.session_state.tiempo_inicio:
            tiempo_transcurrido = int((datetime.now() - st.session_state.tiempo_inicio).total_seconds())
            tiempo_limite = TIEMPO_EXAMEN_MINUTOS * 60
            tiempo_restante = max(0, tiempo_limite - tiempo_transcurrido)
            
            st.markdown(f'<div class="timer-box">⏱️ {formatear_tiempo(tiempo_restante)}</div>', 
                       unsafe_allow_html=True)
            
            if tiempo_restante == 0:
                st.error("⏰ ¡Tiempo agotado!")
                if st.button("Ver Resultados"):
                    st.session_state.pagina_actual = 'resultados'
                    st.rerun()
        
        # Botón para abandonar
        st.markdown("---")
        if st.button("🚪 Abandonar Simulacro", type="secondary", use_container_width=True):
            if st.session_state.respuestas:
                st.session_state.pagina_actual = 'resultados'
            else:
                st.session_state.pagina_actual = 'home'
            st.rerun()

# ==========================================
# PÁGINA HOME
# ==========================================
def mostrar_home():
    st.title(TEXTOS['titulo_app'])
    st.markdown(TEXTOS['subtitulo'])
    
    st.markdown(TEXTOS['descripcion_home'])
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="stat-card">
            <h3>🎯 Modo Examen</h3>
            <p>Simula las condiciones reales del examen:</p>
            <ul>
                <li>100 preguntas aleatorias</li>
                <li>Sin feedback inmediato</li>
                <li>Tiempo limitado (opcional)</li>
                <li>Resultados al final</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚀 Comenzar Examen", use_container_width=True, type="primary"):
            st.session_state.pagina_actual = 'configurar'
            st.session_state.modo = 'examen'
            st.rerun()
    
    with col2:
        st.markdown("""
        <div class="stat-card">
            <h3>📚 Modo Práctica</h3>
            <p>Aprende mientras practicas:</p>
            <ul>
                <li>Elige cantidad de preguntas</li>
                <li>Filtra por categoría</li>
                <li>Feedback inmediato</li>
                <li>Explicaciones detalladas</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("📖 Modo Práctica", use_container_width=True):
            st.session_state.pagina_actual = 'configurar'
            st.session_state.modo = 'practica'
            st.rerun()
    
    st.markdown("---")
    
    # Estadísticas globales (si existen)
    st.subheader("📊 Estadísticas Globales")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Preguntas", "374")
    with col2:
        st.metric("Preguntas con Imagen", "48")
    with col3:
        st.metric("Categorías", len(CATEGORIAS))
    with col4:
        st.metric("Aprobación Requerida", f"{PORCENTAJE_APROBACION}%")

# ==========================================
# PÁGINA CONFIGURAR SIMULACRO
# ==========================================
def mostrar_configurar():
    st.title("⚙️ Configurar Simulacro")
    
    modo = st.session_state.modo
    
    if modo == 'examen':
        st.info("🎯 **Modo Examen**: Simula las condiciones reales del examen de ANAC")
        
        st.subheader("Configuración del Examen")
        
        con_timer = st.checkbox(
            "⏱️ Activar timer de 2 horas",
            value=False,
            help="El examen real tiene un límite de 2 horas"
        )
        
        st.session_state.con_timer = con_timer
        cantidad = 100
        categoria_seleccionada = "todas"
        
    else:  # modo práctica
        st.info("📚 **Modo Práctica**: Personaliza tu sesión de estudio")
        
        st.subheader("Configuración de Práctica")
        
        col1, col2 = st.columns(2)
        
        with col1:
            cantidad = st.slider(
                "Cantidad de preguntas",
                min_value=10,
                max_value=100,
                value=50,
                step=10
            )
        
        with col2:
            categorias_opciones = ["todas"] + list(CATEGORIAS.keys())
            categorias_labels = ["📋 Todas las categorías"] + [CATEGORIAS[k] for k in CATEGORIAS.keys()]
            
            categoria_seleccionada = st.selectbox(
                "Categoría",
                options=categorias_opciones,
                format_func=lambda x: categorias_labels[categorias_opciones.index(x)]
            )
        
        st.session_state.con_timer = False
    
    st.markdown("---")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("◀️ Volver", use_container_width=True):
            st.session_state.pagina_actual = 'home'
            st.rerun()
    
    with col2:
        if st.button("▶️ Comenzar", use_container_width=True, type="primary"):
            # Cargar preguntas
            todas_preguntas = cargar_preguntas("datos_quiz.json")
            
            if not todas_preguntas:
                st.error("❌ No se pudieron cargar las preguntas")
                return
            
            # Seleccionar preguntas según configuración
            st.session_state.preguntas = seleccionar_preguntas(
                todas_preguntas,
                cantidad,
                categoria_seleccionada,
                modo
            )
            
            # Resetear estados
            st.session_state.indice = 0
            st.session_state.respuestas = []
            st.session_state.respondido = False
            
            if st.session_state.con_timer:
                st.session_state.tiempo_inicio = datetime.now()
            
            st.session_state.pagina_actual = 'examen'
            st.rerun()

# ==========================================
# PÁGINA EXAMEN/PRÁCTICA
# ==========================================
def mostrar_examen():
    if not st.session_state.preguntas:
        st.error("❌ No hay preguntas cargadas")
        if st.button("Volver al inicio"):
            st.session_state.pagina_actual = 'home'
            st.rerun()
        return
    
    idx = st.session_state.indice
    total = len(st.session_state.preguntas)
    
    # Verificar si terminó
    if idx >= total:
        st.session_state.pagina_actual = 'resultados'
        st.rerun()
        return
    
    pregunta = st.session_state.preguntas[idx]
    modo = st.session_state.modo
    
    # Título según modo
    if modo == 'examen':
        st.title("🎯 Examen Simulado")
    else:
        st.title("📚 Modo Práctica")
    
    # Mostrar categoría (si existe)
    categoria = pregunta.get('categoria', 'general')
    if categoria in CATEGORIAS:
        st.markdown(f'<div class="categoria-badge">{CATEGORIAS[categoria]}</div>', 
                   unsafe_allow_html=True)
    
    # Pregunta
    st.markdown(f'<div class="pregunta-box"><h3>Pregunta {idx + 1} de {total}</h3><p style="font-size: 1.1rem;">{pregunta["pregunta"]}</p></div>', 
               unsafe_allow_html=True)
    
    # Imagen si existe
    if "imagen" in pregunta and pregunta["imagen"]:
        if os.path.exists(pregunta["imagen"]):
            st.image(pregunta["imagen"], use_container_width=True, caption="Referencia de la pregunta")
        else:
            st.warning("⚠️ Imagen de referencia no encontrada")
    
    # Opciones
    st.markdown("### Selecciona tu respuesta:")
    
    # Crear un key único para cada pregunta
    radio_key = f"pregunta_{idx}"
    
    seleccion = st.radio(
        "Opciones:",
        options=pregunta["opciones"],
        key=radio_key,
        disabled=st.session_state.respondido,
        label_visibility="collapsed"
    )
    
    # Lógica de respuesta según modo
    if modo == 'practica':
        # En modo práctica: feedback inmediato
        if not st.session_state.respondido:
            if st.button("✅ Enviar Respuesta", use_container_width=True, type="primary"):
                st.session_state.respondido = True
                st.rerun()
        else:
            # Mostrar feedback
            idx_sel = pregunta["opciones"].index(seleccion)
            es_correcta = idx_sel == pregunta["correcta"]
            
            if es_correcta:
                st.success("✅ ¡Correcto!")
            else:
                correcta_txt = pregunta["opciones"][pregunta["correcta"]]
                st.error(f"❌ Incorrecto. La respuesta correcta es: **{correcta_txt}**")
            
            # Mostrar explicación si existe
            if pregunta.get("explicacion"):
                with st.expander("📖 Ver explicación"):
                    st.info(pregunta["explicacion"])
            
            # Guardar respuesta
            if len(st.session_state.respuestas) <= idx:
                st.session_state.respuestas.append({
                    'pregunta': pregunta['pregunta'],
                    'respuesta_usuario': seleccion,
                    'respuesta_correcta': pregunta["opciones"][pregunta["correcta"]],
                    'correcta': es_correcta,
                    'categoria': categoria,
                    'explicacion': pregunta.get('explicacion', '')
                })
            
            # Botón siguiente
            col1, col2 = st.columns([1, 1])
            with col2:
                if st.button("➡️ Siguiente Pregunta", use_container_width=True, type="primary"):
                    # Verificar si era la última pregunta
                    if st.session_state.indice >= len(st.session_state.preguntas) - 1:
                        # Era la última, ir a resultados
                        st.session_state.pagina_actual = 'resultados'
                    else:
                        # Hay más preguntas
                        st.session_state.indice += 1
                    st.session_state.respondido = False
                    st.rerun()
    
    else:  # modo examen
        # En modo examen: sin feedback, solo avanzar
        if st.button("➡️ Siguiente Pregunta", use_container_width=True, type="primary"):
            # Guardar respuesta
            idx_sel = pregunta["opciones"].index(seleccion)
            es_correcta = idx_sel == pregunta["correcta"]
            
            st.session_state.respuestas.append({
                'pregunta': pregunta['pregunta'],
                'respuesta_usuario': seleccion,
                'respuesta_correcta': pregunta["opciones"][pregunta["correcta"]],
                'correcta': es_correcta,
                'categoria': categoria,
                'explicacion': pregunta.get('explicacion', '')
            })
            
            # Verificar si era la última pregunta
            if st.session_state.indice >= len(st.session_state.preguntas) - 1:
                # Era la última, ir a resultados
                st.session_state.pagina_actual = 'resultados'
            else:
                # Hay más preguntas
                st.session_state.indice += 1
            st.rerun()

# ==========================================
# PÁGINA RESULTADOS
# ==========================================
def mostrar_resultados():
    if not st.session_state.respuestas:
        st.warning("⚠️ No hay resultados para mostrar")
        if st.button("Volver al inicio"):
            st.session_state.pagina_actual = 'home'
            st.rerun()
        return
    
    stats = calcular_estadisticas(st.session_state.respuestas)
    
    # Animación de globos si aprobó
    if stats['aprobado']:
        st.balloons()
        st.success(f"### {TEXTOS['aprobado']}")
        st.markdown(f"**{TEXTOS['msg_aprobado']}**")
    else:
        st.error(f"### {TEXTOS['desaprobado']}")
        st.markdown(f"**{TEXTOS['msg_desaprobado']}**")
    
    st.markdown("---")
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Preguntas", stats['total'])
    with col2:
        st.metric("Correctas", stats['correctas'], delta=f"+{stats['correctas']}")
    with col3:
        st.metric("Incorrectas", stats['incorrectas'], delta=f"-{stats['incorrectas']}", delta_color="inverse")
    with col4:
        color_delta = "normal" if stats['aprobado'] else "inverse"
        st.metric("Porcentaje", f"{stats['porcentaje']:.1f}%", 
                 delta=f"{stats['porcentaje'] - PORCENTAJE_APROBACION:.1f}%",
                 delta_color=color_delta)
    
    st.markdown("---")
    
    # Resultados por categoría
    st.subheader("📊 Resultados por Categoría")
    
    for cat, data in stats['por_categoria'].items():
        cat_nombre = CATEGORIAS.get(cat, cat)
        porcentaje = data['porcentaje']
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.write(f"**{cat_nombre}**")
            st.progress(porcentaje / 100)
        
        with col2:
            color = "🟢" if porcentaje >= 80 else "🟡" if porcentaje >= 60 else "🔴"
            st.write(f"{color} {data['correctas']}/{data['total']} ({porcentaje:.0f}%)")
    
    st.markdown("---")
    
    # Preguntas incorrectas
    if stats['incorrectas'] > 0:
        with st.expander(f"❌ Ver {stats['incorrectas']} pregunta(s) incorrecta(s)"):
            for idx, r in enumerate(st.session_state.respuestas):
                if not r['correcta']:
                    st.markdown(f"**{idx + 1}. {r['pregunta']}**")
                    st.markdown(f"- Tu respuesta: ❌ {r['respuesta_usuario']}")
                    st.markdown(f"- Respuesta correcta: ✅ {r['respuesta_correcta']}")
                    if r.get('explicacion'):
                        st.info(f"📖 {r['explicacion']}")
                    st.markdown("---")
    
    # Botones de acción
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Descargar reporte
        reporte = generar_reporte_texto(stats, st.session_state.respuestas)
        st.download_button(
            label="📥 Descargar Reporte",
            data=reporte,
            file_name=f"reporte_ppa_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain",
            use_container_width=True
        )
    
    with col2:
        if st.button("🔄 Nuevo Simulacro", use_container_width=True):
            st.session_state.pagina_actual = 'configurar'
            st.rerun()
    
    with col3:
        if st.button("🏠 Volver al Inicio", use_container_width=True):
            st.session_state.pagina_actual = 'home'
            st.rerun()

# ==========================================
# PÁGINA AYUDA
# ==========================================
def mostrar_ayuda():
    st.title("❓ Ayuda y Soporte")
    
    st.markdown("""
    ## ¿Cómo usar el simulador?
    
    ### 🎯 Modo Examen
    1. Simula las condiciones reales del examen de ANAC
    2. 100 preguntas aleatorias del banco oficial
    3. Puedes activar el timer de 2 horas
    4. No recibes feedback hasta terminar
    5. Al finalizar ves tus resultados completos
    
    ### 📚 Modo Práctica
    1. Elige cuántas preguntas quieres responder
    2. Filtra por categoría específica
    3. Recibes feedback inmediato
    4. Puedes ver explicaciones detalladas
    5. Ideal para repasar temas específicos
    
    ## 📋 Requisitos del Examen Real
    - **Preguntas**: 100 preguntas de selección múltiple
    - **Tiempo**: 2 horas máximo
    - **Aprobación**: 80% mínimo (80 respuestas correctas)
    - **Temas**: Todas las áreas del programa de PPA
    
    ## 💡 Consejos de Estudio
    1. Practica por categorías para identificar tus puntos débiles
    2. Repasa las preguntas incorrectas y sus explicaciones
    3. Simula el examen completo varias veces antes del real
    4. Estudia la RAAC (Regulaciones Argentinas de Aviación Civil)
    5. Consulta con tu instructor ante dudas
    
    ## 🆘 Soporte Técnico
    Si encuentras algún problema o tienes sugerencias:
    - Email: soporte@simuladorppa.com
    - Teléfono: +54 11 XXXX-XXXX
    
    ## ✈️ Recursos Adicionales
    - [ANAC - Página Oficial](https://www.anac.gov.ar)
    - [RAAC - Regulaciones](https://www.anac.gov.ar/raac)
    - Manuales de estudio (disponibles en tu escuela)
    """)

# ==========================================
# PÁGINA ESTADÍSTICAS (placeholder para futuro)
# ==========================================
def mostrar_estadisticas():
    st.title("📊 Mis Estadísticas")
    st.info("🚧 Esta funcionalidad estará disponible en la versión con registro de usuarios")
    
    st.markdown("""
    ### Próximamente podrás ver:
    - 📈 Historial de simulacros
    - 🎯 Evolución de tu puntaje
    - 📊 Rendimiento por categoría
    - ⏱️ Tiempo promedio por pregunta
    - 🏆 Logros y medallas
    - 📅 Calendario de práctica
    """)
    
    if st.button("🏠 Volver al Inicio"):
        st.session_state.pagina_actual = 'home'
        st.rerun()

# ==========================================
# ROUTER PRINCIPAL
# ==========================================
def main():
    pagina = st.session_state.pagina_actual
    
    if pagina == 'home':
        mostrar_home()
    elif pagina == 'configurar':
        mostrar_configurar()
    elif pagina == 'examen':
        mostrar_examen()
    elif pagina == 'resultados':
        mostrar_resultados()
    elif pagina == 'ayuda':
        mostrar_ayuda()
    elif pagina == 'estadisticas':
        mostrar_estadisticas()
    else:
        mostrar_home()

if __name__ == "__main__":
    main()