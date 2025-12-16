    # Teeko 🎮

## Description

Implementation of the **Teeko** strategy game with a graphical interface in Python using Tkinter. This project features an advanced artificial intelligence based on the **Minimax algorithm with Alpha-Beta pruning**.

## 📋 Game Rules

### Game Board

- **5×5** grid
- Each player has **4 pieces** (X and O)
- **X always starts** first

### Game Flow

#### Phase 1 – Placement

- Players place their pieces alternately on an empty cell
- After 8 turns, each player will have placed their 4 pieces

#### Phase 2 – Movement

- Players move one of their pieces to an adjacent empty cell
- Movements are allowed horizontally, vertically, or diagonally

### Victory Conditions

The first player to achieve one of the following patterns wins:

- **4 pieces aligned** (row, column, or diagonal)
- **2×2 square** with their 4 pieces

### Draw Conditions

- After **30 moves** (15 moves per player) in the movement phase
- If an **identical position repeats 3 times**

## 🎯 Main Features

### 1. **Multiple Game Modes**

- **🎮 Player vs Player (PvP)**: Two human players compete
- **🤖 Player vs AI**: Challenge the artificial intelligence
- **🤖 AI vs AI**: Watch two AIs compete

### 2. **Advanced Artificial Intelligence**

#### Minimax Algorithm with Alpha-Beta Pruning

- **Configurable search depth** (1 to 5 levels)
- **Sophisticated heuristic evaluation**:
  - Detection of sequences of 2, 3, and 4 aligned pieces
  - Bonus for center control
  - Evaluation of threats and opportunities
- **Optimizations**:
  - Immediate detection of winning moves
  - Priority blocking of opponent threats
  - Move ordering by heuristic to improve pruning

#### Difficulty Levels

- **Easy**: Depth 1 (fast reactions, little foresight)
- **Medium**: Depth 3 (good balance)
- **Hard**: Depth 5 (deep analysis, very competitive)

### 3. **Intuitive Graphical Interface**

- **Chess.com-inspired design** with professional color palette
- **5×5 grid** with 90×90 pixel cells
- **Visual pieces**: black (X) and cream (O) circles
- **Highlighting**:
  - Selected piece with green border
  - Grid with subtle lines
- **Real-time information**:
  - Current turn
  - Human player and AI colors
  - Minimax evaluation (optional)

### 4. **AI vs AI Mode**

- **Configuration of both AIs**:
  - Independent level for each AI (Easy, Medium, Hard)
  - Display of levels and colors for each AI
- **Visualization modes**:
  - **Automatic**: AIs play continuously with 1-second delay
  - **Step by Step**: Advance move by move with a "Next Turn" button

### 5. **Customizable Settings**

- **Color choice**: Play X (start first) or O (AI starts)
- **AI difficulty**: Easy, Medium, or Hard
- **Evaluation display**: Visualize the Minimax score calculated by the AI

### 6. **Draw Detection System**

- **Move counter**: Limit of 30 moves in the movement phase
- **Repetition detection**: Identifies positions repeated 3 times
- **Optimized history**: Keeps the last 10 positions to save memory

### 7. **Navigation and Ergonomics**

- **Main menu** with access to all modes
- **"Return to menu" button** available during games
- **Fullscreen window** for better experience
- **Rules display**: Dedicated window with all game rules

## 🚀 Installation and Launch

### Prerequisites

- Python 3.x
- Tkinter (usually included with Python)

### Launching the Game

```bash
python Teeko_iaV4.py
```

## 🏗️ Code Architecture

### Main Classes

#### `TeekoGame`

Main game class managing:

- Game board and logic
- Graphical interface
- User interactions
- AI with Minimax
- Victory and draw detection

#### `TeekoGameAIvsAI`

Class inheriting from `TeekoGame` for AI vs AI mode:

- Management of two AIs with different levels
- Automatic or step-by-step mode
- Display of information for both AIs

#### `TeekoMenu`

Class managing the main menu:

- Game mode selection
- Settings configuration
- Rules display
- Navigation between screens

### Key Methods

#### Minimax Algorithm

```python
minimax(board, depth, alpha, beta, maximizing, perspective_player)
```

- Recursive search with Alpha-Beta pruning
- Evaluation from a specific player's perspective
- Returns the best move and its score

#### Board Evaluation

```python
evaluate_board_for_player(board, perspective_player)
```

- Analysis of sequences of 2, 3, and 4 pieces
- Bonus for center control
- Differential score between player and opponent

#### Victory Detection

```python
check_win_board(board, player)
```

- Checks the 4 alignments (rows, columns, diagonals)
- Checks 2×2 squares

## 🎨 Design and Style

### Color Palette

- **Board background**: `#f0d9b5` (light beige)
- **Grid**: `#b58863` (brown)
- **X pieces**: `#000000` (black)
- **O pieces**: `#fffacd` (cream)
- **Selection**: `#00ff00` (green)
- **Buttons**: `#017cbf` (UTBM blue)
- **Interface**: `#f0f0f0` (light gray)

### Visual Effects

- **Button hover**: Color change on hover
- **Highlighting**: Green border for selected piece
- **Modal windows**: For settings and rules

## 📊 AI Performance

### Complexity

- **Placement phase**: ~25 possible positions per move
- **Movement phase**: ~12-16 possible positions per move
- **Depth 5**: Can analyze several thousand positions

### Implemented Optimizations

1. **Alpha-Beta Pruning**: Drastically reduces the search tree
2. **Move ordering**: Heuristic sorting to improve pruning
3. **Immediate detection**: Short-circuits Minimax for obvious moves
4. **Intelligent source selection**: In movement phase, selects the best piece to move

## 🔧 Customization

### Modify Difficulty

In the `DIFFICULTIES` dictionary:

```python
DIFFICULTIES = {
    "Easy": 1,
    "Medium": 3,
    "Hard": 5
}
```

### Adjust Board Size

Modify the `SIZE` constant (currently 5)

### Change AI Delays

- Normal mode: `self.root.after(200, self.ai_play)`
- AI vs AI mode: `self.root.after(1000, self.ai_turn)`

## 📝 Author

Project completed as part of the **IA41** course at **UTBM** (University of Technology of Belfort-Montbéliard)

## 📄 License

Academic project - UTBM 2025
