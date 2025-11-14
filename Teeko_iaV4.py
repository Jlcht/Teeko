# teeko_full_fixed.py
import tkinter as tk
from tkinter import messagebox
import random
import math
import copy

# ---------------- Constants ----------------
SIZE = 5
CELL_SIZE = 90
PLAYER1 = "X"   # X goes first by rule
PLAYER2 = "O"
EMPTY = "."
COLORS = {PLAYER1: "black", PLAYER2: "beige", EMPTY: "grey"}

# Difficulty presets
DIFFICULTIES = {
    "Facile": 1,
    "Moyen": 3,
    "Difficile": 5
}

# ------------------ Main Game Class ------------------
class TeekoGame:
    def __init__(self, root, *,
                 ai_mode=False,
                 human_side=PLAYER1,
                 minimax_depth=3,
                 show_eval=False,
                 return_to_menu_cb=None):
        self.root = root
        self.ai_mode = ai_mode
        self.human_side = human_side
        self.ai_side = PLAYER2 if human_side == PLAYER1 else PLAYER1
        self.minimax_depth = minimax_depth
        self.show_eval = show_eval
        self.return_to_menu_cb = return_to_menu_cb

        self.board = [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]
        self.turn = PLAYER1  # X always starts
        self.total_pieces = 0
        self.selected_piece = None

        # last eval text to keep it visible after draw_board
        self.last_eval_text = ""

        # UI
        self.root.title("Teeko")
        self.frame = tk.Frame(self.root)
        self.frame.pack()
        self.canvas = tk.Canvas(self.frame, width=SIZE*CELL_SIZE, height=SIZE*CELL_SIZE, bg="white")
        self.canvas.grid(row=0, column=0, columnspan=3)
        self.canvas.bind("<Button-1>", self.on_click)

        self.label_info = tk.Label(self.frame, text=self._info_text(), font=("Arial", 12))
        self.label_info.grid(row=1, column=0, sticky="w", padx=6, pady=6)

        self.label_eval = tk.Label(self.frame, text="", font=("Arial", 10))
        self.label_eval.grid(row=1, column=1, sticky="e", padx=6, pady=6)

        self.btn_menu = tk.Button(self.frame, text="Retour au menu", command=self._return_to_menu)
        self.btn_menu.grid(row=1, column=2, sticky="e", padx=6, pady=6)

        self.draw_board()

        # If AI is to move first (human chose O), let IA play
        if self.ai_mode and self.turn == self.ai_side:
            self.root.after(300, self.ai_play)

    def _info_text(self):
        return f"Tour: {self.turn}    Joueur humain: {self.human_side}    IA: {self.ai_side}"

    def _update_labels(self, eval_text=None):
        # if eval_text provided, update stored text only if show_eval enabled
        if eval_text is not None:
            if self.show_eval:
                self.last_eval_text = eval_text
            else:
                self.last_eval_text = ""
        # update info label
        self.label_info.config(text=self._info_text())
        # update eval label based on show_eval and stored text
        if self.show_eval and self.last_eval_text:
            self.label_eval.config(text=self.last_eval_text)
        else:
            self.label_eval.config(text="")

    def _return_to_menu(self):
        # destroy window and call callback
        if self.return_to_menu_cb:
            self.root.destroy()
            self.return_to_menu_cb()
        else:
            self.root.destroy()

    # ---------------- Drawing ----------------
    def draw_board(self):
        self.canvas.delete("all")
        for r in range(SIZE):
            for c in range(SIZE):
                x1 = c * CELL_SIZE
                y1 = r * CELL_SIZE
                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE
                # Draw rectangle with slight offset so borders are visible
                self.canvas.create_rectangle(x1+3, y1+3, x2, y2, outline="black", width=2)
                piece = self.board[r][c]
                if piece != EMPTY:
                    color = COLORS[piece]
                    self.canvas.create_oval(x1+12, y1+12, x2-12, y2-12, fill=color, outline="black")
        if self.selected_piece:
            r, c = self.selected_piece
            x1 = c * CELL_SIZE
            y1 = r * CELL_SIZE
            x2 = x1 + CELL_SIZE
            y2 = y1 + CELL_SIZE
            self.canvas.create_rectangle(x1+2, y1+2, x2, y2, outline="gold", width=4)
        # update labels but do not clear eval unless requested
        self._update_labels()

    # ---------------- Input Handling ----------------
    def on_click(self, event):
        # ignore clicks if it's AI's turn
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

        # Phase movement
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
            # move
            self.board[r1][c1] = EMPTY
            self.board[r][c] = self.turn
            self.selected_piece = None
            if self.check_win(self.turn):
                self.draw_board()
                self.end_game(self.turn)
                return
            self._advance_turn()

    def _advance_turn(self):
        # alternate
        self.turn = PLAYER1 if self.turn == PLAYER2 else PLAYER2
        self.draw_board()
        # if ai mode and ai's turn -> schedule ai play
        if self.ai_mode and self.turn == self.ai_side:
            self.root.after(200, self.ai_play)

    # ---------------- Utilities ----------------
    def adjacent(self, r1, c1, r2, c2):
        return abs(r1 - r2) <= 1 and abs(c1 - c2) <= 1 and not (r1 == r2 and c1 == c2)

    def count_pieces_board(self, board, player):
        return sum(row.count(player) for row in board)

    # ---------------- Winning check ----------------
    def check_win_board(self, board, player):
        # rows and columns
        for r in range(SIZE):
            for c in range(SIZE - 3):
                if all(board[r][c + i] == player for i in range(4)):
                    return True
        for r in range(SIZE - 3):
            for c in range(SIZE):
                if all(board[r + i][c] == player for i in range(4)):
                    return True
        # diagonals
        for r in range(SIZE - 3):
            for c in range(SIZE - 3):
                if all(board[r + i][c + i] == player for i in range(4)):
                    return True
                if all(board[r + 3 - i][c + i] == player for i in range(4)):
                    return True
        # 2x2 square
        for r in range(SIZE - 1):
            for c in range(SIZE - 1):
                if all(board[r + i][c + j] == player for i in range(2) for j in range(2)):
                    return True
        return False

    def check_win(self, player):
        return self.check_win_board(self.board, player)

    # ---------------- End game ----------------
    def end_game(self, winner):
        messagebox.showinfo("Victoire", f"🎉 Le joueur {winner} a gagné !")
        # keep window open but unbind clicks
        self.canvas.unbind("<Button-1>")

    # ---------------- AI Entry ----------------
    def ai_play(self):
        # first: immediate win or block (placement or movement)
        immediate = self.find_immediate_win_or_block()
        if immediate is not None:
            # apply immediate target
            self.apply_target(immediate, self.ai_side)
            # show eval if enabled
            if self.show_eval:
                self._update_labels(eval_text=f"Eval IA: immediate")
            return

        # otherwise minimax
        move, score = self.minimax(self.board, depth=self.minimax_depth_for_call(), alpha=-math.inf, beta=math.inf, maximizing=True)
        if self.show_eval:
            self._update_labels(eval_text=f"Eval IA: {score:.1f}")
        if move is not None:
            self.apply_target(move, self.ai_side)
        else:
            # fallback random legal target
            targets = self.get_all_targets(self.board, self.ai_side)
            if targets:
                self.apply_target(random.choice(targets), self.ai_side)

    def minimax_depth_for_call(self):
        return self.minimax_depth

    # ---------------- Immediate win/block ----------------
    def find_immediate_win_or_block(self):
        # all targets IA can reach
        ai_targets = self.get_all_targets(self.board, self.ai_side)
        # check IA winning target
        for t in ai_targets:
            newb = self.simulate_move(self.board, t, self.ai_side)
            if self.check_win_board(newb, self.ai_side):
                return t
        # check opponent immediate threats -> block them
        opp_targets = self.get_all_targets(self.board, self.human_side)
        for t in opp_targets:
            newb = self.simulate_move(self.board, t, self.human_side)
            if self.check_win_board(newb, self.human_side):
                # can we play on that target? if AI can reach that same cell, play there
                if t in ai_targets:
                    return t
                # otherwise let minimax handle (no direct block reachable)
        return None

    # ---------------- Generate targets ----------------
    def get_all_targets(self, board, player):
        """Return list of empty cells that player could target:
           - placement phase: all empties
           - movement phase: empties adjacent to at least one player's piece
           Representation: target is (r, c) cell to occupy (not source)."""
        targets = []
        if self.count_pieces_board(board, PLAYER1) < 4 or self.count_pieces_board(board, PLAYER2) < 4:
            # placement
            for r in range(SIZE):
                for c in range(SIZE):
                    if board[r][c] == EMPTY:
                        targets.append((r, c))
        else:
            # movement: empty cells adjacent to at least one of player's pieces
            for r in range(SIZE):
                for c in range(SIZE):
                    if board[r][c] != EMPTY:
                        continue
                    reachable = False
                    for dr in (-1, 0, 1):
                        for dc in (-1, 0, 1):
                            if dr == 0 and dc == 0:
                                continue
                            rr, cc = r + dr, c + dc
                            if 0 <= rr < SIZE and 0 <= cc < SIZE and board[rr][cc] == player:
                                reachable = True
                                break
                        if reachable:
                            break
                    if reachable:
                        targets.append((r, c))
        return targets

    # ---------------- Simulate target (choose best source in movement) ----------------
    def simulate_move(self, board, target, player):
        """Return new board after player occupies 'target'.
           If in placement phase: just place.
           If movement: choose best source (adjacent) for this simulation (try all candidates and keep best)."""
        nb = copy.deepcopy(board)
        if self.count_pieces_board(board, PLAYER1) < 4 or self.count_pieces_board(board, PLAYER2) < 4:
            r, c = target
            nb[r][c] = player
            return nb

        tr, tc = target
        candidates = []
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                sr, sc = tr + dr, tc + dc
                if 0 <= sr < SIZE and 0 <= sc < SIZE and board[sr][sc] == player:
                    candidates.append((sr, sc))
        if not candidates:
            return nb  # unreachable, but safe

        best_nb = None
        if player == self.ai_side:
            best_score = -math.inf
            for (sr, sc) in candidates:
                tmp = copy.deepcopy(board)
                tmp[sr][sc] = EMPTY
                tmp[tr][tc] = player
                score = self.evaluate_board(tmp)
                if score > best_score:
                    best_score = score
                    best_nb = tmp
        else:
            best_score = math.inf
            for (sr, sc) in candidates:
                tmp = copy.deepcopy(board)
                tmp[sr][sc] = EMPTY
                tmp[tr][tc] = player
                score = self.evaluate_board(tmp)
                if score < best_score:
                    best_score = score
                    best_nb = tmp
        return best_nb if best_nb is not None else nb

    # ---------------- Apply target to real board ----------------
    def apply_target(self, target, player):
        if self.total_pieces < 8:
            r, c = target
            self.board[r][c] = player
            self.total_pieces += 1
        else:
            tr, tc = target
            # choose best source to move from (prefer highest evaluation after move)
            candidates = []
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dr == 0 and dc == 0:
                        continue
                    sr, sc = tr + dr, tc + dc
                    if 0 <= sr < SIZE and 0 <= sc < SIZE and self.board[sr][sc] == player:
                        candidates.append((sr, sc))
            if candidates:
                best_src = None
                best_score = -math.inf
                for (sr, sc) in candidates:
                    tmp = copy.deepcopy(self.board)
                    tmp[sr][sc] = EMPTY
                    tmp[tr][tc] = player
                    score = self.evaluate_board(tmp)
                    if score > best_score:
                        best_score = score
                        best_src = (sr, sc)
                if best_src:
                    sr, sc = best_src
                    self.board[sr][sc] = EMPTY
                    self.board[tr][tc] = player

        # after applying, check win and advance turn
        if self.check_win_board(self.board, player):
            self.draw_board()
            self.end_game(player)
            return
        # next turn
        self.turn = PLAYER1 if self.turn == PLAYER2 else PLAYER2
        self.draw_board()
        # schedule AI if needed
        if self.ai_mode and self.turn == self.ai_side:
            self.root.after(200, self.ai_play)

    # ---------------- Minimax (alpha-beta) ----------------
    def minimax(self, board, depth, alpha, beta, maximizing):
        # terminal checks on this board
        if self.check_win_board(board, self.ai_side):
            return None, 100000
        if self.check_win_board(board, self.human_side):
            return None, -100000
        if depth == 0:
            return None, self.evaluate_board(board)

        player = self.ai_side if maximizing else self.human_side
        targets = self.get_all_targets(board, player)
        # order moves by heuristic
        targets.sort(key=lambda t: -self.move_order_heur(board, t, player))

        best_move = None
        if maximizing:
            max_eval = -math.inf
            for t in targets:
                newb = self.simulate_move(board, t, player)
                _, eval_score = self.minimax(newb, depth-1, alpha, beta, False)
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
                _, eval_score = self.minimax(newb, depth-1, alpha, beta, True)
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = t
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            return best_move, min_eval

    def move_order_heur(self, board, target, player):
        # prefer center and adjacency to allies
        r, c = target
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
    def evaluate_board(self, board):
        # check immediate wins/losses
        if self.check_win_board(board, self.ai_side): return 100000
        if self.check_win_board(board, self.human_side): return -100000

        def seq_score_for(player):
            score = 0
            sequences = []
            # rows
            for r in range(SIZE):
                for c in range(SIZE-3):
                    sequences.append([board[r][c+i] for i in range(4)])
            # cols
            for c in range(SIZE):
                for r in range(SIZE-3):
                    sequences.append([board[r+i][c] for i in range(4)])
            # diag
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

        score = seq_score_for(self.ai_side) - seq_score_for(self.human_side)

        # center control small bonus
        center = (SIZE-1)/2
        for r in range(SIZE):
            for c in range(SIZE):
                if board[r][c] == self.ai_side:
                    score += max(0, 3 - (abs(r-center) + abs(c-center)))
                elif board[r][c] == self.human_side:
                    score -= max(0, 3 - (abs(r-center) + abs(c-center)))

        return score

