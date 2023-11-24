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

st.set_page_config(page_title="Revisor de Modelos IFC", page_icon="📈")

st.title("Revisor de Modelos IFC")

def cargar_datos_desde_json(tipo_modelo, nivel_avance):
    # Genera la ruta completa del archivo JSON basado en la selección del usuario
    nombre_archivo = f"{tipo_modelo}_{nivel_avance}.json"
    ruta_archivo = os.path.join("D:\documentos\IfcStudio\Json", nombre_archivo)
    
    try:
        # Intenta abrir y cargar el archivo JSON correspondiente
        with open(ruta_archivo, 'r') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        st.error(f"No existe EAIM para este tipo de modelo.")
        return None
    except Exception as e:
        st.error(f"Error datos")
        return None


def obtener_informacion(data, tipo_modelo, nivel_avance):
    if data and tipo_modelo in data and nivel_avance in data[tipo_modelo]:
        info_seleccionada = data[tipo_modelo][nivel_avance]
        rows = []
        for entidad, ndi_info in info_seleccionada.items():
            for ndi, ndi_data in ndi_info.items():
                atributos = ndi_data.get('Atributos', None)
                Propiedades = ndi_data.get('Propiedades', None)

                # Utiliza apply con una función lambda para formatear la columna 'Atributos'
                atributos_str = ', '.join(atributos) if atributos else ''

                rows.append([entidad, ndi, atributos_str, Propiedades])

        df = pd.DataFrame(rows, columns=['Entidad', 'NDI', 'Atributos', 'Propiedades'])
        return df
    else:
        return pd.DataFrame({'Mensaje': ['No se encontró información para la selección']})


# Crear la aplicación de Streamlit con el tamaño de título personalizado
#st.markdown("<h1 style='text-left: center; font-size: 35px;'>Revisor de Modelos IFC</h1>", unsafe_allow_html=True)

# Definir las listas de tipos de modelo y niveles de avance
tipos_modelo = ["Sitio", "Volumetrico", "Arquitectura","Estructura",
               "MEP", "Coordinacion", "Construccion", "As-Built", "Operacion"]

nivel_avance = ["DC", "DA", "DB", "DD", "CC", "CM","AB","PM","GM"]

# Etiqueta para el tipo de modelo
st.write("Seleccione el tipo de modelo:")
tipo_modelo = st.selectbox("Tipo de Modelo:", tipos_modelo)

# Etiqueta para el nivel de avance
st.write("Seleccione el EAIM:")
nivel_avance = st.selectbox("EAIM:", nivel_avance)

data = cargar_datos_desde_json(tipo_modelo, nivel_avance)   
 
# Agrega un botón de "Aceptar"
if st.button("Aceptar"):
    st.write("Entidades, atributos y propiedades minimas de EBPP")
    # Código que se ejecutará cuando se presione el botón
    resultado_df = obtener_informacion(data, tipo_modelo, nivel_avance)
    #st.write(resultado_df)  # Muestra el resultado en la aplicación

resultado_df = obtener_informacion(data, tipo_modelo, nivel_avance)

    
# Crear la aplicación de Streamlit con el tamaño de título personalizado
st.markdown("<h1 style='text-left: center; font-size: 25px;'>Cargar Modelo IFC</h1>", unsafe_allow_html=True)
#st.write("Seleccione y cargue el modelo ifc que desea validar:")

def get_objects_data_by_class(entity):
    psets = Element.get_psets(entity)
    attribute_names = [attribute for attribute in dir(entity) if not attribute.startswith("_")]
    
    # Initialize a dictionary to store properties grouped by Pset name
    propiedades_dict = {}

    for pset_name, properties in psets.items():
        propiedades = []
        for property_name, property_value in properties.items():
            if isinstance(property_value, ifcopenshell.entity_instance):
                property_value = property_value.Name
            propiedades.append(property_name)
        propiedades_dict[pset_name] = propiedades

    object_data = {
        'Entidad': entity.is_a(),
        'Atributos': ', '.join(attribute_names),
        'Propiedades': propiedades_dict,
    }

    return object_data

class_type = "IfcProduct"  # Change this to the desired class

