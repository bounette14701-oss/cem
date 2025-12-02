import streamlit as st

# --- Le mot mystère est maintenant fixé ici ---
MOT_MYSTERE_FIXE = "QUIETUDE"
LONGUEUR_MOT = len(MOT_MYSTERE_FIXE)  # Longueur: 8
PREMIERE_LETTRE = MOT_MYSTERE_FIXE[0]  # Première lettre: Q
# ---------------------------------------------

# --- Styles CSS pour les cases ---
# Les classes CSS sont définies pour le Vert, Jaune, Gris
STYLE_SUTOM = """
<style>
    /* Styles généraux des lignes et de la grille */
    .ligne-sutom {
        display: flex;
        justify-content: center;
        margin: 5px 0;
    }
    /* Styles de base pour chaque case (carré) */
    .case-sutom {
        display: inline-flex;
        justify-content: center;
        align-items: center;
        width: 45px;
        height: 45px;
        margin: 3px;
        border: 2px solid #787c7e; /* Gris par défaut */
        background-color: #fff; /* Fond blanc par défaut */
        color: #333;
        font-size: 24px;
        font-weight: bold;
        border-radius: 4px;
        text-transform: uppercase;
    }
    /* Classes de couleur basées sur l'évaluation */
    .correct {
        background-color: #6aaa64 !important; /* Vert */
        border-color: #6aaa64 !important;
        color: white !important;
    }
    .misplaced {
        background-color: #c9b458 !important; /* Jaune */
        border-color: #c9b458 !important;
        color: white !important;
    }
    .absent {
        background-color: #787c7e !important; /* Gris foncé */
        border-color: #787c7e !important;
        color: white !important;
    }
</style>
"""

# Injection du style au début de l'application
st.markdown(STYLE_SUTOM, unsafe_allow_html=True)


def evaluer_proposition_sutom(mot_mystere, proposition):
    """
    Évalue la proposition selon les règles de couleur du SUTOM.
    Retourne une liste de tuples (lettre, classe_css).
    """
    mot_mystere = mot_mystere.upper()
    proposition = proposition.upper()
    
    if len(proposition) != len(mot_mystere):
        return [(l, "absent") for l in proposition]

    mot_mystere_list = list(mot_mystere)
    proposition_list = list(proposition)
    
    comptage_mystere = {}
    for lettre in mot_mystere:
        comptage_mystere[lettre] = comptage_mystere.get(lettre, 0) + 1
        
    evaluation = [None] * LONGUEUR_MOT
    
    # Phase 1 : Marquage du Vert (lettre bien placée)
    for i in range(LONGUEUR_MOT):
        if proposition_list[i] == mot_mystere_list[i]:
            evaluation[i] = (proposition_list[i], "correct")
            comptage_mystere[proposition_list[i]] -= 1
        else:
            evaluation[i] = (proposition_list[i], "absent") # Temporaire

    # Phase 2 : Marquage du Jaune (mal placée) et du Gris final (absente)
    for i in range(LONGUEUR_MOT):
        if evaluation[i][1] == "absent":  # Si ce n'est pas Vert
            lettre = proposition_list[i]
            if lettre in comptage_mystere and comptage_mystere[lettre] > 0:
                evaluation[i] = (lettre, "misplaced")  # Jaune
                comptage_mystere[lettre] -= 1
            else:
                evaluation[i] = (lettre, "absent") # Gris

    return evaluation

def afficher_grille_sutom(evaluation):
    """
    Affiche une ligne de la grille SUTOM en utilisant les classes CSS.
    """
    html_content = ""
    
    for lettre, classe_css in evaluation:
        # Utilisation de la classe CSS pour la couleur et le style
        html_content += f"""
        <div class="case-sutom {classe_css}">
            {lettre}
        </div>
        """
    # Utilisation de la ligne CSS pour centrer et organiser
    st.markdown(f'<div class="ligne-sutom">{html_content}</div>', unsafe_allow_html=True)


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
    # Afficher la première ligne avec la première lettre révélée (stylisée)
    premiere_ligne = [(PREMIERE_LETTRE, "correct")] + [(" ", "case-sutom")] * (LONGUEUR_MOT - 1)
    # L'affichage de la première ligne non encore jouée doit utiliser une classe "case-sutom" générique
    html_content = ""
    for lettre, classe in premiere_ligne:
        # Si c'est la première lettre, on lui donne la classe "correct"
        if lettre == PREMIERE_LETTRE:
             html_content += f'<div class="case-sutom correct">{lettre}</div>'
        # Sinon, c'est une case vide non colorée par défaut
        else:
             html_content += f'<div class="case-sutom"> </div>'
    st.markdown(f'<div class="ligne-sutom">{html_content}</div>', unsafe_allow_html=True)


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
