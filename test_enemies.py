import pygame
from endless_mode import EndlessGameManager
from entities import Player
from constants import SCREEN_WIDTH

pygame.init()
pygame.display.set_mode((800, 600))
mgr = EndlessGameManager()
p = Player(0, mgr.GROUND_Y - 50, None, None, None, None, stage=3)

# advance a bit
for i in range(300):
    p.x += 5
    mgr.update(p, 1/60.0)

print(f"Alive enemies: {mgr.enemies_alive()}")
print(f"Total enemies generated: {len(mgr.enemies)}")
for e in mgr.enemies:
    print(f"Enemy type: {type(e).__name__}, alive: {e.alive}, pos: ({e.x}, {e.y}), health: {e.health}")
