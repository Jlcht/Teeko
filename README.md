# Teeko 🎮

## Description

Implémentation du jeu de stratégie **Teeko** avec interface graphique en Python utilisant Tkinter. Ce projet propose une intelligence artificielle avancée basée sur l'algorithme **Minimax avec élagage Alpha-Beta**.

## 📋 Règles du jeu

### Plateau de jeu

- Grille de **5×5** cases
- Chaque joueur possède **4 pièces** (X et O)
- **X commence toujours** en premier

### Déroulement de la partie

#### Phase 1 – Placement

- Les joueurs placent leurs pièces à tour de rôle sur une case vide
- Après 8 tours, chaque joueur aura placé ses 4 pièces

#### Phase 2 – Mouvement

- Les joueurs déplacent l'une de leurs pièces vers une case vide adjacente
- Les déplacements sont autorisés horizontalement, verticalement ou en diagonale

### Conditions de victoire

Le premier joueur à réaliser l'un des motifs suivants gagne :

- **4 pièces alignées** (ligne, colonne ou diagonale)
- **Carré 2×2** avec ses 4 pièces

### Conditions de match nul

- Après **30 coups** (15 coups par joueur) en phase de mouvement
- Si une **position identique se répète 3 fois**

## 🎯 Fonctionnalités principales

### 1. **Modes de jeu multiples**

- **🎮 Joueur vs Joueur (PvP)** : Deux joueurs humains s'affrontent
- **🤖 Joueur vs IA** : Affrontez l'intelligence artificielle
- **🤖 IA vs IA** : Observez deux IA s'affronter

### 2. **Intelligence Artificielle avancée**

#### Algorithme Minimax avec élagage Alpha-Beta

- **Profondeur de recherche configurable** (1 à 5 niveaux)
- **Évaluation heuristique sophistiquée** :
  - Détection des séquences de 2, 3 et 4 pièces alignées
  - Bonus pour le contrôle du centre du plateau
  - Évaluation des menaces et opportunités
- **Optimisations** :
  - Détection immédiate des coups gagnants
  - Blocage prioritaire des menaces adverses
  - Tri des coups par heuristique pour améliorer l'élagage

#### Niveaux de difficulté

- **Facile** : Profondeur 1 (réactions rapides, peu de prévoyance)
- **Moyen** : Profondeur 3 (bon équilibre)
- **Difficile** : Profondeur 5 (analyse approfondie, très compétitif)

### 3. **Interface graphique intuitive**

- **Design inspiré de Chess.com** avec palette de couleurs professionnelle
- **Grille 5×5** avec cases de 90×90 pixels
- **Pièces visuelles** : cercles noirs (X) et crème (O)
- **Mise en évidence** :
  - Sélection de pièce avec bordure verte
  - Grille avec lignes subtiles
- **Informations en temps réel** :
  - Tour actuel
  - Couleur du joueur humain et de l'IA
  - Évaluation Minimax (optionnelle)

### 4. **Mode IA vs IA**

- **Configuration des deux IA** :
  - Niveau indépendant pour chaque IA (Facile, Moyen, Difficile)
  - Affichage des niveaux et couleurs de chaque IA
- **Modes de visualisation** :
  - **Automatique** : Les IA jouent en continu avec délai de 1 seconde
  - **Step by Step** : Avancez coup par coup avec un bouton "Next Turn"

### 5. **Paramètres personnalisables**

