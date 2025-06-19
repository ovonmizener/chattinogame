// Jetpack Escape - JavaScript Version
class JetpackEscape {
    constructor() {
        this.canvas = document.getElementById('game-canvas');
        this.ctx = this.canvas.getContext('2d');
        this.canvas.width = 800;
        this.canvas.height = 600;
        
        // Game state
        this.state = 'menu'; // menu, modeSelect, traditional, continuous, gameOver, credits, rules
        this.gameMode = 'traditional';
        this.score = 0;
        this.lives = 3;
        this.gatesCleared = 0;
        
        // Frame rate - fast with very mild restrictions
        this.FPS = 100;  // Much faster for responsive gameplay
        this.frameTime = 1000 / this.FPS; // 10ms per frame
        this.lastFrameTime = 0;
        
        // Player
        this.player = {
            x: 100,
            y: 300,
            width: 50,
            height: 50,
            velocity: 0,
            gravity: 0.5,        // EXACTLY matching Python: gravity = 0.5
            jumpPower: -8        // EXACTLY matching Python: jump_power = -8
        };
        
        // Obstacles
        this.obstacles = [];
        this.obstacleSpeed = 7;  // Increased from 5 for more dynamic gameplay
        this.obstacleWidth = 50;
        this.obstacleGap = 200;
        this.lastScoredObstacle = null;
        
        // Enemy
        this.enemy = {
            x: 650,
            y: 255,
            width: 90,
            height: 90,
            active: false,
            direction: { x: 0, y: 0 },
            speed: 3
        };
        
        // Continuous mode variables - EXACTLY matching Python constants
        this.continuousObstacles = [];
        this.continuousScore = 0;
        this.continuousStartTime = 0;
        this.continuousGameStarted = false;
        this.continuousGroundY = 550;
        this.continuousGroundHeight = 50;
        this.continuousCanDoubleJump = false;
        this.continuousHasDoubleJumped = false;
        this.continuousSpeedBoostTimer = 0;
        this.continuousCurrentSpeed = 5;
        this.continuousJumpPower = -15;     // EXACTLY matching Python: continuous_jump_power = -15
        this.continuousGravity = 0.8;       // EXACTLY matching Python: continuous_gravity = 0.8
        this.continuousObstacleSpeed = 7;   // Increased from 5 for more dynamic gameplay
        this.continuousSpeedBoost = 10;     // EXACTLY matching Python: continuous_speed_boost = 10
        this.continuousSpeedBoostDuration = 60; // EXACTLY matching Python: continuous_speed_boost_duration = 60
        this.continuousObstacleSpawnChance = 0.02; // EXACTLY matching Python: continuous_obstacle_spawn_chance = 0.02
        this.continuousFloatingChance = 0.3; // EXACTLY matching Python: continuous_floating_obstacle_chance = 0.3
        
        // Tunnel
        this.tunnelRect = { x: 0, y: 500, width: 800, height: 100 };
        
        // Colors
        this.colors = {
            white: '#FFFFFF',
            black: '#000000',
            blue: '#00FFFF',
            orange: '#FF8C00',
            red: '#FF0000',
            pink: '#FF00FF',
            green: '#00FF00',
            gray: 'rgba(128, 128, 128, 0.6)',
            gold: '#FFD700'
        };
        
        // Load images
        this.images = {};
        this.loadImages();
        
        // Input
        this.keys = {};
        this.keysPressed = {};  // Track if key was already pressed this frame
        this.setupInput();
        
        // Start game loop
        this.gameLoop();
    }
    
    loadImages() {
        const imageFiles = ['background.png', 'jetpack_character.png', 'enemy.png'];
        let loadedCount = 0;
        
        imageFiles.forEach(filename => {
            const img = new Image();
            img.onload = () => {
                loadedCount++;
                if (loadedCount === imageFiles.length) {
                    console.log('All images loaded successfully');
                }
            };
            img.onerror = () => {
                console.log(`Failed to load ${filename}, using fallback`);
            };
            img.src = filename;
            this.images[filename] = img;
        });
    }
    
