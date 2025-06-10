# 📄 Module : Importation Google Sheets → PostgreSQL (Railway)

Ce module lit automatiquement un ou plusieurs onglets d’un Google Sheets partagé et injecte leur contenu dans des tables PostgreSQL hébergées sur Railway. Chaque onglet devient une table, avec le même nom (respect des majuscules/minuscules).

---

## ⚙️ Fonctionnement

- Le script lit tous les onglets du Google Sheet.
- Pour chaque onglet :
  - Le nom de l’onglet devient le nom de la table.
  - La première ligne de l’onglet est utilisée comme nom des colonnes.
  - Les données sont insérées ligne par ligne dans la table correspondante.
  - Si la table existe déjà, elle est supprimée puis recréée pour éviter les doublons.

---

## 🗂 Arborescence

services/

└── GoogleSheetsVersBDD/

├── main.py # Script principal de synchronisation

├── Dockerfile # Image Docker pour déploiement sur Railway

└── README.md # Ce fichier


---

## 🧾 Pré-requis

1. **Un compte de service Google Cloud** ayant accès à votre Google Sheet  
2. **Un fichier JSON** d’authentification (`numerologie-import-bdd.json`)
3. **Un projet Railway** avec :
   - un plugin PostgreSQL actif
   - les variables d’environnement suivantes définies :
     - `PGHOST`
     - `PGPORT`
     - `PGDATABASE`
     - `PGUSER`
     - `PGPASSWORD`
     - `SHEET_ID` (ID de votre Google Sheet)
     - `GOOGLE_APPLICATION_CREDENTIALS_JSON` (contenu brut du fichier JSON)

---

## 🔐 Variables d’environnement (Railway)

À définir **dans l’onglet Variables du service** (pas dans les fichiers du repo) :

| Variable | Rôle |
|----------|------|
| `PGHOST` | Adresse de la BDD (ex: `postgres.railway.internal`) |
| `PGPORT` | Port (en général `5432`) |
| `PGDATABASE` | Nom de la base (souvent `railway`) |
| `PGUSER` | Nom d’utilisateur PostgreSQL |
| `PGPASSWORD` | Mot de passe PostgreSQL |
| `SHEET_ID` | ID du Google Sheet (entre `/d/` et `/edit`) |
| `GOOGLE_APPLICATION_CREDENTIALS_JSON` | Contenu complet (copié-collé brut) du fichier JSON d’authentification du compte de service |

---

## 🚀 Déploiement

1. Poussez les fichiers sur GitHub.
2. Connectez Railway à votre dépôt (root directory = `services/GoogleSheetsVersBDD`).
3. Railway va automatiquement builder et lancer le conteneur.
4. Vous verrez les logs s'afficher si la synchronisation réussit.

---

## ✅ Exemple de log en cas de succès

🟢 Connexion à Google Sheets établie
📄 Onglet traité : TexteIdentite
🗑 Ancienne table supprimée : TexteIdentite
✅ Nouvelle table créée : TexteIdentite
📥 34 lignes insérées
...
🏁 Importation terminée avec succès



---

## ❓FAQ

**Q : Est-ce que ce module lit tous les onglets ?**  
Oui, automatiquement.

**Q : Que se passe-t-il si je modifie une cellule dans Google Sheets ?**  
Il suffit de redéployer ce module pour réinjecter toutes les données.

**Q : Le nom des tables est-il sensible à la casse ?**  
Oui. Le script crée les tables avec le même nom exact que les onglets, majuscules incluses.

---

## 🧼 Sécurité

Ne poussez **jamais** le fichier `.json` de vos identifiants Google dans GitHub.  
Utilisez uniquement la variable d’environnement `GOOGLE_APPLICATION_CREDENTIALS_JSON`.

---

