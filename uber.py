import os
import altair as alt
import numpy as np
import pandas as pd
import pydeck as pdk
import streamlit as st
import requests

#from streamlit_lottie import st_lottie

# SETTING PAGE CONFIG TO WIDE MODE AND ADDING A TITLE AND FAVICON
st.set_page_config(layout="wide", page_title="TAXIMETRO nyc", page_icon=":car:")

def cargar_url(url):
    respuesta= requests.get(url)
    if respuesta.status_code !=200:
        return None
    return respuesta.json()
codigo_saludo= cargar_url("https://assets2.lottiefiles.com/packages/lf20_brmihxji.json")


# LOAD DATA ONCE
@st.cache_resource
def cargar_datos():
    path = "uber-raw-data-sep14.csv.gz"
    if not os.path.isfile(path):
        path = f"https://github.com/streamlit/demo-uber-nyc-pickups/raw/main/{path}"

    datos = pd.read_csv(
        path,
        nrows=100000,  
        names=[
            "date/time",
            "lat",
            "lon",
        ],  
        skiprows  =1,  
        usecols=[0, 1, 2],
        parse_dates=[
            "date/time"
        ],  
    )

    return datos


def mapa(datos, lat, lon, zoom):
    st.write(
        pdk.Deck(
            map_style="mapbox://styles/mapbox/light-v9",
            initial_view_state={
                "latitude": lat,
                "longitude": lon,
                "zoom": zoom,
                "pitch": 50,
            },
            layers=[
                pdk.Layer(
                    "HexagonLayer",
                    data=datos,
                    get_position=["lon", "lat"],
                    radius=100,
                    elevation_scale=4,
                    elevation_range=[0, 1000],
                    pickable=True,
                    extruded=True,
                ),
            ],
        )
    )
    

@st.cache_data
def filtrar_datos(df, hora_seleccionada):
    return df[df["date/time"].dt.hour == hora_seleccionada]


@st.cache_data
def mapa_puntos(latitud, longitud):
    return (np.average(latitud), np.average(longitud))


@st.cache_data
def historial_datos(df, hora):
    filtrar = datos[
        (df["date/time"].dt.hour >= hora) & (df["date/time"].dt.hour < (hora + 1))
    ]

    hist = np.histogram(filtrar["date/time"].dt.minute, bins=60, range=(0, 60))[0]

    return pd.DataFrame({"minute": range(60), "pickups": hist})


datos = cargar_datos()

columna_1, columna_2 = st.columns((2, 3))


if not st.session_state.get("url_synced", False):
    try:
        hora_pico = int(st.experimental_get_query_params()["hora_pico"][0])
        st.session_state["hora_pico"] = hora_pico
        st.session_state["url_synced"] = True
    except KeyError:
        pass


def actualizar_parametrosquery():
    hora_seleccionada= st.session_state["hora_pico"]
    st.experimental_set_query_params(hora_pico=hora_seleccionada)


with columna_1:
    st.title("Datos de viajes  en Uber en la ciudad de Nueva York")
    hora_seleccionada = st.slider(
        "Selecciona la Hora Pico", 0, 23, key="hora_pico", on_change= actualizar_parametrosquery
    )


with columna_2:
    st_lottie(codigo_saludo, height=300, key="hola")

    st.write(
        """
    ##
   Examinar cómo las recolecciones de Uber varían con el tiempo en la ciudad de Nueva York y en sus principales aeropuertos regionales.
    Al deslizar el control deslizante de la izquierda, puede ver diferentes períodos de tiempo y explorar diferentes tendencias de transporte.
    """

    )


columna_texto, columna_laguardia, columna_jfk, columna_newark = st.columns((2, 1, 1, 1))

la_guardia = [40.7900, -73.8700]
jfk = [40.6650, -73.7821]
newark = [40.7090, -74.1805]
zoom_level = 12
midpoint = mapa_puntos(datos["lat"], datos["lon"])

with columna_texto:
    st.write(
        f"""**Ciudad de New York :city_sunset:  entre {hora_seleccionada}:00 and {(hora_seleccionada + 1) % 24}:00**"""
    )
    mapa(filtrar_datos(datos, hora_seleccionada), midpoint[0], midpoint[1], 11)

with columna_laguardia:
    st.write("**Aeropuerto La Guardia**")
    mapa(filtrar_datos(datos, hora_seleccionada), la_guardia[0], la_guardia[1], zoom_level)

with columna_jfk:
    st.write("**Aerpuerto JFK**")
    mapa(filtrar_datos(datos, hora_seleccionada), jfk[0], jfk[1], zoom_level)

with columna_newark:
    st.write("**Aeropuerto Newark**")
    mapa(filtrar_datos(datos, hora_seleccionada), newark[0], newark[1], zoom_level)

chart_data = historial_datos(datos, hora_seleccionada)

st.write(
    f"""** viajes por minuto entre {hora_seleccionada}:00 y  {(hora_seleccionada + 1) % 24}:00**"""
)