    setupInput() {
        document.addEventListener('keydown', (e) => {
            this.keys[e.code] = true;
            this.keysPressed[e.code] = true;  // Mark as pressed this frame
            
            // Handle continuous mode start
            if (this.state === 'continuous' && e.code === 'Space' && !this.continuousGameStarted) {
                this.continuousGameStarted = true;
                this.continuousStartTime = Date.now();
            }
            
            // Handle ESC key
            if (e.code === 'Escape') {
                if (this.state === 'traditional' || this.state === 'continuous') {
                    this.state = 'menu';
                }
            }
        });
        
        document.addEventListener('keyup', (e) => {
            this.keys[e.code] = false;
            this.keysPressed[e.code] = false;  // Reset pressed state
        });
        
        this.canvas.addEventListener('click', (e) => {
            this.handleClick(e);
        });
    }
    
    handleClick(e) {
        const rect = this.canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        if (this.state === 'menu') {
            // Check which button was clicked
            if (y > 200 && y < 270) {
                this.state = 'modeSelect';
            } else if (y > 290 && y < 360) {
                this.state = 'rules';
            } else if (y > 380 && y < 450) {
                this.state = 'credits';
            }
        } else if (this.state === 'modeSelect') {
            if (y > 200 && y < 250) {
                this.state = 'traditional';
                this.gameMode = 'traditional';
                this.resetGame();
            } else if (y > 280 && y < 330) {
                this.state = 'continuous';
                this.gameMode = 'continuous';
                this.resetContinuousGame();
            } else if (y > 360 && y < 410) {
                this.state = 'menu';
            }
        } else if (this.state === 'gameOver') {
            if (y > 350 && y < 410) {
                // Try Again
                if (this.gameMode === 'continuous') {
                    this.state = 'continuous';
                    this.resetContinuousGame();
                } else {
                    this.state = 'traditional';
                    this.resetGame();
                }
            } else if (y > 430 && y < 490) {
                // Main Menu
                this.state = 'menu';
            }
        } else if (this.state === 'credits' || this.state === 'rules') {
            if (y > 520 && y < 565) {
                this.state = 'menu';
            }
        }
    }
    
    resetGame() {
        this.score = 0;
        this.lives = 3;
        this.obstacles = [];
        this.gatesCleared = 0;
        this.enemy.active = false;
        this.player.x = 100;
        this.player.y = 300;
        this.player.velocity = 0;
        this.lastScoredObstacle = null;
    }
    
    resetContinuousGame() {
        this.continuousScore = 0;
        this.continuousObstacles = [];
        this.continuousGameStarted = false;
        this.continuousCanDoubleJump = false;
        this.continuousHasDoubleJumped = false;
        this.continuousSpeedBoostTimer = 0;
        this.continuousCurrentSpeed = 5;
        this.player.x = 100;
        this.player.y = this.continuousGroundY - this.player.height;
        this.player.velocity = 0;
    }
    
    update() {
        if (this.state === 'traditional') {
            this.updateTraditional();
        } else if (this.state === 'continuous') {
            this.updateContinuous();
        }
    }
    
