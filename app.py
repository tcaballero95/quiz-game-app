import streamlit as st
import json
import random
import os
import pandas as pd
import plotly.express as px

# --- Utils dentro de este archivo ---
PREGUNTAS_FILE = "preguntas.json"
RESPUESTAS_FILE = "respuestas.json"

def cargar_preguntas():
	with open(PREGUNTAS_FILE, "r", encoding="utf-8") as f:
		data = json.load(f)
		return data["preguntas"]

def cargar_respuestas():
	if not os.path.exists(RESPUESTAS_FILE):
		return []
	try:
		with open(RESPUESTAS_FILE, "r", encoding="utf-8") as f:
			contenido = f.read().strip()
			if not contenido:
				return []
			return json.loads(contenido)
	except Exception:
		return []
	
def guardar_respuesta(respuesta):
	respuestas = cargar_respuestas()
	respuestas.append(respuesta)
	with open(RESPUESTAS_FILE, "w", encoding="utf-8") as f:
		json.dump(respuestas, f, ensure_ascii=False, indent=2)

def obtener_pregunta_aleatoria(preguntas, ya_respondidas):
	disponibles = [p for p in preguntas if p["id"] not in ya_respondidas]
	if not disponibles:
		return None
	return random.choice(disponibles)

def calcular_puntajes(respuestas, preguntas):
	# Map: participante -> lista de respuestas
	participantes = {}
	for r in respuestas:
		nombre = r["nombre"]
		if nombre not in participantes:
			participantes[nombre] = []
		participantes[nombre].append(r)
	# Map: id_pregunta -> respuesta correcta
	correctas = {str(p["id"]): p["respuesta_correcta"] for p in preguntas}
	puntajes = {}
	for nombre, resps in participantes.items():
		puntos = 0
		for r in resps:
			idp = str(r["id_pregunta"])
			if idp in correctas and r["respuesta"] == correctas[idp]:
				puntos += 1
		puntajes[nombre] = puntos + 1  # punto base
	return puntajes

# --- App principal ---
st.set_page_config(page_title="Juego de Preguntas", layout="centered")

tabs = st.tabs(["Jugar", "Resultados"])

# --- Tab 1: Jugar ---
with tabs[0]:
	st.header("Juego de Preguntas")
	nombre_input = st.text_input("Ingresa tu nombre:")
	if nombre_input:
		# Si el nombre cambia, reiniciar el estado de la sesión
		if st.session_state.get("nombre_participante") != nombre_input:
			st.session_state["nombre_participante"] = nombre_input
			st.session_state["respuestas_usuario"] = []
			st.session_state["preguntas_respondidas"] = []
			st.session_state["pregunta_actual"] = None
		nombre = st.session_state["nombre_participante"]
		preguntas = cargar_preguntas()
		if "respuestas_usuario" not in st.session_state:
			st.session_state["respuestas_usuario"] = []
		if "preguntas_respondidas" not in st.session_state:
			st.session_state["preguntas_respondidas"] = []
		if "pregunta_actual" not in st.session_state or st.session_state["pregunta_actual"] is None:
			st.session_state["pregunta_actual"] = obtener_pregunta_aleatoria(preguntas, st.session_state["preguntas_respondidas"])
		if len(st.session_state["preguntas_respondidas"]) < 6:
			pregunta = st.session_state["pregunta_actual"]
			if pregunta:
				st.markdown(f"**Pregunta {len(st.session_state['preguntas_respondidas'])+1}/6:** {pregunta['pregunta']}")
				alternativas = pregunta["alternativas"]
				respuesta_idx = st.radio(
					"Selecciona una alternativa:",
					list(enumerate(alternativas, 1)),
					format_func=lambda x: x[1],
					key=f"alt_{pregunta['id']}_{nombre}"
				)
				if st.button("Enviar respuesta", key=f"btn_{pregunta['id']}_{nombre}"):
					respuesta_num = respuesta_idx[0]  # índice + 1
					st.session_state["respuestas_usuario"].append({
						"nombre": nombre,
						"id_pregunta": pregunta["id"],
						"respuesta": respuesta_num
					})
					st.session_state["preguntas_respondidas"].append(pregunta["id"])
					guardar_respuesta({
						"nombre": nombre,
						"id_pregunta": pregunta["id"],
						"respuesta": respuesta_num
					})
					if len(st.session_state["preguntas_respondidas"]) < 6:
						st.session_state["pregunta_actual"] = obtener_pregunta_aleatoria(preguntas, st.session_state["preguntas_respondidas"])
						st.rerun()
					else:
						st.success("¡Has respondido las 6 preguntas!")
						st.session_state["pregunta_actual"] = None
			else:
				st.info("No hay más preguntas disponibles.")
		else:
			st.success("¡Has respondido las 6 preguntas!")
	else:
		st.info("Por favor, ingresa tu nombre para comenzar.")

# --- Tab 2: Resultados ---
with tabs[1]:
	if st.button("Calcular el ganador", type="secondary"):
		preguntas = cargar_preguntas()
		respuestas = cargar_respuestas()
		puntajes = calcular_puntajes(respuestas, preguntas)
		if puntajes:
			max_puntaje = max(puntajes.values())
			ganadores = [nombre for nombre, p in puntajes.items() if p == max_puntaje]
			st.balloons()
			st.markdown(f"<h1 style='text-align:center; color:green;'>🏆 GANADOR{'ES' if len(ganadores)>1 else ''}:<br>{' y '.join(ganadores)}</h1>", unsafe_allow_html=True)
			st.markdown(f"<h2 style='text-align:center;'>Puntaje: {max_puntaje}</h2>", unsafe_allow_html=True)
			participantes_unicos = set(r["nombre"] for r in respuestas)
			# Nombres de los participantes
			st.subheader("Participantes:")
			if participantes_unicos:
				st.write(", ".join(participantes_unicos))
		else:
			st.info("No hay participantes aún.")

	with st.expander("Otras Opciones", expanded=False):
		if st.button("Borrar todas las respuestas"):
			with open(RESPUESTAS_FILE, "w", encoding="utf-8") as f:
				f.write("[]")
			st.success("¡Respuestas reseteadas!")
			st.rerun()

		if st.button("Calcular puntajes"):
			preguntas = cargar_preguntas()
			respuestas = cargar_respuestas()
			puntajes = calcular_puntajes(respuestas, preguntas)
			st.subheader("Puntajes por participante:")
			df = pd.DataFrame(list(puntajes.items()), columns=["Participante", "Puntaje"])
			st.dataframe(df, hide_index=True)
			fig = px.bar(df, x="Participante", y="Puntaje", title="Puntaje por participante", text="Puntaje")
			fig.update_traces(textposition='inside')
			st.plotly_chart(fig, use_container_width=True)
			st.subheader("Estadísticas generales:")
			st.write(f"Puntaje promedio: {df['Puntaje'].mean():.1f}")
			st.write(f"Puntaje máximo: {df['Puntaje'].max()}")
			st.write(f"Puntaje mínimo: {df['Puntaje'].min()}")