def main():
    df_Ifc = None
    tmp_filename = None
    
    archivo_subido = st.file_uploader("Seleccione y cargue el modelo ifc que desea validar:", type=["ifc"])

    if archivo_subido is not None:
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(archivo_subido.read())
            tmp_filename = tmp_file.name

        modelo = ifcopenshell.open(tmp_filename)
        entity_list = modelo.by_type(class_type)  # Use 'class_type' here
        entity_data_list = [get_objects_data_by_class(entidad) for entidad in entity_list]

        df = pd.DataFrame(entity_data_list)
        df_Ifc = df.drop_duplicates(subset=["Entidad", "Atributos"])

        # Eliminar el archivo temporal
        #os.unlink(tmp_filename)

    # Return the DataFrame df_Ifc
    return df_Ifc

df_Ifc  = main()

# Crear la aplicación de Streamlit
st.markdown("<h1 style='text-left: center; font-size: 25px;'>Iniciar validación</h1>", unsafe_allow_html=True)
st.write("haga click en validar para obtener estadisitcas de cumplimiento de su modelo :")  


# Cargar el primer DataFrame
df1 = resultado_df
#st.write(df1)
# Cargar el segundo DataFrame
df2 = df_Ifc
#st.write(df2)

# Inicializar un nuevo DataFrame para resumir los resultados
resumen = pd.DataFrame(columns=['Entidad', 'Entidad_existe_si/no', 'Atributos', 'Atributos_existe_si/no'])
   

