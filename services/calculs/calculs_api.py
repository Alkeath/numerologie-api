"""
Ce script contient les fonctions de traitement numérologique utilisées dans l'API.

🔁 Le processus global est structuré en 5 étapes distinctes :

1. 🧮 Calcul initial (traitement_etape_1) :
   - Traitement des données brutes envoyées par le frontend (nom, prénoms, date de naissance).
   - Calcul de toutes les variables numérologiques, y compris les versions ajustées des nombres maîtres 11 et 22 selon toutes les combinaisons d’activation (oui/non).
   - Ces valeurs sont retournées au frontend, qui décidera de poser ou non des questions via modales conditionnelles.

2. 💬 Interaction utilisateur (gérée côté frontend) :
   - Affichage conditionnel des modales (activation de 11 et 22, choix entre un ou tous les prénoms pour certains nombres).
   - Réception des réponses de l’utilisateur.
   - Transmission au backend de la configuration finale choisie (ActNbMaitre11/22 et les 3 choix Exp, Rea, Ame).

3. 📄 Génération du rapport HTML :
   - Sélection des textes dans la base de données selon les résultats retenus et la langue.
   - Injection dans un template HTML structuré.

4. 📦 Création du PDF :
   - Conversion du HTML généré en fichier PDF lisible et stylisé.

5. ✉️ Livraison :
   - Envoi du PDF personnalisé par  à l’utilisateur.
   - Ouverture automatique du fichier dans une nouvelle fenêtre navigateur.

Ce découpage assure modularité, scalabilité et clarté du traitement, tout en optimisant les performances du frontend et du backend.
"""


from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional
import unicodedata
import re
import requests
import os
import io

# ✅ Initialisation du routeur FastAPI
router = APIRouter()

# ✅ Mémoire temporaire entre les étapes
memoire_utilisateurs = {}

class ChoixUtilisateur(BaseModel):
    uuidRequete: Optional[str] = None
    Email_Formulaire : str
    ActNbMaitre11: str
    ActNbMaitre22: str
    RepAct11_Q1: str = "NonApplicable"
    RepAct11_Q2: str = "NonApplicable"
    RepAct11_Q3: str = "NonApplicable"
    RepAct22_Q1: str = "NonApplicable"
    RepAct22_Q2: str = "NonApplicable"
    RepAct22_Q3: str = "NonApplicable"
    ApprocheCalculs: str = "NonApplicable"
    RepExpUnPrenomTousPrenoms: str = "NonApplicable"
    RepReaUnPrenomTousPrenoms: str = "NonApplicable"
    RepAmeUnPrenomTousPrenoms: str = "NonApplicable"


######### CREATION DES ROUTES #############

@router.post("/retraitement_variables")
def retraitement_variables(choix: ChoixUtilisateur):
    print(f"🎯 Traitement des données étape 1 pour {choix.Email_Formulaire} :")
    print(f"  - ActNbMaitre11 : {choix.ActNbMaitre11}")
    print(f"  - ActNbMaitre22 : {choix.ActNbMaitre22}")
    print(f"  - Prénoms : {choix.ApprocheCalculs}")
    return {
        "message": "Traitement final reçu avec succès",
        "email_formulaire": choix.Email_Formulaire
    }

@router.post("/etape2")
async def appel_etape_2(choix: ChoixUtilisateur, request: Request):
    try:
        print("📩 Données reçues :", choix.dict(), flush=True)

        raw = await request.body()
        print("📦 Corps brut reçu :", raw.decode())

        print("📨 Payload Pydantic :", choix.dict())

        email_formulaire = choix.Email_Formulaire
        if email_formulaire not in memoire_utilisateurs:
            raise HTTPException(status_code=400, detail="Email_Formulaire inconnu ou session expirée")

        donnees = memoire_utilisateurs[email_formulaire].copy()
        donnees.update(choix.dict())

        print("📡 Point de vérification router /etape 2 avant appel à la fonction")
        etape_2_recalculs_final_et_affectations(donnees)

        import pprint
        print("🧪 Données finales à retourner (brutes) :")
        pprint.pprint(donnees)

        # 🔧 Vérification spéciale : nettoyage des objets non sérialisables (comme StreamingResponse)
        if "url_html" in donnees and isinstance(donnees["url_html"], dict):
            if not isinstance(donnees["url_html"].get("url_html"), str):
                donnees["url_html"]["url_html"] = str(donnees["url_html"].get("url_html", ""))
            if not isinstance(donnees["url_html"].get("chemin_pdf"), str):
                donnees["url_html"]["chemin_pdf"] = str(donnees["url_html"].get("chemin_pdf", ""))

        try:
            jsonable_encoder(donnees)
            print("✅ Encodage JSON réussi")
        except Exception as e:
            print("❌ Erreur d'encodage JSON :", str(e))
            import traceback
            traceback.print_exc()

        print("✅ Fin traitement /etape2, envoi réponse JSON")
        return JSONResponse(content={"donnees": jsonable_encoder(donnees)})

    except Exception as e:
        import traceback
        print("🔥 Exception dans /etape2 :", str(e))
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Erreur serveur dans /etape2")



