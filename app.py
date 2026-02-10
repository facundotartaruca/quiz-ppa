import streamlit as st
import json
import os
import random

# 1. Configuración de página
st.set_page_config(page_title="Simulador PPA", page_icon="✈️")

# 2. Carga de datos
@st.cache_data
def cargar_datos():
    if os.path.exists("datos_quiz.json"):
        with open("datos_quiz.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# 3. Inicialización de Estados
if 'indice' not in st.session_state:
    datos = cargar_datos()
    if datos:
        st.session_state.preguntas = random.sample(datos, min(len(datos), 10))   ###
        st.session_state.indice = 0
        st.session_state.aciertos = 0
        st.session_state.respondido = False # Para saber si ya clickeó "Enviar"
        st.session_state.finalizado = False

# --- INTERFAZ ---
st.title("✈️ Simulador PPA")

if 'preguntas' in st.session_state and not st.session_state.finalizado:
    idx = st.session_state.indice
    p = st.session_state.preguntas[idx]

    # Barra de progreso
    st.progress((idx + 1) / 10)        #####
    st.write(f"Pregunta {idx + 1} de 10")        #####
    
    st.subheader(p["pregunta"])

    # Selección de respuesta (se deshabilita si ya respondió)
    seleccion = st.radio("Elegí una opción:", p["opciones"], disabled=st.session_state.respondido)

    # Lógica de Botones
    if not st.session_state.respondido:
        if st.button("Enviar Respuesta"):
            st.session_state.respondido = True
            st.rerun()
    else:
        # Mostramos si acertó o no
        idx_sel = p["opciones"].index(seleccion)
        if idx_sel == p["correcta"]:
            st.success("¡Correcto! ✅")
        else:
            correcta_txt = p["opciones"][p["correcta"]]
            st.error(f"Incorrecto ❌. La respuesta era: {correcta_txt}")
        
        # Botón para pasar a la siguiente (aparece solo después de responder)
        if st.button("Siguiente Pregunta ➡️"):
            if st.session_state.indice < len(st.session_state.preguntas) - 1:
                st.session_state.indice += 1
                st.session_state.respondido = False # Reseteamos para la próxima
                if idx_sel == p["correcta"]: # Sumamos el punto recién acá
                    st.session_state.aciertos += 1
                st.rerun()
            else:
                st.session_state.finalizado = True
                st.rerun()

elif st.session_state.get('finalizado'):
    st.balloons()
    st.header("¡Examen Terminado! 🏁")
    
    # Guardamos los aciertos en una variable para que sea más fácil de leer
    nota = st.session_state.aciertos
    st.metric("Puntaje Final", f"{nota}/100")

    # --- Lógica de Aprobación ---
    if nota >= 8:        #####
        st.success(f"### ✅ APROBADO")
        st.write(f"¡Excelente desempeño, piloto! Con **{nota}%** estás por encima del estándar requerido.")
    else:
        st.error(f"### ❌ DESAPROBADO")
        st.write(f"Obtuviste un **{nota}%**. Recordá que necesitás al menos **80%** para aprobar. ¡A repasar la RAAC y volver a intentar!")

    # Botón para reiniciar
    if st.button("🔄 Reiniciar Simulacro"):
        # Limpiamos todo el estado para empezar de cero
        for key in list(st.session_state.keys()):
            del st.session_state[key]

        st.rerun()
