// Dual Snake Game - Two Player Competitive Snake Game
// Game initialization
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
const startButton = document.getElementById('startButton');
const restartButton = document.getElementById('restartButton');
const pauseButton = document.getElementById('pauseButton');
const soundToggle = document.getElementById('soundToggle');
const fullscreenButton = document.getElementById('fullscreenButton');
const startOverlay = document.getElementById('startOverlay');
const gameOverOverlay = document.getElementById('gameOverOverlay');

// Game state
let gameState = {
    isRunning: false,
    isPaused: false,
    gameMode: 'normal',
    timeLeft: 120, // 2 minutes in seconds
    gameTimer: null,
    soundEnabled: true,
    score1: 0,
    score2: 0,
    foodEaten1: 0,
    foodEaten2: 0,
    powerups: []
};

// Game constants
const GRID_SIZE = 20;
const GRID_WIDTH = canvas.width / GRID_SIZE;
const GRID_HEIGHT = canvas.height / GRID_SIZE;

// Player 1 (Red snake) - Controls: W, A, S, D
const player1 = {
    color: '#ff4757',
    headColor: '#ff3838',
    body: [{x: 5, y: 10}, {x: 4, y: 10}, {x: 3, y: 10}],
    direction: 'right',
    nextDirection: 'right',
    score: 0,
    speed: 1.0,
    invincible: false,
    doublePoints: false,
    speedBoost: false,
    powerupTimer: 0
};

// Player 2 (Blue snake) - Controls: Arrow keys
const player2 = {
    color: '#3742fa',
    headColor: '#5352ed',
    body: [{x: 15, y: 10}, {x: 16, y: 10}, {x: 17, y: 10}],
    direction: 'left',
    nextDirection: 'left',
    score: 0,
    speed: 1.0,
    invincible: false,
    doublePoints: false,
    speedBoost: false,
    powerupTimer: 0
};

// Food
let foods = [];
let powerups = [];

// Power-up types
const POWERUP_TYPES = {
    SPEED: {color: '#ffd700', icon: '⚡', duration: 10000, name: 'Speed Boost'},
    INVINCIBLE: {color: '#32cd32', icon: '🛡️', duration: 5000, name: 'Invincibility'},
    DOUBLE_POINTS: {color: '#ff1493', icon: '2X', duration: 15000, name: 'Double Points'},
    CUT_SNAKE: {color: '#8a2be2', icon: '✂️', duration: 0, name: 'Snake Cut'}
};

// Initialize game
function initGame() {
    // Reset players
    player1.body = [{x: 5, y: 10}, {x: 4, y: 10}, {x: 3, y: 10}];
    player1.direction = 'right';
    player1.nextDirection = 'right';
    player1.score = 0;
    player1.speed = 1.0;
    player1.invincible = false;
    player1.doublePoints = false;
    player1.speedBoost = false;
    
    player2.body = [{x: 15, y: 10}, {x: 16, y: 10}, {x: 17, y: 10}];
    player2.direction = 'left';
    player2.nextDirection = 'left';
    player2.score = 0;
    player2.speed = 1.0;
    player2.invincible = false;
    player2.doublePoints = false;
    player2.speedBoost = false;
    
    // Reset game state
    gameState.score1 = 0;
    gameState.score2 = 0;
    gameState.foodEaten1 = 0;
    gameState.foodEaten2 = 0;
    gameState.powerups = [];
    gameState.timeLeft = 120;
    
    // Clear foods and powerups
    foods = [];
    powerups = [];
    
    // Generate initial food
    generateFood();
    generateFood();
    generateFood();
    
    // Update UI
    updateUI();
}

// Generate food at random position
function generateFood() {
    let food;
    let overlapping;
    
    do {
        overlapping = false;
        food = {
            x: Math.floor(Math.random() * GRID_WIDTH),
            y: Math.floor(Math.random() * GRID_HEIGHT),
            type: 'normal',
            color: '#ffd32a'
        };
        
        // Check if food overlaps with players or existing food
        for (let segment of player1.body) {
            if (segment.x === food.x && segment.y === food.y) overlapping = true;
        }
        for (let segment of player2.body) {
            if (segment.x === food.x && segment.y === food.y) overlapping = true;
        }
        for (let existingFood of foods) {
            if (existingFood.x === food.x && existingFood.y === food.y) overlapping = true;
        }
        
    } while (overlapping);
    
    foods.push(food);
    
    // Random chance to spawn powerup instead of food
    if (Math.random() < 0.1) { // 10% chance
        generatePowerup();
    }
}

