import streamlit as st

# --- Configuration du Jeu ---
MOT_MYSTERE_FIXE = "QUIETUDE"
LONGUEUR_MOT = len(MOT_MYSTERE_FIXE)  # Longueur: 8
PREMIERE_LETTRE = MOT_MYSTERE_FIXE[0]  # Première lettre: Q

# Liste des lettres du clavier pour l'affichage (AZERTY)
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
if 'etat_clavier' not in st.session_state:
    st.session_state.etat_clavier = {chr(i): 'default' for i in range(ord('A'), ord('Z') + 1)}
# Assurez-vous que l'input est initialisé à la première lettre
if 'input_prop' not in st.session_state:
    st.session_state.input_prop = PREMIERE_LETTRE


# --- Styles CSS et SCRIPT JS pour l'interface ---
# Ce bloc contient le style de la grille/clavier ET le JavaScript d'interactivité
STYLE_SUTOM = f"""
<style>
    /* 1. Styles généraux pour le fond sombre */
    body {{
        background-color: #212121 !important;
        color: #f0f0f0 !important;
    }}
    .stApp {{
        background-color: #212121 !important;
        color: #f0f0f0 !important;
    }}
    /* 2. Style de la grille et des cases (Bleu avec bordures blanches) */
    .ligne-sutom {{
        display: flex;
        justify-content: center;
        margin: 0;
    }}
    .case-sutom {{
        display: inline-flex;
        justify-content: center;
        align-items: center;
        width: 45px;
        height: 45px;
        margin: -1px; 
        font-size: 24px;
        font-weight: bold;
        text-transform: uppercase;
        border: 1px solid #ffffff;
        background-color: #1a73e8;
        color: white;
    }}
    
    /* 3. Styles des touches du clavier (Cliquable) */
    .clavier-ligne {{
        display: flex;
        justify-content: center;
        margin: 5px 0;
    }}
    .clavier-touche {{
        display: inline-flex;
        justify-content: center;
        align-items: center;
        width: 40px; 
        height: 45px;
        margin: 3px;
        font-size: 16px;
        font-weight: bold;
        border-radius: 4px;
        text-transform: uppercase;
        border: 2px solid #555;
        cursor: pointer; /* Curseur main pour indiquer l'interactivité */
        user-select: none;
    }}
    .clavier-fonction {{
        width: 55px;
    }}

    /* 4. Classes de couleur (Rouge pour l'absence) */
    .correct {{ background-color: #6aaa64 !important; border-color: #6aaa64 !important; color: white !important; }}
    .misplaced {{ background-color: #ff9900 !important; border-color: #ff9900 !important; color: white !important; }} /* Orange */
    .absent {{ background-color: #cc0000 !important; border-color: #cc0000 !important; color: white !important; }} /* Rouge */
    .default {{ 
        background-color: #444 !important;
        color: #f0f0f0 !important; 
        border-color: #555 !important;
    }}
</style>

<script>
    function getStreamlitInput() {{
        // Tente de trouver la zone de texte Streamlit par son type, son rôle ou son ID généré.
        // C'est fragile, mais souvent le moyen le plus simple dans Streamlit.
        // Nous allons chercher l'input text qui n'est pas caché et qui a la bonne longueur max.
        let input = document.querySelector('input[type="text"][maxlength="{LONGUEUR_MOT}"]');
        return input;
    }}

    function handleClickClavier(action, lettre) {{
        const input = getStreamlitInput();
        if (!input) return;

        let currentValue = input.value.toUpperCase();
        const maxLength = {LONGUEUR_MOT};
        const premiereLettre = '{PREMIERE_LETTRE}';

        if (action === 'lettre') {{
            // Remplir si l'espace le permet (après la première lettre)
            if (currentValue.length < maxLength) {{
                input.value = currentValue + lettre;
            }}
        }} else if (action === 'delete') {{
            // Supprimer, mais laisser la première lettre
            if (currentValue.length > 1) {{
                input.value = currentValue.slice(0, -1);
            }}
        }} else if (action === 'submit') {{
            // Simuler la touche Entrée pour soumettre le formulaire
            // Nécessite de trouver le bouton Soumettre Streamlit et de cliquer dessus.
            
            // On cherche le bouton par son texte (méthode fragile mais courante)
            const submitButton = document.querySelector('button'); 

            if (input.value.length === maxLength && submitButton) {{
                submitButton.click();
            }} else {{
                // Si la longueur n'est pas atteinte, on ne fait rien
                // Le message d'erreur sera géré par la logique Python à la soumission.
            }}
        }}

        // Déclencher un événement 'input' pour que Streamlit enregistre le changement
        input.dispatchEvent(new Event('input', {{ bubbles: true }}));
        input.focus();
    }}
</script>
"""
st.markdown(STYLE_SUTOM, unsafe_allow_html=True)


# --- Fonctions d'évaluation et d'affichage ---

