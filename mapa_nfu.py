# -*- coding: utf-8 -*-


import pandas as pd 
import folium

# Leer los archivos csv y convertir todo a string
df = pd.read_excel("/content/NFU_RN2000.csv").convert_dtypes()
df2 = pd.read_excel('/content/NFU.csv').convert_dtypes()

# Unir los dataframes por la columna 'Id' mediante una Left Join
joined = df.merge(df2, on='Id', how='left')

# Seleccionar las columnas deseadas de todas que se han producido
joined = joined[['Id', 'Latitud', 'Longitud', 'Municipio_x', 'Provincia_x', 'Ubicación_x', 'Cantidad_x', 'Código LIC', 'Código ZEPA']]

# Convertir '-' a 'False' y rellenar los valores nulos también con 'False'
joined[['Código LIC', 'Código ZEPA']] = joined[['Código LIC', 'Código ZEPA']].fillna('False').replace('-', 'False')

# Añadir una nueva columna 'Descripción' desde df y rellenar los valores nulos
joined['Descripción'] = df.iloc[:, 7].fillna('NeumaticOUT')

# Añadir una nueva columna 'Fuente' al dataframe
joined['Fuente'] = ['MARNOBA' if 'MARNOBA' in i else 'NeumaticOUT' for i in joined['Descripción']]

joined

# Crea un objeto Map centrado en España con el mapa de satélite de ESRI
m = folium.Map(
    location=[40.965, -5.664], 
    zoom_start=6, 
    tiles=folium.TileLayer(
        tiles = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr = 'Esri',
        name = 'Esri Satellite',
        overlay = False,
        control = True
       ))

#Añado las capas que me interesan/gustan
folium.TileLayer(tiles='OpenStreetMap', name='Open Street Map').add_to(m)
folium.TileLayer(
        tiles = 'https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}',
        attr = 'Google',
        name = 'Google Satellite',
        overlay = False,
        control = True).add_to(m)
folium.TileLayer(tiles='https://stamen-tiles-{s}.a.ssl.fastly.net/toner-hybrid/{z}/{x}/{y}.png',
                 attr ='Map tiles by http://stamen.com', 
                 name='Stamen.TonerHybrid',
                 overlay = True,
                 control = True).add_to(m)


# Crea un objeto de control de capas y lo agrega al mapa
folium.LayerControl().add_to(m)

# Extrae la información de los puntos y crea marcadores con información personalizada
for point in joined.iterrows():
    y = point[1]['Latitud']
    x = point[1]['Longitud']
    provincia = point[1]['Provincia_x']
    cantidad = point[1]['Cantidad_x']
    cod_lic = point[1]['Código LIC']
    cod_zepa = point[1]['Código ZEPA']
    municipio = point[1]['Municipio_x']
    fuente = point[1]['Fuente']
    id_ = point[1]['Id']
    #Añado marcadores según si están en la RN y si son LIC,ZEPA o ambas
    if cod_lic != 'False' and cod_zepa !='False':
      texto = f' <b>Id:</b> {id_} <br> <b>Municipio:</b> {municipio} <br> <b>Provincia:</b> {provincia} <br> <b>Cantidad:</b> {cantidad} <br> <b>ZEPA:</b> {cod_zepa} <br> <b>LIC:</b> {cod_lic} <br> <b>Fuente:</b> {fuente}'
      popup = folium.Popup(texto, min_width=100, max_width=500)           
      folium.Marker([y, x], popup=popup, tooltip='Click para ver información',icon=folium.Icon(color= 'green')).add_to(m)
    elif cod_zepa !='False':
      texto = f' <b>Id:</b> {id_} <br> <b>Municipio:</b> {municipio} <br> <b>Provincia:</b> {provincia} <br> <b>Cantidad:</b> {cantidad} <br> <b>ZEPA:</b> {cod_zepa} <br> <b>Fuente:</b> {fuente}'
      popup = folium.Popup(texto, min_width=100, max_width=500)           
      folium.Marker([y, x], popup=popup, tooltip='Click para ver información',  icon=folium.Icon(color= 'green')).add_to(m)
    elif cod_lic != 'False':
      texto = f'<b>Id:</b> {id_} <br> <b>Municipio:</b> {municipio} <br> <b>Provincia:</b> {provincia} <br> <b>Cantidad:</b> {cantidad} <br> <b>LIC:</b> {cod_lic} <br> <b>Fuente:</b> {fuente}'
      popup = folium.Popup(texto, min_width=100, max_width=500)           
      folium.Marker([y, x], popup=popup, tooltip='Click para ver información', icon=folium.Icon(color= 'green')).add_to(m)
    else:
      texto = f' <b>Id:</b> {id_} <br> <b>Municipio:</b> {municipio} <br> <b>Provincia:</b> {provincia} <br> <b>Cantidad:</b> {cantidad} <br> <b>Fuente:</b> {fuente}'
      popup = folium.Popup(texto, min_width=100, max_width=500)           
      folium.Marker([y, x], popup=popup, icon=folium.Icon(color="cadetblue"), tooltip='Click para ver información').add_to(m)

# Crea una leyenda para los marcadores
legend_html = '''
   <div style="position: fixed;
    bottom: 50px; 
    left: 50px;
    width: 180px;
    height: 110px;
    border:2px solid grey;
    z-index:9999;
    font-size:14px; 
    background-color: white; 
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.2); 
    border-radius: 5px;
     padding: 10px;"
     >
    <h4 style="margin: 0 0 10px;"><b>Zonas con NFU</b></h4>
    <div style="display: flex; align-items: center; margin-bottom: 5px;">
        <i class="fa fa-map-marker fa-2x" style="color:#8BC34A"></i>
        <span style="margin-left: 10px;">LIC y/o ZEPA</span>
    </div>
    <div style="display: flex; align-items: center;">
        <i class="fa fa-map-marker fa-2x" style="color:#427e80"></i>
        <span style="margin-left: 10px;">Otras zonas</span>
    </div>
</div>

'''

m.get_root().html.add_child(folium.Element(legend_html))

# Guarda el mapa en un archivo HTML
m.save('mapadef.html')


