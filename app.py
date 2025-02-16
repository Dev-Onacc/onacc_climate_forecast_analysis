import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
from io import BytesIO
from datetime import datetime
from json import JSONDecodeError

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
        # 🚀 Objectif de l'application
        Onacc Climate Forecast Analysis est une application interactive permettant d'obtenir des **prévisions météorologiques et climatiques** pour des localités spécifiques. L'application utilise des **coordonnées GPS**, des **fichiers Excel** ou une **saisie manuelle** pour générer des prévisions précises et interactives en exploitant l'API **ONACC-MC**.
        

        # 🌍 Fonctionnalités
        ### 📂 Importation de Données
        - Importation d’un **fichier Excel** contenant des localités (latitude, longitude, altitude, région, pays).
        - Sélection et **filtrage avancé** des localités par région et pays.
        - Visualisation interactive des localités sélectionnées.

        ### 🔎 Types de Prévisions
        L'utilisateur peut choisir entre trois types de prévisions :
        1. **Prévisions décadaires (1 à 14 jours)**
        - Température maximale / minimale (°C)
        - Précipitations (mm)
        - Sélection de la période (jours fixes ou plage personnalisée)
        2. **Prévisions saisonnières (45 jours à 9 mois)**
        - Analyse des tendances climatiques sur des périodes prolongées
        3. **Projections climatiques (jusqu’à 2050)**
        - Simulation des changements climatiques à long terme
        - Sélection du **modèle climatique** utilisé

        ### 📊 Visualisation Interactive
        - **Graphiques dynamiques** pour afficher :
        - Température maximale/minimale sous forme de courbes.
        - Précipitations sous forme d’histogramme.
        - **Affichage personnalisé** selon le type de prévision.

        ### 📤 Exportation des Données
        - Sauvegarde des prévisions sous **CSV** ou **Excel**.
        - Génération de **rapports météorologiques** exploitables pour l’analyse.
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
        git clone https://github.com/Dev-Onacc/onacc_climate_forecast_analysis.git
        
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


# ================= FONCTIONS UTILITAIRES =================
def create_dataframe(data, lat, lon, localite, mode):
    """Crée le DataFrame à partir des données API avec validation"""
    try:
        time_data = data["daily"]["time"]
    except KeyError:
        raise ValueError("Données temporelles manquantes dans la réponse API")
    
    df = pd.DataFrame({
        "Localite": localite,
        "Date": pd.to_datetime(time_data),
        "Latitude": lat,
        "Longitude": lon
    })

    param_mapping = {
        "temperature_2m_max": "Température max (°C)",
        "temperature_2m_min": "Température min (°C)",
        "precipitation_sum": "Précipitations (mm)"
    }

    for api_param, df_column in param_mapping.items():
        df[df_column] = data["daily"].get(api_param, None)

    return df

def get_api_error(response_data, status_code):
    """Gestion améliorée des erreurs API"""
    error_message = f"Erreur HTTP {status_code}"
    error_mapping = {
        400: "Requête invalide - Vérifiez les paramètres",
        401: "Authentification requise",
        403: "Accès refusé",
        404: "Endpoint introuvable",
        500: "Erreur serveur"
    }
    
    if isinstance(response_data, dict):
        return f"{error_mapping.get(status_code, error_message)} : {response_data.get('reason', 'Erreur inconnue')}"
    
    return error_mapping.get(status_code, error_message)

def add_metadata(df, mode, params):
    """Ajoute les métadonnées de prévision"""
    df["Type de prévision"] = mode
    if mode == "Projections climatiques":
        df["Modèle climatique"] = params["model"]
    elif mode == "Prévisions saisonnières":
        df["Durée prévision"] = params["duration"]
    return df