// Generate power-up
function generatePowerup() {
    const types = Object.keys(POWERUP_TYPES);
    const randomType = types[Math.floor(Math.random() * types.length)];
    const powerupType = POWERUP_TYPES[randomType];
    
    let powerup;
    let overlapping;
    
    do {
        overlapping = false;
        powerup = {
            x: Math.floor(Math.random() * GRID_WIDTH),
            y: Math.floor(Math.random() * GRID_HEIGHT),
            type: randomType,
            color: powerupType.color,
            icon: powerupType.icon,
            name: powerupType.name,
            duration: powerupType.duration
        };
        
        // Check if powerup overlaps with players, food, or existing powerups
        for (let segment of player1.body) {
            if (segment.x === powerup.x && segment.y === powerup.y) overlapping = true;
        }
        for (let segment of player2.body) {
            if (segment.x === powerup.x && segment.y === powerup.y) overlapping = true;
        }
        for (let food of foods) {
            if (food.x === powerup.x && food.y === powerup.y) overlapping = true;
        }
        for (let existingPowerup of powerups) {
            if (existingPowerup.x === powerup.x && existingPowerup.y === powerup.y) overlapping = true;
        }
        
    } while (overlapping);
    
    powerups.push(powerup);
}

// Update player positions
function updatePlayers() {
    // Update player 1
    player1.direction = player1.nextDirection;
    const head1 = {...player1.body[0]};
    
    switch (player1.direction) {
        case 'up': head1.y--; break;
        case 'down': head1.y++; break;
        case 'left': head1.x--; break;
        case 'right': head1.x++; break;
    }
    
    // Check wall collision for player 1
    if (!player1.invincible) {
        if (head1.x < 0 || head1.x >= GRID_WIDTH || head1.y < 0 || head1.y >= GRID_HEIGHT) {
            gameOver('Player 2');
            return;
        }
    } else {
        // Wrap around if invincible
        if (head1.x < 0) head1.x = GRID_WIDTH - 1;
        if (head1.x >= GRID_WIDTH) head1.x = 0;
        if (head1.y < 0) head1.y = GRID_HEIGHT - 1;
        if (head1.y >= GRID_HEIGHT) head1.y = 0;
    }
    
    // Check self collision for player 1
    if (!player1.invincible) {
        for (let i = 1; i < player1.body.length; i++) {
            if (player1.body[i].x === head1.x && player1.body[i].y === head1.y) {
                gameOver('Player 2');
                return;
            }
        }
    }
    
    // Update player 2
    player2.direction = player2.nextDirection;
    const head2 = {...player2.body[0]};
    
    switch (player2.direction) {
        case 'up': head2.y--; break;
        case 'down': head2.y++; break;
        case 'left': head2.x--; break;
        case 'right': head2.x++; break;
    }
    
    // Check wall collision for player 2
    if (!player2.invincible) {
        if (head2.x < 0 || head2.x >= GRID_WIDTH || head2.y < 0 || head2.y >= GRID_HEIGHT) {
            gameOver('Player 1');
            return;
        }
    } else {
        // Wrap around if invincible
        if (head2.x < 0) head2.x = GRID_WIDTH - 1;
        if (head2.x >= GRID_WIDTH) head2.x = 0;
        if (head2.y < 0) head2.y = GRID_HEIGHT - 1;
        if (head2.y >= GRID_HEIGHT) head2.y = 0;
    }
    
    // Check self collision for player 2
    if (!player2.invincible) {
        for (let i = 1; i < player2.body.length; i++) {
            if (player2.body[i].x === head2.x && player2.body[i].y === head2.y) {
                gameOver('Player 1');
                return;
            }
        }
    }
    
    // Check collision between players
    if (!player1.invincible || !player2.invincible) {
        // Player 1 head vs Player 2 body
        for (let segment of player2.body) {
            if (segment.x === head1.x && segment.y === head1.y) {
                if (!player1.invincible) {
                    gameOver('Player 2');
                    return;
                }
            }
        }
        
        // Player 2 head vs Player 1 body
        for (let segment of player1.body) {
            if (segment.x === head2.x && segment.y === head2.y) {
                if (!player2.invincible) {
                    gameOver('Player 1');
                    return;
                }
            }
        }
        
        // Head to head collision
        if (head1.x === head2.x && head1.y === head2.y) {
            gameOver('Draw');
            return;
        }
    }
    
    // Check food collision for player 1
    for (let i = foods.length - 1; i >= 0; i--) {
        const food = foods[i];
        if (food.x === head1.x && food.y === head1.y) {
            // Remove food
            foods.splice(i, 1);
            
            // Add score
            let points = 10;
            if (player1.doublePoints) points *= 2;
            player1.score += points;
            gameState.score1 = player1.score;
            gameState.foodEaten1++;
            
            // Grow snake
            player1.body.unshift(head1);
            
            // Generate new food
            generateFood();
            
            // Play sound
            if (gameState.soundEnabled) {
                playSound('eat');
            }
            
            break;
        }
    }
    
    // Check food collision for player 2
    for (let i = foods.length - 1; i >= 0; i--) {
        const food = foods[i];
        if (food.x === head2.x && food.y === head2.y) {
            // Remove food
            foods.splice(i, 1);
            
            // Add score
            let points = 10;
            if (player2.doublePoints) points *= 2;
            player2.score += points;
            gameState.score2 = player2.score;
            gameState.foodEaten2++;
            
            // Grow snake
            player2.body.unshift(head2);
            
            // Generate new food
            generateFood();
            
            // Play sound
            if (gameState.soundEnabled) {
                playSound('eat');
            }
            
            break;
        }
    }
    
    // Check powerup collision
    for (let i = powerups.length - 1; i >= 0; i--) {
        const powerup = powerups[i];
        let collected = false;
        
        // Player 1 collects powerup
        if (powerup.x === head1.x && powerup.y === head1.y) {
            applyPowerup(player1, powerup.type);
            collected = true;
            updatePowerupDisplay();
        }
        
        // Player 2 collects powerup
        if (powerup.x === head2.x && powerup.y === head2.y) {
            applyPowerup(player2, powerup.type);
            collected = true;
            updatePowerupDisplay();
        }
        
        if (collected) {
            powerups.splice(i, 1);
            if (gameState.soundEnabled) {
                playSound('powerup');
            }
        }
    }
    
    // Update player positions
    player1.body.unshift(head1);
    player1.body.pop();
    
    player2.body.unshift(head2);
    player2.body.pop();
    
    // Update powerup timers
    updatePowerupTimers();
}