######## FONCTIONS UTILITAIRES #########

def convertir_en_int(valeur):
    try:
        return int(valeur.strip())
    except:
        return 0

def nettoyer_chaine_nom_prenom(texte, majuscules=False):
    texte = texte.replace("ß", "SS")
    texte = texte.replace("Œ", "OE").replace("œ", "oe")
    texte = texte.replace("Æ", "AE").replace("æ", "ae")
    texte = re.sub(r"\s*[-‑–—]\s*", "-", texte)
    texte = re.sub(r"\s*[’']\s*", "'", texte)
    texte = re.sub(r"\s+", " ", texte).strip()

    def est_lettre_latine(c):
        try:
            return "LATIN" in unicodedata.name(c) and c.isalpha()
        except ValueError:
            return False
    texte_filtré = ''.join(c if est_lettre_latine(c) or c in " -'" else "" for c in texte)
    if majuscules:
        return texte_filtré.upper()

    def cap_mot(mot):
        for sep in ["-", "'"]:
            if sep in mot:
                return sep.join(part.capitalize() for part in mot.split(sep))
        return mot.capitalize()
    return ' '.join(cap_mot(mot) for mot in texte_filtré.split())

def normaliser_chaine(texte):
    remplacements_speciaux = {
        'ø': 'o', 'Ø': 'O', 'æ': 'ae', 'Æ': 'AE', 'œ': 'oe', 'Œ': 'OE', 'å': 'a', 'Å': 'A',
        'ð': 'd', 'Ð': 'D', 'ł': 'l', 'Ł': 'L', 'þ': 'th', 'Þ': 'Th', 'ñ': 'n', 'Ñ': 'N',
        'ß': 'ss', 'ç': 'c', 'Ç': 'C', 'ś': 's', 'Ś': 'S', 'ž': 'z', 'Ž': 'Z',
        'š': 's', 'Š': 'S', 'ę': 'e', 'Ę': 'E'
    }
    for char, repl in remplacements_speciaux.items():
        texte = texte.replace(char, repl)
    texte = unicodedata.normalize('NFD', texte)
    texte = ''.join(c for c in texte if unicodedata.category(c) != 'Mn')
    return texte

def valeur_lettre(lettre):
    lettre = lettre.upper()
    if lettre < 'A' or lettre > 'Z':
        return 0
    return (ord(lettre) - ord('A')) % 9 + 1

def est_voyelle(lettre):
    return lettre.upper() in 'AEIOUY'

def ReductionNombre(nombre):
    while True:
        if nombre in (11, 22):
            return nombre
        total = sum(int(c) for c in str(nombre))
        if total in (11, 22) or total < 10:
            return total
        nombre = total

def ReductionForcee(nombre):
    while nombre >= 10:
        nombre = sum(int(c) for c in str(nombre))
    return nombre

def calcul_grille_intensite(texte):
    compteur = {i: 0 for i in range(1, 10)}
    total_lettres = 0
    for lettre in texte:
        if lettre.isalpha():
            val = valeur_lettre(lettre)
            if val > 0:
                compteur[val] += 1
                total_lettres += 1
    diagonale_asc = compteur[7] + compteur[5] + compteur[3]
    diagonale_desc = compteur[1] + compteur[5] + compteur[9]
    seuil_exces = (total_lettres / 9) * 1.2
    manquants = [str(i) for i in range(1, 10) if compteur[i] == 0]
    exces = [str(i) for i in range(1, 10) if compteur[i] > seuil_exces]
    resultat = {
        "NombreLettresTotal": str(total_lettres),
        "IntensiteDiagonaleAscendante": str(diagonale_asc),
        "IntensiteDiagonaleDescendante": str(diagonale_desc),
        "IntensiteSeuilExces": f"{seuil_exces:.2f}",
        "NombresManquants": ", ".join(manquants),
        "NombresEnExces": ", ".join(exces),
    }
    for i in range(1, 10):
        resultat[f"NombreDe{i}"] = str(compteur[i])
    return resultat

