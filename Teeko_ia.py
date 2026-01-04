# teeko_full_fixed.py
import tkinter as tk
from tkinter import messagebox
import random
import math
import copy
import sys

def style_button(btn):
    btn.configure(bg="#017cbf", fg="#ffffff", font=("Arial", 12, "bold"), bd=0, relief="flat", padx=10, pady=5)
    btn.bind("<Enter>", lambda e: btn.configure(bg="#009344"))
    btn.bind("<Leave>", lambda e: btn.configure(bg="#017cbf"))


# ---------------- Constantes ----------------
SIZE = 5
CELL_SIZE = 90
PLAYER1 = "X"   # X commence tjrs
PLAYER2 = "O"
EMPTY = "."
COLORS = {PLAYER1: "black", PLAYER2: "beige", EMPTY: "grey"}

# Niveaux de difficulté
DIFFICULTIES = {
    "Facile": 1,
    "Moyen": 3,
    "Difficile": 5
}

MISTAKE_PROBS = {
    1: 0.25,
    3: 0.10,
    5: 0.0
}

# ------------------ Classe principale du jeu ------------------
class TeekoGame:
    def __init__(self, root, *,
                 ai_mode=False,
                 human_side=PLAYER1,
                 minimax_depth=3,
                 show_eval=False,
                 return_to_menu_cb=None,
                 pos_nb=0,
                 pos=None):
        self.root = root
        self.ai_mode = ai_mode
        self.human_side = human_side
        self.ai_side = PLAYER2 if human_side == PLAYER1 else PLAYER1
        self.minimax_depth = minimax_depth
        self.show_eval = show_eval
        self.return_to_menu_cb = return_to_menu_cb
        self.pos_nb = pos_nb
        if pos is None:
            self.pos = []
        else:
            self.pos = pos

        self.board = [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]
        self.turn = PLAYER1  # X commence tjrs
        self.total_pieces = 0
        self.selected_piece = None

        # dernier txt d'eval pr le garder visible après draw_board
        self.last_eval_text = ""

        # Interface
        self.root.title("Teeko")
        self.frame = tk.Frame(self.root)
        self.frame.pack()
        self.canvas = tk.Canvas(self.frame, width=SIZE*CELL_SIZE, height=SIZE*CELL_SIZE, bg="white")
        self.canvas.grid(row=0, column=0, columnspan=3)
        self.canvas.bind("<Button-1>", self.on_click)

        self.label_info = tk.Label(self.frame, text=self._info_text(), font=("Arial", 14, "bold"), fg="#333333", bg="#f0f0f0")
        self.label_info.grid(row=1, column=0, sticky="w", padx=6, pady=6)

        self.label_eval = tk.Label(self.frame, text="", font=("Arial", 12), fg="#555555", bg="#f0f0f0")
        self.label_eval.grid(row=1, column=1, sticky="e", padx=6, pady=6)

        self.btn_menu = tk.Button(self.frame, text="Retour au menu", command=self._return_to_menu)
        self.btn_menu.grid(row=1, column=2, sticky="e", padx=6, pady=6)
        style_button(self.btn_menu)  
        self.draw_board()
     

        # Si l'IA doit jouer en 1er (humain a choisi O), lancer IA
        if self.ai_mode and self.turn == self.ai_side:
            self.root.after(300, self.ai_play)

    def _info_text(self):
        return f"Tour: {self.turn}    Joueur humain: {self.human_side}    IA: {self.ai_side}"

    def _update_labels(self, eval_text=None):
        # si eval_text fourni, màj txt stocké seulement si show_eval activé
        if eval_text is not None:
            if self.show_eval:
                self.last_eval_text = eval_text
            else:
                self.last_eval_text = ""
        # màj label info
        self.label_info.config(text=self._info_text())
        # màj label eval selon show_eval et txt stocké
        if self.show_eval and self.last_eval_text:
            self.label_eval.config(text=self.last_eval_text)
        else:
            self.label_eval.config(text="")

    def _return_to_menu(self):
        # détruire fenêtre et appeler callback
        if self.return_to_menu_cb:
            self.root.destroy()
            self.return_to_menu_cb()
        else:
            self.root.destroy()

    # ---------------- Dessin ----------------
    def draw_board(self):
        self.canvas.delete("all")
        self.canvas.configure(bg="#f0d9b5")

        for r in range(SIZE):
            for c in range(SIZE):
                x1 = c * CELL_SIZE
                y1 = r * CELL_SIZE
                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE
                # dessiner grille subtile
                self.canvas.create_rectangle(x1, y1, x2, y2, outline="#b58863", width=2)

                piece = self.board[r][c]
                if piece != EMPTY:
                    color = "#000000" if piece==PLAYER1 else "#fffacd"  # pions noir & crème
                    self.canvas.create_oval(x1+15, y1+15, x2-15, y2-15, fill=color, outline="#555555", width=2)

        # surligner pion sélectionné
        if self.selected_piece:
            r, c = self.selected_piece
            x1 = c * CELL_SIZE
            y1 = r * CELL_SIZE
            x2 = x1 + CELL_SIZE
            y2 = y1 + CELL_SIZE
            self.canvas.create_rectangle(x1+2, y1+2, x2-2, y2-2, outline="#00ff00", width=4)    

        # màj labels
        self._update_labels()

    # ---------------- Gestion des clics ----------------
    def on_click(self, event):
        # ignorer clics si c'est le tour de l'IA
        if self.ai_mode and self.turn == self.ai_side:
            return

        c = event.x // CELL_SIZE
        r = event.y // CELL_SIZE
        if not (0 <= r < SIZE and 0 <= c < SIZE):
            return

        # Phase placement
        if self.total_pieces < 8:
            if self.board[r][c] == EMPTY:
                self.board[r][c] = self.turn
                self.total_pieces += 1
                if self.check_win(self.turn):
                    self.draw_board()
                    self.end_game(self.turn)
                    return
                self._advance_turn()
            return

        # Phase mouvement
        if self.selected_piece is None:
            if self.board[r][c] == self.turn:
                self.selected_piece = (r, c)
                self.draw_board()
        else:
            r1, c1 = self.selected_piece
            if (r, c) == (r1, c1):
                self.selected_piece = None
                self.draw_board()
                return
            if self.board[r][c] != EMPTY:
                return
            if not self.adjacent(r1, c1, r, c):
                return
            # déplacer
            self.board[r1][c1] = EMPTY
            self.board[r][c] = self.turn
            self.selected_piece = None
            self.pos_nb += 1
            if self.check_win(self.turn):
                self.draw_board()
                self.end_game(self.turn)
                return
            if self.check_draw(self.turn):
                self.draw_board()
                self.end_game_draw()
                return
            self._advance_turn()

    def _advance_turn(self):
        # alterner
        self.turn = PLAYER1 if self.turn == PLAYER2 else PLAYER2
        self.draw_board()
        # si mode IA et tour de l'IA -> planifier jeu IA
        if self.ai_mode and self.turn == self.ai_side:
            self.root.after(200, self.ai_play)

    # ---------------- Utilitaires ----------------
    def adjacent(self, r1, c1, r2, c2):
        return abs(r1 - r2) <= 1 and abs(c1 - c2) <= 1 and not (r1 == r2 and c1 == c2)

    def count_pieces_board(self, board, player):
        return sum(row.count(player) for row in board)

    # ---------------- Vérif victoire ----------------
    def check_win_board(self, board, player):
        # lignes et colonnes
        for r in range(SIZE):
            for c in range(SIZE - 3):
                if all(board[r][c + i] == player for i in range(4)):
                    return True
        for r in range(SIZE - 3):
            for c in range(SIZE):
                if all(board[r + i][c] == player for i in range(4)):
                    return True
        # diagonales
        for r in range(SIZE - 3):
            for c in range(SIZE - 3):
                if all(board[r + i][c + i] == player for i in range(4)):
                    return True
                if all(board[r + 3 - i][c + i] == player for i in range(4)):
                    return True
        # carré 2x2
        for r in range(SIZE - 1):
            for c in range(SIZE - 1):
                if all(board[r + i][c + j] == player for i in range(2) for j in range(2)):
                    return True
        return False

    def check_win(self, player):
        return self.check_win_board(self.board, player)
    
    def check_draw(self, player):
        # Nulle après 15 coups
        if self.pos_nb == 30:
            return True
        
        # Signature du plateau
        current_signature = tuple(tuple(row) for row in self.board)
        
        # Ajout signature actuelle
        self.pos.append(current_signature)
        
        count = self.pos.count(current_signature)
        
        if count >= 3:
            return True
        
        if len(self.pos) > 10:
            self.pos.pop(0)
        
        return False

    # ---------------- Fin de partie ----------------
    def end_game(self, winner):
        messagebox.showinfo("Victoire", f"🎉 Le joueur {winner} a gagné !")
        # garder fenêtre ouverte mais unbind clics
        self.canvas.unbind("<Button-1>")
    
    def end_game_draw(self):
        messagebox.showinfo("Egalité",f"Egalité après 15 coups ou position répétée 3 fois")
        # garder fenêtre ouverte mais unbind clics
        self.canvas.unbind("<Button-1>")
    
    # ---------------- Entrée IA ----------------
    def ai_play(self):
        # d'abord: victoire ou blocage imm (placement ou mvt)
        immediate = self.find_immediate_win_or_block()
        if immediate is not None:
            # appliquer cible imm
            self.apply_target(immediate, self.ai_side)
            # afficher eval si activé
            if self.show_eval:
                self._update_labels(eval_text=f"Eval IA: immediate")
            return
        
        # joue parfois au hasard en fonction de la difficulté
        chance_erreur = MISTAKE_PROBS.get(self.get_minimax_depth(), 0.0)
        if random.random() < chance_erreur:
            targets = self.get_all_targets(self.board, self.ai_side)
            if targets:
                self.apply_target(random.choice(targets), self.ai_side)
                if self.show_eval:
                    self._update_labels(eval_text="Eval IA: erreur volontaire")
                return

        # sinon minimax
        move, score = self.minimax(self.board, depth=self.get_minimax_depth(), alpha=-math.inf, beta=math.inf, maximizing=True, perspective_player=self.ai_side)
        if self.show_eval:
            self._update_labels(eval_text=f"Eval IA: {score:.1f}")
        if move is not None:
            self.apply_target(move, self.ai_side)
        else:
            # fallback cible légale aléatoire
            targets = self.get_all_targets(self.board, self.ai_side)
            if targets:
                self.apply_target(random.choice(targets), self.ai_side)

    def get_minimax_depth(self):
        return self.minimax_depth

    # ---------------- Victoire/blocage imm ----------------
    def find_immediate_win_or_block(self):
        ai_moves = self.get_all_targets(self.board, self.ai_side)
        
        # Vérif victoire immédiate
        for move in ai_moves:
            newb = self.simulate_move(self.board, move, self.ai_side)
            if self.check_win_board(newb, self.ai_side):
                return move
        
        # Vérif blocage
        opp_moves = self.get_all_targets(self.board, self.human_side)
        for opp_move in opp_moves:
            newb = self.simulate_move(self.board, opp_move, self.human_side)
            if self.check_win_board(newb, self.human_side):
                # Chercher si l'IA peut occuper cette destination
                _, opp_dest = opp_move
                for ai_move in ai_moves:
                    _, ai_dest = ai_move
                    if ai_dest == opp_dest:
                        return ai_move
        
        return None

    # ---------------- Générer cibles ----------------
    def get_all_targets(self, board, player):
        """Retourne (source, destination) pour tous les coups.
        En phase placement: source = None"""
        targets = []
        player_piece_count = self.count_pieces_board(board, player)
        
        if player_piece_count < 4:
            # Phase placement
            for r in range(SIZE):
                for c in range(SIZE):
                    if board[r][c] == EMPTY:
                        targets.append((None, (r, c)))
        else:
            # Phase mouvement
            for sr in range(SIZE):
                for sc in range(SIZE):
                    if board[sr][sc] != player:
                        continue
                    for dr in (-1, 0, 1):
                        for dc in (-1, 0, 1):
                            if dr == 0 and dc == 0:
                                continue
                            tr, tc = sr + dr, sc + dc
                            if 0 <= tr < SIZE and 0 <= tc < SIZE and board[tr][tc] == EMPTY:
                                targets.append(((sr, sc), (tr, tc)))
        return targets

    def simulate_move(self, board, move, player):
        """move = (source, dest) où source peut être None"""
        nb = copy.deepcopy(board)
        source, dest = move
        
        if source is None:
            # Phase placement
            r, c = dest
            nb[r][c] = player
        else:
            # Phase mouvement
            sr, sc = source
            dr, dc = dest
            nb[sr][sc] = EMPTY
            nb[dr][dc] = player
        
        return nb

    def apply_target(self, move, player):
        """move = (source, dest)"""
        source, dest = move
        
        if source is None:
            # Phase placement
            r, c = dest
            self.board[r][c] = player
            self.total_pieces += 1
        else:
            # Phase mouvement
            sr, sc = source
            dr, dc = dest
            self.board[sr][sc] = EMPTY
            self.board[dr][dc] = player
        
        # Vérifications post-coup
        self.pos_nb += 1
        if self.check_win_board(self.board, player):
            self.draw_board()
            self.end_game(player)
            return
        if self.check_draw(self.turn):
            self.draw_board()
            self.end_game_draw()
            return
        
        self.turn = PLAYER1 if self.turn == PLAYER2 else PLAYER2
        self.draw_board()
        
        if self.ai_mode and self.turn == self.ai_side:
            self.root.after(200, self.ai_play)

    # ---------------- Minimax (alpha-beta) ----------------
