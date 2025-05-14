import streamlit as st
import pandas as pd
from openai import OpenAI

# Título y descripción
st.title("🔍 Chatbot Analista de Datos")
st.write(
    "Este chatbot utiliza un modelo de OpenAI para responder preguntas relacionadas con un dataset de consumo de combustible. "
    "Proporcione su clave de API de OpenAI para comenzar. Puede obtenerla [aquí](https://platform.openai.com/account/api-keys)."
)

# Entrada para la API Key
openai_api_key = st.text_input("🔑 Clave de API de OpenAI", type="password")
if not openai_api_key:
    st.info("Por favor ingresa tu clave de API para continuar.", icon="🗝️")
    st.stop()

# Crear cliente de OpenAI
client = OpenAI(api_key=openai_api_key)

# Cargar dataset
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("FuelConsumption (1).csv")
        return df
    except Exception as e:
        st.error(f"No se pudo cargar el dataset: {e}")
        return None

df = load_data()
if df is None:
    st.stop()

# Mostrar vista previa
st.subheader("📊 Vista previa del dataset")
st.dataframe(df.head(100))

# Estado del chat
if "messages" not in st.session_state:
    # Mensaje del sistema con contexto del dataset
    df_context = df.head(100).to_string()
    st.session_state.messages = [
        {
            "role": "system",
            "content": "Eres un analista de datos. Solo debes responder preguntas relacionadas con el siguiente dataset:\n\n"
                       + df_context +
                       "\n\nSi la pregunta no tiene relación con los datos, responde: 'Por ahora solo me centro en responder preguntas del dataset'."
        }
    ]

# Mostrar historial del chat
for msg in st.session_state.messages[1:]:  # omitimos el system
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Entrada de chat
if prompt := st.chat_input("Haz una pregunta sobre el dataset..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        # Respuesta del modelo
        stream = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=st.session_state.messages,
            stream=True
        )

        # Mostrar y guardar respuesta
        with st.chat_message("assistant"):
            response = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": response})

    except Exception as e:
        st.error(f"❌ Error al consultar la API: {e}")