# Crear un botón de validación
if st.button("Validar Ifc"):
    # Revisar las entidades
    for entidad in df1['Entidad']:
        if entidad in df2['Entidad'].values:
            cumple_entidad = 'Si'
        else:
            cumple_entidad = 'La entidad no existe en el modelo'
        row = pd.DataFrame({'Entidad': [entidad], 'Entidad_existe_si/no': [cumple_entidad]})
        resumen = pd.concat([resumen, row], ignore_index=True)

    # Revisar los atributos
    for entidad, atributos in zip(df1['Entidad'], df1['Atributos']):
        if entidad in df2['Entidad'].values:
            # Dividir los atributos de df2 en una lista
            atributos_df2 = df2[df2['Entidad'] == entidad]['Atributos'].iloc[0].split(", ")
            
            # Verificar si alguno de los atributos en df1 coincide con los atributos en df2
            if any(atributo in atributos_df2 for atributo in atributos.split(', ')):
                cumple_atributo = 'Si'
                
            else:
                cumple_atributo = 'No'

        else:
            cumple_atributo = 'No'  # Si la entidad no existe en df2, los atributos tampoco pueden existir
      
        resumen.loc[resumen['Entidad'] == entidad, 'Atributos'] = atributos
        resumen.loc[resumen['Entidad'] == entidad, 'Atributos_existe_si/no'] = cumple_atributo

    # Rellenar los valores faltantes en el DataFrame de resumen2
    resumen.fillna('', inplace=True)

    # Mostrar el resumen de propiedades en Streamlit
    st.write("Resultados de Validación de entidades y atributos:")
    st.write(resumen)
   
    # Datos del DataFrame 1
    data_df1 = {
        'Entidad': df1['Entidad'],
        #'Grupo de Propiedades': df1['Propiedades'].apply(lambda x: set(x.keys())),
        'Propiedades': df1['Propiedades'].apply(lambda x: ', '.join([f'{key}: {value}' for key, value in x.items()]))
    }
    df1_nuevo = pd.DataFrame(data_df1)

    # Datos del DataFrame 2
    data_df2 = {
        'Entidad': df2['Entidad'],
        #'Grupo de Propiedades': df2['Propiedades'].apply(lambda x: set(x.keys())),
        'Propiedades': df2['Propiedades'].apply(lambda x: ', '.join([f'{key}: {value}' for key, value in x.items()]))
    }
    df2_nuevo = pd.DataFrame(data_df2)
      
    #st.write(df1_nuevo)
    #st.write(df2_nuevo)
    
    # Encontrar grupos que coinciden y que no coinciden
    grupos_coinciden = df1_nuevo[df1_nuevo.apply(lambda x: x['Entidad'] in df2_nuevo['Entidad'].values, axis=1)]
    grupos_no_coinciden1 = df1_nuevo[~df1_nuevo['Entidad'].isin(df2_nuevo['Entidad'].values)]
    #grupos_no_coinciden2 = df2_nuevo[~df2_nuevo['Entidad'].isin(df1_nuevo['Entidad'].values)]
    #st.write(grupos_coinciden)
    st.write("Propiedades que faltan agregar por entidad")
    st.write(grupos_no_coinciden1)
    
    
    propiedades1= grupos_coinciden
    propiedades2 = df2_nuevo
    
    #st.write(propiedades1)
    #st.write(propiedades2)
    
    # Función para extraer grupos y propiedades de la cadena
    def extraer_grupos_propiedades(cadena):
        grupos_propiedades = re.findall(r"(\w+): \[(.*?)\]", cadena)
        resultado = {}
        for grupo, propiedades in grupos_propiedades:
            resultado[grupo] = propiedades.split(', ')
        return resultado
 
    # Crear una lista para almacenar los datos
    data = []

    # Iterar a través de las filas de propiedades1
    for index, row in propiedades1.iterrows():
        entidad = row['Entidad']
        propiedades_grupo1 = extraer_grupos_propiedades(row['Propiedades'])
        
        # Iterar sobre los grupos y propiedades en el grupo
        for grupo, propiedades in propiedades_grupo1.items():
            if entidad in propiedades2['Entidad'].values:
                propiedades_grupo2 = extraer_grupos_propiedades(propiedades2[propiedades2['Entidad'] == entidad]['Propiedades'].values[0])
                coincide_grupo = "Si" if grupo in propiedades_grupo2 else "No"
                
                propiedades_coinciden = []
                for propiedad in propiedades:
                    if propiedad in propiedades_grupo2.get(grupo, []):
                        coincide_propiedad = "Si"
                    else:
                        coincide_propiedad = "No"
                    propiedades_coinciden.append((propiedad, coincide_propiedad))
            else:
                coincide_grupo = "No"
                propiedades_coinciden = [(propiedad, "No") for propiedad in propiedades]

            data.extend([(entidad, grupo, coincide_grupo, prop, coincide_prop) for prop, coincide_prop in propiedades_coinciden])

    # Crear el DataFrame
    df = pd.DataFrame(data, columns=["Entidad", "Grupo", "Grupo_coincide_si/no_EBPP", "Propiedad", "Propiedad_coincide_si/no_EBPP"])
    
    st.write("Resultados de Validación: grupos de propiedades y propiedades:")
    # Imprimir el DataFrame
    st.write(df)
   
     
    # Definir los colores que deseas usar para cada sección
    colores = ['#1f77b4', '#ff7f0e']  # Puedes cambiar estos códigos de color según tus preferencias
    
    
    # Crear un DataFrame a partir de resultados_df
    resultados_df_dataframe = pd.DataFrame(resumen)
    
    # Realizar estadísticas simples sobre resultados_df_dataframe
    if not resultados_df_dataframe.empty:
        st.subheader("Estadísticas sobre los resultados")
        num_coincidencias = len(resultados_df_dataframe[resultados_df_dataframe['Entidad_existe_si/no'] == "Si"])
        num_diferencias = len(resultados_df_dataframe[resultados_df_dataframe['Entidad_existe_si/no'] == "La entidad no existe en el modelo"])
        # Crear un gráfico de anillo con Plotly para las estadísticas globales
        anillo = px.pie(
            names=["La entidad existe en el modelo", "La entidad no existe en el modelo"],
            values=[num_coincidencias, num_diferencias],
            hole=0.4,  # Controla el tamaño del agujero en el centro del gráfico (0.4 significa un donut)
            color_discrete_sequence=colores,  # Especifica los colores personalizados aquí
            labels={"names": "Estadisitcas del modelo"}
        )
            # Personalizar el diseño del gráfico
        anillo.update_layout(
            title='Cumplimiento del modelo según EBPP '
            )
        # Mostrar el gráfico de anillo en Streamlit
        st.plotly_chart(anillo)

    
    # Calcular el recuento de cada tipo en 'Entidad_existe_si/no'
    counts = resultados_df_dataframe['Entidad_existe_si/no'].value_counts()
    # Definir los colores que deseas usar para cada sección
    colores = ['#1f77b4', '#ff7f0e']  # Puedes cambiar estos códigos de color según tus preferencias
    # Filtrar el DataFrame para obtener los nombres de entidades donde 'Entidad_existe_si/no' es igual a 'Si'
    nombres_entidades = resumen[resumen['Entidad_existe_si/no'] == 'Si']['Entidad']
    nombres_entidades2 = resumen[resumen['Entidad_existe_si/no'] == 'La entidad no existe en el modelo']['Entidad']
    serie_de_nombres = pd.Series(nombres_entidades)
    serie_de_nombres2 = pd.Series(nombres_entidades2)
    # Concatena los elementos de la serie en un solo texto
    texto_concatenado = serie_de_nombres.str.cat(sep=',')
    texto_concatenado1 = serie_de_nombres2.str.cat(sep=',')   

    # Crear el gráfico de barras personalizado con los valores numéricos encima de las barras y colores personalizados
    fig = go.Figure()
    
    for index, row in counts.items():
        color_barra = colores.pop(0)  # Obtener el próximo color de la lista
        entidad_name = nombres_entidades if index == 'Si' else nombres_entidades2
        entidad_name = ', '.join(entidad_name)  # Convierte la lista en una cadena separada por comas
        fig.add_trace(go.Bar(
            x=[index],
            y=[row],
            text=[row],  # Agregar el valor numérico encima de la barra
            textposition=['outside'],  # Posicionar el valor fuera de la barra
            name=str(index),  # Usar el valor como etiqueta
            marker_color=color_barra  # Establecer el color de la barra
        ))

    # Personalizar el diseño del gráfico
    fig.update_layout(
        xaxis_title='Cumplimiento',
        yaxis_title='N° de Clases',   #[f"{index} ({entidad_name})"]
        title='Cumplimiento por Entidades',
        yaxis_title_text="N° de Clases"
    )
    
    st.write("Entidades que cumplen: "+texto_concatenado) 
    st.write("Entidades que no cumplen: "+texto_concatenado1) 
    # Mostrar el gráfico de barras en Streamlit
    #st.plotly_chart(fig)
    
       
    # Crear un DataFrame a partir de resultados_df
    df = pd.DataFrame(df)

    # Realizar estadísticas y crear un gráfico de barras apilado con Plotly
    fig1 = go.Figure()

    # Agrupar los datos y crear un gráfico de barras apilado
    grouped = df.groupby(['Entidad', 'Grupo_coincide_si/no_EBPP']).size().reset_index(name='Cantidad')
    fig1 = px.bar(grouped, x='Entidad', y='Cantidad', color='Grupo_coincide_si/no_EBPP',color_discrete_sequence=['#1f77b4', 'lightblue'])

    # Personalizar el diseño del gráfico
    fig1.update_layout(
        xaxis_title='Entidad',
        yaxis_title='Cumplimiento',
        title='Cumplimiento de grupos de propiedades por entidades existentes en el modelo',
    )
    
    fig1.update_traces(texttemplate='%{y}', textposition='outside')

    # Mostrar el gráfico con st.plotly_chart en Streamlit
    st.plotly_chart(fig1)
    
    # Crear un DataFrame a partir de resultados_df
    df = pd.DataFrame(df)

    # Realizar estadísticas y crear un gráfico de barras apilado con Plotly
    barra_propiedades = go.Figure()

    # Agrupar los datos y crear un gráfico de barras apilado
    grouped = df.groupby(['Grupo', 'Propiedad_coincide_si/no_EBPP']).size().reset_index(name='Cantidad')
    barra_propiedades = px.bar(grouped, x='Grupo', y='Cantidad', color='Propiedad_coincide_si/no_EBPP',color_discrete_sequence=['#1f77b4', 'lightblue'])

    # Personalizar el diseño del gráfico
    barra_propiedades.update_layout(
        xaxis_title='Entidad',
        yaxis_title='Cumplimiento',
        title='Cumplimiento propiedades por grupo de propiedades',
        margin=dict(l=50, r=50, b=250, t=50)  # Márgenes izquierdo, derecho, inferior y superior
    )

    # Agregar el valor numérico encima de cada barra
    barra_propiedades.update_traces(texttemplate='%{y}', textposition='inside')

    # Mostrar el gráfico con st.plotly_chart en Streamlit
    st.plotly_chart(barra_propiedades)
    
           
    # Crear un escritor Excel para guardar los DataFrames en hojas diferentes
    with pd.ExcelWriter('resultados_validacion.xlsx', engine='xlsxwriter') as writer:
        resumen.to_excel(writer, sheet_name='Resumen_entidades')
        df.to_excel(writer, sheet_name='Resumen_Propiedades')
        grupos_no_coinciden1.to_excel(writer, sheet_name='entidades_propiedades_faltantes')

    # Generar el enlace para descargar el archivo Excel
    with open('resultados_validacion.xlsx', 'rb') as f:
        excel_data = f.read()
    b64 = base64.b64encode(excel_data).decode()
    href = f'<a href="data:file/excel;base64,{b64}" download="resultados_validacion.xlsx">Descargar Resultados de Validación (Excel)</a>'
    st.markdown(href, unsafe_allow_html=True)
    
    # Guardar los gráficos como imágenes JPG
    pio.write_image(anillo, 'grafico_anillo.jpg', format='jpg',width=800, height=600,)
    pio.write_image(fig1, 'grafico_barras_entidades.jpg', format='jpg',width=800, height=600)
    pio.write_image(barra_propiedades, 'grafico_barras_propiedades.jpg', format='jpg',width=1200, height=800)

    # Función para crear enlaces de descarga
    def get_binary_file_downloader_html(bin_file, file_label='Archivo'):
        with open(bin_file, 'rb') as f:
            data = f.read()
        bin_str = base64.b64encode(data).decode()
        href = f'<a href="data:file/jpg;base64,{bin_str}" download="{file_label}.jpg">Descargar {file_label}</a>'
        return href

    # Agregar enlaces de descarga para los gráficos
    st.markdown(get_binary_file_downloader_html('grafico_anillo.jpg', 'Grafico_Anillo'), unsafe_allow_html=True)
    st.markdown(get_binary_file_downloader_html('grafico_barras_entidades.jpg', 'grafico_barras_entidades'), unsafe_allow_html=True)
    st.markdown(get_binary_file_downloader_html('grafico_barras_propiedades.jpg', 'grafico_barras_propiedades'), unsafe_allow_html=True)
        
