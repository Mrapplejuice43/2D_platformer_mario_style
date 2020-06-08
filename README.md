# 2D_platformer_mario_style
 
2D platformer made with only numpy and pygame

### Run Window.py as the main


## Keys to play the game :

- Directional arrows left and right to move left and right
- Space to jump
- Escape to toggle menu
- r to reset the game
- F10 to toggle the debug menu

## Controls for the editor :

- Left click to place or remove a block
- Mode 0 stands for Placing blocks and 1 for Remove blocks

## What's implemented :

- A physics motor which calculates collisions, movements and gravity
- Damages to ennemies and to the player (For now the player dies instantly)
- The editor exporting a new world file that the game can read

## What's missing :

- A LOT of menus to make the program working without going into the code
- Animations (the class is here but not working yet)
- AI to make enemies moving
- An ending block (Just a gameObject that toggles a variable)


## To modify certain things in the code :

- To change the physics in the game, all variables are in the Actor.py file

- To change the world you play : Line 35 of file Window.py

- To change the size of the window : Line 10 of Window.py

- To change the life of the player : Line 333 of Actor.py
- To change the life of the enemies : Line 399 of Actor.py

# How it works

When we launch the program, we first create the instances of everything we need : Window, World, Editor, Game, Camera...

- The Window class is where the main loop is. Here we handle all inputs, events and hold variables that determine what we should render, where we are in the program (playing the game, editing a world, in the main menu...) and make a link between instances.

- The Game class is here to make the code clearer. I mean that the class has no real purpose but separate things that is more game related and put them into this class and let what's left in the World class.

- The World class stores everything that is in the game (gameObjects, players, enemies..) and holds a camera to follow the player as he is moving through the world. It also loads and unloads objects that are in the game is they are on screen or not for performance.

- The gameObject class hold variables like position, width, height. There are subclasses per object types to differenciate them.

- The overlay and component classes are used to generate the menus. There are subclasses of component to differenciate them and make them act properly : 
  - The buttons throw events when the user clicks on them caught by the main loop
  - Other components are here to display things like text, images, a background color
  
  We can put an infinity of components inside a component to make things like images in a button used in the editor overlay.
  
- The camera class makes the world move with the player. We can see where the camera is by using F10 while playing.