# Remplacer uniquement la fonction minimax dans la classe TeekoGame

    def minimax(self, board, depth, alpha, beta, maximizing, perspective_player=None):
        
        # Si perspective_player pas fourni, utiliser ai_side
        if perspective_player is None:
            perspective_player = self.ai_side
        
        opponent = PLAYER2 if perspective_player == PLAYER1 else PLAYER1
        
        # Vérifications terminales avec bonus/malus selon profondeur
        if self.check_win_board(board, perspective_player):
            # victoire plus proch preferable
            return None, 100000 + depth
        
        if self.check_win_board(board, opponent):
            # retarder la si inévitable
            return None, -100000 - depth
        
        if depth == 0:
            return None, self.evaluate_board_for_player(board, perspective_player)

        player = perspective_player if maximizing else opponent
        targets = self.get_all_targets(board, player)
        # Trier mvts par heuristique
        targets.sort(key=lambda t: -self.move_order_heur(board, t, player))

        best_move = None
        if maximizing:
            max_eval = -math.inf
            for t in targets:
                newb = self.simulate_move(board, t, player)
                _, eval_score = self.minimax(newb, depth-1, alpha, beta, False, perspective_player)
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = t
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            return best_move, max_eval
        else:
            min_eval = math.inf
            for t in targets:
                newb = self.simulate_move(board, t, player)
                _, eval_score = self.minimax(newb, depth-1, alpha, beta, True, perspective_player)
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = t
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            return best_move, min_eval

    def move_order_heur(self, board, move, player):
        # préférer centre et adjacence aux alliés
        source, dest = move
        r, c = dest
        center = (SIZE-1)/2
        center_score = - (abs(r-center) + abs(c-center))
        ally_neighbors = 0
        for dr in (-1,0,1):
            for dc in (-1,0,1):
                if dr==0 and dc==0: continue
                rr, cc = r+dr, c+dc
                if 0<=rr<SIZE and 0<=cc<SIZE and board[rr][cc]==player:
                    ally_neighbors += 1
        return center_score + ally_neighbors*1.2

    # ---------------- Evaluation ----------------
    def evaluate_sequences(self, board, player):
        """Calcule le score des séquences pour un joueur."""
        score = 0
        sequences = []
        
        # Lignes
        for r in range(SIZE):
            for c in range(SIZE-3):
                sequences.append([board[r][c+i] for i in range(4)])
        
        # Colonnes
        for c in range(SIZE):
            for r in range(SIZE-3):
                sequences.append([board[r+i][c] for i in range(4)])
        
        # Diagonales
        for r in range(SIZE-3):
            for c in range(SIZE-3):
                sequences.append([board[r+i][c+i] for i in range(4)])
                sequences.append([board[r+3-i][c+i] for i in range(4)])
        
        for seq in sequences:
            cnt = seq.count(player)
            empt = seq.count(EMPTY)
            if cnt == 4:
                score += 10000
            elif cnt == 3 and empt == 1:
                score += 300
            elif cnt == 2 and empt == 2:
                score += 60
            elif cnt == 1 and empt == 3:
                score += 5
        
        return score

    def evaluate_board_for_player(self, board, perspective_player):
        
        opponent = PLAYER2 if perspective_player == PLAYER1 else PLAYER1
        
        # Vérifications terminales
        if self.check_win_board(board, perspective_player): 
            return 100000
        if self.check_win_board(board, opponent): 
            return -100000
        
        # Score des séquences
        score = self.evaluate_sequences(board, perspective_player) - \
                self.evaluate_sequences(board, opponent)
        
        # Bonus centre
        center = (SIZE-1) / 2
        for r in range(SIZE):
            for c in range(SIZE):
                center_bonus = max(0, 3 - (abs(r-center) + abs(c-center)))
                if board[r][c] == perspective_player:
                    score += center_bonus
                elif board[r][c] == opponent:
                    score -= center_bonus
        
        return score

