# Gomoku AI with Alpha-Beta Pruning

A sophisticated AI implementation for the classic Gomoku (Five in a Row) board game, featuring advanced minimax algorithms with multiple performance optimizations.

<p align="center">
  <img src="https://github.com/MohamedAboAlaa/gomokuAI/blob/4c971ff94798aa234facc11761dda12baa4a12ae/Code/gomokuAI-py/analysis/game_animation.gif" />
</p>

## 🎮 Game Overview

Gomoku is a two-player strategy board game played on a 15×15 grid. Players alternate placing stones (black and white) on empty intersections, with the goal of being the first to form an unbroken chain of five stones horizontally, vertically, or diagonally.

## 🤖 AI Features

### Core Algorithm
- **Minimax with Alpha-Beta Pruning**: Strategic decision-making algorithm that evaluates all possible moves
- **Pattern Recognition**: Sophisticated evaluation system based on strategic formations
- **4-Level Deep Search**: Looks ahead 4 moves to anticipate consequences
- **Real-time Performance**: Optimized to respond within 1-3 seconds per move

### Advanced Optimizations

1. **Boundary Optimization**
   - Reduces search space from 225 to ~20-30 relevant moves
   - 87% reduction in move consideration space
   - 7-11× faster search performance

2. **Transposition Table (Memoization)**
   - Zobrist hashing for efficient position lookup
   - 30-50% reduction in computation time
   - Avoids recalculating previously seen positions

3. **Move Ordering**
   - Examines promising moves first for better pruning
   - 50-75% reduction in nodes examined
   - Theoretical improvement to O(b^(d/2)) complexity

4. **Incremental Evaluation**
   - Only calculates value changes from new moves
   - 99% reduction in evaluation time per move
   - Efficient pattern-based scoring system

5. **Strategic Distant Monitoring**
   - Monitors potential threats developing away from main action
   - Prevents missing distant winning combinations
   - Throttled checks for optimal performance

## 📊 Performance Metrics

<p align="center">
  <img src="https://github.com/MohamedAboAlaa/gomokuAI/blob/4c971ff94798aa234facc11761dda12baa4a12ae/Code/gomokuAI-py/analysis/ai_move_time_graph.png" />
</p>

### Time Complexity
- **Without Optimizations**: O(225^d) ≈ 11.4 billion nodes at depth 3
- **With Optimizations**: O(20^(d/2)) ≈ 894 nodes at depth 3
- **Overall Improvement**: 99.99992% reduction in nodes examined

### Benchmark Results
- **Depth 1**: ~0.24 seconds
- **Depth 2**: ~1.65 seconds  
- **Depth 3**: ~24.57 seconds (unoptimized)
- **Depth 4**: ~1-3 seconds (with all optimizations) ⭐ *Default*
- **Depth 5**: ~30+ seconds (with optimizations)

## 🎯 Strategic Capabilities

### Pattern Recognition System
The AI evaluates positions using a sophisticated pattern dictionary:

- **Win Conditions** (Five in a row): 10,000,000 points
- **Immediate Threats** (Live Four): 1,000,000 points
- **Forcing Patterns** (Double Fours): 1,000,000 points
- **Strategic Patterns** (Live Three): 200,000 points
- **Defensive Patterns** (Block threats): -2,500,000 points
- **Transitional Patterns** (Two with potential): 1,000 points

### Game Stage Analysis
- **Early Game**: Fast decisions with optimal center opening
- **Mid Game**: Complex pattern evaluation with highest computation time
- **Late Game**: Efficient endgame calculation with reduced search space

## 🚀 Getting Started

### Prerequisites
- Python 3.7+
- Required libraries: `math`, `random` (standard library)

### Installation
```bash
git clone https://github.com/MohamedAboAlaa/gomokuAI.git
cd gomokuAI
python play.py
```

                    
## 💡 Key Technical Insights

1. **Combined Optimizations**: Individual optimizations provide substantial benefits, but their combined effect transforms an impractical algorithm into a responsive game AI.

2. **Pattern-Based Evaluation**: Strategic formations are more important than simple stone counting, enabling the AI to recognize complex tactical situations.

3. **Balanced Performance**: The default depth of 4 represents an optimal balance between strategic strength and computational efficiency.

## 🎮 Gameplay Features

- **Opening Strategy**: Always plays optimally at center (7,7)
- **Defensive Capability**: Recognizes and blocks opponent threats
- **Offensive Tactics**: Creates advantageous patterns and winning combinations
- **Win Detection**: Correctly identifies and executes winning moves

## 📈 Performance Visualization

The AI demonstrates consistent performance across different game stages:
- **Spatial Distribution**: Central moves require more computation than edge moves
- **Temporal Analysis**: Mid-game positions typically have highest computation requirements
- **Pruning Efficiency**: Alpha-beta pruning effectiveness varies with move ordering quality

## 🔧 Customization

### Adjusting AI Difficulty
```python
# Easier AI (faster, less strategic)
ai = GomokuAI(depth=2)

# Harder AI (slower, more strategic)
ai = GomokuAI(depth=5)  # Warning: 30+ seconds per move
```

### Pattern Weights
Modify the pattern dictionary in `utils.py` to adjust AI behavior and strategy priorities.

## 🤝 Contributing

This project was developed as part of ELE335 coursework.

## 👥 Development Team

- **Mohamed Alaa** (ID: 30, Section 2)
- **Abdelrahman Osama** (ID: 13, Section 1)  
- **Mohamed Hamdy** (ID: 27, Section 2)
- **Abdullah Khaled** (ID: 18, Section 1)
- **Mohamed Abdelmonem** (ID: 29, Section 2)

## 📚 Technical Details

For comprehensive technical analysis, algorithm explanations, and detailed performance benchmarks, see the [full project report](https://github.com/MohamedAboAlaa/gomokuAI/blob/b9c52c101900dd37f9a76fe989faacdc83200ce0/Report/Project_1_Report_G8.pdf).

## 🏆 Results

The implementation successfully demonstrates how classical AI search techniques can be optimized for practical applications, achieving a ~99.99992% reduction in computational complexity through combined optimizations while maintaining strategic gameplay quality.

---