    updateTraditional() {
        // Handle input - EXACTLY matching Python version
        if (this.keys['Space'] && this.player.velocity > -5) {
            this.player.velocity = this.player.jumpPower;
        }
        
        // Update player physics - EXACTLY matching Python version
        this.player.velocity += this.player.gravity;
        if (this.player.velocity > 5) this.player.velocity = 5;  // EXACTLY matching Python: if velocity > 5: velocity = 5
        if (this.player.velocity > 0) this.player.velocity -= 0.1;  // EXACTLY matching Python: if velocity > 0: velocity -= 0.1
        this.player.y += this.player.velocity;
        
        // Screen boundaries - EXACTLY matching Python version
        if (this.player.y > this.canvas.height - this.player.height) {
            this.player.y = this.canvas.height - this.player.height;
        }
        if (this.player.y < 0) this.player.y = 0;
        
        // Generate obstacles - EXACTLY matching Python version
        if (this.obstacles.length === 0 || this.obstacles[this.obstacles.length - 1].x < this.canvas.width - 300) {
            if (this.gatesCleared >= 4 && Math.random() < 0.3) {
                // Multi-opening gate - EXACTLY matching Python version
                const gapPositions = this.getRandomGapPositions(3);
                for (let i = 0; i < gapPositions.length; i++) {
                    if (i === 0) {
                        this.obstacles.push({
                            x: this.canvas.width,
                            y: 0,
                            width: this.obstacleWidth,
                            height: gapPositions[i]
                        });
                    } else {
                        this.obstacles.push({
                            x: this.canvas.width,
                            y: gapPositions[i-1] + this.obstacleGap,
                            width: this.obstacleWidth,
                            height: gapPositions[i] - (gapPositions[i-1] + this.obstacleGap)
                        });
                    }
                }
                this.obstacles.push({
                    x: this.canvas.width,
                    y: gapPositions[gapPositions.length - 1] + this.obstacleGap,
                    width: this.obstacleWidth,
                    height: this.canvas.height - (gapPositions[gapPositions.length - 1] + this.obstacleGap)
                });
            } else {
                // Regular single-gap gate - EXACTLY matching Python version
                const gapY = Math.floor(Math.random() * (this.canvas.height - this.obstacleGap - 200)) + 100;
                this.obstacles.push({
                    x: this.canvas.width,
                    y: 0,
                    width: this.obstacleWidth,
                    height: gapY
                });
                this.obstacles.push({
                    x: this.canvas.width,
                    y: gapY + this.obstacleGap,
                    width: this.obstacleWidth,
                    height: this.canvas.height - gapY - this.obstacleGap
                });
            }
        }
        
        // Move obstacles
        this.obstacles.forEach(obstacle => {
            obstacle.x -= this.obstacleSpeed;
        });
        this.obstacles = this.obstacles.filter(obstacle => obstacle.x > -this.obstacleWidth);
        
        // Scoring - more forgiving condition to match Python behavior
        this.obstacles.forEach(obstacle => {
            if (obstacle.x + obstacle.width <= this.player.x && obstacle.x + obstacle.width > this.player.x - this.obstacleSpeed && obstacle !== this.lastScoredObstacle) {
                this.score++;
                this.gatesCleared++;
                this.lastScoredObstacle = obstacle;
            }
        });
        
        // Tunnel penalty
        this.obstacles.forEach((obstacle, index) => {
            if (this.isInTunnel() && obstacle.x < this.player.x && this.player.x < obstacle.x + obstacle.width) {
                this.score -= 2;
                this.obstacles.splice(index, 1);
            }
        });
        
        // Collision detection (only if not in tunnel)
        if (!this.isInTunnel()) {
            this.obstacles.forEach(obstacle => {
                if (this.checkCollision(this.player, obstacle)) {
                    this.lives--;
                    if (this.lives <= 0) {
                        this.state = 'gameOver';
                    } else {
                        this.resetPlayerPosition();
                    }
                }
            });
        }
        
        // Enemy logic
        if (this.gatesCleared >= 3) {
            if (!this.enemy.active) {
                this.enemy.active = true;
                this.enemy.x = this.canvas.width - 150;
                this.enemy.y = this.canvas.height / 2 - 45;
                this.setRandomEnemyDirection();
            }
            
            if (this.enemy.active) {
                this.updateEnemy();
                
                if (this.checkCollision(this.player, this.enemy)) {
                    this.lives--;
                    if (this.lives <= 0) {
                        this.state = 'gameOver';
                    } else {
                        this.resetPlayerPosition();
                        this.resetEnemy();
                    }
                }
            }
        }
    }
    