def calcul_plan_expression(texte):
    texte = texte.replace(" ", "").upper()
    plan_expression = {
        "MenCar": list("A"),
        "MenMut": list("HJNP"),
        "MenFix": list("GL"),
        "PhyCar": list("E"),
        "PhyMut": list("W"),
        "PhyFix": list("DM"),
        "EmoCar": list("ORIZ"),
        "EmoMut": list("BSTX"),
        "EmoFix": [],
        "IntCar": list("K"),
        "IntMut": list("FQUY"),
        "IntFix": list("CV"),
    }
    resultats = {cle: 0 for cle in plan_expression}
    for lettre in texte:
        for cle, lettres in plan_expression.items():
            if lettre in lettres:
                resultats[cle] += 1
    # Totaux par domaine
    for domaine in ["Men", "Phy", "Emo", "Int"]:
        resultats[f"{domaine}Tot"] = sum(
            resultats[f"{domaine}{typ}"] for typ in ["Car", "Mut", "Fix"]
        )
    # Totaux par type
    for typ in ["Car", "Mut", "Fix"]:
        resultats[f"{typ}Tot"] = sum(
            resultats[f"{domaine}{typ}"] for domaine in ["Men", "Phy", "Emo", "Int"]
        )
    return {k: str(v) for k, v in resultats.items()}

# --- Constitution de la liste des nombres maîtres, sous-nombres, nombres karmiques ---
def constitution_liste_nombres_speciaux(valeurs_totales):
    def somme_chiffres(n):
        return sum(int(c) for c in str(n))
    karmiques_fixes = [13, 14, 16, 19]
    nombres_maitres = []
    sous_nombres = []
    karmiques = []
    for val in valeurs_totales:
        if isinstance(val, int):
            est_maitre = (val % 11 == 0) or (somme_chiffres(val) % 11 == 0 and somme_chiffres(val) != 0)
            if est_maitre:
                nombres_maitres.append(val)
            else:
                sous_nombres.append(val)
            if val in karmiques_fixes:
                karmiques.append(val)
    sous_nombres_str = ", ".join(str(n) for n in sorted(sous_nombres))
    nombres_maitres_str = ", ".join(str(n) for n in sorted(nombres_maitres))
    karmiques_str = ", ".join(str(n) for n in sorted(karmiques))
    return sous_nombres_str, nombres_maitres_str, karmiques_str


# --- Ajuste la valeur selon l’activation des nombres maîtres 11 et 22 ---
def ajuster_nombre_maitre(valeur_str, activer_11=False, activer_22=False):
    try:
        val = int(valeur_str)
    except:
        return valeur_str  # ne rien faire si ce n’est pas un nombre
    if val == 11:
        return 11 if activer_11 else 2
    elif val == 22:
        return 22 if activer_22 else 4
    return val


# --- Présentation des résultats pour la charte numérologique en format tot/reduit ---
def afficher_charte(total, reduit):
    return str(reduit) if total == reduit else f"{total}/{reduit}"

def reduction_nombre(n):
    while n > 9 and n not in (11, 22):
        n = sum(int(chiffre) for chiffre in str(n))
    return n

