import streamlit as st

# --- Configuration du Jeu ---
MOT_MYSTERE_FIXE = "QUIETUDE"
LONGUEUR_MOT = len(MOT_MYSTERE_FIXE)  # Longueur: 8
PREMIERE_LETTRE = MOT_MYSTERE_FIXE[0]  # Première lettre: Q

# Liste des lettres du clavier pour l'affichage
CLAVIER_LAYOUT = [
    "AZERTYUIOP",
    "QSDFGHJKLM",
    "WXCVBN"
]

# --- Initialisation de l'état de session ---
if 'historique_propositions' not in st.session_state:
    st.session_state.historique_propositions = []
if 'trouve' not in st.session_state:
    st.session_state.trouve = False
if 'message_erreur' not in st.session_state:
    st.session_state.message_erreur = ""
# État du clavier : {'A': 'default', 'B': 'absent', 'C': 'correct', ...}
if 'etat_clavier' not in st.session_state:
    st.session_state.etat_clavier = {chr(i): 'default' for i in range(ord('A'), ord('Z') + 1)}

# --- Styles CSS pour l'interface (Inclus Clavier) ---
STYLE_SUTOM = """
<style>
    /* Styles de base pour les cases de la grille */
    .ligne-sutom, .clavier-ligne {
        display: flex;
        justify-content: center;
        margin: 5px 0;
    }
    .case-sutom, .clavier-touche {
        display: inline-flex;
        justify-content: center;
        align-items: center;
        margin: 2px;
        font-weight: bold;
        border-radius: 4px;
        text-transform: uppercase;
        transition: background-color 0.3s;
    }
    .case-sutom {
        width: 45px;
        height: 45px;
        font-size: 24px;
        border: 2px solid #787c7e;
        background-color: #fff;
        color: #333;
    }
    .clavier-touche {
        width: 32px; /* Taille plus petite pour le clavier */
        height: 40px;
        font-size: 14px;
        background-color: #d3d6da; /* Gris clair par défaut */
        color: #333;
        border: none;
        cursor: default;
    }
    /* Classes de couleur */
    .correct { background-color: #6aaa64 !important; border-color: #6aaa64 !important; color: white !important; }
    .misplaced { background-color: #c9b458 !important; border-color: #c9b458 !important; color: white !important; }
    .absent { background-color: #787c7e !important; border-color: #787c7e !important; color: white !important; }
    .default { background-color: #d3d6da !important; color: #333 !important; }
</style>
"""
st.markdown(STYLE_SUTOM, unsafe_allow_html=True)


# --- Fonctions d'évaluation et d'affichage ---

def evaluer_proposition_sutom(mot_mystere, proposition):
    """
    Évalue la proposition et met à jour l'état du clavier.
    """
    mot_mystere = mot_mystere.upper()
    proposition = proposition.upper()
    mot_mystere_list = list(mot_mystere)
    proposition_list = list(proposition)
    
    comptage_mystere = {lettre: mot_mystere.count(lettre) for lettre in mot_mystere}
    evaluation = [None] * LONGUEUR_MOT
    
    # 1. Marquage du Vert (correct)
    for i in range(LONGUEUR_MOT):
        if proposition_list[i] == mot_mystere_list[i]:
            evaluation[i] = (proposition_list[i], "correct")
            comptage_mystere[proposition_list[i]] -= 1
            # Mise à jour du clavier : le vert est prioritaire
            st.session_state.etat_clavier[proposition_list[i]] = 'correct'
        else:
            evaluation[i] = (proposition_list[i], "absent") # Temporaire

    # 2. Marquage du Jaune (misplaced) ou Gris (absent)
    for i in range(LONGUEUR_MOT):
        lettre = proposition_list[i]
        if evaluation[i][1] == "absent":  # Si pas encore Vert
            if comptage_mystere.get(lettre, 0) > 0:
                evaluation[i] = (lettre, "misplaced")
                comptage_mystere[lettre] -= 1
                # Mise à jour du clavier : Jaune si pas déjà Vert
                if st.session_state.etat_clavier[lettre] != 'correct':
                    st.session_state.etat_clavier[lettre] = 'misplaced'
            else:
                evaluation[i] = (lettre, "absent")
                # Mise à jour du clavier : Gris si pas déjà Vert ou Jaune
                if st.session_state.etat_clavier[lettre] not in ['correct', 'misplaced']:
                    st.session_state.etat_clavier[lettre] = 'absent'

    return evaluation

