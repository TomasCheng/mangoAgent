# Dual Snake - Competitive Two-Player Snake Game

A modern, competitive two-player snake game built with HTML5 Canvas, CSS3, and JavaScript.

## 🎮 Game Features

- **Two-Player Local Battle**: Play with a friend on the same keyboard
- **Competitive Gameplay**: Compete for high scores while avoiding collisions
- **Power-Up System**: Collect special abilities to gain advantages
- **Multiple Game Modes**: Normal, Speed, and Survival modes
- **Real-time Statistics**: Track scores, lengths, food eaten, and active power-ups
- **Responsive Design**: Works on desktop browsers
- **Fullscreen Support**: Immersive gaming experience

## 👥 Player Controls

### Player 1 (Red Snake)
- **W** - Move Up
- **A** - Move Left  
- **S** - Move Down
- **D** - Move Right

### Player 2 (Blue Snake)
- **↑** - Move Up
- **↓** - Move Down
- **←** - Move Left
- **→** - Move Right

### Game Controls
- **SPACE** - Pause/Resume game
- **F** - Toggle fullscreen (via button)

## ⚡ Power-Ups

| Power-Up | Effect | Duration | Color |
|----------|--------|----------|-------|
| Speed Boost | Increases snake speed | 10 seconds | Gold |
| Invincibility | Can pass through walls | 5 seconds | Green |
| Double Points | Doubles score from food | 15 seconds | Pink |
| Snake Cut | Cuts opponent's snake in half | Instant | Purple |

## 🚀 How to Run the Game

### Option 1: Using Node.js (Recommended)
```bash
# Navigate to the game directory
cd /path/to/snake-game

# Start the server
node server.js

# Open your browser and visit:
# http://localhost:8080
```

### Option 2: Using Python
```bash
# Navigate to the game directory
cd /path/to/snake-game

# Start the server
python3 -m http.server 8080

# Open your browser and visit:
# http://localhost:8080
```

### Option 3: Direct File Access
Simply open `index.html` in your web browser (some features may be limited).

## 🎯 Game Rules

1. **Objective**: Eat as much food as possible to grow and earn points
2. **Collisions**: Avoid hitting walls, yourself, or the other snake
3. **Power-Ups**: Collect colored orbs for special abilities
4. **Winning**: The player with the highest score when time runs out wins
5. **Game Over**: Game ends immediately if a player collides

## 🕹️ Game Modes

- **Normal Mode**: 2-minute battle with standard rules
- **Speed Mode**: Faster gameplay with 1.5-minute timer  
- **Survival Mode**: 3-minute battle with increased challenge

## 🏗️ Project Structure

```
snake-game/
├── index.html          # Main HTML file
├── style.css           # Game styling
├── game.js             # Game logic and controls
├── server.js           # Local development server
├── package.json        # Node.js dependencies
└── README.md           # This file
```

## 🛠️ Technologies Used

- **HTML5 Canvas** - Game rendering
- **CSS3** - Modern styling with animations
- **JavaScript (ES6)** - Game logic and controls
- **Font Awesome** - Icons
- **Google Fonts** - Typography

## 📱 Browser Compatibility

Works best in modern browsers:
- Chrome 60+
- Firefox 55+
- Safari 11+
- Edge 79+

## 🎨 Customization

You can customize the game by modifying:
- Colors in `style.css`
- Game speed in `game.js` (GRID_SIZE and update intervals)
- Power-up probabilities in `game.js`
- Game duration in `game.js`

## 🎵 Sound Notes

The game includes sound effect placeholders. To add actual sound effects:
1. Add audio files to the project
2. Uncomment and update the `playSound()` function in `game.js`
3. Use the Web Audio API for better performance

## 🤝 Contributing

Feel free to fork and modify this game! Some ideas for improvements:
- Add online multiplayer
- Implement different arenas
- Add more power-ups
- Create AI opponents
- Add sound effects and music

## 📄 License

This project is open source and available under the MIT License.

## 🎉 Enjoy the Game!

Start the server and open http://localhost:8080 in your browser to begin the battle!

**Tip**: For the best experience, use a keyboard with good key rollover so both players can press keys simultaneously without issues.