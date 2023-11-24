import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import ifcopenshell
import ifcopenshell.util.element as Element
import tempfile
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import os
import json
import re
import matplotlib.pyplot as plt
import base64
import pdfkit

st.set_page_config(page_title="Que es IFC", page_icon="📈")


st.write("# Que es un archivo/modelo IFC! ")
# Crear la aplicación de Streamlit
st.markdown("<h1 style='text-left: center; font-size: 25px;'>¿Que es un modelo IFC, para que sirve y para que no sirve?</h1>", unsafe_allow_html=True)
st.write("Según la definición del Estándar BIM para Proyectos Públicos de Planbim, IFC o Industry Foundation Classes es un “esquema de base de datos ampliable que representa información de la construcción para el intercambio de distintos software para arquitectura, ingeniería y construcción.”") 
st.write("Versión de revisón IFC: IFC4_ADD2_TC1 - 4.0.2.1 [Official]") 

st.markdown("<h1 style='text-left: center; font-size: 25px;'>Estructura modelos IFC:</h1>", unsafe_allow_html=True)
st.write("La estructura de un modelo IFC se compone de distintos tipos de datos, estos datos pueden ser geométricos como tambien no geométrica (información).")

st.markdown("<h1 style='text-left: center; font-size: 25px;'>Información geométrica</h1>", unsafe_allow_html=True)
st.write("Información geométrica: se compone de dos tipos, información parametrica y BREP (Boundary Representation)")
st.write("Información parametrica: Se refiere a una representación geométrica de objetos de construcción que se define mediante parámetros y fórmulas matemáticas. En lugar de describir una forma geométrica de manera estática y precisa, la geometría paramétrica utiliza parámetros variables para definir y modificar la forma y las propiedades de un objeto.")
st.write("BREP (Boundary Representation): Es una técnica de modelado que se utiliza para representar la geometría detallada y la topología de objetos de construcción en un modelo BIM. Esto es esencial para lograr una representación precisa y detallada y estática.")

st.markdown("<h1 style='text-left: center; font-size: 25px;'>Información no geométrica (Información)</h1>", unsafe_allow_html=True)
st.write("Información no geométrica o información se clasifica en Entidades o clases, atributos y propiedades")

st.markdown("<h1 style='text-left: center; font-size: 25px;'>Entidades o clases</h1>", unsafe_allow_html=True)
st.write("las Entidades o clases: Se refiere a una clase de información que se define por un conjunto específico de atributos y restricciones comunes. Las entidades son elementos fundamentales en la estructura de datos de un modelo IFC y se utilizan para representar distintos tipos de objetos o componentes en un proyecto de construcción. como puertas, muros, ventanas, etc.")

st.markdown("<h1 style='text-left: center; font-size: 25px;'>Atributos</h1>", unsafe_allow_html=True)
st.write("Atributos: Los atributos son unidades de información que se utilizan para describir las características y propiedades de las entidades o clases de información.")

st.markdown("<h1 style='text-left: center; font-size: 25px;'>Propiedades</h1>", unsafe_allow_html=True)
st.write("Propiedades: Se refiere a una unidad de información que se define dinámicamente como una instancia particular de una entidad.Las propiedades en un modelo IFC pueden variar de una instancia de entidad a otra, lo que permite la flexibilidad para describir características específicas de cada objeto.")