def afficher_grille_sutom(evaluation):
    """Affiche une ligne de la grille en utilisant les classes CSS."""
    html_content = ""
    for lettre, classe_css in evaluation:
        html_content += f'<div class="case-sutom {classe_css}">{lettre}</div>'
    st.markdown(f'<div class="ligne-sutom">{html_content}</div>', unsafe_allow_html=True)

def afficher_clavier():
    """Affiche le clavier virtuel avec les couleurs de l'état."""
    for ligne in CLAVIER_LAYOUT:
        html_content = ""
        for lettre in ligne:
            # Récupère l'état de la lettre (default, correct, misplaced, absent)
            classe = st.session_state.etat_clavier.get(lettre, 'default')
            html_content += f'<div class="clavier-touche {classe}">{lettre}</div>'
        st.markdown(f'<div class="clavier-ligne">{html_content}</div>', unsafe_allow_html=True)

# --- Logique de Soumission ---
def gerer_proposition_soumise(proposition_utilisateur):
    """Traite la proposition et met à jour l'état du jeu."""
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
    
    if not st.session_state.trouve:
        st.session_state.input_prop = ""

# --- Interface Utilisateur Streamlit ---

st.title("🤫 SUTOM Personnalisé : QUIETUDE")
st.markdown(f"Trouvez le mot mystère de **{LONGUEUR_MOT} lettres** qui commence par **{PREMIERE_LETTRE}**.")
st.markdown("> *🟢 Vert : Bonne lettre, bonne position. 🟡 Jaune : Bonne lettre, mauvaise position.*")

# --- Section Grille d'Historique ---
st.header("Grille d'Historique")

# 1. Afficher les tentatives précédentes
if st.session_state.historique_propositions:
    for evaluation in st.session_state.historique_propositions:
        afficher_grille_sutom(evaluation)

# 2. Afficher la ligne de départ (tant que le jeu n'est pas terminé et que le joueur n'a pas encore fait de tentative)
if not st.session_state.trouve and not st.session_state.historique_propositions:
    # Ligne de départ non jouée avec la première lettre en Vert
    html_content = ""
    for i in range(LONGUEUR_MOT):
        lettre = PREMIERE_LETTRE if i == 0 else " "
        classe = "correct" if i == 0 else ""
        html_content += f'<div class="case-sutom {classe}">{lettre}</div>'
    st.markdown(f'<div class="ligne-sutom">{html_content}</div>', unsafe_allow_html=True)


# --- Section Fin de Partie ---
if st.session_state.trouve:
    st.success(f"🎉 FÉLICITATIONS ! Le mot mystère était **{MOT_MYSTERE_FIXE}** ! Vous avez trouvé en {len(st.session_state.historique_propositions)} tentatives.")
    st.balloons()
    st.header("Partie Terminée")
    
# --- Section Formulaire de Jeu ---
if not st.session_state.trouve:
    st.header("Faites une Proposition")
    
    proposition_utilisateur = st.text_input(
        f"Votre mot de {LONGUEUR_MOT} lettres :", 
        key="input_prop", 
        value=st.session_state.get('input_prop', '')
    ).strip().upper()
    
    st.button(
        "Soumettre",
        on_click=gerer_proposition_soumise,
        args=[proposition_utilisateur]
    )
    
    if st.session_state.message_erreur:
        st.error(st.session_state.message_erreur)
        st.session_state.message_erreur = ""

# --- Section Clavier Virtuel ---
st.header("Clavier Virtuel")
afficher_clavier()

# --- Option de Réinitialisation ---
if st.session_state.trouve or st.button("Recommencer une nouvelle partie"):
    def reinitialiser_jeu():
        st.session_state.historique_propositions = []
        st.session_state.trouve = False
        st.session_state.input_prop = "" 
        st.session_state.etat_clavier = {chr(i): 'default' for i in range(ord('A'), ord('Z') + 1)}
    
    if st.session_state.trouve:
        # Bouton de réinitialisation après victoire
        if st.button("Recommencer", on_click=reinitialiser_jeu):
            st.rerun()
    elif "Recommencer" not in st.session_state:
        # Si le bouton "Recommencer" générique a été cliqué
        reinitialiser_jeu()
        st.rerun()
