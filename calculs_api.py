import unicodedata
import re
from datetime import datetime, date


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

def calcul_grille_intensite(texte, prefixe, lignes):
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

    # ➕ Mise à jour dans `lignes`
    for ligne in lignes:
        cle = ligne[0].strip()
        if cle == f"NombreLettresTotal_{prefixe}":
            ligne[1] = str(total_lettres)
        for i in range(1, 10):
            if cle == f"NombreDe{i}_{prefixe}":
                ligne[1] = str(compteur[i])
        if cle == f"IntensiteDiagonaleAscendante_{prefixe}":
            ligne[1] = str(diagonale_asc)
        elif cle == f"IntensiteDiagonaleDescendante_{prefixe}":
            ligne[1] = str(diagonale_desc)
        elif cle == f"IntensiteSeuilExces_{prefixe}":
            ligne[1] = f"{seuil_exces:.2f}"
        elif cle == f"NombresManquants_{prefixe}":
            ligne[1] = ", ".join(manquants)
        elif cle == f"NombresEnExces_{prefixe}":
            ligne[1] = ", ".join(exces)

    # ➕ Retourner un dictionnaire pour `data.update(...)`
    resultat = {
        f"NombreLettresTotal_{prefixe}": str(total_lettres),
        f"IntensiteDiagonaleAscendante_{prefixe}": str(diagonale_asc),
        f"IntensiteDiagonaleDescendante_{prefixe}": str(diagonale_desc),
        f"IntensiteSeuilExces_{prefixe}": f"{seuil_exces:.2f}",
        f"NombresManquants_{prefixe}": ", ".join(manquants),
        f"NombresEnExces_{prefixe}": ", ".join(exces),
    }
    for i in range(1, 10):
        resultat[f"NombreDe{i}_{prefixe}"] = str(compteur[i])

    return resultat

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

def calcul_plan_expression(texte, suffixe):
    texte = texte.replace(" ", "").upper()
    resultats = {cle + f"_{suffixe}": 0 for cle in plan_expression}

    for lettre in texte:
        for cle, lettres in plan_expression.items():
            if lettre in lettres:
                resultats[cle + f"_{suffixe}"] += 1

    for domaine in ["Men", "Phy", "Emo", "Int"]:
        resultats[f"{domaine}Tot_{suffixe}"] = sum(
            resultats[f"{domaine}{typ}_{suffixe}"] for typ in ["Car", "Mut", "Fix"]
        )

    for typ in ["Car", "Mut", "Fix"]:
        resultats[f"{typ}Tot_{suffixe}"] = sum(
            resultats[f"{domaine}{typ}_{suffixe}"] for domaine in ["Men", "Phy", "Emo", "Int"]
        )

    return resultats


# --- Détection des nombres maîtres, sous-nombres, nombres karmiques ---
def calcul_nombres_speciaux(data, mode="UnPrenom"):
    nombres_maitres_fixes = {11, 22, 33, 44, 55, 66, 77, 88, 99}
    nombres_karmiques_fixes = {13, 14, 16, 19}

    if mode == "UnPrenom":
        cles = [
            "NbExpTotal_UnPrenom", "NbReaTotal_UnPrenom", "NbAmeTotal_UnPrenom",
            "NbActifTotal_UnPrenom", "NbCdVTotal"
        ]
    elif mode == "TousPrenoms":
        cles = [
            "NbExpTotal_TousPrenoms", "NbReaTotal_TousPrenoms", "NbAmeTotal_TousPrenoms",
            "NbActifTotal_TousPrenoms", "NbCdVTotal"
        ]
    else:
        return [], [], []

    # Extraction des sous-nombres
    sous_nombres = set()
    for cle in cles:
        val = data.get(cle)
        if val and val.isdigit():
            sous_nombres.add(int(val))

    # Détection des maîtres
    def est_maitre(n):
        return (
            n in nombres_maitres_fixes
            or (sum(int(c) for c in str(n)) % 11 == 0 and sum(int(c) for c in str(n)) > 0)
        )

    nombres_maitres = sorted({n for n in sous_nombres if est_maitre(n)})
    nombres_karmiques = sorted({n for n in sous_nombres if n in nombres_karmiques_fixes})

    return sorted(sous_nombres), nombres_maitres, nombres_karmiques

# --- Formatage de la liste des nombres maîtres, sous-nombres, nombres karmiques pour la charte
def formater_liste(liste):
    """Retourne une chaîne triée de nombres uniques séparés par virgules."""
    return ", ".join(str(n) for n in sorted(set(liste)))


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