# ------------------ Menu / Settings UI ------------------
class TeekoMenu:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Menu Teeko")

        self.ai_difficulty = "Moyen"
        self.human_color = PLAYER1  # default human = X
        self.show_eval = False

        tk.Label(self.root, text="Bienvenue dans Teeko !", font=("Arial", 16)).pack(pady=10)

        tk.Button(self.root, text=" Jouer à deux", font=("Arial", 14), width=25,
                  command=self.start_pvp).pack(pady=6)
        tk.Button(self.root, text=" Jouer contre l'IA", font=("Arial", 14), width=25,
                  command=self.start_vs_ai).pack(pady=6)
        tk.Button(self.root, text="Règles du jeu", font=("Arial", 12), width=25,
                  command=self.show_rules).pack(pady=6)
        tk.Button(self.root, text=" Quitter", font=("Arial", 12), width=25,
                  command=self.root.quit).pack(pady=6)

        self.root.mainloop()

    def start_pvp(self):
        self.root.destroy()
        w = tk.Tk()
        TeekoGame(w, ai_mode=False, human_side=self.human_color,
                 minimax_depth=DIFFICULTIES[self.ai_difficulty],
                 show_eval=self.show_eval,
                 return_to_menu_cb=self.show_menu)
        w.mainloop()

    def start_vs_ai(self):
        # open settings first (modal) so user chooses difficulty/color before starting
        self.open_settings(modal=True)
        self.root.destroy()
        w = tk.Tk()
        TeekoGame(w, ai_mode=True, human_side=self.human_color,
                 minimax_depth=DIFFICULTIES[self.ai_difficulty],
                 show_eval=self.show_eval,
                 return_to_menu_cb=self.show_menu)
        w.mainloop()

    def show_rules(self):
        """Display the rules of Teeko in a message box."""
        rules = (
            "📜 RÈGLES DU JEU TEEKO\n\n"
            "• Le jeu se joue sur une grille 5×5.\n"
            "• Chaque joueur possède 4 pièces (X et O).\n"
            "• X commence toujours.\n\n"
            "Phase 1 — Placement :\n"
            "Les joueurs placent leurs pièces à tour de rôle sur une case vide.\n"
            "Après 8 tours, chaque joueur aura placé ses 4 pièces.\n\n"
            "Phase 2 — Mouvement :\n"
            "À partir de ce moment, les joueurs déplacent l’une de leurs pièces\n"
            "vers une case vide adjacente (horizontalement, verticalement ou en diagonale).\n\n"
            "🎯 Objectif :\n"
            "Former l’un des motifs suivants :\n"
            "• 4 pièces alignées (ligne, colonne ou diagonale)\n"
            "• ou un carré 2×2.\n\n"
            "Le premier joueur à réussir cela gagne la partie !"
        )
        messagebox.showinfo("Règles du jeu", rules)    

    def show_menu(self):
        # relaunch menu
        self.__init__()

    def open_settings(self, modal=False):
        s = tk.Toplevel(self.root)
        s.title("Paramètres")
        s.geometry("360x320")
        s.transient(self.root)

        # Difficulty
        tk.Label(s, text="Difficulté IA:", font=("Arial", 11)).pack(anchor="w", padx=10, pady=(8,0))
        diff_var = tk.StringVar(value=self.ai_difficulty)
        for name in DIFFICULTIES.keys():
            tk.Radiobutton(s, text=name, variable=diff_var, value=name).pack(anchor="w", padx=20)

        # Color choice
        tk.Label(s, text="Couleur du joueur (X commence):", font=("Arial", 11)).pack(anchor="w", padx=10, pady=(8,0))
        color_var = tk.StringVar(value=self.human_color)
        tk.Radiobutton(s, text="Jouer X (commence)", variable=color_var, value=PLAYER1).pack(anchor="w", padx=20)
        tk.Radiobutton(s, text="Jouer O (IA commence)", variable=color_var, value=PLAYER2).pack(anchor="w", padx=20)

        # Show eval checkbox
        show_var = tk.BooleanVar(value=self.show_eval)
        tk.Checkbutton(s, text="Afficher évaluation Minimax pendant la partie", variable=show_var).pack(anchor="w", padx=10, pady=10)

        def apply_and_close():
            self.ai_difficulty = diff_var.get()
            self.human_color = color_var.get()
            self.show_eval = show_var.get()
            s.destroy()

        tk.Button(s, text="Appliquer", command=apply_and_close).pack(pady=10)

        if modal:
            s.grab_set()
            s.wait_window()

# ------------------ Run ------------------
if __name__ == "__main__":
    TeekoMenu()