def create_visualization(df, mode):
    """Crée la visualisation adaptée au type de prévision"""
    fig = go.Figure()
    
    # Courbes de température
    if "Température max (°C)" in df.columns:
        fig.add_trace(go.Scatter(
            x=df["Date"], 
            y=df["Température max (°C)"],
            name="Température max",
            line=dict(color='#FF5733', width=2),
            yaxis='y1'
        ))
    
    if "Température min (°C)" in df.columns:
        fig.add_trace(go.Scatter(
            x=df["Date"], 
            y=df["Température min (°C)"],
            name="Température min",
            line=dict(color='#3380FF', width=2),
            yaxis='y1'
        ))
    
    # Histogrammes de précipitations
    if "Précipitations (mm)" in df.columns:
        fig.add_trace(go.Bar(
            x=df["Date"], 
            y=df["Précipitations (mm)"],
            name="Précipitations",
            marker=dict(color='#33FF47', opacity=0.6),
            yaxis='y2'
        ))
    
    # Configuration du layout
    layout_config = {
        "title": f"Prévisions {mode} - Onacc",
        "xaxis": dict(title="Date", gridcolor='lightgray'),
        "yaxis": dict(
            title=dict(text="Température (°C)", font=dict(color='#1f77b4')),
            tickfont=dict(color='#1f77b4'),
            gridcolor='lightgray',
            side='left'
        ),
        "yaxis2": dict(
            title=dict(text="Précipitations (mm)", font=dict(color='#2ca02c')),
            tickfont=dict(color='#2ca02c'),
            overlaying='y',
            side='right'
        ),
        "legend": dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        "plot_bgcolor": 'rgba(255,255,255,0.9)',
        "hovermode": "x unified"
    }
    
    if mode == "Prévisions saisonnières":
        layout_config.update({
            "shapes": [dict(
                type="rect",
                xref="paper",
                yref="paper",
                x0=0, y0=0,
                x1=1, y1=1,
                fillcolor="rgba(200,200,200,0.2)",
                line={"width": 0}
            )]
        })
    
    fig.update_layout(**layout_config)
    return fig

def export_data(df):
    """Gère l'export des données"""
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


# ================= INTERFACE UTILISATEUR =================
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

    forecast_mode = st.radio(
        "Type de prévision :",
        options=["Prévisions décadaires", "Prévisions saisonnières", "Projections climatiques"],
        horizontal=True
    )

    col1, col2 = st.columns(2)
    
    with col1:
        if forecast_mode == "Prévisions décadaires":
            forecast_type = st.radio(
                "Période de prévision :",
                ["Jours fixes", "Plage personnalisée"]
            )
            if forecast_type == "Jours fixes":
                forecast_days = st.selectbox("Durée :", [1, 3, 7, 10, 14], index=2)
            else:
                date_range = st.date_input("Plage de dates :", [])
                forecast_days = (date_range[1] - date_range[0]).days + 1 if date_range else 1
                
        elif forecast_mode == "Prévisions saisonnières":
            forecast_length = st.selectbox(
                "Durée :",
                ["45 days", "3 months", "6 months", "9 months"]
            )
            
        elif forecast_mode == "Projections climatiques":
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input(
                    "Début :",
                    value=datetime(2020, 1, 1),
                    min_value=datetime(1950, 1, 1),
                    max_value=datetime(2050, 12, 31)
                )
            with col2:
                end_date = st.date_input(
                    "Fin :", 
                    value=datetime(2040, 1, 1),
                    min_value=start_date,
                    max_value=datetime(2050, 12, 31)
                )
            model = st.selectbox(
                "Modèle :",
                options=["MRI_AGCM3_2_S", "FGOALS_f3_H", "CMCC_CM2_VHR4"]
            )
    
    with col2:
        st.write("Paramètres à prédire :")
        temp_max = st.checkbox("Température maximale (2m)", True)
        temp_min = st.checkbox("Température minimale (2m)", True)
        precipitation = st.checkbox("Précipitations", True)
    
    submitted = st.form_submit_button("Générer la prévision")

