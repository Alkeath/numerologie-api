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









def traitement_numerologie_depuis_json(data):
    # --- Logiques à partir du formulaire ---
    somme_11 = sum(convertir_en_int(data.get(f"QuestionAct11_{i}_Formulaire", 0)) for i in range(1, 4))
    somme_22 = sum(convertir_en_int(data.get(f"QuestionAct22_{i}_Formulaire", 0)) for i in range(1, 4))
    somme_prenoms = sum(convertir_en_int(data.get(k, 0)) for k in ["QuestionExp_Formulaire", "QuestionRea_Formulaire", "QuestionAme_Formulaire"])

    data["QuestionAct11_Somme"] = str(somme_11)
    data["QuestionAct22_Somme"] = str(somme_22)
    data["QuestionsPrenomsSomme"] = str(somme_prenoms)
    data["TousLesPrenoms"] = "oui" if somme_prenoms >= 0 else "non"
    data["ActNbMaitre11"] = "oui" if somme_11 >= 2 else "non"
    data["ActNbMaitre22"] = "oui" if somme_22 >= 2 else "non"

    # --- Champs noms/prénoms nettoyés ---
    secondaire = data.get("PrenomsSecondaires_Formulaire", "").strip()
    data["PrenomsComplets_Formulaire"] = f"{data.get('PrenomPremier_Formulaire', '').strip()} {secondaire}".strip()
    data["Nom"] = nettoyer_chaine_nom_prenom(data.get("Nom_Formulaire", ""), majuscules=True)
    data["PrenomPremier"] = nettoyer_chaine_nom_prenom(data.get("PrenomPremier_Formulaire", ""))
    data["PrenomsComplets"] = nettoyer_chaine_nom_prenom(data.get("PrenomsComplets_Formulaire", ""))
    data["PrenomNom_UnPrenom"] = f"{data['PrenomPremier']} {data['Nom']}".strip()
    data["PrenomNom_TousPrenoms"] = f"{data['PrenomsComplets']} {data['Nom']}".strip()

    for champ in ["Nom", "PrenomPremier", "PrenomsComplets"]:
        data[f"{champ}_normalise"] = normaliser_chaine(data[champ])

    textes = {
        "UnPrenom": (data["PrenomPremier_normalise"] + data["Nom_normalise"]).replace(" ", ""),
        "TousPrenoms": (data["PrenomsComplets_normalise"] + data["Nom_normalise"]).replace(" ", "")
    }

    for prefixe in ["UnPrenom", "TousPrenoms"]:
        texte = textes[prefixe]
        data.update(calcul_grille_intensite(texte, prefixe, []))
        plan = calcul_plan_expression(texte, prefixe)
        if isinstance(plan, dict):
            data.update(plan)

    chiffres_date = [int(c) for c in data.get("DateDeNaissance_Formulaire", "") if c.isdigit()]
    total_cdv = sum(chiffres_date)
    reduit_cdv = ReductionNombre(total_cdv)
    data["NbCdVTotal"] = str(total_cdv)
    data["NbCdV_AvantTestAct"] = str(reduit_cdv)

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
        data[f"NbAmeTotal_{prefixe}"] = str(total_ame)
        data[f"NbReaTotal_{prefixe}"] = str(total_rea)
        data[f"NbExp_{prefixe}_AvantTestAct"] = str(ReductionNombre(total_exp))
        data[f"NbAme_{prefixe}_AvantTestAct"] = str(ReductionNombre(total_ame))
        data[f"NbRea_{prefixe}_AvantTestAct"] = str(ReductionNombre(total_rea))

        prenom_txt = data["PrenomPremier_normalise"] if prefixe == "UnPrenom" else data["PrenomsComplets_normalise"]
        total_actif = sum(valeur_lettre(l) for l in prenom_txt if l.isalpha())
        data[f"NbActifTotal_{prefixe}"] = str(total_actif)
        data[f"NbActif_{prefixe}_AvantTestAct"] = str(ReductionNombre(total_actif))
        data[f"NbActif_Charte_{prefixe}"] = afficher_charte(total_actif, ReductionNombre(total_actif))

        for cle_base in ["NbExp", "NbAme", "NbRea"]:
            total = data[f"{cle_base}Total_{prefixe}"]
            reduit = data[f"{cle_base}_{prefixe}_AvantTestAct"]
            data[f"{cle_base}_Charte_{prefixe}_AvantTestAct"] = afficher_charte(total, reduit)

    texte_nom = data.get("Nom_normalise", "")
    total_h = sum(valeur_lettre(l) for l in texte_nom if l.isalpha())
    reduit_h = ReductionNombre(total_h)
    data["NbHerediteTotal"] = str(total_h)
    data["NbHeredite"] = str(reduit_h)
    data["NbHeredite_Charte"] = afficher_charte(total_h, reduit_h)

    utiliser_tous = data["TousLesPrenoms"].lower() == "oui"
    activer_11 = data["ActNbMaitre11"].lower() == "oui"
    activer_22 = data["ActNbMaitre22"].lower() == "oui"
    suffixe = "TousPrenoms" if utiliser_tous else "UnPrenom"

    def get_val(cle): return data.get(f"{cle}_{suffixe}_AvantTestAct", "")
    def get_total(cle): return data.get(f"{cle}Total_{suffixe}", "")

    for cle_base in ["NbExp", "NbRea", "NbAme", "NbActif"]:
        data[cle_base] = str(ajuster_nombre_maitre(get_val(cle_base), activer_11, activer_22))
        data[f"{cle_base}Total"] = get_total(cle_base)
        data[f"{cle_base}_Charte"] = afficher_charte(data[f"{cle_base}Total"], data[cle_base])

    data["NbCdV"] = str(ajuster_nombre_maitre(data["NbCdV_AvantTestAct"], activer_11, activer_22))
    data["NbCdV_Charte"] = afficher_charte(data["NbCdVTotal"], data["NbCdV"])
    data["NbActif_Charte"] = data[f"NbActif_Charte_{suffixe}"]
    data["NbHeredite_Charte"] = afficher_charte(data["NbHerediteTotal"], data["NbHeredite"])

    for i in range(1, 10):
        data[f"NombreDe{i}"] = data.get(f"NombreDe{i}_{suffixe}", "")

    for nom in [
        "NombreLettresTotal", "IntensiteDiagonaleAscendante", "IntensiteDiagonaleDescendante",
        "IntensiteSeuilExces", "NombresEnExces", "NombresManquants"
    ]:
        data[nom] = data.get(f"{nom}_{suffixe}", "")

    for plan in [
        "MenCar", "MenMut", "MenFix", "MenTot",
        "PhyCar", "PhyMut", "PhyFix", "PhyTot",
        "EmoCar", "EmoMut", "EmoFix", "EmoTot",
        "IntCar", "IntMut", "IntFix", "IntTot",
        "CarTot", "MutTot", "FixTot"
    ]:
        data[plan] = data.get(f"{plan}_{suffixe}", "")

    try:
        date_naissance = datetime.strptime(data["DateDeNaissance_Formulaire"], "%d/%m/%Y")
        jour, mois, annee = date_naissance.day, date_naissance.month, date_naissance.year
        jour_r, mois_r, annee_r = ReductionNombre(jour), ReductionNombre(mois), ReductionNombre(annee)

        data["JourDeNaissanceTot"] = str(jour)
        data["MoisDeNaissanceTot"] = str(mois)
        data["AnneeDeNaissanceTot"] = str(annee)
        data["JourDeNaissance"] = str(jour_r)
        data["MoisDeNaissance"] = str(mois_r)
        data["AnneeDeNaissance"] = str(annee_r)
        data["JourDeNaissance_Charte"] = afficher_charte(jour, jour_r)
        data["MoisDeNaissance_Charte"] = afficher_charte(mois, mois_r)
        data["AnneeDeNaissance_Charte"] = afficher_charte(annee, annee_r)

        data["CycleFormatif"] = str(ReductionForcee(mois))
        data["CycleProductif"] = str(ReductionForcee(jour))
        data["CycleMoisson"] = str(ReductionForcee(annee))

        p1 = ReductionForcee(jour + mois)
        p2 = ReductionForcee(jour + annee)
        p3 = ReductionForcee(p1 + p2)
        p4 = ReductionForcee(mois + annee)
        data.update({
            "Periode1": str(p1), "Periode2": str(p2), "Periode3": str(p3), "Periode4": str(p4),
            "AnneePersonnelle": str(ReductionForcee(jour + mois + date.today().year)),
            "Age": str(date.today().year - annee - ((date.today().month, date.today().day) < (mois, jour))),
            "DefiMineur1": str(ReductionForcee(abs(jour - mois))),
            "DefiMineur2": str(ReductionForcee(abs(jour_r - annee_r))),
            "DefiMajeur": str(ReductionForcee(abs(ReductionForcee(abs(jour - mois)) - ReductionForcee(abs(jour_r - annee_r)))))
        })
    except Exception as e:
        data["Erreur_DateNaissance"] = str(e)

    for mode in ["UnPrenom", "TousPrenoms"]:
        sous, maitres, karmiques = calcul_nombres_speciaux(data, mode)
        data[f"SousNombres_{mode}"] = formater_liste(sous)
        data[f"NombresMaitres_{mode}"] = formater_liste(maitres)
        data[f"NombresKarmiques_{mode}"] = formater_liste(karmiques)

    final = "TousPrenoms" if utiliser_tous else "UnPrenom"
    for key in ["SousNombres", "NombresMaitres", "NombresKarmiques"]:
        data[key] = data[f"{key}_{final}"]
        data[f"{key}_Charte"] = data[key]

    return data