// Apply powerup to player
function applyPowerup(player, type) {
    switch (type) {
        case 'SPEED':
            player.speedBoost = true;
            player.speed = 1.5;
            player.powerupTimer = POWERUP_TYPES.SPEED.duration;
            break;
        case 'INVINCIBLE':
            player.invincible = true;
            player.powerupTimer = POWERUP_TYPES.INVINCIBLE.duration;
            break;
        case 'DOUBLE_POINTS':
            player.doublePoints = true;
            player.powerupTimer = POWERUP_TYPES.DOUBLE_POINTS.duration;
            break;
        case 'CUT_SNAKE':
            // Cut opponent's snake in half
            const opponent = player === player1 ? player2 : player1;
            const newLength = Math.floor(opponent.body.length / 2);
            opponent.body = opponent.body.slice(0, newLength);
            break;
    }
    
    // Add to active powerups display
    gameState.powerups.push({
        player: player === player1 ? 'Player 1' : 'Player 2',
        type: POWERUP_TYPES[type].name,
        duration: POWERUP_TYPES[type].duration
    });
}

// Update powerup timers
function updatePowerupTimers() {
    if (player1.powerupTimer > 0) {
        player1.powerupTimer -= 16; // Assuming 60fps
        if (player1.powerupTimer <= 0) {
            player1.speedBoost = false;
            player1.invincible = false;
            player1.doublePoints = false;
            player1.speed = 1.0;
            player1.powerupTimer = 0;
        }
    }
    
    if (player2.powerupTimer > 0) {
        player2.powerupTimer -= 16; // Assuming 60fps
        if (player2.powerupTimer <= 0) {
            player2.speedBoost = false;
            player2.invincible = false;
            player2.doublePoints = false;
            player2.speed = 1.0;
            player2.powerupTimer = 0;
        }
    }
    
    // Clean up expired powerups from display
    for (let i = gameState.powerups.length - 1; i >= 0; i--) {
        const powerup = gameState.powerups[i];
        if (powerup.player === 'Player 1' && player1.powerupTimer <= 0) {
            gameState.powerups.splice(i, 1);
        } else if (powerup.player === 'Player 2' && player2.powerupTimer <= 0) {
            gameState.powerups.splice(i, 1);
        }
    }
}

