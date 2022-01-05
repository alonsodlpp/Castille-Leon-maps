import pandas as pd
import plotly.express as px
import geopandas as gpd
import pyproj
import streamlit as st
from PIL import Image

img = Image.open("CyL.png")
st.set_page_config(page_title="CyL en mapas", page_icon=img)

st.markdown(
        f""" <style>.reportview-container .main .block-container{{
        max-width: {1500}px;
        padding-top: {1}rem;
        padding-right: {6}rem;
        padding-left: {6}rem;
        padding-bottom: {0}rem;
    }},
    .sidebar .sidebar-content {{
                width: 200px;
</style>
""", unsafe_allow_html=True)


st.markdown("""
    <div style="background-color:#FF815F;padding:0px">
    <h1 style="color:#FFFFFF ;text-align:center;">Castilla y León en mapas</h1>
    </div>
""", unsafe_allow_html=True)

st.markdown("<h4 style='text-align: center; '>A continuación se presentan en forma de mapas interactivos los resultados"
            "de las 3 últimas citas electorales en Castilla y Léon.</h4>",
            unsafe_allow_html=True)

st.markdown("<h5 style='text-align: center; '>"
            "¿Recuerdas lo que ocurrió en tu municipio en anteriores elecciones? ¡Descúbrelo en el mapa!</h5>",
            unsafe_allow_html=True)

modo = st.sidebar.radio(label="Elija el modo de visualización",
                        options=['% de voto por partidos', 'Ganador de las elecciones'],
                        help="Podrá visualizar, por un lado, mapas correspondientes al resultado de cada partido"
                             " en cada provincia. También tiene la opción de ver cada municipio coloreado según el partido"
                             " ganador, o el segundo más votado")


c1, c2, c3 = st.columns((1, 1, 1))
with c1:
    elecciones_elegidas = st.selectbox('Seleccione una de las pasadas elecciones:',
                                       ('Elecciones generales noviembre de 2019',
                                        'Elecciones autonómicas mayo de 2019',
                                        'Elecciones generales abril de 2019'))
with c2:
    provincia_elegida = st.selectbox('Elija qué provincia desea visualizar:',
                                     ('Castilla y León', 'Ávila', 'Burgos', 'León', 'Palencia',
                                      'Salamanca', 'Segovia', 'Soria', 'Valladolid', 'Zamora'))
    zoom = 8
    if provincia_elegida == 'Castilla y León':
        center = {"lat": 41.6300, "lon": -4.2700}
        zoom = 6.5
    elif provincia_elegida == 'Ávila':
        center = {"lat": 40.6300, "lon": -5.0000}
    elif provincia_elegida == 'Burgos':
        center = {"lat": 42.3316, "lon": -3.5000}
        zoom = 7.3
    elif provincia_elegida == 'León':
        center = {"lat": 42.6346, "lon": -5.9724}
        zoom = 7.8
    elif provincia_elegida == 'Palencia':
        center = {"lat": 42.4000, "lon": -4.5400}
        zoom = 7.75
    elif provincia_elegida == 'Salamanca':
        center = {"lat": 40.7500, "lon": -6.0255}
    elif provincia_elegida == 'Segovia':
        center = {"lat": 41.1000, "lon": -4.0000}
        zoom = 8.2
    elif provincia_elegida == 'Soria':
        center = {"lat": 41.6000, "lon": -2.5959}
    elif provincia_elegida == 'Valladolid':
        center = {"lat": 41.6987, "lon": -4.8418}
        zoom = 7.85
    else:
        center = {"lat": 41.6880, "lon": -6.0919}

if modo == 'Ganador de las elecciones':
    with c3:
        ganador = st.selectbox('Cada municipio tendrá el color del:',
                              ('Ganador', 'Segundo'))
else:
    with c3:
        partido_elegido = st.selectbox('Elija un partido o la participación electoral:',
                                      ('Participación', 'PP', 'PSOE', 'Vox', 'Podemos', 'Ciudadanos', 'UPL', 'XAV'))


mapa_cyl = "au.muni_cyl_recintos_comp.shp"
mapa_cyl = gpd.read_file(mapa_cyl)


@st.cache(show_spinner=False)
def seleccionar_elecciones(elecciones):
    if elecciones == "Elecciones generales noviembre de 2019":
        cyl_datos = pd.read_excel("CyL.xlsx", sheet_name="CyL noviembre 2019")
    elif elecciones == "Elecciones autonómicas mayo de 2019":
        cyl_datos = pd.read_excel("CyL.xlsx", sheet_name="CyL mayo 2019")
    else:
        cyl_datos = pd.read_excel("CyL.xlsx", sheet_name="CyL abril 2019")

    return cyl_datos


@st.cache(show_spinner=False)
def seleccionar_provincia(mapa, provincia):
    if provincia == 'Castilla y León':
        mapa_provincia = mapa

    else:
        codigo_provincia = ""
        for prov, codigo in (("Ávila", "05"), ("Burgos", "09"), ("León", "24"), ("Palencia", "34"),
                                  ("Salamanca", "37"), ("Segovia", "40"), ("Soria", "42"), ("Valladolid", "47"),
                                  ("Zamora", "49")):
            if prov == provincia:
                codigo_provincia = codigo

        mapa_provincia = mapa[mapa["c_prov_id"] == codigo_provincia]

    mapa_provincia.to_crs(pyproj.CRS.from_epsg(4326), inplace=True)
    mapa_provincia["codmun"] = mapa_provincia["codmun"].astype(int)

    return mapa_provincia


