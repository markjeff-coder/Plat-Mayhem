import pygame
import sys
import os
import json
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, GRAVITY, LEVEL_WIDTH, LEVEL_TEMPLATES, LEVEL_TEMPLATES_STAGE2
from entities import Player
from level import LevelManager, EndlessLevel, fade_transition
from ui import UI, run_customization, run_stage_select, run_start_screen, show_end_screen, draw_pause_menu, play_music

# Save file path for persisted top scores
SAVE_FILE = os.path.join(os.path.dirname(__file__), "savescores.json")


def load_saved_scores():
    default = {"first": [0, 0, 0, 0], "second": [0, 0, 0, 0], "third": [0, 0, 0, 0], "continue": False}
    try:
        if not os.path.exists(SAVE_FILE):
            with open(SAVE_FILE, "w") as f:
                json.dump(default, f)
            return default
        with open(SAVE_FILE, "r") as f:
            data = json.load(f)
        for k in ("first", "second", "third"):
            if k not in data or not isinstance(data[k], list):
                data[k] = default[k]
                continue
            values = [int(v) for v in data[k] if isinstance(v, int) or (isinstance(v, str) and v.isdigit())]
            if len(values) == 3:
                top_scores = sorted(values, reverse=True)[:3]
                data[k] = [0] + top_scores
            else:
                last_score = values[0] if values else 0
                top_scores = sorted(values[1:], reverse=True)[:3]
                while len(top_scores) < 3:
                    top_scores.append(0)
                data[k] = [last_score] + top_scores
        if "continue" not in data or not isinstance(data["continue"], bool):
            data["continue"] = any(v > 0 for v in data["first"] + data["second"] + data["third"])
        return data
    except Exception:
        with open(SAVE_FILE, "w") as f:
            json.dump(default, f)
        return default


def write_saved_scores(data):
    try:
        with open(SAVE_FILE, "w") as f:
            json.dump(data, f)
    except Exception:
        pass