def evaluer_proposition_sutom(mot_mystere, proposition):
    """Évalue la proposition et met à jour l'état du clavier."""
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
            st.session_state.etat_clavier[proposition_list[i]] = 'correct'
        else:
            evaluation[i] = (proposition_list[i], "absent")

    # 2. Marquage du Orange (misplaced) ou Rouge (absent)
    for i in range(LONGUEUR_MOT):
        lettre = proposition_list[i]
        if evaluation[i][1] == "absent":  # Si pas encore Vert
            if comptage_mystere.get(lettre, 0) > 0:
                evaluation[i] = (lettre, "misplaced")
                comptage_mystere[lettre] -= 1
                if st.session_state.etat_clavier[lettre] != 'correct':
                    st.session_state.etat_clavier[lettre] = 'misplaced'
            else:
                evaluation[i] = (lettre, "absent")
                if st.session_state.etat_clavier[lettre] not in ['correct', 'misplaced']:
                    st.session_state.etat_clavier[lettre] = 'absent'

    return evaluation

def afficher_grille_sutom(evaluation):
    """Affiche une ligne de la grille d'historique."""
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
        classe = "correct" if i == 0 else ""
        html_content += f'<div class="case-sutom {classe}">{lettre}</div>'
        
    st.markdown(f'### 📝 Proposition Actuelle\n<div class="ligne-sutom">{html_content}</div>', unsafe_allow_html=True)

def afficher_clavier():
    """Affiche le clavier virtuel avec les couleurs et les gestionnaires de clic."""
    st.markdown("---")
    st.header("Clavier AZERTY")
    
    for ligne in CLAVIER_LAYOUT:
        html_content = ""
        for lettre in ligne:
            classe = st.session_state.etat_clavier.get(lettre, 'default')
            # Ajout de l'événement onClick pour simuler la saisie
            html_content += f"""
            <div class="clavier-touche {classe}" onclick="handleClickClavier('lettre', '{lettre}')">
                {lettre}
            </div>
            """
        st.markdown(f'<div class="clavier-ligne">{html_content}</div>', unsafe_allow_html=True)
    
    # Ligne des fonctions (Entrée / Supprimer)
    html_fonction = f"""
    <div class="clavier-ligne">
        <div class="clavier-touche clavier-fonction" onclick="handleClickClavier('submit')">ENTRÉE</div>
        <div class="clavier-touche clavier-fonction" onclick="handleClickClavier('delete')">SUPPR</div>
    </div>
    """
    st.markdown(html_fonction, unsafe_allow_html=True)
    st.markdown("---")

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
        # Réinitialisation de l'entrée à la première lettre (prêt pour la tentative suivante)
        st.session_state.input_prop = PREMIERE_LETTRE 

# --- Interface Utilisateur Streamlit ---

st.title("🤫 SUTOM Personnalisé : QUIETUDE")
st.markdown(f"Trouvez le mot mystère de **{LONGUEUR_MOT} lettres** qui commence par **{PREMIERE_LETTRE}**.")
st.markdown("> *🟢 Vert : Bonne position. 🟠 Orange : Mal placée. 🔴 Rouge : Absente.*")

# --- Formulaire de Saisie (Zone de texte masquée) ---
# La zone de texte est masquée mais doit exister pour capter l'entrée du clavier cliquable.

if not st.session_state.trouve:
    # 1. Zone de texte Streamlit (cachée mais nécessaire)
    proposition_utilisateur = st.text_input(
        f"Votre mot de {LONGUEUR_MOT} lettres :", 
        key="input_prop", 
        max_chars=LONGUEUR_MOT,
        # Masquer l'input pour ne laisser visible que la grille stylisée
        label_visibility="collapsed" 
    ).strip().upper()

    # 2. Afficher la ligne de saisie active stylisée
    afficher_ligne_saisie(proposition_utilisateur)
    
    # 3. Afficher les messages d'erreur au-dessus du clavier
    if st.session_state.message_erreur:
        st.error(st.session_state.message_erreur)
        st.session_state.message_erreur = ""

# --- Grille d'Historique ---
st.header("Historique des Tentatives")

if st.session_state.historique_propositions:
    for evaluation in st.session_state.historique_propositions:
        afficher_grille_sutom(evaluation)
else:
    # Afficher la première ligne de l'historique vide
    html_content = ""
    for i in range(LONGUEUR_MOT):
        lettre = PREMIERE_LETTRE if i == 0 else " "
        classe = "correct" if i == 0 else ""
        html_content += f'<div class="case-sutom {classe}">{lettre}</div>'
    st.markdown(f'### 🏁 Ligne de Départ\n<div class="ligne-sutom">{html_content}</div>', unsafe_allow_html=True)


# --- Clavier Virtuel ---
# Le bouton de soumission est remplacé par la touche ENTRÉE du clavier virtuel
if not st.session_state.trouve:
    afficher_clavier()


# --- Fin de Partie et Réinitialisation ---
if st.session_state.trouve:
    st.success(f"🎉 FÉLICITATIONS ! Le mot mystère était **{MOT_MYSTERE_FIXE}** ! Vous avez trouvé en {len(st.session_state.historique_propositions)} tentatives.")
    st.balloons()

def reinitialiser_jeu():
    st.session_state.historique_propositions = []
    st.session_state.trouve = False
    st.session_state.input_prop = PREMIERE_LETTRE
    st.session_state.etat_clavier = {chr(i): 'default' for i in range(ord('A'), ord('Z') + 1)}

if st.session_state.trouve:
    st.header("Partie Terminée")
    st.button("Recommencer une nouvelle partie", on_click=reinitialiser_jeu)
elif st.button("Réinitialiser le jeu"):
    reinitialiser_jeu()
    st.rerun()