# --- calculs des cycles, defis, periode, annee personnelle ---
def calcul_elements_date_naissance(date_str, date_du_jour_str=None):
    date_naissance = datetime.strptime(date_str, "%d/%m/%Y")
    jour = date_naissance.day
    mois = date_naissance.month
    annee = date_naissance.year
    # Cycles
    cycle1 = reduction_nombre(mois)
    cycle2 = reduction_nombre(jour)
    cycle3 = reduction_nombre(annee)
    # Défis
    defi1 = reduction_nombre(abs(reduction_nombre(jour) - reduction_nombre(mois)))
    defi2 = reduction_nombre(abs(reduction_nombre(jour) - reduction_nombre(annee)))
    defi_majeur = abs(defi1 - defi2)
    # Réalisations
    realisation1 = reduction_nombre(jour + mois)
    realisation2 = reduction_nombre(jour + annee)
    realisation3 = reduction_nombre(realisation1 + realisation2)
    realisation4 = reduction_nombre(mois + annee)
    # Année personnelle
    if date_du_jour_str is None:
        date_du_jour = datetime.today()
    else:
        date_du_jour = datetime.strptime(date_du_jour_str, "%Y-%m-%d")
    a_p = reduction_nombre(
        sum(int(c) for c in f"{jour:02d}{mois:02d}{date_du_jour.year}")
    )
    return {
        # 📆 Données brutes et réduites pour affichage charte
        "JourDeNaissanceTotal": jour,
        "JourDeNaissance": reduction_nombre(jour),
        "MoisDeNaissanceTotal": mois,
        "MoisDeNaissance": reduction_nombre(mois),
        "AnneeDeNaissanceTotal": annee,
        "AnneeDeNaissance": reduction_nombre(annee),
        # 🔁 Cycles
        "Cycle1": cycle1,
        "Cycle2": cycle2,
        "Cycle3": cycle3,
        # 🎯 Défis
        "DefiMineur1": defi1,
        "DefiMineur2": defi2,
        "DefiMajeur": defi_majeur,
        # 🎯 Réalisations
        "Realisation1": realisation1,
        "Realisation2": realisation2,
        "Realisation3": realisation3,
        "Realisation4": realisation4,
        # 📅 Année personnelle
        "AnneePersonnelle": a_p
    }





########### Etape 0 ################

# Etape 0 : traiement des données entrées, formatage des prénoms nom et date de naissance 
def etape_0_mise_en_forme_prenoms_nom_et_date_de_naissance(data):
    
    # Récupération des champs bruts depuis le formulaire
    Genre_Formulaire = data.get("Genre_Formulaire", "").strip()
    PrenomPremier_Formulaire = data.get("PrenomPremier_Formulaire", "").strip()
    PrenomsSecondaires_Formulaire = data.get("PrenomsSecondaires_Formulaire", "").strip()
    Nom_Formulaire = data.get("Nom_Formulaire", "").strip()
    Jour_Formulaire = data.get("Jour_Formulaire", "").strip()
    Mois_Formulaire = data.get("Mois_Formulaire", "").strip()
    Annee_Formulaire = data.get("Annee_Formulaire", "").strip()

    # Étape 1 : nettoyage
    PrenomPremier = nettoyer_chaine_nom_prenom(PrenomPremier_Formulaire, majuscules=False)
    PrenomsSecondaires = nettoyer_chaine_nom_prenom(PrenomsSecondaires_Formulaire, majuscules=False)
    PrenomsComplets = f"{PrenomPremier} {PrenomsSecondaires}".strip()
    Nom = nettoyer_chaine_nom_prenom(Nom_Formulaire, majuscules=True)
   
    # Étape 2 : normalisation
    PrenomPremier_normalise = normaliser_chaine(PrenomPremier)
    PrenomsComplets_normalise = normaliser_chaine(PrenomsComplets)
    Nom_normalise = normaliser_chaine(Nom)
   
    # Sauvegarde dans les variables de travail
    data["Genre_Formulaire"] = Genre_Formulaire
    data["PrenomPremier"] = PrenomPremier
    data["PrenomsSecondaires"] = PrenomsSecondaires
    data["PrenomsComplets"] = PrenomsComplets
    data["Nom"] = Nom
    data["PrenomPremier_normalise"] = PrenomPremier_normalise
    data["PrenomsComplets_normalise"] = PrenomsComplets_normalise
    data["Nom_normalise"] = Nom_normalise
    data["PrenomNom_UnPrenom"] = f"{PrenomPremier} {Nom}"
    data["PrenomNom_TousPrenoms"] = f"{PrenomsComplets} {Nom}"
   
    # ✅ Variable pour affichage utilisateur : version formatée (sans normalisation)
    data["PrenomsNomFormates"] = f"{PrenomsComplets} {Nom}"


    # Constitution de la date de naissance au format JJ/MM/AAAA
    if Jour_Formulaire and Mois_Formulaire and Annee_Formulaire:
        data["DateDeNaissance"] = f"{Jour_Formulaire.zfill(2)}/{Mois_Formulaire.zfill(2)}/{Annee_Formulaire}"
    else:
        data["DateDeNaissance"] = ""

    return data