# Traitement des données
if submitted:
    try:
        # Initialiser coords_list
        coords_list = []
        
        # Nettoyer et valider les coordonnées
        if coords:
            pairs = [pair.strip() for pair in coords.split(", ") if pair.strip()]
            
            for pair in pairs:
                parts = pair.split(",")
                if len(parts) != 2:
                    st.warning(f"Format de coordonnées invalide pour la paire : {pair}")
                    st.stop()
                coords_list.extend([parts[0].strip(), parts[1].strip()])
        
        if not coords_list:
            st.warning("Aucune coordonnée valide fournie !")
            st.stop()

        localite_map = {}
        if not st.session_state.selected_locations.empty:
            selected_locations = st.session_state.selected_locations.copy()
            
            # Conversion en strings pour éviter les problèmes de types
            selected_locations['latitude'] = selected_locations['latitude'].astype(str).str.strip()
            selected_locations['longitude'] = selected_locations['longitude'].astype(str).str.strip()
            
            # Création du dictionnaire de correspondance
            for _, row in selected_locations.iterrows():
                localite_map[(row['latitude'], row['longitude'])] = row['localite']
        

        # Configuration API
        base_params = {
            "latitude": coords_list[::2],
            "longitude": coords_list[1::2],
            "daily": []
        }

        if forecast_mode == "Prévisions décadaires":
            endpoint = "https://api.open-meteo.com/v1/forecast"
            base_params.update({
                "forecast_days": forecast_days,
                "timezone": "auto",
                "daily": ["temperature_2m_max", "temperature_2m_min", "precipitation_sum"]
            })
            
        elif forecast_mode == "Prévisions saisonnières":
            endpoint = "https://open-meteo.com/en/docs/seasonal-forecast-api"
            base_params.update({
                "daily": ["temperature_2m_max", "temperature_2m_min", "precipitation_sum"],
                "models": "ecmwf_ifs",
                "forecast_months": int(forecast_length.split()[0])
            })
            
        elif forecast_mode == "Projections climatiques":
            endpoint = "https://climate-api.open-meteo.com/v1/climate"
            base_params.update({
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "models": model,
                "daily": ["temperature_2m_max", "temperature_2m_min", "precipitation_sum"]
            })

        # Appel API
        response = requests.get(endpoint, params=base_params)
        
        try:
            data = response.json()
        except JSONDecodeError:
            raise ValueError("Réponse API invalide (non JSON)")
        
        if response.status_code != 200:
            raise ValueError(get_api_error(data, response.status_code))

        dfs = []
        if isinstance(data, list):
            for idx, (lat, lon) in enumerate(zip(base_params["latitude"], base_params["longitude"])):
                if idx >= len(data):
                    break
                forecast = data[idx]
                
                # Vérification de la structure des données
                if not isinstance(forecast, dict) or 'daily' not in forecast:
                    st.warning(f"Données invalides pour {lat},{lon}")
                    continue
                
                df_coord = create_dataframe(
                    forecast, 
                    lat, 
                    lon, 
                    localite_map.get((lat, lon), 'N/A'),
                    forecast_mode
                )
                dfs.append(df_coord)
        else:
            # Traitement d'une réponse unique
            if 'daily' not in data:
                raise ValueError("Structure de réponse API invalide : clé 'daily' manquante")
            
            df_coord = create_dataframe(
                data,
                base_params["latitude"][0],
                base_params["longitude"][0],
                localite_map.get((base_params["latitude"][0], base_params["longitude"][0]), 'N/A'),
                forecast_mode
            )
            dfs.append(df_coord)
        
        # Création du DataFrame final
        df = pd.concat(dfs, ignore_index=True)
        df = add_metadata(df, forecast_mode, {
            "model": model if forecast_mode == "Projections climatiques" else None,
            "duration": forecast_length if forecast_mode == "Prévisions saisonnières" else None
        })
        
        # Visualisation
        fig = create_visualization(df, forecast_mode)
        st.plotly_chart(fig, use_container_width=True)
        
        # Export
        export_data(df)

    except Exception as e:
        st.error(f"Erreur : {str(e)}")