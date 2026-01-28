🐔 Crossy Road Python
An infinite-scrolling arcade game built with Python and Pygame. Dodge traffic, hop across rivers, and stay ahead of the creeping camera in this high-speed survival game.

🌟 Features
Infinite Gameplay: Procedurally generated levels that never end.

Multiple Terrains: Navigate Roads (cars/trucks), Railways (trains), Rivers (logs), and Grass (trees).

The Chase: The camera moves automatically. If you get pushed off the bottom of the screen, you lose!

Dynamic Difficulty: The game gets faster and the traffic gets denser every 100 points.

Cinematic Game Over: Obstacles explode into eggs one-by-one, followed by a randomized "Game Over" animation and a joke-telling chicken.

Modern UI: Semi-transparent, floating HUD for scores and levels.

🕹️ Controls
Arrow Keys: Move the chicken.

Spacebar: Restart after a game over.

🚀 Installation
Install Pygame:
  Bash
  pip install pygame

Run the Game:
  Bash
  python crossy_road.py

🛠️ Code Structure
Lane Class: Handles the logic for different terrains and static textures.

Vehicle/Log Classes: Manages movement, wrapping, and variety of obstacles.

Game Over Sequence: A staged animation system that manages the transition from death to the restart menu.