########### Etape 1 ################

# Etape 1 : premiers calculs partiels des nombres à envoyer au backend pour poser des questions supplémentaires 

def etape_1_calculs_preliminaires_nombres_principaux(data):
    # 📅 Calcul du chemin de vie
    chiffres_date = [int(c) for c in data.get("DateDeNaissance", "") if c.isdigit()]
    total_cdv = sum(chiffres_date)
    reduit_cdv = ReductionNombre(total_cdv)
    data["NbCdVTotal"] = str(total_cdv)
    data["NbCdV_AvantTestAct"] = str(reduit_cdv)

    # 🔠 Calcul des nombres d'Expression, Réalisation et Âme avant test d'activation des nombres maîtres
    textes = {
        "UnPrenom": normaliser_chaine(data["PrenomNom_UnPrenom"]).replace(" ", ""),
        "TousPrenoms": normaliser_chaine(data["PrenomNom_TousPrenoms"]).replace(" ", "")
    }

    for prefixe in ["UnPrenom", "TousPrenoms"]:
        texte = textes[prefixe]
        total_exp = total_ame = total_rea = 0

        for lettre in texte:
            if lettre.isalpha():
                val = valeur_lettre(lettre)
                total_exp += val
                if est_voyelle(lettre):
                    total_ame += val
                else:
                    total_rea += val

        data[f"NbExpTotal_{prefixe}"] = str(total_exp)
        data[f"NbReaTotal_{prefixe}"] = str(total_rea)
        data[f"NbAmeTotal_{prefixe}"] = str(total_ame)
        data[f"NbExp_{prefixe}_AvantTestAct"] = str(ReductionNombre(total_exp))
        data[f"NbRea_{prefixe}_AvantTestAct"] = str(ReductionNombre(total_rea))
        data[f"NbAme_{prefixe}_AvantTestAct"] = str(ReductionNombre(total_ame))

    # 🔍 Détection des maîtres
    valeurs = [
        data.get("NbCdV_AvantTestAct", ""),
        data.get("NbExp_UnPrenom_AvantTestAct", ""),
        data.get("NbRea_UnPrenom_AvantTestAct", ""),
        data.get("NbAme_UnPrenom_AvantTestAct", ""),
        data.get("NbExp_TousPrenoms_AvantTestAct", ""),
        data.get("NbRea_TousPrenoms_AvantTestAct", ""),
        data.get("NbAme_TousPrenoms_AvantTestAct", "")
    ]
    data["Presence11"] = "oui" if "11" in valeurs else "non"
    data["Presence22"] = "oui" if "22" in valeurs else "non"

    # 🔧 Ajustement en fonction des activations
    def ajuster(val, act11, act22):
        try:
            v = int(val)
        except:
            return val
        if v == 11 and act11 == "non":
            return 2
        if v == 22 and act22 == "non":
            return 4
        return v

    combinaisons = [
        ("oui", "non", "Si11Act22Desact"),
        ("non", "oui", "Si11Desact22Act"),
        ("oui", "oui", "Si11Act22Act"),
        ("non", "non", "Si11Desact22Desact"),
    ]
    noms = ["Exp", "Rea", "Ame"]
    types = ["UnPrenom", "TousPrenoms"]

    for nom in noms:
        for type_prenom in types:
            valeur_avant = data.get(f"Nb{nom}_{type_prenom}_AvantTestAct", "")
            for act11, act22, suffixe in combinaisons:
                cle_finale = f"Nb{nom}_{type_prenom}_{suffixe}"
                data[cle_finale] = ajuster(valeur_avant, act11, act22)

    valeur_cdv_avant = data.get("NbCdV_AvantTestAct", "")
    for act11, act22, suffixe in combinaisons:
        data[f"NbCdV_{suffixe}"] = ajuster(valeur_cdv_avant, act11, act22)

    # 💾 Sauvegarde pour étape 2
    memoire_utilisateurs[data["Email_Formulaire"]] = {
        "Nom": data["Nom"],
        "PrenomPremier": data["PrenomPremier"],
        "PrenomsComplets": data["PrenomsComplets"],
        "Nom_normalise": data["Nom_normalise"],
        "PrenomPremier_normalise": data["PrenomPremier_normalise"],
        "PrenomsComplets_normalise": data["PrenomsComplets_normalise"],
        "DateDeNaissance": data["DateDeNaissance"],
        "Genre_Formulaire": data["Genre_Formulaire"]
    }