    updateContinuous() {
        if (!this.continuousGameStarted) return;
        
        // Update score based on time - EXACTLY matching Python version
        this.continuousScore = Math.floor((Date.now() - this.continuousStartTime) / 1000);
        
        // Handle speed boost - EXACTLY matching Python version
        if (this.continuousSpeedBoostTimer > 0) {
            this.continuousSpeedBoostTimer--;
            this.continuousCurrentSpeed = this.continuousObstacleSpeed + this.continuousSpeedBoost;
        } else {
            this.continuousCurrentSpeed = this.continuousObstacleSpeed;
        }
        
        // Handle input - EXACTLY matching Python version (only on key press, not hold)
        if (this.keys['Space'] && !this.keysPressed['Space']) {
            if (this.player.y + this.player.height >= this.continuousGroundY) {
                this.player.velocity = this.continuousJumpPower;
                this.continuousCanDoubleJump = true;
                this.continuousHasDoubleJumped = false;
            } else if (this.continuousCanDoubleJump && !this.continuousHasDoubleJumped) {
                this.player.velocity = this.continuousJumpPower * 0.8;
                this.continuousHasDoubleJumped = true;
                this.continuousCanDoubleJump = false;
            }
        }
        
        // Update physics - EXACTLY matching Python version
        this.player.velocity += this.continuousGravity;
        this.player.y += this.player.velocity;
        
        // Ground collision - EXACTLY matching Python version
        if (this.player.y + this.player.height > this.continuousGroundY) {
            this.player.y = this.continuousGroundY - this.player.height;
            this.player.velocity = 0;
            this.continuousCanDoubleJump = true;
            this.continuousHasDoubleJumped = false;
        }
        
        // Generate obstacles - EXACTLY matching Python version
        if (Math.random() < this.continuousObstacleSpawnChance) {
            const isFloating = Math.random() < this.continuousFloatingChance;
            if (isFloating) {
                // Floating obstacle at jump height - EXACTLY matching Python
                this.continuousObstacles.push({
                    x: this.canvas.width,
                    y: this.continuousGroundY - 150,  // Higher up like Python
                    width: 30,
                    height: 50,
                    isFloating: true
                });
            } else {
                // Ground obstacle - EXACTLY matching Python
                this.continuousObstacles.push({
                    x: this.canvas.width,
                    y: this.continuousGroundY - 50,
                    width: 30,
                    height: 50,
                    isFloating: false
                });
            }
        }
        
        // Update obstacles - EXACTLY matching Python version
        this.continuousObstacles.forEach(obstacle => {
            obstacle.x -= this.continuousCurrentSpeed;
        });
        this.continuousObstacles = this.continuousObstacles.filter(obstacle => obstacle.x > -obstacle.width);
        
        // Collision detection - EXACTLY matching Python version
        this.continuousObstacles.forEach(obstacle => {
            if (this.checkCollision(this.player, obstacle)) {
                if (obstacle.isFloating && this.player.y + this.player.height <= obstacle.y + 10 && this.player.velocity > 0) {
                    // Bounce off floating obstacle - EXACTLY matching Python: velocity = continuous_jump_power * 0.7
                    this.player.velocity = this.continuousJumpPower * 0.7;
                    this.continuousSpeedBoostTimer = this.continuousSpeedBoostDuration;
                    this.continuousCanDoubleJump = true;
                    this.continuousHasDoubleJumped = false;
                } else {
                    // Normal collision - game over
                    this.state = 'gameOver';
                }
            }
        });
    }
    
    updateEnemy() {
        this.enemy.x += this.enemy.direction.x * this.enemy.speed;
        this.enemy.y += this.enemy.direction.y * this.enemy.speed;
        
        // Bounce off screen edges
        if (this.enemy.x <= 0 || this.enemy.x + this.enemy.width >= this.canvas.width) {
            this.enemy.direction.x *= -1;
        }
        if (this.enemy.y <= 0 || this.enemy.y + this.enemy.height >= this.canvas.height - 100) {
            this.enemy.direction.y *= -1;
        }
        
        // Occasionally change direction
        if (Math.random() < 0.02) {
            this.setRandomEnemyDirection();
        }
    }
    
