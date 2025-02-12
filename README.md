# Onacc Climate Forecast Analysis

Onacc Climate Forecast Analysis est une application interactive permettant d'obtenir des **prévisions météorologiques et climatiques** pour des localités spécifiques. L'application utilise des **coordonnées GPS**, des **fichiers Excel** ou une **saisie manuelle** pour générer des prévisions précises et interactives en exploitant l'API **ONACC-MC**.

---

## 🌍 Fonctionnalités

### 📂 Importation de Données
- Importation d’un **fichier Excel** contenant des localités (latitude, longitude, altitude, région, pays).
- Sélection et **filtrage avancé** des localités par région et pays.
- Visualisation interactive des localités sélectionnées.

### 🔎 Types de Prévisions
L'utilisateur peut choisir entre trois types de prévisions :
1. **Prévisions météo (1 à 14 jours)**
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

---

## 💻 Installation et Déploiement

### 🚀 Installation Locale
1. **Cloner le dépôt GitHub**
   ```bash
   git clone https://github.com/Dev-Onacc/onacc_climate_forecast_analysis.git
   ```
2. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```
3. **Lancer l'application**
   ```bash
   streamlit run app.py
   ```

### 🌍 Déploiement en Production
#### Dockerisation
Créer un fichier `Dockerfile` avec le contenu suivant :
```dockerfile
FROM python:3.9-slim
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["streamlit", "run", "app.py", "--server.port=8501"]
```
Construire et exécuter le conteneur :
```bash
docker build -t onacc-climate-forecast .
docker run -p 8501:8501 onacc-climate-forecast
```
#### Déploiement sur le Cloud
- **AWS EC2**
- **Google Cloud Run**
- **Azure App Service**
- **Heroku**

---

## 🆘 Support
- **Contact** : Équipe ONACC - DSI
- **Email** : poum.bimbar@onacc.org

Cette application est un outil essentiel pour **les chercheurs, météorologues et analystes climatiques**, facilitant **la prise de décision basée sur des prévisions précises et interactives**. 🌦️📈
