import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
from io import BytesIO

# Configuration de la page
st.set_page_config(
    page_title="Onacc Climate Forecast Analysis",
    page_icon="⛅",
    layout="wide"
)

# Style CSS personnalisé
st.markdown("""
    <style>
    .main {background-color: #fff;}
    h1 {color: #1f77b4;}
    h2 {color: #2ca02c; border-bottom: 2px solid #1f77b4;}
    .stTextArea textarea {height: 150px;}
    .stDownloadButton button {width: 100%;}
    .logo {text-align: center;}
    .dataframe {margin-bottom: 20px;}
    .doc-section {margin: 20px 0; padding: 15px; background: #fff; border-radius: 10px;}
    code {background: #f0f0f0; padding: 2px 5px; border-radius: 3px;}
    </style>
    """, unsafe_allow_html=True)

# Navigation
pages = {
    "Application": "app",
    "Documentation": "docs"
}

st.sidebar.title("Navigation")
selected_page = st.sidebar.radio("", list(pages.keys()))

# Page de documentation
if selected_page == "Documentation":
    st.title("📚 Documentation - Onacc Climate Forecast")
    
    with st.expander("## 🌟 Présentation générale", expanded=True):
        st.markdown("""
        ### Objectif de l'application
        Cette application permet de générer des prévisions météorologiques pour des localités spécifiques en utilisant :
        - Des coordonnées GPS (latitude/longitude)
        - Un fichier Excel de localités
        - L'API ONACC-MC

        ### Fonctionnalités clés
        - Import de fichiers Excel avec gestion des localités
        - Filtrage multicritère (région/pays)
        - Visualisation interactive des données
        - Export des résultats en CSV/Excel
        - Prévisions sur mesure (1 à 14 jours)
        """)

    with st.expander("## 🛠 Guide d'utilisation", expanded=False):
        st.markdown("""
        ### Workflow principal
        1. **Importation des données** (Section 📤 Importer un fichier)
        2. **Filtrage des localités** (Région/Pays)
        3. **Sélection des coordonnées**
        4. **Configuration des paramètres**
        5. **Génération des prévisions**
        6. **Export des résultats**

        ### Préparation des données
        Format du fichier Excel requis :
        ```csv
        localite,latitude,longitude,altitude,region,country
        Yaoundé,3.8480,11.5021,726,Centre,Cameroun
        Douala,4.0511,9.7679,13,Littoral,Cameroun
        ```

        ### Formats d'export
        - CSV : Structure légère pour analyse rapide
        - Excel : Format complet avec mise en forme
        """)

    with st.expander("## 🚀 Déploiement", expanded=False):
        st.markdown("""
        ### Prérequis
        - Python 3.8+
        - Librairies : `streamlit pandas requests plotly openpyxl xlsxwriter`

        ### Installation
        ```bash
        # Cloner le dépôt
        git clone https://github.com/onacc/weather-forecast-app.git
        
        # Installer les dépendances
        pip install -r requirements.txt
        
        # Lancer l'application
        streamlit run app.py
        ```

        ### Déploiement en production
        1. **Docker** :
        ```dockerfile
        FROM python:3.9-slim
        COPY . /app
        WORKDIR /app
        RUN pip install -r requirements.txt
        CMD ["streamlit", "run", "app.py", "--server.port=8501"]
        ```

        2. **Services cloud** :
        - AWS EC2
        - Google Cloud Run
        - Azure App Service
        - Heroku
        """)

    with st.expander("## 🆘 Support technique", expanded=False):
        st.markdown("""
        ### Problèmes courants
        | Symptôme | Solution |
        |----------|----------|
        | Erreur API | Vérifier la connexion internet |
        | Format de fichier invalide | Valider les colonnes obligatoires |
        | Données manquantes | Vérifier les filtres appliqués |

        ### Contact support
        **Équipe Onacc - DSI**  
        📧 poum.bimbar@onacc.org  
        """)

    st.stop()

# Entête avec logo
col1, col2 = st.columns([1, 4])
with col1:
    st.image("./logo.png", width=100)
with col2:
    st.title("Onacc Climate Forecast Analysis")
    st.caption("Powered by Onacc")

# Gestion de l'état de session
if 'coordinates' not in st.session_state:
    st.session_state.coordinates = ""
if 'selected_locations' not in st.session_state:
    st.session_state.selected_locations = pd.DataFrame()