// Update powerup display
function updatePowerupDisplay() {
    const powerupList = document.getElementById('powerupList');
    powerupList.innerHTML = '';
    
    gameState.powerups.forEach(powerup => {
        const item = document.createElement('div');
        item.className = 'powerup-item';
        item.innerHTML = `
            <span style="color: ${powerup.player === 'Player 1' ? '#ff4757' : '#3742fa'}">
                ${powerup.player}
            </span>: ${powerup.type}
        `;
        powerupList.appendChild(item);
    });
}

// Draw game
function drawGame() {
    // Clear canvas
    ctx.fillStyle = '#111';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Draw grid
    drawGrid();
    
    // Draw food
    drawFood();
    
    // Draw powerups
    drawPowerups();
    
    // Draw players
    drawPlayer(player1);
    drawPlayer(player2);
}

// Draw grid
function drawGrid() {
    ctx.strokeStyle = '#222';
    ctx.lineWidth = 1;
    
    // Vertical lines
    for (let x = 0; x <= canvas.width; x += GRID_SIZE) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, canvas.height);
        ctx.stroke();
    }
    
    // Horizontal lines
    for (let y = 0; y <= canvas.height; y += GRID_SIZE) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(canvas.width, y);
        ctx.stroke();
    }
}

// Draw food
function drawFood() {
    foods.forEach(food => {
        ctx.fillStyle = food.color;
        ctx.beginPath();
        ctx.arc(
            food.x * GRID_SIZE + GRID_SIZE / 2,
            food.y * GRID_SIZE + GRID_SIZE / 2,
            GRID_SIZE / 2 - 2,
            0,
            Math.PI * 2
        );
        ctx.fill();
        
        // Draw apple-like stem
        ctx.fillStyle = '#8b4513';
        ctx.fillRect(
            food.x * GRID_SIZE + GRID_SIZE / 2 - 1,
            food.y * GRID_SIZE + 2,
            2,
            GRID_SIZE / 4
        );
    });
}

// Draw powerups
function drawPowerups() {
    powerups.forEach(powerup => {
        // Draw powerup background
        ctx.fillStyle = powerup.color;
        ctx.beginPath();
        ctx.arc(
            powerup.x * GRID_SIZE + GRID_SIZE / 2,
            powerup.y * GRID_SIZE + GRID_SIZE / 2,
            GRID_SIZE / 2 - 1,
            0,
            Math.PI * 2
        );
        ctx.fill();
        
        // Draw powerup icon
        ctx.fillStyle = '#000';
        ctx.font = 'bold 14px Arial';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(
            powerup.icon,
            powerup.x * GRID_SIZE + GRID_SIZE / 2,
            powerup.y * GRID_SIZE + GRID_SIZE / 2
        );
    });
}