@st.cache(show_spinner=False)
def preparar_dataframe():
    cyl_datos = seleccionar_elecciones(elecciones_elegidas)
    mapa_provincia = seleccionar_provincia(mapa_cyl, provincia_elegida)
    mapa_provincia_merged = mapa_provincia.merge(cyl_datos, on="codmun")
    mapa_provincia_merged = mapa_provincia_merged.set_index("Municipio")

    return mapa_provincia_merged


@st.cache(suppress_st_warning=True, show_spinner=False)
def pintar_mapa_ganador(mapa_provincia_merged, coordenadas, zoom_arg):
    fig_provincia = px.choropleth_mapbox(mapa_provincia_merged, geojson=mapa_provincia_merged.geometry,
                                         locations=mapa_provincia_merged.index, color=ganador,
                                         color_discrete_map={"PSOE":"red",
                                                             "PP":"blue",
                                                             "VOX":'green',
                                                             "Podemos":"purple",
                                                             "Ciudadanos":"orange",
                                                             "UPL":"brown",
                                                             "Por Ávila":"black"},
                                         hover_data=(["Provincia", "Segundo"] if ganador == "Ganador" else ["Provincia", "Ganador"]),
                                         center=coordenadas,
                                         mapbox_style="open-street-map",
                                         zoom=zoom_arg,
                                         opacity=0.75,
                                         height=600)
    fig_provincia.update_geos(fitbounds="locations", visible=False)

    fig_provincia.update_layout(
        title_text=('Primera' if ganador=="Ganador" else 'Segunda') + ' fuerza en cada municipio de ' + provincia_elegida + ' en las ' + elecciones_elegidas,
        title=dict(x=0.5),
        plot_bgcolor="rgb(245, 245, 245)",
        margin={"r": 5, "t": 35, "l": 5, "b": 10},
        hoverlabel=dict(align="left", bgcolor="forestgreen", font_family="Rockwell", font_size=14))
    fig_provincia.update_traces(marker=dict(line=dict(color='grey')))

    return fig_provincia


def pintar_mapa_partidos(mapa_provincia_merged, coordenadas, zoom_arg):
    minimo_color_votos = 5
    maximo_color_votos = 40
    hover_data = ["Provincia", "Total censo electoral", partido_elegido + " Votos", partido_elegido + " %"]
    color_axis_colorbar = {'title':' % Votos',
                           'tickvals': ["10", "20", "30", "40"],
                           'ticktext': ["10", "20", "30", "40 o más"]}

    if partido_elegido == "PSOE":
        color = "Reds"
        bgcolor = "indianred"
    elif partido_elegido == "PP":
        color = "Blues"
        bgcolor = "lightblue"
    elif partido_elegido == "Vox":
        color = "Greens"
        bgcolor = "forestgreen"
    elif partido_elegido == "Podemos":
        color = "Purples"
        bgcolor = "rebeccapurple"
    elif partido_elegido == "Ciudadanos":
        color = "Oranges"
        bgcolor = "orangered"
    elif partido_elegido == "UPL":
        st.warning("El partido UPL sólo se presenta en las circunscripciones de León, Zamora y Salamanca")
        color = "pinkyl"
        bgcolor = "deeppink"
    elif partido_elegido == "XAV":
        st.warning("El partido XAV (Por Ávila) sólo se presenta en la circunscripción de Ávila")
        color = "Greys"
        bgcolor = "darkgray"
    else:
        color = "turbid"
        bgcolor = "floralwhite"
        minimo_color_votos = 40
        maximo_color_votos = 90
        hover_data = ["Provincia", "Total censo electoral", "Total votos", partido_elegido + " %"]
        color_axis_colorbar = {'title': ' % Votos',
                               'tickvals': ["40", "50", "60", "70", "80", "90"],
                               'ticktext': ["40", "50", "60", "70", "80", "90 o más"]}

    fig_provincia = px.choropleth_mapbox(mapa_provincia_merged, geojson=mapa_provincia_merged.geometry,
                                         locations=mapa_provincia_merged.index, color=partido_elegido + " %",
                                         hover_data=hover_data,
                                         color_continuous_scale=color,
                                         center=coordenadas,
                                         mapbox_style="open-street-map",
                                         opacity=0.75,
                                         zoom=zoom_arg,
                                         height=600)
    fig_provincia.update_geos(fitbounds="locations", visible=False)
    fig_provincia.update_coloraxes(cmin=minimo_color_votos, cmax=maximo_color_votos)

    fig_provincia.update_layout(
        title_text='Resultados de ' + partido_elegido + ' en ' + provincia_elegida + ' (Elecciones generales noviembre 2019)',
        title=dict(x=0.5),
        margin={"r":5,"t":35,"l":5,"b":10},
        hoverlabel =dict(align="left", bgcolor=bgcolor, font_family="Rockwell", font_size=14),
        coloraxis_colorbar=color_axis_colorbar)

    return fig_provincia


try:
    if modo == "Ganador de las elecciones":
        mapa_provincia = preparar_dataframe()
        mapa = pintar_mapa_ganador(mapa_provincia, center, zoom)
        st.plotly_chart(mapa, use_container_width=True)
    else:
        mapa_provincia = preparar_dataframe()
        mapa = pintar_mapa_partidos(mapa_provincia, center, zoom)
        st.plotly_chart(mapa, use_container_width=True)
except ValueError:
     st.warning("La configuración que ha elegido da lugar a un resultado inexistente."
                "Si ha seleccionado UPL o XAV en las elecciones de abril de 2019, no se puede desplegar ningún mapa,"
                " pues estos partidos no concurrieron a dichas elecciones. Por favor, seleccione otra configuración.")