    setRandomEnemyDirection() {
        const angle = Math.random() * 2 * Math.PI;
        this.enemy.direction.x = Math.cos(angle);
        this.enemy.direction.y = Math.sin(angle);
    }
    
    resetPlayerPosition() {
        this.player.x = 100;
        this.player.y = 300;
        this.player.velocity = 0;
    }
    
    resetEnemy() {
        this.enemy.x = this.canvas.width - 150;
        this.enemy.y = this.canvas.height / 2 - 45;
        this.setRandomEnemyDirection();
    }
    
    getRandomGapPositions(count) {
        const positions = [];
        for (let i = 0; i < count; i++) {
            positions.push(100 + Math.random() * (this.canvas.height - 200));
        }
        return positions.sort((a, b) => a - b);
    }
    
    isInTunnel() {
        return this.player.x >= this.tunnelRect.x && 
               this.player.x <= this.tunnelRect.x + this.tunnelRect.width &&
               this.player.y >= this.tunnelRect.y && 
               this.player.y <= this.tunnelRect.y + this.tunnelRect.height;
    }
    
    checkCollision(rect1, rect2) {
        return rect1.x < rect2.x + rect2.width &&
               rect1.x + rect1.width > rect2.x &&
               rect1.y < rect2.y + rect2.height &&
               rect1.y + rect1.height > rect2.y;
    }
    