# ------------------ Classe IA vs IA ------------------
class TeekoGameAIvsAI(TeekoGame):
    def __init__(self, root, *, ai1_level=3, ai2_level=3, step_mode=False, return_to_menu_cb=None):
        # IA vs IA: override planif IA parent
        super().__init__(root, ai_mode=True, human_side=PLAYER1, minimax_depth=3,
                        show_eval=False, return_to_menu_cb=return_to_menu_cb)
        self.ai1_level = ai1_level
        self.ai2_level = ai2_level
        self.step_mode = step_mode
        self.turn = PLAYER1
        self.total_pieces = 0

        # *** AJOUT CRUCIAL : Désactiver les clics humains ***
        self.canvas.unbind("<Button-1>")

        # Désactiver planif IA parent
        self.auto_ai_schedule = False

        # Ajout labels sous le board
        self.label_ai1 = tk.Label(self.frame, text=f"AI 1: Niveau {self.ai1_level}, Couleur {PLAYER1}", font=("Arial", 12))
        self.label_ai1.grid(row=2, column=0, pady=6)

        self.label_ai2 = tk.Label(self.frame, text=f"AI 2: Niveau {self.ai2_level}, Couleur {PLAYER2}", font=("Arial", 12))
        self.label_ai2.grid(row=2, column=2, pady=6)

        # Bouton étape pr mode manuel
        if self.step_mode:
            self.btn_next = tk.Button(self.frame, text="Tour suivant", command=self.next_turn)
            self.btn_next.grid(row=2, column=1, pady=6)
            style_button(self.btn_next)  # *** AJOUT : style le bouton ***

        # Démarrer 1er mvt auto si mode auto
        if not self.step_mode:
            self.root.after(300, self.ai_turn)

    # Override pr retirer avancement auto du tour dans parent
    def apply_target(self, move, player):
        """Appliquer un mvt sans changer tour automatiquement."""
        source, dest = move
        
        if source is None:
            # Phase placement
            r, c = dest
            self.board[r][c] = player
            self.total_pieces += 1
        else:
            # Phase mouvement
            sr, sc = source
            dr, dc = dest
            self.board[sr][sc] = EMPTY
            self.board[dr][dc] = player

        self.draw_board()
        # vérif victoire
        self.pos_nb += 1
        if self.check_win(player):
            messagebox.showinfo("Fin de partie", f"IA {player} gagne!")
            return True
        if self.check_draw(self.turn):
            self.draw_board()
            self.end_game_draw()
            return True
        return False

    def ai_turn(self):
        current_ai = self.turn
        depth = self.ai1_level if current_ai==PLAYER1 else self.ai2_level
        
        # D'abord: vérif victoire ou blocage imm
        immediate = self.find_immediate_win_or_block_aivsai(current_ai)
        if immediate is not None:
            game_over = self.apply_target(immediate, current_ai)
            if game_over:
                return
        else:
            # ajout de chance de coup aléatoire
            chance_erreur = MISTAKE_PROBS.get(depth, 0.0)
            played_randomly = False
            if random.random() < chance_erreur:
                targets = self.get_all_targets(self.board, current_ai)
                if targets:
                    random_target = random.choice(targets)
                    game_over = self.apply_target(random_target, current_ai)
                    if game_over: return
                    played_randomly = True

            # Utiliser minimax
            if not played_randomly:
                maximizing = True  # Tjrs maximiser pr joueur actuel
                move, _ = self.minimax(self.board, depth, -math.inf, math.inf, maximizing=maximizing, perspective_player=current_ai)
                if move:
                    game_over = self.apply_target(move, current_ai)
                    if game_over:
                        return

        # Changer tour manuellement
        self.turn = PLAYER1 if self.turn==PLAYER2 else PLAYER2

        # Planifier tour suivant seulement en mode auto
        if not self.step_mode:
            self.root.after(1000, self.ai_turn)
    
    def find_immediate_win_or_block_aivsai(self, current_ai):
        """Trouver victoire ou blocage imm pr mode IA vs IA."""
        opponent = PLAYER2 if current_ai==PLAYER1 else PLAYER1
        
        # Vérif si IA actuelle peut gagner imm
        ai_targets = self.get_all_targets(self.board, current_ai)
        for t in ai_targets:
            newb = self.simulate_move(self.board, t, current_ai)
            if self.check_win_board(newb, current_ai):
                return t
        
        # Vérif si adversaire menace de gagner -> bloquer
        opp_targets = self.get_all_targets(self.board, opponent)
        for opp_move in opp_targets:
            newb = self.simulate_move(self.board, opp_move, opponent)
            if self.check_win_board(newb, opponent):
                # Chercher si l'IA peut occuper cette destination
                _, opp_dest = opp_move
                for ai_move in ai_targets:
                    _, ai_dest = ai_move
                    if ai_dest == opp_dest:
                        return ai_move
        
        return None

    def next_turn(self):
        """Mode étape manuelle: exécuter un seul mvt IA."""
        self.ai_turn()

    # Override _info_text pr masquer labels humain/IA
    def _info_text(self):
        return f"Tour: {self.turn}"


