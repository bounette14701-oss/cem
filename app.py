import streamlit as st

# --- Le mot mystère est maintenant fixé ici ---
MOT_MYSTERE_FIXE = "QUIETUDE"
LONGUEUR_MOT = len(MOT_MYSTERE_FIXE)  # Longueur: 8
PREMIERE_LETTRE = MOT_MYSTERE_FIXE[0]  # Première lettre: Q
# ---------------------------------------------

def evaluer_proposition_sutom(mot_mystere, proposition):
    """
    Évalue la proposition selon les règles de couleur du SUTOM.
    Retourne une liste de tuples (lettre, couleur_css).
    """
    mot_mystere = mot_mystere.upper()
    proposition = proposition.upper()
    
    # Vérification de la longueur pour la sécurité
    if len(proposition) != len(mot_mystere):
        return [(l, "#787c7e") for l in proposition]

    mot_mystere_list = list(mot_mystere)
    proposition_list = list(proposition)
    
    # Étape 1 : Compter les occurrences de lettres dans le mot mystère
    comptage_mystere = {}
    for lettre in mot_mystere:
        comptage_mystere[lettre] = comptage_mystere.get(lettre, 0) + 1
        
    evaluation = [None] * LONGUEUR_MOT
    
    # Phase 1 : Marquage du Vert (lettre bien placée)
    for i in range(LONGUEUR_MOT):
        if proposition_list[i] == mot_mystere_list[i]:
            evaluation[i] = (proposition_list[i], "#6aaa64")  # Vert
            comptage_mystere[proposition_list[i]] -= 1
        else:
            evaluation[i] = (proposition_list[i], "#787c7e")  # Gris (Temporaire)

    # Phase 2 : Marquage du Jaune (lettre présente, mauvaise position) et du Gris final
    for i in range(LONGUEUR_MOT):
        if evaluation[i][1] == "#787c7e":  # Si ce n'est pas Vert
            lettre = proposition_list[i]
            if lettre in comptage_mystere and comptage_mystere[lettre] > 0:
                evaluation[i] = (lettre, "#c9b458")  # Jaune
                comptage_mystere[lettre] -= 1
            else:
                evaluation[i] = (lettre, "#787c7e")  # Gris

    return evaluation

def afficher_grille_sutom(evaluation):
    """
    Affiche une ligne de la grille SUTOM avec des couleurs de fond en HTML/CSS.
    """
    html_content = ""
    # Taille de case standard pour 8 lettres
    taille_case = "45px"
    
    for lettre, couleur in evaluation:
        html_content += f"""
        <div style="
            display: inline-flex;
            justify-content: center;
            align-items: center;
            width: {taille_case};
            height: {taille_case};
            margin: 2px;
            border: 2px solid {couleur};
            background-color: {couleur};
            color: white;
            font-size: 20px;
            font-weight: bold;
            border-radius: 4px;
        ">{lettre}</div>
        """
    st.markdown(f'<div style="display: flex; justify-content: center; margin: 10px 0;">{html_content}</div>', unsafe_allow_html=True)


# --- Fonction de rappel pour la soumission ---
def gerer_proposition_soumise(proposition_utilisateur):
    """
    Traite la proposition et l'ajoute à l'historique.
    """
    proposition_utilisateur = proposition_utilisateur.strip().upper()

    if not proposition_utilisateur or len(proposition_utilisateur) != LONGUEUR_MOT:
        st.session_state.message_erreur = f"Veuillez entrer un mot de {LONGUEUR_MOT} lettres."
        return
        
    if proposition_utilisateur[0] != PREMIERE_LETTRE:
        st.session_state.message_erreur = f"Le mot doit commencer par la lettre '{PREMIERE_LETTRE}'."
        return

    st.session_state.message_erreur = ""
    
    evaluation = evaluer_proposition_sutom(MOT_MYSTERE_FIXE, proposition_utilisateur)
    
    st.session_state.historique_propositions.append(evaluation)
    
    if proposition_utilisateur == MOT_MYSTERE_FIXE:
        st.session_state.trouve = True
    
    # Réinitialisation SÛRE du champ d'entrée
    if not st.session_state.trouve:
        st.session_state.input_prop = ""

# --- Initialisation de l'application Streamlit ---

st.title("🤫 SUTOM Personnalisé : QUIETUDE")
st.markdown(f"Trouvez le mot mystère de **{LONGUEUR_MOT} lettres** qui commence par **{PREMIERE_LETTRE}**.")
st.markdown("> *🟢 Vert : Bonne lettre, bonne position. 🟡 Jaune : Bonne lettre, mauvaise position.*")

# Initialisation des variables de session
if 'historique_propositions' not in st.session_state:
    st.session_state.historique_propositions = []
if 'trouve' not in st.session_state:
    st.session_state.trouve = False
if 'message_erreur' not in st.session_state:
    st.session_state.message_erreur = ""

# --- Affichage de l'historique de la grille SUTOM ---
st.header("Grille de Jeu")

if st.session_state.historique_propositions:
    for evaluation in st.session_state.historique_propositions:
        afficher_grille_sutom(evaluation)
else:
    # Afficher la première ligne avec la première lettre révélée
    premiere_ligne = [(PREMIERE_LETTRE, "#6aaa64")] + [(" ", "#787c7e")] * (LONGUEUR_MOT - 1)
    afficher_grille_sutom(premiere_ligne)

# --- Formulaire de Jeu ---
if not st.session_state.trouve:
    st.header("Faites une Proposition")
    
    proposition_utilisateur = st.text_input(
        f"Votre mot de {LONGUEUR_MOT} lettres :", 
        key="input_prop", 
        value=st.session_state.get('input_prop', '')
    ).strip().upper()
    
    # Vérification et appel de la fonction de rappel
    st.button(
        "Soumettre",
        on_click=gerer_proposition_soumise,
        args=[proposition_utilisateur]
    )
    
    if st.session_state.message_erreur:
        st.error(st.session_state.message_erreur)
        st.session_state.message_erreur = ""

# --- Fin de partie et Option de Réinitialisation ---
if st.session_state.trouve:
    st.success(f"🎉 FÉLICITATIONS ! Le mot mystère était **{MOT_MYSTERE_FIXE}** ! Vous avez trouvé en {len(st.session_state.historique_propositions)} tentatives.")
    st.balloons()

    st.header("Partie Terminée")
    def reinitialiser_jeu():
        st.session_state.historique_propositions = []
        st.session_state.trouve = False
        st.session_state.input_prop = "" 

    if st.button("Recommencer une nouvelle partie", on_click=reinitialiser_jeu):
        st.rerun()