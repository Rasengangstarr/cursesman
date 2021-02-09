# Cursesman

![image-example](https://raw.githubusercontent.com/Rasengangstarr/cursesman/main/docs/bombermanexample.jpg)

Terminology and Concepts:  
----
* Room - a room is composed of n static tiles, arrayed in a spaced checkerboard pattern.  
  * The static(non-bricked) tiles here are non-destructable. The room is also surrounded by static tiles.
  * The other (bricked) tiles are destructable, they can be destroyed by bombs and may have items behind them such as:
    * Powerups which confer special bonuses that last between rooms, but are lost when the player dies. There is one powerup per room and the powerup for a given room number is statically defined
    * Doors which take the player to the next room, but only when all enemies in the room have been destroyed.
    * Bonus items -- these are revealed when the player takes a specific action or series of actions - we will not be considering them for the MVP
  * The colorful characters are enemies, with a variety of behaviours and effects  
  
  TTD:
  ----

* MVP - 1
  * Screen Draw around Player
  * Room Generation
  * Player Movement + Collision
  * Bomb Placement
  * Bomb explosion
  * Entity destruction by bombs
  * Door Generation
  * Moving between rooms via doors
* MVP - 2
  * Powerup placement
  * Powerup consumption and effect activation
  * Basic enemies [Balloom](https://strategywiki.org/wiki/Bomberman/How_to_play#Enemies)
  * Player death and loss of a 'life' (with associated loss of powerups)
  * Game over state
* MVP - 3
  * Networking and multiplayer features - we can expand on this when we get there.
