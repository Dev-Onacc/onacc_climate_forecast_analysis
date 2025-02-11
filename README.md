# Weather Forecast App

## 🌍 Objectif de l'application
Cette application permet de générer des prévisions météorologiques pour des localités spécifiques en utilisant :
- Des coordonnées GPS (latitude/longitude)
- Un fichier Excel de localités
- L'API ONACC-MC

## ✨ Fonctionnalités clés
- Import de fichiers Excel avec gestion des localités
- Filtrage multicritère (région/pays)
- Visualisation interactive des données
- Export des résultats en CSV/Excel
- Prévisions sur mesure (1 à 14 jours)

## 🛠 Guide d'utilisation
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
- **CSV** : Structure légère pour analyse rapide
- **Excel** : Format complet avec mise en forme

## 🚀 Déploiement
### Prérequis
- Python 3.8+
- Librairies requises : `streamlit pandas requests plotly openpyxl xlsxwriter`

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
#### 1. **Docker**
```dockerfile
FROM python:3.9-slim
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["streamlit", "run", "app.py", "--server.port=8501"]
```

#### 2. **Services cloud**
- AWS EC2
- Google Cloud Run
- Azure App Service
- Heroku

## 🆘 Support technique
### Problèmes courants
| Symptôme | Solution |
|----------|----------|
| Erreur API | Vérifier la connexion internet |
| Format de fichier invalide | Valider les colonnes obligatoires |
| Données manquantes | Vérifier les filtres appliqués |

### Contact support
**Équipe Onacc - DSI**  
📧 poum.bimbar@onacc.cm  