#st.write(df)


resultado_dict = {}
# Mostrar el valor obtenido
if 'df' in locals():
    #st.write(df)
        
    # Filtrar el DataFrame original según la condición "Grupo_coincide_si/no_EBPP" sea "No"
    df_filtrado = df[df['Grupo_coincide_si/no_EBPP'] == 'No']
    
    # Seleccionar las columnas de interés
    mapeo_de_grupos = df_filtrado[['Grupo']]
    mapeo_de_propiedades = df_filtrado[['Propiedad']]
    mapeo_de_entidad = df_filtrado[['Entidad']]
    
    # Combinar los resultados en un solo DataFrame
    resultado_de_validacion = pd.concat([mapeo_de_entidad,mapeo_de_grupos, mapeo_de_propiedades], axis=1)
    
    # Convertir el DataFrame a una cadena JSON
    resultado_json = resultado_de_validacion.to_json(orient='records')
        
    resultado_dict = {}

    for entidad, grupo, propiedad in resultado_de_validacion[['Entidad', 'Grupo', 'Propiedad']].values:
        entidad_dict = resultado_dict.setdefault(entidad, {})
        propiedades_dict = entidad_dict.setdefault('Propiedades', {})
        
        if grupo not in propiedades_dict:
            propiedades_dict[grupo] = [propiedad]
        else:
            propiedades_dict[grupo].append(propiedad)
     
    
    # Mostrar el resultado en formato JSON
    #resultado_json = json.dumps(resultado_dict, indent=4)
    # Mostrar el JSON en Streamlit
    #st.write("Resultado de la validación (JSON):")
    #st.write(resultado_dict)


