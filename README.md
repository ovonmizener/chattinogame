# chattinogame
Just for fun, I started making a "Flappy Bird" style game in Python. It's themed after popular streamer Raora, and her character Chattino. I'm just doing this for the experience, I may never finish it, but I wanted a repository available so I can share with friends. Feel free to take/use/modify this however you want. 

# Jetpack Escape

A fast-paced, jetpack-powered arcade game inspired by Flappy Bird, but with dynamic obstacles, an enemy AI, and a unique tunnel mechanic. Developed for fun and learning, with plans for original assets in the future.

---

## Game Description

**Jetpack Escape** challenges you to guide your character through a series of gates and obstacles, avoiding both static hazards and a dynamic enemy that lunges in unpredictable ways. Survive as long as you can, rack up your score, and master the tunnel at the bottom of the screen for extra challenge!

### Game Goals
- Pass through as many gates as possible to increase your score.
- Avoid colliding with obstacles and the enemy.
- Survive as long as you can and set a high score!

---

## Installation & Requirements

- **Python 3.8+**
- **Pygame** (for local play)
- **pygbag** (for web build)

### Install for Local Play
```sh
pip install pygame
```

### Install for Web Build
```sh
pip install pygbag
```

---

## How to Play

- Use the **Spacebar** to jump and control your jetpack-powered character.
- Navigate through the gates and avoid obstacles.
- After clearing 3 gates, an enemy will appear and lunge in various patterns as you progress.
- Entering the tunnel at the bottom is risky—avoid obstacles there for a higher score.

### Controls
- **Spacebar**: Jump
- **Up Arrow**: Increase volume
- **Down Arrow**: Decrease volume
- **Mouse**: Navigate menu and credits
- **Esc/Close**: Quit

---

## Running the Game

### Local (Desktop)
1. Place all files (`ChattinoGame.py`, images, `jump.wav`, etc.) in one folder.
2. Run:
   ```sh
   python ChattinoGame.py
   ```

### Web (Browser) (WIP - This is far from complete and not published, but I wanted to put this here in advance as a coming soon.)
1. Place all files in one folder.
2. Build for web:
   ```sh
   pygbag --build ChattinoGame.py
   ```
3. Open `build/web/index.html` in your browser, or upload to a static web host.

---

## Credits
- **Developer:** Oliver von Mizener
- **Concept & Code:** Oliver von Mizener
- **Assets:** Temporary/placeholder as of 5/22/25. Will be replaced with original work in the future.
- **Audio:** Some sound effects sourced from [Freesound.org](https://freesound.org/)
- **Engine:** [Pygame](https://www.pygame.org/), [pygbag](https://pygbag.dev/)

---

## Asset Note
All graphical and audio assets are temporary and for development purposes only. Some audio is sourced from [Freesound.org](https://freesound.org/). Final release will feature original artwork and sounds.

---

## License
Feel free to use, modify, and share this project for learning and fun. Attribution appreciated!