def main(stage=1):
    pygame.init()
    try:
        pygame.mixer.init()
    except Exception:
        pass
    # Verify sprites folder and expected PNG assets (non-fatal: falls back to shapes)
    def _check_sprites():
        sprites_dir = os.path.join(os.path.dirname(__file__), "sprites")
        expected = [
            "PlayerStandRight.png", "PlayerStandLeft.png",
            "PlayerWalk1.png", "PlayerWalk2.png", "PlayerWalk3.png",
            "PlayerWalkLeft1.png", "PlayerWalkLeft2.png", "PlayerWalkLeft3.png",
            "PlayerAttack1.png", "PlayerAttack2.png", "PlayerAttackLeft1.png", "PlayerAttackLeft2.png",
            "PlayerJump.png", "PlayerFall.png",
            "PlayerSkin.png", "PlayerHair.png", "PlayerShirt.png", "PlayerPant.png",
            "WeaponFist.png", "WeaponStick.png", "WeaponSword.png", "WeaponHammer.png",
            "WeaponSpear.png", "WeaponAxe.png", "WeaponDagger.png",
            "LootWeapon.png", "LootHealth.png", "LootScore.png",
            "EnemyBee1.png", "EnemyBee2.png", "EnemyBee3.png", "EnemyBee4.png", "EnemyBee.png",
            "EnemyLizard1.png", "EnemyLizard2.png", "EnemyLizard3.png", "EnemyLizard4.png", "EnemyLizard.png",
            "Crate.png", "DoorLocked.png", "DoorOpen.png",
            "PlatformTile.png", "PlatformGround.png", "PlatformMoving.png",
        ]
        missing = []
        if not os.path.isdir(sprites_dir):
            print("Warning: sprites/ directory missing; game will use shape fallbacks.")
            return
        for fname in expected:
            if not os.path.isfile(os.path.join(sprites_dir, fname)):
                missing.append(fname)
        if missing:
            print("Warning: Missing sprite files (fallbacks will be used):")
            for m in missing:
                print(" - ", m)

    _check_sprites()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Plat-Mayhem")
    clock = pygame.time.Clock()

    # Load persisted scoreboard data
    scoreboard = load_saved_scores()

    def save_score_callback(stage_idx, score):
        if stage_idx == 1:
            key = "first"
        elif stage_idx == 2:
            key = "second"
        else:
            key = "third"
        arr = scoreboard.get(key, [0, 0, 0, 0])[:]
        last_score = int(score)
        top_scores = arr[1:4] if len(arr) > 1 else [0, 0, 0]
        top_scores.append(last_score)
        top_scores = sorted(top_scores, reverse=True)[:3]
        scoreboard[key] = [last_score] + top_scores
        scoreboard["continue"] = True
        write_saved_scores(scoreboard)

    def reset_scores_callback():
        scoreboard["first"] = [0, 0, 0, 0]
        scoreboard["second"] = [0, 0, 0, 0]
        scoreboard["third"] = [0, 0, 0, 0]
        scoreboard["continue"] = False
        write_saved_scores(scoreboard)

    start_result = None
    while True:
        if start_result is None:
            start_result = run_start_screen(screen, clock, scoreboard, reset_scores_callback)
        if start_result is None:
            continue
        hard_mode = False
        if len(start_result) == 6:
            skin, hair, shirt, pants, hard_mode, stage = start_result
        elif len(start_result) == 5:
            skin, hair, shirt, pants, stage = start_result
        else:
            skin, hair, shirt, pants = start_result
            stage = 1
        if stage == 3:
            level_manager = None
            level = EndlessLevel(stage=stage, hard_mode=hard_mode)
        else:
            templates = LEVEL_TEMPLATES if stage == 1 else LEVEL_TEMPLATES_STAGE2
            level_manager = LevelManager(templates)
            level = level_manager.load_level(0)
        player = Player(100, level.GROUND_Y - Player.H - 10, skin, hair, shirt, pants, stage=stage, hard_mode=hard_mode)
        ui = UI()
        play_music("GamePlayScreen.mp3", volume=0.8)
        won = False
        score_accum = 0.0 if stage == 3 else None

        paused = False
        running = True
        while running:
            keys = pygame.key.get_pressed()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    paused = not paused
                    if paused:
                        break
                if paused:
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        mouse_pos = event.pos
                        current_index = level_manager.current_index if level_manager is not None else 0
                        resume_rect, restart_rect, quit_rect = draw_pause_menu(screen, current_index)
                        if resume_rect.collidepoint(mouse_pos):
                            paused = False
                            play_music("GamePlayScreen.mp3", volume=0.8)
                        elif restart_rect.collidepoint(mouse_pos):
                                # Preserve score, fully reset level and player state per requirements
                                current_score = player.score
                                if stage == 3:
                                    level = EndlessLevel(stage=stage, hard_mode=hard_mode)
                                else:
                                    level = level_manager.load_level(level_manager.current_index)
                                # Create a fresh player instance with defaults for this stage
                                player = Player(100, level.GROUND_Y - Player.H - 10, skin, hair, shirt, pants, stage=stage, hard_mode=hard_mode)
                                # Restore score only; everything else reset to defaults
                                player.score = current_score
                                # Ensure full health according to stage
                                player.health = player.max_health
                                # Reset position and velocities
                                player.x = 100
                                player.y = level.GROUND_Y - Player.H - 10
                                player.vx = 0
                                player.vy = 0
                                # Reset combat & timers
                                player.attacking = False
                                player.attack_timer = 0
                                player.attack_cooldown = 0
                                player.attack_rect = None
                                player.invincible = 0
                                player.knockback_timer = 0
                                # Reset jumps and ground state
                                player.jumps_left = 2
                                player.on_ground = False
                                player.ground_platform = None
                                paused = False
                        elif quit_rect.collidepoint(mouse_pos):
                            pygame.quit()
                            sys.exit()
                    continue
                player.handle_event(event)

            if paused:
                current_index = level_manager.current_index if level_manager is not None else 0
                draw_pause_menu(screen, current_index)
                pygame.display.flip()
                clock.tick(FPS)
                continue

            player.update(level.platforms, keys)
            
            if stage == 3:
                # Endless mode: use delta_time for proper scaling
                delta_time = 1.0 / FPS
                level.update(player, delta_time)
                score_accum += player.score_multiplier / FPS
                if score_accum >= 1.0:
                    extra = int(score_accum)
                    player.score += extra
                    score_accum -= extra
            else:
                # Normal levels: no delta time needed
                level.update(player)

            cam_x = int(player.x) - SCREEN_WIDTH // 2
            if hasattr(level, "level_width"):
                cam_x = max(0, min(cam_x, level.level_width - SCREEN_WIDTH))
            else:
                cam_x = max(0, cam_x)

            if stage != 3 and level.door.active and player.rect.colliderect(level.door.rect):
                next_level = level_manager.next_level()
                if next_level is None:
                    won = True
                    running = False
                else:
                    fade_transition(screen, clock)
                    level = next_level
                    player.x = 100
                    player.y = level.GROUND_Y - Player.H - 10
                    player.vx = 0
                    player.vy = 0
                    player.health = min(player.max_health, player.health + 20)
                continue

            if not player.alive:
                running = False

            level.draw(screen, cam_x)
            player.draw(screen, cam_x)
            ui.draw(screen, player, level.total_enemies, level.enemies_alive())

            pygame.display.flip()
            clock.tick(FPS)

        # Provide save callback so user can save the score from the end screen
        end_result = show_end_screen(screen, clock, won, player.score, save_callback=save_score_callback, stage=stage, scoreboard=scoreboard)
        start_result = end_result


if __name__ == "__main__":
    main()