ifcfile = None  # Definir ifcfile en el ámbito global
ifc_path = None  # Definir ifc_path en el ámbito global
save_path = None  # Definir save_path en el ámbito global


# Función para cargar el archivo IFC
def cargar_archivo_ifc(ifc_file):
    global ifcfile, ifc_path  # Usar las variables ifcfile e ifc_path globales
    if ifc_file is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".ifc") as temp_file:
            temp_file.write(ifc_file.read())
            ifc_path = temp_file.name
            ifcfile = ifcopenshell.open(ifc_path)
        return ifcfile  


# Función para procesar los archivos cargados
def procesar_archivos(ifcfile, json_data):
    if ifcfile is not None and json_data is not None:
        owner_history = ifcfile.by_type("IfcProduct")[0]

        for entity_type, entity_info in json_data.get(f"{tipo_modelo}", {}).get(f"{nivel_avance}", {}).items():
            for _, data in entity_info.items():
                propiedades = data.get("Propiedades", {})

                try:
                    # Filtrar entidades por tipo
                    entities = set([entity for entity in ifcfile.by_type(entity_type) if entity.is_a(entity_type)])
                    for entity in entities:
                        for pset_name, properties in propiedades.items():
                            property_set = None
                            existing_property_sets = entity.IsDefinedBy
                            for existing_pset in existing_property_sets:
                                if hasattr(existing_pset, "RelatingPropertyDefinition") and hasattr(existing_pset.RelatingPropertyDefinition, "HasProperties") and hasattr(existing_pset.RelatingPropertyDefinition, "Name"):
                                    if existing_pset.RelatingPropertyDefinition.Name == pset_name:
                                        property_set = existing_pset
                                        break
                                     
                            if property_set is None:
                                property_values = []
                                for property_name in set(properties):  # Utiliza un conjunto para obtener propiedades únicas
                                    # Verificar si la propiedad ya existe por su nombre
                                    if not any(p.Name == property_name for p in property_values):
                                        property_values.append(
                                            ifcfile.createIfcPropertySingleValue(property_name, "Value", ifcfile.create_entity("IfcText", "0"), None)
                                        )
                                #print(f"Propiedades a agregar al conjunto: {property_values}")

                                # Crear un nuevo conjunto de propiedades y asignarlo a la entidad
                                property_set = ifcfile.createIfcPropertySet(entity.GlobalId, owner_history, pset_name, None, property_values)
                                ifcfile.createIfcRelDefinesByProperties(entity.GlobalId, owner_history, None, None, [entity], property_set)
                            else:
                                # Si se encontró un conjunto de propiedades existente, verificar y crear propiedades que falten
                                existing_properties = set(p.Name for p in property_set.RelatingPropertyDefinition.HasProperties)
                                missing_properties = set(properties) - existing_properties

                                if missing_properties:
                                    missing_property_values = []
                                    for property_name in missing_properties:
                                        if not any(p.Name == property_name for p in property_values):
                                            missing_property_values.append(
                                                ifcfile.createIfcPropertySingleValue(property_name, "Value", ifcfile.create_entity("IfcText", "0"), None)
                                            )

                                    # Actualizar el conjunto de propiedades existente con las propiedades faltantes
                                    property_set.RelatingPropertyDefinition.HasProperties = list(property_set.RelatingPropertyDefinition.HasProperties) + missing_property_values
                                    #print(f"Propiedades agregadas al conjunto existente: {missing_properties}")

                except Exception as e:
                    print(f"Error al procesar entidad '{entity_type}': {str(e)}")





# Función para obtener el enlace de descarga
def get_binary_file_downloader_html(bin_file, label='Archivo'):
    if bin_file is not None:
        with open(bin_file, 'rb') as f:
            data = f.read()
        b64 = base64.b64encode(data).decode()
        href = f'<a href="data:application/octet-stream;base64,{b64}" download="{os.path.basename(bin_file)}">{label}</a>'
        return href
    else:
        return ''  # Si no se ha cargado un archivo IFC, devuelve una cadena vacía