// Draw player
function drawPlayer(player) {
    // Draw body
    player.body.forEach((segment, index) => {
        if (index === 0) {
            // Head
            ctx.fillStyle = player.headColor;
            if (player.invincible) {
                // Draw invincible effect
                ctx.shadowColor = player.headColor;
                ctx.shadowBlur = 10;
            }
        } else {
            // Body
            ctx.fillStyle = player.color;
        }
        
        // Draw segment
        ctx.fillRect(
            segment.x * GRID_SIZE + 2,
            segment.y * GRID_SIZE + 2,
            GRID_SIZE - 4,
            GRID_SIZE - 4
        );
        
        // Draw rounded corners
        ctx.fillStyle = player.color;
        if (index === 0) {
            ctx.fillStyle = player.headColor;
        }
        drawRoundedRect(
            segment.x * GRID_SIZE + 2,
            segment.y * GRID_SIZE + 2,
            GRID_SIZE - 4,
            GRID_SIZE - 4,
            4
        );
        
        // Draw eyes on head
        if (index === 0) {
            ctx.fillStyle = '#fff';
            
            // Eye positions based on direction
            let eye1X, eye1Y, eye2X, eye2Y;
            
            switch (player.direction) {
                case 'right':
                    eye1X = segment.x * GRID_SIZE + GRID_SIZE - 6;
                    eye1Y = segment.y * GRID_SIZE + 6;
                    eye2X = segment.x * GRID_SIZE + GRID_SIZE - 6;
                    eye2Y = segment.y * GRID_SIZE + GRID_SIZE - 6;
                    break;
                case 'left':
                    eye1X = segment.x * GRID_SIZE + 6;
                    eye1Y = segment.y * GRID_SIZE + 6;
                    eye2X = segment.x * GRID_SIZE + 6;
                    eye2Y = segment.y * GRID_SIZE + GRID_SIZE - 6;
                    break;
                case 'up':
                    eye1X = segment.x * GRID_SIZE + 6;
                    eye1Y = segment.y * GRID_SIZE + 6;
                    eye2X = segment.x * GRID_SIZE + GRID_SIZE - 6;
                    eye2Y = segment.y * GRID_SIZE + 6;
                    break;
                case 'down':
                    eye1X = segment.x * GRID_SIZE + 6;
                    eye1Y = segment.y * GRID_SIZE + GRID_SIZE - 6;
                    eye2X = segment.x * GRID_SIZE + GRID_SIZE - 6;
                    eye2Y = segment.y * GRID_SIZE + GRID_SIZE - 6;
                    break;
            }
            
            ctx.beginPath();
            ctx.arc(eye1X, eye1Y, 2, 0, Math.PI * 2);
            ctx.fill();
            
            ctx.beginPath();
            ctx.arc(eye2X, eye2Y, 2, 0, Math.PI * 2);
            ctx.fill();
            
            // Draw pupils
            ctx.fillStyle = '#000';
            ctx.beginPath();
            ctx.arc(eye1X, eye1Y, 1, 0, Math.PI * 2);
            ctx.fill();
            
            ctx.beginPath();
            ctx.arc(eye2X, eye2Y, 1, 0, Math.PI * 2);
            ctx.fill();
        }
        
        // Reset shadow
        ctx.shadowBlur = 0;
    });
}

// Draw rounded rectangle
function drawRoundedRect(x, y, width, height, radius) {
    ctx.beginPath();
    ctx.moveTo(x + radius, y);
    ctx.lineTo(x + width - radius, y);
    ctx.quadraticCurveTo(x + width, y, x + width, y + radius);
    ctx.lineTo(x + width, y + height - radius);
    ctx.quadraticCurveTo(x + width, y + height, x + width - radius, y + height);
    ctx.lineTo(x + radius, y + height);
    ctx.quadraticCurveTo(x, y + height, x, y + height - radius);
    ctx.lineTo(x, y + radius);
    ctx.quadraticCurveTo(x, y, x + radius, y);
    ctx.closePath();
    ctx.fill();
}