# Section d'importation de fichier
with st.expander("📤 Importer un fichier de localités", expanded=True):
    uploaded_file = st.file_uploader(
        "Télécharger un fichier Excel (format requis : localite,latitude,longitude,altitude,region,country)",
        type=["xlsx"]
    )

    if uploaded_file:
        try:
            df_locations = pd.read_excel(uploaded_file)
            required_columns = ['localite', 'latitude', 'longitude', 'region', 'country']
            
            if not all(col in df_locations.columns for col in required_columns):
                st.error("Structure de fichier incorrecte! Les colonnes requises sont : localite, latitude, longitude, region, country")
            else:
                df_locations = df_locations.dropna(subset=['latitude', 'longitude'])
                df_locations = df_locations.astype({'latitude': str, 'longitude': str})
                
                col1, col2 = st.columns(2)
                with col1:
                    selected_regions = st.multiselect(
                        "Filtrer par région:",
                        options=df_locations['region'].unique()
                    )
                with col2:
                    selected_countries = st.multiselect(
                        "Filtrer par pays:",
                        options=df_locations['country'].unique()
                    )

                if selected_regions:
                    df_locations = df_locations[df_locations['region'].isin(selected_regions)]
                if selected_countries:
                    df_locations = df_locations[df_locations['country'].isin(selected_countries)]

                st.write("Sélectionnez les localités (Ctrl+Click pour multi-sélection):")
                edited_df = st.data_editor(
                    df_locations[['localite', 'latitude', 'longitude', 'region', 'country']],
                    key="locations_editor",
                    use_container_width=True,
                    num_rows="dynamic"
                )

                selected_indices = edited_df.index[edited_df['latitude'].notna() & edited_df['longitude'].notna()]
                selected_locations = edited_df.loc[selected_indices].copy()
                
                selected_coords = [
                    f"{row['latitude']},{row['longitude']}"
                    for _, row in selected_locations.iterrows()
                ]
                st.session_state.coordinates = ", ".join(selected_coords)
                st.session_state.selected_locations = selected_locations[['localite', 'latitude', 'longitude']]

        except Exception as e:
            st.error(f"Erreur de lecture du fichier : {str(e)}")

# Formulaire principal
with st.form("input_form"):
    coords = st.text_area(
        "Coordonnées sélectionnées (latitude,longitude):",
        value=st.session_state.coordinates,
        help="Format requis : 6.8399,13.2509, 6.4606,13.1184, ..."
    )

    col1, col2 = st.columns(2)
    with col1:
        forecast_type = st.radio(
            "Type de prévision :",
            ["Jours fixes", "Plage personnalisée"]
        )
        
        if forecast_type == "Jours fixes":
            forecast_days = st.selectbox(
                "Durée de prévision :",
                [1, 3, 7, 10, 14],
                index=2
            )
        else:
            date_range = st.date_input("Sélectionnez une plage de dates :", [])
            if date_range:
                forecast_days = (date_range[1] - date_range[0]).days + 1
    
    with col2:
        st.write("Paramètres à prédire :")
        temp_max = st.checkbox("Température maximale (2m)", True)
        temp_min = st.checkbox("Température minimale (2m)", True)
        precipitation = st.checkbox("Précipitations", True)
    
    submitted = st.form_submit_button("Générer la prévision")