- **Choix de la couleur** : Jouez X (commencez en premier) ou O (l'IA commence)
- **Difficulté de l'IA** : Facile, Moyen ou Difficile
- **Affichage de l'évaluation** : Visualisez le score Minimax calculé par l'IA

### 6. **Système de détection de match nul**

- **Compteur de coups** : Limite de 30 coups en phase de mouvement
- **Détection de répétition** : Identifie les positions répétées 3 fois
- **Historique optimisé** : Conservation des 10 dernières positions pour économiser la mémoire

### 7. **Navigation et ergonomie**

- **Menu principal** avec accès à tous les modes
- **Bouton "Retour au menu"** disponible pendant les parties
- **Fenêtre plein écran** pour une meilleure expérience
- **Affichage des règles** : Fenêtre dédiée avec toutes les règles du jeu

## 🚀 Installation et lancement

### Prérequis

- Python 3.x
- Tkinter (généralement inclus avec Python)

### Lancement du jeu

```bash
python Teeko_iaV4.py
```

## 🏗️ Architecture du code

### Classes principales

#### `TeekoGame`

Classe principale du jeu gérant :

- Le plateau de jeu et la logique
- L'interface graphique
- Les interactions utilisateur
- L'IA avec Minimax
- La détection de victoire et de match nul

#### `TeekoGameAIvsAI`

Classe héritant de `TeekoGame` pour le mode IA vs IA :

- Gestion de deux IA avec niveaux différents
- Mode automatique ou pas à pas
- Affichage des informations des deux IA

#### `TeekoMenu`

Classe gérant le menu principal :

- Sélection des modes de jeu
- Configuration des paramètres
- Affichage des règles
- Navigation entre les écrans

### Méthodes clés

#### Algorithme Minimax

```python
minimax(board, depth, alpha, beta, maximizing, perspective_player)
```

- Recherche récursive avec élagage Alpha-Beta
- Évaluation depuis la perspective d'un joueur spécifique
- Retourne le meilleur coup et son score

#### Évaluation du plateau

```python
evaluate_board_for_player(board, perspective_player)
```

- Analyse des séquences de 2, 3 et 4 pièces
- Bonus pour le contrôle du centre
- Score différentiel entre le joueur et l'adversaire

#### Détection de victoire

```python
check_win_board(board, player)
```

- Vérifie les 4 alignements (lignes, colonnes, diagonales)
- Vérifie les carrés 2×2

## 🎨 Design et style

### Palette de couleurs

- **Fond du plateau** : `#f0d9b5` (beige clair)
- **Grille** : `#b58863` (marron)
- **Pièces X** : `#000000` (noir)
- **Pièces O** : `#fffacd` (crème)
- **Sélection** : `#00ff00` (vert)
- **Boutons** : `#00a651` (vert UTBM)
- **Interface** : `#f0f0f0` (gris clair)

### Effets visuels

- **Hover sur boutons** : Changement de couleur au survol
- **Mise en évidence** : Bordure verte pour la pièce sélectionnée
- **Fenêtres modales** : Pour les paramètres et règles

## 📊 Performances de l'IA

### Complexité

- **Phase de placement** : ~25 positions possibles par coup
- **Phase de mouvement** : ~12-16 positions possibles par coup
- **Profondeur 5** : Peut analyser plusieurs milliers de positions

### Optimisations implémentées

1. **Élagage Alpha-Beta** : Réduit drastiquement l'arbre de recherche
2. **Tri des coups** : Heuristique de tri pour améliorer l'élagage
3. **Détection immédiate** : Court-circuite Minimax pour les coups évidents
4. **Choix intelligent de la source** : En phase de mouvement, sélectionne la meilleure pièce à déplacer

## 🔧 Personnalisation

### Modifier la difficulté

Dans le dictionnaire `DIFFICULTIES` :

```python
DIFFICULTIES = {
    "Facile": 1,
    "Moyen": 3,
    "Difficile": 5
}
```

### Ajuster la taille du plateau

Modifier la constante `SIZE` (actuellement 5)

### Changer les délais de l'IA

- Mode normal : `self.root.after(200, self.ai_play)`
- Mode IA vs IA : `self.root.after(1000, self.ai_turn)`

## 📝 Auteur

Projet réalisé dans le cadre du cours **IA41** à l'**UTBM** (Université de Technologie de Belfort-Montbéliard)

## 📄 Licence

Projet académique - UTBM 2025