return data






########### Etape 2 ################

def etape_2_recalculs_final_et_affectations(data):

    print("📡 [calculs_api.py] Vérification : appel_etape_2 bien reçue (début fonction étape 2)")

    # 0. Récupération de la variable Genre
    data["Genre_Formulaire"] = data.get("Genre_Formulaire", "")
    
    
    # 1. 🔤 Texte normalisé pour tous les calculs à partir du nom complet
    approches_un_prenom = [
        "UnPrenomDefaut", "UnPrenomQuestions", "ChoixUnPrenom"
    ]
    if data["ApprocheCalculs"] in approches_un_prenom:
        texte_prenom_normalise = data["PrenomPremier_normalise"]
    else:
        texte_prenom_normalise = data["PrenomsComplets_normalise"]
    texte_normalise = texte_prenom_normalise + data["Nom_normalise"]
    data["PrenomNom_Final_normalise"] = texte_normalise
    data["TextePrenom_Final_normalise"] = texte_prenom_normalise  # utilisé pour le nombre actif



    # 2. 📅 Calcul du chemin de vie
    chiffres_date = [int(c) for c in data.get("DateDeNaissance", "") if c.isdigit()]
    total_cdv = sum(chiffres_date)
    reduit_cdv = ReductionNombre(total_cdv)

    # 3. 🧮 Calcul des totaux Exp / Rea / Ame
    total_exp = total_ame = total_rea = 0
    for lettre in texte_normalise:
        if lettre.isalpha():
            val = valeur_lettre(lettre)
            total_exp += val
            if est_voyelle(lettre):
                total_ame += val
            else:
                total_rea += val

    # 4. ⚙️ Application des règles d’activation et constitution des variables finales
    act11 = data.get("ActNbMaitre11", "non") == "oui"
    act22 = data.get("ActNbMaitre22", "non") == "oui"
    # 🔢 Réductions des nombres principaux
    reduit_cdv = ReductionNombre(total_cdv)
    reduit_exp = ReductionNombre(total_exp)
    reduit_rea = ReductionNombre(total_rea)
    reduit_ame = ReductionNombre(total_ame)
    # 🔢 Ajustements selon activation 11/22
    final_cdv = ajuster_nombre_maitre(reduit_cdv, activer_11=act11, activer_22=act22)
    final_exp = ajuster_nombre_maitre(reduit_exp, activer_11=act11, activer_22=act22)
    final_rea = ajuster_nombre_maitre(reduit_rea, activer_11=act11, activer_22=act22)
    final_ame = ajuster_nombre_maitre(reduit_ame, activer_11=act11, activer_22=act22)
    # 🔢 Enregistrement des totaux
    data["NbCdVTotal_Final"] = total_cdv
    data["NbExpTotal_Final"] = total_exp
    data["NbReaTotal_Final"] = total_rea
    data["NbAmeTotal_Final"] = total_ame
    # 🔢 Enregistrement des versions finales (réduites + ajustées)
    data["NbCdV_Final"] = final_cdv
    data["NbExp_Final"] = final_exp
    data["NbRea_Final"] = final_rea
    data["NbAme_Final"] = final_ame
    # 🔢 Nombre Actif et Hérédité
    total_actif = sum(valeur_lettre(l) for l in texte_prenom_normalise if l.isalpha())
    total_heredite = sum(valeur_lettre(l) for l in data["Nom_normalise"] if l.isalpha())
    reduit_actif = ReductionNombre(total_actif)
    reduit_heredite = ReductionNombre(total_heredite)
    data["NbActifTotal"] = total_actif
    data["NbHerediteTotal"] = total_heredite
    data["NbActif"] = reduit_actif
    data["NbHeredite"] = reduit_heredite

    # 5. 🔢 Grille d’intensité
    data.update(calcul_grille_intensite(texte_normalise))

    # 6. 🧭 Plans d’expression
    data.update(calcul_plan_expression(texte_normalise))

    # 7. 📆 Cycles, Réalisations, Défis, Année personnelle
    data.update(calcul_elements_date_naissance(data["DateDeNaissance"]))

    # 8. 🗂️ Constitution des affichage charte total/reduction
    data["NbCdV_Charte"] = afficher_charte(total_cdv, final_cdv)
    data["NbExp_Charte"] = afficher_charte(total_exp, final_exp)
    data["NbRea_Charte"] = afficher_charte(total_rea, final_rea)
    data["NbAme_Charte"] = afficher_charte(total_ame, final_ame)
    data["NbActif_Charte"] = afficher_charte(int(data["NbActifTotal"]), int(data["NbActif"]))
    data["NbHeredite_Charte"] = afficher_charte(int(data["NbHerediteTotal"]), int(data["NbHeredite"]))
    data["JourDeNaissance_Charte"] = afficher_charte(int(data["JourDeNaissanceTotal"]), int(data["JourDeNaissance"]))
    data["MoisDeNaissance_Charte"] = afficher_charte(int(data["MoisDeNaissanceTotal"]), int(data["MoisDeNaissance"]))
    data["AnneeDeNaissance_Charte"] = afficher_charte(int(data["AnneeDeNaissanceTotal"]), int(data["AnneeDeNaissance"]))
    #constitution des listes de nombres maîtres, karmiques et sous-nombres
    sous_nombres, nombres_maitres, nombres_karmiques = constitution_liste_nombres_speciaux(
        [
            data["NbCdVTotal_Final"],
            data["NbExpTotal_Final"],
            data["NbReaTotal_Final"],
            data["NbAmeTotal_Final"],
            data["NbActifTotal"],
            data["NbHerediteTotal"]
        ]
    )
    data["SousNombres"] = sous_nombres
    data["NombresMaitres"] = nombres_maitres
    data["NombresKarmiques"] = nombres_karmiques



    # pour visualiser les réslutat dans la console serveur ou Railway
    print("[calculs_api.py]  === Données après étape 2 ===")
    for cle, valeur in data.items():
        print(f"{cle} : {valeur}")

    #appel de la fonction de l'étape 3
    #data["url_html"] = etape_3_injection_textes_dans_html(data)