    render() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        if (this.state === 'menu') {
            this.renderMenu();
        } else if (this.state === 'modeSelect') {
            this.renderModeSelect();
        } else if (this.state === 'traditional') {
            this.renderTraditional();
        } else if (this.state === 'continuous') {
            this.renderContinuous();
        } else if (this.state === 'gameOver') {
            this.renderGameOver();
        } else if (this.state === 'credits') {
            this.renderCredits();
        } else if (this.state === 'rules') {
            this.renderRules();
        }
    }
    
    renderMenu() {
        this.ctx.fillStyle = this.colors.black;
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Draw scanline effect
        this.ctx.fillStyle = 'rgba(255, 255, 255, 0.1)';
        for (let y = 0; y < this.canvas.height; y += 4) {
            this.ctx.fillRect(0, y, this.canvas.width, 1);
        }
        
        this.ctx.fillStyle = this.colors.pink;
        this.ctx.font = '72px Arial';
        this.ctx.textAlign = 'center';
        this.ctx.fillText('Jetpack Escape', this.canvas.width / 2, 120);
        
        this.ctx.fillStyle = this.colors.blue;
        this.ctx.font = '36px Arial';
        
        const buttons = [
            { text: 'Start Game', y: 240 },
            { text: 'Rules', y: 320 },
            { text: 'Credits', y: 400 }
        ];
        
        buttons.forEach((button, index) => {
            // Button background
            this.ctx.fillStyle = this.colors.black;
            this.ctx.fillRect(240, button.y - 30, 320, 60);
            
            // Button border
            this.ctx.strokeStyle = this.colors.blue;
            this.ctx.lineWidth = 4;
            this.ctx.strokeRect(240, button.y - 30, 320, 60);
            
            // Button shadow
            this.ctx.fillStyle = 'rgba(64, 64, 64, 0.8)';
            this.ctx.fillRect(244, button.y - 26, 320, 60);
            
            // Button text
            this.ctx.fillStyle = this.colors.blue;
            this.ctx.fillText(button.text, this.canvas.width / 2, button.y + 15);
        });
    }
    
    renderModeSelect() {
        this.ctx.fillStyle = this.colors.black;
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Draw scanline effect
        this.ctx.fillStyle = 'rgba(255, 255, 255, 0.1)';
        for (let y = 0; y < this.canvas.height; y += 4) {
            this.ctx.fillRect(0, y, this.canvas.width, 1);
        }
        
        this.ctx.fillStyle = this.colors.pink;
        this.ctx.font = '64px Arial';
        this.ctx.textAlign = 'center';
        this.ctx.fillText('Select Mode', this.canvas.width / 2, 120);
        
        this.ctx.fillStyle = this.colors.blue;
        this.ctx.font = '36px Arial';
        
        const buttons = [
            { text: 'Traditional', y: 240 },
            { text: 'Continuous', y: 320 },
            { text: 'Back', y: 400 }
        ];
        
        buttons.forEach((button, index) => {
            // Button background
            this.ctx.fillStyle = this.colors.black;
            this.ctx.fillRect(240, button.y - 25, 320, 50);
            
            // Button border
            this.ctx.strokeStyle = this.colors.blue;
            this.ctx.lineWidth = 4;
            this.ctx.strokeRect(240, button.y - 25, 320, 50);
            
            // Button shadow
            this.ctx.fillStyle = 'rgba(64, 64, 64, 0.8)';
            this.ctx.fillRect(244, button.y - 21, 320, 50);
            
            // Button text
            this.ctx.fillStyle = this.colors.blue;
            this.ctx.fillText(button.text, this.canvas.width / 2, button.y + 10);
        });
    }
    
    renderTraditional() {
        // Draw background image or fallback
        if (this.images['background.png'] && this.images['background.png'].complete) {
            this.ctx.drawImage(this.images['background.png'], 0, 0, this.canvas.width, this.canvas.height);
        } else {
            // Fallback gradient background
            const gradient = this.ctx.createLinearGradient(0, 0, 0, this.canvas.height);
            gradient.addColorStop(0, '#87CEEB');
            gradient.addColorStop(1, '#98FB98');
            this.ctx.fillStyle = gradient;
            this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        }
        
        // Draw tunnel
        this.ctx.fillStyle = this.colors.gray;
        this.ctx.fillRect(this.tunnelRect.x, this.tunnelRect.y, this.tunnelRect.width, this.tunnelRect.height);
        
        // Draw player image or fallback
        if (this.images['jetpack_character.png'] && this.images['jetpack_character.png'].complete) {
            this.ctx.drawImage(this.images['jetpack_character.png'], this.player.x, this.player.y, this.player.width, this.player.height);
        } else {
            this.ctx.fillStyle = this.colors.blue;
            this.ctx.fillRect(this.player.x, this.player.y, this.player.width, this.player.height);
        }
        
        // Draw obstacles
        this.ctx.fillStyle = this.colors.orange;
        this.obstacles.forEach(obstacle => {
            this.ctx.fillRect(obstacle.x, obstacle.y, obstacle.width, obstacle.height);
        });
        
        // Draw enemy image or fallback
        if (this.enemy.active) {
            if (this.images['enemy.png'] && this.images['enemy.png'].complete) {
                this.ctx.drawImage(this.images['enemy.png'], this.enemy.x, this.enemy.y, this.enemy.width, this.enemy.height);
            } else {
                this.ctx.fillStyle = this.colors.red;
                this.ctx.fillRect(this.enemy.x, this.enemy.y, this.enemy.width, this.enemy.height);
            }
        }
        
        // Draw UI
        this.ctx.fillStyle = this.colors.black;
        this.ctx.font = '24px Arial';
        this.ctx.textAlign = 'left';
        this.ctx.fillText(`Score: ${this.score}`, 10, 30);
        this.ctx.fillText(`Lives: ${this.lives}`, 10, 60);
    }
    
    renderContinuous() {
        // Draw background
        this.ctx.fillStyle = this.colors.white;
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Draw ground
        this.ctx.fillStyle = this.colors.green;
        this.ctx.fillRect(0, this.continuousGroundY, this.canvas.width, this.continuousGroundHeight);
        
        // Draw obstacles
        this.ctx.fillStyle = this.colors.orange;
        this.continuousObstacles.forEach(obstacle => {
            this.ctx.fillRect(obstacle.x, obstacle.y, obstacle.width, obstacle.height);
        });
        
        // Draw player
        if (this.images['jetpack_character.png'] && this.images['jetpack_character.png'].complete) {
            this.ctx.drawImage(this.images['jetpack_character.png'], this.player.x, this.player.y, this.player.width, this.player.height);
        } else {
            this.ctx.fillStyle = this.colors.blue;
            this.ctx.fillRect(this.player.x, this.player.y, this.player.width, this.player.height);
        }
        
        if (this.continuousGameStarted) {
            // Draw UI
            this.ctx.fillStyle = this.colors.black;
            this.ctx.font = '24px Arial';
            this.ctx.textAlign = 'left';
            this.ctx.fillText(`Score: ${this.continuousScore}`, 10, 30);
            
            if (this.continuousSpeedBoostTimer > 0) {
                this.ctx.fillStyle = this.colors.gold;
                this.ctx.fillText('Speed Boost!', this.canvas.width - 150, 30);
            }
        } else {
            // Draw start message
            this.ctx.fillStyle = this.colors.black;
            this.ctx.font = '48px Arial';
            this.ctx.textAlign = 'center';
            this.ctx.fillText('Press Space to Start', this.canvas.width / 2, this.canvas.height / 2);
        }
    }
    
    renderGameOver() {
        this.ctx.fillStyle = this.colors.black;
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Draw scanline effect
        this.ctx.fillStyle = 'rgba(255, 255, 255, 0.1)';
        for (let y = 0; y < this.canvas.height; y += 4) {
            this.ctx.fillRect(0, y, this.canvas.width, 1);
        }
        
        this.ctx.fillStyle = this.colors.pink;
        this.ctx.font = '72px Arial';
        this.ctx.textAlign = 'center';
        this.ctx.fillText('Game Over!', this.canvas.width / 2, 200);
        
        this.ctx.fillStyle = this.colors.blue;
        this.ctx.font = '36px Arial';
        const finalScore = this.gameMode === 'continuous' ? this.continuousScore : this.score;
        this.ctx.fillText(`Final Score: ${finalScore}`, this.canvas.width / 2, 280);
        
        // Draw buttons
        const buttons = [
            { text: 'Try Again', y: 380 },
            { text: 'Main Menu', y: 460 }
        ];
        
        buttons.forEach((button, index) => {
            // Button background
            this.ctx.fillStyle = this.colors.black;
            this.ctx.fillRect(270, button.y - 25, 260, 50);
            
            // Button border
            this.ctx.strokeStyle = this.colors.blue;
            this.ctx.lineWidth = 4;
            this.ctx.strokeRect(270, button.y - 25, 260, 50);
            
            // Button shadow
            this.ctx.fillStyle = 'rgba(64, 64, 64, 0.8)';
            this.ctx.fillRect(274, button.y - 21, 260, 50);
            
            // Button text
            this.ctx.fillStyle = this.colors.blue;
            this.ctx.font = '36px Arial';
            this.ctx.fillText(button.text, this.canvas.width / 2, button.y + 10);
        });
    }
    
    renderCredits() {
        this.ctx.fillStyle = this.colors.black;
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Draw scanline effect
        this.ctx.fillStyle = 'rgba(255, 255, 255, 0.1)';
        for (let y = 0; y < this.canvas.height; y += 4) {
            this.ctx.fillRect(0, y, this.canvas.width, 1);
        }
        
        this.ctx.fillStyle = this.colors.pink;
        this.ctx.font = '48px Arial';
        this.ctx.textAlign = 'center';
        this.ctx.fillText('Credits', this.canvas.width / 2, 60);
        
        this.ctx.fillStyle = this.colors.blue;
        this.ctx.font = '20px Arial';
        this.ctx.textAlign = 'center';
        
        const credits = [
            'This game was developed by Oliver von Mizener.',
            '',
            'Game is actively under development with regular updates on GitHub.',
            '',
            'Future plans include:',
            '  - New custom artwork and animations',
            '  - Story mode with unique levels',
            '  - Additional game modes and features',
            '',
            'Current assets are temporary and will be replaced in future updates.'
        ];
        
        credits.forEach((line, index) => {
            this.ctx.fillText(line, this.canvas.width / 2, 120 + index * 25);
        });
        
        // Back button
        this.ctx.fillStyle = this.colors.black;
        this.ctx.fillRect(290, 520, 180, 45);
        this.ctx.strokeStyle = this.colors.blue;
        this.ctx.lineWidth = 3;
        this.ctx.strokeRect(290, 520, 180, 45);
        this.ctx.fillStyle = this.colors.blue;
        this.ctx.font = '24px Arial';
        this.ctx.fillText('Back', this.canvas.width / 2, 550);
    }
    
    renderRules() {
        this.ctx.fillStyle = this.colors.black;
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Draw scanline effect
        this.ctx.fillStyle = 'rgba(255, 255, 255, 0.1)';
        for (let y = 0; y < this.canvas.height; y += 4) {
            this.ctx.fillRect(0, y, this.canvas.width, 1);
        }
        
        this.ctx.fillStyle = this.colors.pink;
        this.ctx.font = '36px Arial';
        this.ctx.textAlign = 'center';
        this.ctx.fillText('How to Play', this.canvas.width / 2, 30);
        
        this.ctx.fillStyle = this.colors.blue;
        this.ctx.font = '20px Arial';
        this.ctx.textAlign = 'left';
        
        const rules = [
            'Traditional Mode:',
            '  - Use SPACE to jump and control your character',
            '  - Navigate through gates to score points',
            '  - You have 3 lives - lose them all and it\'s game over',
            '  - After 3 gates, an enemy appears and moves randomly',
            '  - The tunnel at the bottom is safe but cowardly',
            '  - Score points by passing through gates',
            '  - Using the tunnel deducts points - be brave!',
            '',
            'Continuous Mode:',
            '  - Press SPACE to start the game',
            '  - Use SPACE to jump and double jump',
            '  - Land on floating obstacles to get a speed boost',
            '  - One life only - any collision ends the game',
            '  - Score is based on survival time in seconds',
            '  - Press ESC to return to menu',
            '',
            'Controls:',
            '  - SPACE: Jump/Double Jump',
            '  - ESC: Return to Menu',
            '  - Mouse: Navigate Menus'
        ];
        
        rules.forEach((line, index) => {
            this.ctx.fillText(line, 30, 60 + index * 22);
        });
        
        // Back button
        this.ctx.fillStyle = this.colors.black;
        this.ctx.fillRect(310, 520, 140, 45);
        this.ctx.strokeStyle = this.colors.blue;
        this.ctx.lineWidth = 3;
        this.ctx.strokeRect(310, 520, 140, 45);
        this.ctx.fillStyle = this.colors.blue;
        this.ctx.font = '24px Arial';
        this.ctx.textAlign = 'center';
        this.ctx.fillText('Back', this.canvas.width / 2, 550);
    }
    
    gameLoop() {
        const currentTime = performance.now();
        
        // Only update if enough time has passed (100 FPS limit for fast responsive gameplay)
        if (currentTime - this.lastFrameTime >= this.frameTime) {
            // Reset keysPressed state each frame
            this.keysPressed = {};
            
            this.update();
            this.render();
            
            this.lastFrameTime = currentTime;
        }
        
        requestAnimationFrame(() => this.gameLoop());
    }
}

// Start the game when the page loads
window.addEventListener('load', () => {
    new JetpackEscape();
}); 