# ------------------ Menu / Paramètres UI ------------------
class TeekoMenu:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Menu Teeko")
        self.root.state('normal')

        self.ai_difficulty = "Moyen"
        self.human_color = PLAYER1
        self.show_eval = False

        tk.Label(self.root, text="Bienvenue dans Teeko !", font=("Arial", 16, "bold"), 
                 fg="#333333", bg="#f0f0f0").pack(pady=10)

        btn_pvp = tk.Button(self.root, text="Jouer à deux", command=self.start_pvp)
        btn_pvp.pack(pady=6)
        style_button(btn_pvp)

        btn_vs_ai = tk.Button(self.root, text="Jouer contre l'IA", command=self.start_vs_ai)
        btn_vs_ai.pack(pady=6)
        style_button(btn_vs_ai)

        btn_ai_vs_ai = tk.Button(self.root, text="AI vs AI", command=self.start_ai_vs_ai)
        btn_ai_vs_ai.pack(pady=6)
        style_button(btn_ai_vs_ai)

        btn_rules = tk.Button(self.root, text="Règles du jeu", command=self.show_rules)
        btn_rules.pack(pady=6)
        style_button(btn_rules)

        btn_quit = tk.Button(self.root, text="Quitter", command=self.quit_app)
        btn_quit.pack(pady=6)
        style_button(btn_quit)

        self.root.configure(bg="#f0f0f0")

        self.root.mainloop()

    def quit_app(self):
        self.root.destroy()
        sys.exit()

    def start_pvp(self):
        self.root.destroy()
        w = tk.Tk()
        w.state('normal')
        TeekoGame(w, ai_mode=False, human_side=self.human_color,
                 minimax_depth=DIFFICULTIES[self.ai_difficulty],
                 show_eval=self.show_eval,
                 return_to_menu_cb=self.show_menu)
        w.mainloop()

    def start_vs_ai(self):
        # ouvrir settings pr choix
        self.open_settings(modal=True)
        self.root.destroy()
        w = tk.Tk()
        w.state('normal')
        TeekoGame(w, ai_mode=True, human_side=self.human_color,
                 minimax_depth=DIFFICULTIES[self.ai_difficulty],
                 show_eval=self.show_eval,
                 return_to_menu_cb=self.show_menu)
        w.mainloop()

    def start_ai_vs_ai(self):
        # ouvrir settings pour parametrer partie
        s = tk.Toplevel(self.root)
        s.title("Paramètres AI vs AI")
        s.geometry("600x500")
        s.configure(bg="#f0f0f0")
        s.transient(self.root)

        # titre
        tk.Label(s, text="Paramètres AI vs AI", font=("Arial", 16, "bold"), fg="#333333", bg="#f0f0f0").pack(pady=15)

        # AI niveau 1
        tk.Label(s, text="Niveau AI 1:", font=("Arial", 12, "bold"), fg="#333333", bg="#f0f0f0").pack(anchor="w", padx=20, pady=(10,0))
        ai1_var = tk.IntVar(value=3)
        for name, depth in DIFFICULTIES.items():
            rb = tk.Radiobutton(s, text=name, variable=ai1_var, value=depth, font=("Arial", 11), bg="#f0f0f0", anchor="w")
            rb.pack(anchor="w", padx=40)

        # AI niveau 2
        tk.Label(s, text="Niveau AI 2:", font=("Arial", 12, "bold"), fg="#333333", bg="#f0f0f0").pack(anchor="w", padx=20, pady=(10,0))
        ai2_var = tk.IntVar(value=3)
        for name, depth in DIFFICULTIES.items():
            rb = tk.Radiobutton(s, text=name, variable=ai2_var, value=depth, font=("Arial", 11), bg="#f0f0f0", anchor="w")
            rb.pack(anchor="w", padx=40)


        tk.Label(s, text="Mode de jeu:", font=("Arial", 12, "bold"), fg="#333333", bg="#f0f0f0").pack(anchor="w", padx=20, pady=(10,0))
        mode_var = tk.StringVar(value="auto")
        tk.Radiobutton(s, text="Automatique", variable=mode_var, value="auto", font=("Arial", 11), bg="#f0f0f0", anchor="w").pack(anchor="w", padx=40)
        tk.Radiobutton(s, text="Step by Step", variable=mode_var, value="step", font=("Arial", 11), bg="#f0f0f0", anchor="w").pack(anchor="w", padx=40)

        # bouton start
        btn_start = tk.Button(s, text="Démarrer AI vs AI", font=("Arial", 12, "bold"), command=lambda: apply_and_start())
        btn_start.pack(pady=20)
        style_button(btn_start)

        def apply_and_start():
            ai1_level = ai1_var.get()
            ai2_level = ai2_var.get()
            step_mode = (mode_var.get() == "step")
            s.destroy()
            self.root.destroy()
            w = tk.Tk()
            w.state('normal')
            TeekoGameAIvsAI(w, ai1_level=ai1_level, ai2_level=ai2_level, step_mode=step_mode,
                            return_to_menu_cb=self.show_menu)
            w.mainloop()

        s.grab_set()
        s.wait_window()

    def show_rules(self):
        """Display the rules of Teeko in a styled window."""
        rules_text = (
            "RÈGLES DU JEU TEEKO\n\n"
            "• Le jeu se joue sur une grille 5×5.\n"
            "• Chaque joueur possède 4 pièces (X et O).\n"
            "• X commence toujours.\n\n"
            "Phase 1 – Placement :\n"
            "Les joueurs placent leurs pièces à tour de rôle sur une case vide.\n"
            "Après 8 tours, chaque joueur aura placé ses 4 pièces.\n\n"
            "Phase 2 – Mouvement :\n"
            "À partir de ce moment, les joueurs déplacent l'une de leurs pièces\n"
            "vers une case vide adjacente (horizontalement, verticalement ou en diagonale).\n\n"
            "Objectif :\n"
            "Former l'un des motifs suivants :\n"
            "• 4 pièces alignées (ligne, colonne ou diagonale)\n"
            "• ou un carré 2×2.\n\n"
            "Le premier joueur à réussir cela gagne la partie !"
        )

        # creer fenetre
        w = tk.Toplevel(self.root)
        w.title("Règles du jeu")
        w.geometry("600x500")
        w.configure(bg="#f0f0f0") 
        w.transient(self.root)

        # Titre
        tk.Label(w, text="Règles du jeu Teeko", font=("Arial", 16, "bold"), fg="#333333", bg="#f0f0f0").pack(pady=15)

        # text frame
        text_frame = tk.Frame(w, bg="#f0f0f0")
        text_frame.pack(fill="both", expand=True, padx=20, pady=10)

        rules_label = tk.Label(text_frame, text=rules_text, font=("Arial", 12), justify="left",
                            wraplength=550, fg="#333333", bg="#f0f0f0")
        rules_label.pack(anchor="nw")

        # bouton close
        btn_close = tk.Button(w, text="Fermer", font=("Arial", 12, "bold"), command=w.destroy)
        btn_close.pack(pady=15)
        style_button(btn_close)

        w.grab_set()
        w.wait_window()
    
    def show_menu(self):

        self.__init__()

    def open_settings(self, modal=False):
        s = tk.Toplevel(self.root)
        s.title("Paramètres IA")
        s.geometry("400x380")
        s.configure(bg="#f0f0f0")
        s.transient(self.root)

        # Titre
        tk.Label(s, text="Paramètres du jeu", font=("Arial", 16, "bold"), fg="#333333", bg="#f0f0f0").pack(pady=15)

        content_frame = tk.Frame(s, bg="#f0f0f0")
        content_frame.pack(fill="both", expand=True, padx=20)

        # Difficultée
        tk.Label(content_frame, text="Difficulté IA:", font=("Arial", 12, "bold"), fg="#333333", bg="#f0f0f0").pack(anchor="w", pady=(0,5))
        diff_var = tk.StringVar(value=self.ai_difficulty)
        for name in DIFFICULTIES.keys():
            tk.Radiobutton(content_frame, text=name, variable=diff_var, value=name, font=("Arial", 11), bg="#f0f0f0").pack(anchor="w", padx=10, pady=2)

        # choix couleur
        tk.Label(content_frame, text="Couleur du joueur (X commence):", font=("Arial", 12, "bold"), fg="#333333", bg="#f0f0f0").pack(anchor="w", pady=(10,5))
        color_var = tk.StringVar(value=self.human_color)
        tk.Radiobutton(content_frame, text="Jouer X (commence)", variable=color_var, value=PLAYER1, font=("Arial", 11), bg="#f0f0f0").pack(anchor="w", padx=10, pady=2)
        tk.Radiobutton(content_frame, text="Jouer O (IA commence)", variable=color_var, value=PLAYER2, font=("Arial", 11), bg="#f0f0f0").pack(anchor="w", padx=10, pady=2)

        # afficher eval
        show_var = tk.BooleanVar(value=self.show_eval)
        tk.Checkbutton(content_frame, text="Afficher évaluation Minimax pendant la partie", variable=show_var,
                    font=("Arial", 11), bg="#f0f0f0").pack(anchor="w", pady=(10,5))

        # bouton appliquer
        btn_apply = tk.Button(s, text="Appliquer", font=("Arial", 12, "bold"), command=lambda: apply_and_close())
        btn_apply.pack(pady=15)
        style_button(btn_apply)

        def apply_and_close():
            self.ai_difficulty = diff_var.get()
            self.human_color = color_var.get()
            self.show_eval = show_var.get()
            s.destroy()

        if modal:
            s.grab_set()
            s.wait_window()


# ------------------ Run ------------------
if __name__ == "__main__":
    TeekoMenu()