# Traitement des données
if submitted:
    try:
        pairs = [pair.strip() for pair in coords.split(", ") if pair.strip()]
        coords_list = []
        for pair in pairs:
            parts = pair.split(",")
            if len(parts) != 2:
                st.warning(f"Format de coordonnées invalide pour la paire : {pair}")
                st.stop()
            coords_list.extend(parts)
        
        if not coords_list:
            st.warning("Aucune coordonnée valide fournie !")
            st.stop()

        localite_map = {}
        if not st.session_state.selected_locations.empty:
            selected_locations = st.session_state.selected_locations
            selected_locations['latitude'] = selected_locations['latitude'].astype(str)
            selected_locations['longitude'] = selected_locations['longitude'].astype(str)
            for _, row in selected_locations.iterrows():
                localite_map[(row['latitude'], row['longitude'])] = row['localite']

        params = {
            "latitude": coords_list[::2],
            "longitude": coords_list[1::2],
            "daily": [],
            "timezone": "auto",
            "forecast_days": forecast_days if forecast_type == "Jours fixes" else 16
        }
        
        if temp_max: params["daily"].append("temperature_2m_max")
        if temp_min: params["daily"].append("temperature_2m_min")
        if precipitation: params["daily"].append("precipitation_sum")
        
        response = requests.get("https://api.open-meteo.com/v1/forecast", params=params)
        data = response.json()
        
        if "error" in data:
            raise ValueError(f"Erreur API : {data['error']}")
        
        dfs = []
        if isinstance(data, list):
            for idx, (lat, lon) in enumerate(zip(params["latitude"], params["longitude"])):
                if idx >= len(data):
                    break
                forecast = data[idx]
                if "daily" not in forecast:
                    continue
                
                localite = localite_map.get((lat, lon), 'N/A')
                df_coord = pd.DataFrame({
                    "Localite": localite,
                    "Date": pd.to_datetime(forecast["daily"]["time"]),
                    "Latitude": lat,
                    "Longitude": lon
                })
                
                if temp_max:
                    df_coord["Température max (°C)"] = forecast["daily"].get("temperature_2m_max", [])
                if temp_min:
                    df_coord["Température min (°C)"] = forecast["daily"].get("temperature_2m_min", [])
                if precipitation:
                    df_coord["Précipitations (mm)"] = forecast["daily"].get("precipitation_sum", [])
                
                dfs.append(df_coord)
        else:
            lat = params["latitude"][0]
            lon = params["longitude"][0]
            localite = localite_map.get((lat, lon), 'N/A')
            
            df_coord = pd.DataFrame({
                "Localite": localite,
                "Date": pd.to_datetime(data["daily"]["time"]),
                "Latitude": lat,
                "Longitude": lon
            })
            
            if temp_max:
                df_coord["Température max (°C)"] = data["daily"].get("temperature_2m_max", [])
            if temp_min:
                df_coord["Température min (°C)"] = data["daily"].get("temperature_2m_min", [])
            if precipitation:
                df_coord["Précipitations (mm)"] = data["daily"].get("precipitation_sum", [])
            
            dfs.append(df_coord)
        
        if not dfs:
            raise ValueError("Aucune donnée valide trouvée")
        
        df = pd.concat(dfs, ignore_index=True)
        df = df[['Localite', 'Date', 'Latitude', 'Longitude'] + [col for col in df.columns if col not in ['Localite', 'Date', 'Latitude', 'Longitude']]]

        fig = go.Figure()

        if temp_max:
            fig.add_trace(go.Scatter(
                x=df["Date"],
                y=df["Température max (°C)"],
                name="Température max",
                line=dict(color='#FF5733', width=2),
                yaxis='y1'
            ))
        
        if temp_min:
            fig.add_trace(go.Scatter(
                x=df["Date"],
                y=df["Température min (°C)"],
                name="Température min",
                line=dict(color='#3380FF', width=2),
                yaxis='y1'
            ))

        if precipitation:
            fig.add_trace(go.Bar(
                x=df["Date"],
                y=df["Précipitations (mm)"],
                name="Précipitations",
                marker=dict(color='#33FF47', opacity=0.6),
                yaxis='y2'
            ))

        fig.update_layout(
            title="Prévisions météorologiques - Onacc",
            xaxis=dict(title="Date", gridcolor='lightgray'),
            yaxis=dict(
                title=dict(text="Température (°C)", font=dict(color='#1f77b4')),
                tickfont=dict(color='#1f77b4'),
                gridcolor='lightgray',
                side='left'
            ),
            yaxis2=dict(
                title=dict(text="Précipitations (mm)", font=dict(color='#2ca02c')),
                tickfont=dict(color='#2ca02c'),
                overlaying='y',
                side='right'
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            plot_bgcolor='rgba(255,255,255,0.9)',
            hovermode="x unified"
        )

        st.plotly_chart(fig, use_container_width=True)
        
        col1, col2 = st.columns(2)
        with col1:
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Exporter en CSV",
                data=csv,
                file_name="onacc_forecast.csv",
                mime="text/csv"
            )
        with col2:
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False)
            st.download_button(
                label="Exporter en Excel",
                data=output.getvalue(),
                file_name="onacc_forecast.xlsx",
                mime="application/vnd.ms-excel"
            )
        
    except Exception as e:
        st.error(f"Erreur lors de la récupération des données : {str(e)}")