// Update UI
function updateUI() {
    // Update scores
    document.getElementById('score1').textContent = gameState.score1;
    document.getElementById('score2').textContent = gameState.score2;
    document.getElementById('length1').textContent = player1.body.length;
    document.getElementById('length2').textContent = player2.body.length;
    document.getElementById('food1').textContent = gameState.foodEaten1;
    document.getElementById('food2').textContent = gameState.foodEaten2;
    
    // Update speed indicators
    document.getElementById('speed1').textContent = player1.speedBoost ? 'Fast' : 'Normal';
    document.getElementById('speed2').textContent = player2.speedBoost ? 'Fast' : 'Normal';
    
    // Update timer
    const minutes = Math.floor(gameState.timeLeft / 60);
    const seconds = gameState.timeLeft % 60;
    document.getElementById('timer').textContent = 
        `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    
    // Update status message
    const statusElement = document.getElementById('statusMessage');
    if (!gameState.isRunning) {
        statusElement.textContent = 'Press START BATTLE to begin!';
    } else if (gameState.isPaused) {
        statusElement.textContent = 'PAUSED';
    } else {
        statusElement.textContent = 'BATTLE IN PROGRESS!';
    }
}

// Game loop
let lastTime = 0;
let player1UpdateTimer = 0;
let player2UpdateTimer = 0;

function gameLoop(timestamp) {
    if (!gameState.isRunning || gameState.isPaused) {
        lastTime = timestamp;
        requestAnimationFrame(gameLoop);
        return;
    }
    
    const deltaTime = timestamp - lastTime;
    lastTime = timestamp;
    
    // Update players based on their speed
    player1UpdateTimer += deltaTime;
    player2UpdateTimer += deltaTime;
    
    const player1UpdateInterval = 150 / player1.speed; // Base interval divided by speed
    const player2UpdateInterval = 150 / player2.speed;
    
    if (player1UpdateTimer >= player1UpdateInterval) {
        updatePlayers();
        player1UpdateTimer = 0;
    }
    
    if (player2UpdateTimer >= player2UpdateInterval) {
        // Player 2 update is handled together with player 1 in updatePlayers()
        // This is just for timing purposes
        player2UpdateTimer = 0;
    }
    
    // Draw game
    drawGame();
    
    // Continue game loop
    requestAnimationFrame(gameLoop);
}

// Start game
function startGame() {
    initGame();
    gameState.isRunning = true;
    gameState.isPaused = false;
    
    // Start game timer
    gameState.gameTimer = setInterval(() => {
        if (!gameState.isPaused && gameState.timeLeft > 0) {
            gameState.timeLeft--;
            updateUI();
            
            if (gameState.timeLeft <= 0) {
                endGameByTime();
            }
        }
    }, 1000);
    
    // Hide start overlay
    startOverlay.style.display = 'none';
    gameOverOverlay.style.display = 'none';
    
    // Start game loop
    requestAnimationFrame(gameLoop);
}

// Pause game
function pauseGame() {
    gameState.isPaused = !gameState.isPaused;
    pauseButton.innerHTML = gameState.isPaused ? 
        '<i class="fas fa-play"></i> RESUME' : 
        '<i class="fas fa-pause"></i> PAUSE';
    updateUI();
}

// Game over
function gameOver(winner) {
    gameState.isRunning = false;
    clearInterval(gameState.gameTimer);
    
    // Show game over overlay
    gameOverOverlay.style.display = 'flex';
    
    // Update winner text
    const winnerText = document.getElementById('winnerText');
    if (winner === 'Draw') {
        winnerText.textContent = "It's a Draw!";
    } else {
        winnerText.textContent = `${winner} Wins!`;
    }
    
    // Update final scores
    document.getElementById('finalScore1').textContent = gameState.score1;
    document.getElementById('finalScore2').textContent = gameState.score2;
    
    // Play game over sound
    if (gameState.soundEnabled) {
        playSound('gameover');
    }
}

// End game by time
function endGameByTime() {
    gameState.isRunning = false;
    clearInterval(gameState.gameTimer);
    
    // Determine winner by score
    let winner;
    if (gameState.score1 > gameState.score2) {
        winner = 'Player 1';
    } else if (gameState.score2 > gameState.score1) {
        winner = 'Player 2';
    } else {
        winner = 'Draw';
    }
    
    // Show game over overlay
    gameOverOverlay.style.display = 'flex';
    
    // Update winner text
    const winnerText = document.getElementById('winnerText');
    if (winner === 'Draw') {
        winnerText.textContent = "Time's Up! It's a Draw!";
    } else {
        winnerText.textContent = `Time's Up! ${winner} Wins!`;
    }
    
    // Update final scores
    document.getElementById('finalScore1').textContent = gameState.score1;
    document.getElementById('finalScore2').textContent = gameState.score2;
    
    // Play game over sound
    if (gameState.soundEnabled) {
        playSound('gameover');
    }
}

