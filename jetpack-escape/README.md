# Jetpack Escape - Web Version

A fast-paced jetpack adventure game with two game modes: Traditional and Continuous.

## Files Included

- `game.js` - Main game logic (required)
- `index.html` - Standalone game page (optional)
- `README.md` - This file

## Integration Options

### Option 1: Standalone Game Page
Simply copy the entire `jetpack-escape` folder to your website and link to `index.html`.

### Option 2: Embed in Existing Page
Add this HTML to any page where you want the game:

```html
<canvas id="game-canvas" width="800" height="600" style="border: 2px solid #333; display: block; margin: 0 auto;"></canvas>
<script src="path/to/game.js"></script>
<script>
    window.addEventListener('load', () => {
        new JetpackEscape();
    });
</script>
```

### Option 3: Modal/Popup Game
Add a button that opens the game in a modal:

```html
<button onclick="openGame()">Play Jetpack Escape</button>

<div id="gameModal" style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); z-index: 1000;">
    <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);">
        <canvas id="game-canvas" width="800" height="600" style="border: 2px solid #333;"></canvas>
        <button onclick="closeGame()" style="position: absolute; top: -40px; right: 0;">Close</button>
    </div>
</div>

<script src="path/to/game.js"></script>
<script>
    function openGame() {
        document.getElementById('gameModal').style.display = 'block';
        new JetpackEscape();
    }
    
    function closeGame() {
        document.getElementById('gameModal').style.display = 'none';
        location.reload(); // Reset game
    }
</script>
```

## Game Features

- **Traditional Mode**: 3 lives, enemies appear after 3 gates, tunnel penalty system
- **Continuous Mode**: Endless survival with double jump and speed boosts
- **Responsive Controls**: 100 FPS for smooth gameplay
- **Fallback Graphics**: Works without image assets
- **Menu System**: Complete with rules and credits

## Controls

- **SPACE**: Jump / Double Jump
- **ESC**: Return to Menu
- **Mouse**: Navigate Menus

## Technical Details

- Pure JavaScript (no dependencies)
- Canvas-based rendering
- 100 FPS frame rate for responsiveness
- Self-contained game logic
- Cross-browser compatible

## Optional Assets

If you want the visual assets, also copy:
- `background.png`
- `jetpack_character.png`
- `enemy.png`

The game will work perfectly without these images using colored rectangles as fallbacks. 