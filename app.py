import streamlit as st

# --- Configuration du Jeu ---
MOT_MYSTERE_FIXE = "QUIETUDE"
LONGUEUR_MOT = len(MOT_MYSTERE_FIXE)  # Longueur: 8
PREMIERE_LETTRE = MOT_MYSTERE_FIXE[0]  # Première lettre: Q

# --- Styles CSS pour l'interface (Rouge pour l'absence) ---
STYLE_SUTOM = """
<style>
    /* Styles de base pour les cases de la grille */
    .ligne-sutom {
        display: flex;
        justify-content: center;
        margin: 5px 0;
    }
    .case-sutom {
        display: inline-flex;
        justify-content: center;
        align-items: center;
        width: 45px;
        height: 45px;
        margin: 3px;
        font-size: 24px;
        font-weight: bold;
        border-radius: 4px;
        text-transform: uppercase;
        border: 2px solid #787c7e; 
        background-color: #fff;
        color: #333;
    }
    /* Classes de couleur basées sur l'évaluation */
    .correct {
        background-color: #6aaa64 !important; /* Vert */
        border-color: #6aaa64 !important;
        color: white !important;
    }
    .misplaced {
        background-color: #ff9900 !important; /* Orange/Jaune vif */
        border-color: #ff9900 !important;
        color: white !important;
    }
    .absent {
        background-color: #cc0000 !important; /* ROUGE */
        border-color: #cc0000 !important;
        color: white !important;
    }
</style>
"""
st.markdown(STYLE_SUTOM, unsafe_allow_html=True)


# --- Initialisation de l'état de session ---
if 'historique_propositions' not in st.session_state:
    st.session_state.historique_propositions = []
if 'trouve' not in st.session_state:
    st.session_state.trouve = False
if 'message_erreur' not in st.session_state:
    st.session_state.message_erreur = ""


# --- Fonctions d'évaluation et d'affichage ---

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
    
    comptage_mystere = {lettre: mot_mystere.count(lettre) for lettre in mot_mystere}
    evaluation = [None] * LONGUEUR_MOT
    
    # 1. Marquage du Vert (correct)
    for i in range(LONGUEUR_MOT):
        if proposition_list[i] == mot_mystere_list[i]:
            evaluation[i] = (proposition_list[i], "correct")
            comptage_mystere[proposition_list[i]] -= 1
        else:
            evaluation[i] = (proposition_list[i], "absent") # Temporaire

    # 2. Marquage du Orange (misplaced) ou Rouge (absent)
    for i in range(LONGUEUR_MOT):
        lettre = proposition_list[i]
        if evaluation[i][1] == "absent":  # Si pas encore Vert
            if comptage_mystere.get(lettre, 0) > 0:
                evaluation[i] = (lettre, "misplaced")  # Orange
                comptage_mystere[lettre] -= 1
            else:
                evaluation[i] = (lettre, "absent") # Rouge

    return evaluation

def afficher_grille_sutom(evaluation):
    """Affiche une ligne de la grille d'historique en utilisant les classes CSS."""
    html_content = ""
    for lettre, classe_css in evaluation:
        html_content += f'<div class="case-sutom {classe_css}">{lettre}</div>'
    st.markdown(f'<div class="ligne-sutom">{html_content}</div>', unsafe_allow_html=True)

def afficher_ligne_saisie(mot_saisi):
    """Affiche la ligne de saisie active (simulée dans la grille)."""
    html_content = ""
    mot_saisi = mot_saisi.upper().ljust(LONGUEUR_MOT, ' ')
    
    for i in range(LONGUEUR_MOT):
        lettre = mot_saisi[i]
        # La première lettre est toujours la bonne et est verte
        classe = "correct" if i == 0 else ""
        
        # Le style de la case non remplie est par défaut (non colorée)
        html_content += f'<div class="case-sutom {classe}" style="border: 2px solid #333333; background-color: #f0f0f0;">{lettre}</div>'
        
    st.markdown(f'### 📝 Proposition Actuelle\n<div class="ligne-sutom">{html_content}</div>', unsafe_allow_html=True)


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
    
    # Réinitialisation de l'entrée après soumission
    if not st.session_state.trouve:
        st.session_state.input_prop = PREMIERE_LETTRE 

# --- Interface Utilisateur Streamlit ---

st.title("🤫 SUTOM Personnalisé : QUIETUDE")
st.markdown(f"Trouvez le mot mystère de **{LONGUEUR_MOT} lettres** qui commence par **{PREMIERE_LETTRE}**.")
st.markdown("> *🟢 Vert : Bonne position. 🟠 Orange : Mal placée. 🔴 Rouge : Absente.*")


# --- Section Formulaire de Saisie (Zone de texte cachée) ---

# Nous utilisons une zone de texte pour capturer l'entrée de l'utilisateur
# La valeur par défaut est toujours la première lettre
if not st.session_state.get('input_prop'):
     st.session_state.input_prop = PREMIERE_LETTRE

if not st.session_state.trouve:
    # Simuler la saisie directe dans la grille en affichant la ligne active
    proposition_utilisateur = st.text_input(
        f"Tapez votre mot de {LONGUEUR_MOT} lettres ici :", 
        key="input_prop", 
        max_chars=LONGUEUR_MOT,
        help="La première lettre est déjà remplie."
    ).strip().upper()
    
    # Afficher la ligne de saisie active basée sur ce qui est tapé
    afficher_ligne_saisie(proposition_utilisateur)
    
    st.button(
        "Soumettre la Proposition",
        on_click=gerer_proposition_soumise,
        args=[proposition_utilisateur]
    )
    
    if st.session_state.message_erreur:
        st.error(st.session_state.message_erreur)
        st.session_state.message_erreur = ""

# --- Section Grille d'Historique ---
st.header("Grille d'Historique des Tentatives")

# Afficher les tentatives précédentes
if st.session_state.historique_propositions:
    for evaluation in st.session_state.historique_propositions:
        afficher_grille_sutom(evaluation)
else:
    # Afficher la première ligne de l'historique vide
    html_content = ""
    for i in range(LONGUEUR_MOT):
        lettre = PREMIERE_LETTRE if i == 0 else " "
        classe = "case-sutom correct" if i == 0 else "case-sutom"
        html_content += f'<div class="{classe}">{lettre}</div>'
    st.markdown(f'### 🏁 Première Ligne (Départ)\n<div class="ligne-sutom">{html_content}</div>', unsafe_allow_html=True)


# --- Section Fin de Partie et Réinitialisation ---
if st.session_state.trouve:
    st.success(f"🎉 FÉLICITATIONS ! Le mot mystère était **{MOT_MYSTERE_FIXE}** ! Vous avez trouvé en {len(st.session_state.historique_propositions)} tentatives.")
    st.balloons()

def reinitialiser_jeu():
    st.session_state.historique_propositions = []
    st.session_state.trouve = False
    st.session_state.input_prop = PREMIERE_LETTRE # Réinitialiser à la première lettre

if st.session_state.trouve:
    st.header("Partie Terminée")
    st.button("Recommencer une nouvelle partie", on_click=reinitialiser_jeu)
elif st.button("Réinitialiser le jeu"):
    reinitialiser_jeu()
    st.rerun()