########### Etape 3 ################

 #Étape 3 : appelle l'API d'injection des textes dans le template HTML.
 #Renvoie l'URL du HTML généré (ou chaîne vide en cas d’erreur).
 

def etape_3_injection_textes_dans_html(data: dict) -> dict:
    try:
        injection_url = os.getenv("INJECTION_HTML_URL")
        if not injection_url:
            raise ValueError("INJECTION_HTML_URL n’est pas définie dans les variables d’environnement.")
        
        print("🔁 [calculs_api.py] Appel à l'API d'injection HTML...")
        response = requests.post(injection_url, json=data)
        response.raise_for_status()

        url_html = response.json().get("url_html", "")
        print("📄 [calculs_api.py] HTML généré :", url_html)

        print("📦 [calculs_api.py] Étape 4 : Génération du PDF depuis le HTML")
        chemin_pdf = etape_4_generation_pdf_depuis_html(url_html)

        return {
            "url_html": url_html,
            "chemin_pdf": chemin_pdf
        }

    except Exception as e:
        print(f"❌ [calculs_api.py] Échec de l’injection des textes ou génération PDF : {e}")
        return {"erreur": str(e)}





########### Etape 4 ################

#Génération du pdf à partir du HTML avec les textes injectés

def etape_4_generation_pdf_depuis_html(url_html: str):
    try:
        generation_pdf_url = os.getenv("GENERATION_PDF_URL")
        if not generation_pdf_url:
            raise ValueError("GENERATION_PDF_URL non définie")

        print("📤 Appel à l'API PDF...")
        response = requests.post(generation_pdf_url, json={"html_url": url_html})
        response.raise_for_status()

        pdf_bytes = response.content
        print("✅ PDF généré avec succès (contenu récupéré)")

        # Retourne un StreamingResponse vers le frontend
        return StreamingResponse(io.BytesIO(pdf_bytes), media_type="application/pdf")
    except Exception as e:
        print(f"❌ Erreur lors de la génération du PDF : {e}")
        return None






#############fonctions pour lancer les scripts des étapes depuis main.py

def traitement_etape_1(data):
    lignes = []  # pas utilisé ici mais conservé pour cohérence future
    etape_1_preparer_variables_initiales_et_calculs_avant_test_act(data, lignes)
    return data
