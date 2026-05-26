import pygame
from endless_mode import EndlessGameManager
from entities import Player
from level import EndlessLevel

pygame.init()
pygame.display.set_mode((800, 600))

def run_test():
    level = EndlessLevel(stage=3)
    player = Player(100, level.GROUND_Y - 40, (255, 220, 170), (40, 30, 20), (50, 80, 200), (40, 40, 100), stage=3)
    player.score = 5000  # High score to spawn more stuff

    for i in range(100):
        # Force player to move right constantly
        player.x += 10
        player.rect.x = int(player.x)
        level.update(player, 1.0/60.0)

    print(f"Number of platforms: {len(level.manager.platforms)}")
    print(f"Number of enemies: {len(level.manager.enemies)}")
    print(f"Number of crates: {len(level.manager.crates)}")
    print(f"Number of loots: {len(level.manager.loots)}")

    alive_enemies = [e for e in level.manager.enemies if e.alive]
    print(f"Alive enemies: {len(alive_enemies)}")

    if alive_enemies:
        print(f"Sample enemy type: {type(alive_enemies[0])}")
        print(f"Sample enemy y pos: {alive_enemies[0].y}, platform y pos: {level.manager.platforms[0].rect.y}")

run_test()