// Play sound
function playSound(type) {
    // Simple sound simulation - in a real game you would use Web Audio API
    console.log(`Playing sound: ${type}`);
}

// Toggle sound
function toggleSound() {
    gameState.soundEnabled = !gameState.soundEnabled;
    soundToggle.innerHTML = gameState.soundEnabled ?
        '<i class="fas fa-volume-up"></i> SOUND ON' :
        '<i class="fas fa-volume-mute"></i> SOUND OFF';
}

// Toggle fullscreen
function toggleFullscreen() {
    if (!document.fullscreenElement) {
        canvas.requestFullscreen().catch(err => {
            console.log(`Error attempting to enable fullscreen: ${err.message}`);
        });
        fullscreenButton.innerHTML = '<i class="fas fa-compress"></i> EXIT FULLSCREEN';
    } else {
        document.exitFullscreen();
        fullscreenButton.innerHTML = '<i class="fas fa-expand"></i> FULLSCREEN';
    }
}

// Event listeners
startButton.addEventListener('click', startGame);
restartButton.addEventListener('click', startGame);
pauseButton.addEventListener('click', pauseGame);
soundToggle.addEventListener('click', toggleSound);
fullscreenButton.addEventListener('click', toggleFullscreen);

// Keyboard controls
document.addEventListener('keydown', (event) => {
    // Prevent default behavior for game control keys to stop page scrolling
    const gameKeys = ['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'w', 'a', 's', 'd', 'W', 'A', 'S', 'D', ' '];
    if (gameKeys.includes(event.key)) {
        event.preventDefault();
    }

    if (!gameState.isRunning || gameState.isPaused) return;
    
    // Player 1 controls (W, A, S, D)
    switch (event.key.toLowerCase()) {
        case 'w':
            if (player1.direction !== 'down') player1.nextDirection = 'up';
            break;
        case 's':
            if (player1.direction !== 'up') player1.nextDirection = 'down';
            break;
        case 'a':
            if (player1.direction !== 'right') player1.nextDirection = 'left';
            break;
        case 'd':
            if (player1.direction !== 'left') player1.nextDirection = 'right';
            break;
    }
    
    // Player 2 controls (Arrow keys)
    switch (event.key) {
        case 'ArrowUp':
            if (player2.direction !== 'down') player2.nextDirection = 'up';
            break;
        case 'ArrowDown':
            if (player2.direction !== 'up') player2.nextDirection = 'down';
            break;
        case 'ArrowLeft':
            if (player2.direction !== 'right') player2.nextDirection = 'left';
            break;
        case 'ArrowRight':
            if (player2.direction !== 'left') player2.nextDirection = 'right';
            break;
    }
    
    // Pause game with Space bar
    if (event.key === ' ') {
        pauseGame();
    }
});

// Game mode selection
document.querySelectorAll('.btn-mode').forEach(button => {
    button.addEventListener('click', () => {
        // Remove active class from all buttons
        document.querySelectorAll('.btn-mode').forEach(btn => {
            btn.classList.remove('active');
        });
        
        // Add active class to clicked button
        button.classList.add('active');
        
        // Set game mode
        gameState.gameMode = button.dataset.mode;
        
        // Adjust game settings based on mode
        switch (gameState.gameMode) {
            case 'speed':
                gameState.timeLeft = 90; // 1.5 minutes
                break;
            case 'survival':
                gameState.timeLeft = 180; // 3 minutes
                break;
            default: // normal
                gameState.timeLeft = 120; // 2 minutes
                break;
        }
        
        // Update timer display
        updateUI();
    });
});

// Initialize UI
updateUI();

// Draw initial game state
drawGame();

console.log('Dual Snake Game initialized. Press START BATTLE to begin!');