# Etape 1 : traiement des données entrées, calculs, jusqu'aux qestions pour savoir
# si le nombres maîtres sont activés où pas s'il y a des 11 ou 22
def etape_1_preparer_variables_initiales_et_calculs_avant_test_act(data, lignes):
    
    # Récupération des champs bruts depuis le formulaire
    PrenomPremier_Formulaire = data.get("PrenomPremier_Formulaire", "").strip()
    PrenomsSecondaires_Formulaire = data.get("PrenomsSecondaires_Formulaire", "").strip()
    Nom_Formulaire = data.get("Nom_Formulaire", "").strip()
    Jour_Formulaire = data.get("Jour_Formulaire", "").strip()
    Mois_Formulaire = data.get("Mois_Formulaire", "").strip()
    Annee_Formulaire = data.get("Annee_Formulaire", "").strip()

    # Étape 1 : nettoyage
    PrenomPremier = nettoyer_chaine_nom_prenom(PrenomPremier_Formulaire, majuscules=False)
    PrenomsComplets = f"{PrenomPremier} {nettoyer_chaine_nom_prenom(PrenomsSecondaires_Formulaire, majuscules=False)}".strip()
    Nom = nettoyer_chaine_nom_prenom(Nom_Formulaire, majuscules=True)

    # Étape 2 : normalisation
    PrenomPremier_normalise = normaliser_chaine(PrenomPremier)
    PrenomsComplets_normalise = normaliser_chaine(PrenomsComplets)
    Nom_normalise = normaliser_chaine(Nom)

  


    # Sauvegarde dans les variables de travail
    data["PrenomPremier"] = PrenomPremier
    data["PrenomsComplets"] = PrenomsComplets
    data["Nom"] = Nom
    data["PrenomPremier_normalise"] = PrenomPremier_normalise
    data["PrenomsComplets_normalise"] = PrenomsComplets_normalise
    data["Nom_normalise"] = Nom_normalise
    data["PrenomNom_UnPrenom"] = f"{data['PrenomPremier']} {data['Nom']}"
    data["PrenomNom_TousPrenoms"] = f"{data['PrenomsComplets']} {data['Nom']}"


    # Constitution de la date de naissance au format JJ/MM/AAAA
    if Jour_Formulaire and Mois_Formulaire and Annee_Formulaire:
        data["DateDeNaissance"] = f"{Jour_Formulaire.zfill(2)}/{Mois_Formulaire.zfill(2)}/{Annee_Formulaire}"
    else:
        data["DateDeNaissance"] = ""

    # Calcul du chemin de vie
    chiffres_date = [int(c) for c in data.get("DateDeNaissance", "") if c.isdigit()]
    total_cdv = sum(chiffres_date)
    reduit_cdv = ReductionNombre(total_cdv)
    data["NbCdVTotal"] = str(total_cdv)
    data["NbCdV_AvantTestAct"] = str(reduit_cdv)

    #Calcul des nombres d'Expression, Réalisation, Ame avant test activation Nb Maîtres
    
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
        
    # Détection de la présence d’un 11 ou 22 parmi les 4 nombres principaux
    valeurs = [
        data.get("NbCdV_AvantTestAct", ""),
        data.get("NbExp_UnPrenom_AvantTestAct", ""),
        data.get("NbRea_UnPrenom_AvantTestAct", ""),
        data.get("NbAme_UnPrenom_AvantTestAct", "")
    ]

    data["Presence11"] = "oui" if "11" in valeurs else "non"
    data["Presence22"] = "oui" if "22" in valeurs else "non"


#fonction temporaire de test de l'étape 1
def traitement_etape_1(data):
    lignes = []  # pas utilisé ici mais conservé pour cohérence future
    etape_1_preparer_variables_initiales_et_calculs_avant_test_act(data, lignes)
    return data



#Etape 2 : en fonction des réponses aux quesetions sur  l'activation des nombres maîtres
# on met à jour CdV, Exp, Rea, Ame
def etape_2_appliquer_reponses_activation_maitres(donnees):
    """
    Applique les réponses de l'utilisateur sur l'activation des nombres maîtres 11 et 22,
    en ajustant les variables *_ApresTestAct à partir des *_AvantTestAct.
    - Si 11 désactivé, il devient 2.
    - Si 22 désactivé, il devient 4.
    """
    def ajuster_valeur(valeur_str, act11, act22):
        try:
            valeur = int(valeur_str)
        except:
            return valeur_str  # Retourne la valeur telle quelle si ce n’est pas un entier
        if valeur == 11 and act11 == "non":
            return 2
        elif valeur == 22 and act22 == "non":
            return 4
        else:
            return valeur

    act11 = donnees.get("ActNbMaitre11", "non")
    act22 = donnees.get("ActNbMaitre22", "non")

    # Cas Chemin de Vie (pas de distinction prénoms)
    donnees["NbCdV_ApresTestAct"] = ajuster_valeur(
        donnees.get("NbCdV_AvantTestAct", ""), act11, act22
    )

    # Cas Expression, Réalisation, Âme — Un Prénom
    for nom in ["Exp", "Rea", "Ame"]:
        cle_avant = f"Nb{nom}_UnPrenom_AvantTestAct"
        cle_apres = f"Nb{nom}_UnPrenom_ApresTestAct"
        donnees[cle_apres] = ajuster_valeur(donnees.get(cle_avant, ""), act11, act22)

    # Cas Expression, Réalisation, Âme — Tous les Prénoms
    for nom in ["Exp", "Rea", "Ame"]:
        cle_avant = f"Nb{nom}_TousPrenoms_AvantTestAct"
        cle_apres = f"Nb{nom}_TousPrenoms_ApresTestAct"
        donnees[cle_apres] = ajuster_valeur(donnees.get(cle_avant, ""), act11, act22)
