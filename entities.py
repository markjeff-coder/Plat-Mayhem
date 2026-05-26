import pygame
import math
import os
import random
from constants import GRAVITY, LEVEL_WIDTH, SCREEN_HEIGHT, WHITE, BLACK, RED, GRAY, DGRAY, LGRAY, GREEN, YELLOW, BROWN, LBROWN, GOLD, BLUE, ORANGE, WEAPON_POOL, FIST, ENEMY_HEALTH, ENEMY_HEALTH_STAGE2, ENEMY_HEALTH_STAGE3

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "sprites")


def load_image(name):
    path = os.path.join(ASSETS_DIR, name)
    try:
        surf = pygame.image.load(path)
        if pygame.display.get_init():
            try:
                return surf.convert_alpha()
            except Exception:
                return surf
        return surf
    except Exception:
        return None


def load_image_scaled(name, size):
    img = load_image(name)
    if img is None or size is None:
        return img
    try:
        return pygame.transform.smoothscale(img, size)
    except Exception:
        return img


def tint_surface(src, color):
    if src is None:
        return None
    tinted = src.copy()
    overlay = pygame.Surface(src.get_size(), pygame.SRCALPHA)
    overlay.fill((*color, 255))
    tinted.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return tinted


def _animation_frame(frames, index):
    if not frames:
        return None
    idx = index % len(frames)
    for offset in range(len(frames)):
        frame = frames[(idx + offset) % len(frames)]
        if frame is not None:
            return frame
    return None


PLAYER_SIZE = (28, 46)
PLAYER_STAND = {
    1: load_image_scaled("PlayerStandRight.png", PLAYER_SIZE),
    -1: load_image_scaled("PlayerStandLeft.png", PLAYER_SIZE),
}
PLAYER_WALK = {
    1: [load_image_scaled(f"PlayerWalk{i}.png", PLAYER_SIZE) for i in (1, 2, 3)],
    -1: [load_image_scaled(f"PlayerWalkLeft{i}.png", PLAYER_SIZE) for i in (1, 2, 3)],
}
PLAYER_ATTACK = {
    1: [load_image_scaled("PlayerAttack1.png", PLAYER_SIZE), load_image_scaled("PlayerAttack2.png", PLAYER_SIZE)],
    -1: [load_image_scaled("PlayerAttackLeft1.png", PLAYER_SIZE), load_image_scaled("PlayerAttackLeft2.png", PLAYER_SIZE)],
}
PLAYER_JUMP = load_image_scaled("PlayerJump.png", PLAYER_SIZE)
PLAYER_FALL = load_image_scaled("PlayerFall.png", PLAYER_SIZE)
PLAYER_MASKS = {
    "skin": load_image_scaled("PlayerSkin.png", PLAYER_SIZE),
    "hair": load_image_scaled("PlayerHair.png", PLAYER_SIZE),
    "shirt": load_image_scaled("PlayerShirt.png", PLAYER_SIZE),
    "pants": load_image_scaled("PlayerPant.png", PLAYER_SIZE),
}
WEAPON_IMAGES = {
    "Fist": load_image("WeaponFist.png"),
    "Stick": load_image("WeaponStick.png"),
    "Sword": load_image("WeaponSword.png"),
    "Hammer": load_image("WeaponHammer.png"),
    "Spear": load_image("WeaponSpear.png"),
    "Axe": load_image("WeaponAxe.png"),
    "Dagger": load_image("WeaponDagger.png"),
}
LOOT_IMAGES = {
    "weapon": load_image_scaled("LootWeapon.png", (18, 18)),
    "health": load_image_scaled("LootHealth.png", (18, 18)),
    "score": load_image_scaled("LootScore.png", (18, 18)),
    "invincibility": load_image_scaled("LootInvincible.png", (18, 18)),
    "double_damage": load_image_scaled("LootDamage.png", (18, 18)),
}
BEE_FRAMES = [load_image_scaled(f"EnemyBee{i}.png", (34, 34)) for i in (1, 2, 3, 4)]
BEE_STATIC = load_image_scaled("EnemyBee.png", (34, 34))
LIZARD_FRAMES = [load_image_scaled(f"EnemyLizard{i}.png", (34, 34)) for i in (1, 2, 3, 4)]
LIZARD_STATIC = load_image_scaled("EnemyLizard.png", (34, 34))


class Weapon:
    def __init__(self, data):
        self.name = data["name"]
        self.damage = data["damage"]
        self.range = data["range"]
        self.durability = data["durability"]
        self.color = data["color"]

    def use(self):
        if self.durability is None:
            return True
        self.durability -= 1
        return self.durability > 0

    def is_broken(self):
        return self.durability is not None and self.durability <= 0

    def draw(self, surface, x, y, facing, angle=0):
        img = WEAPON_IMAGES.get(self.name)
        if img is not None:
            try:
                target_width = max(24, min(int(self.range * 1.4), self.range + 20))
                aspect = img.get_width() / img.get_height() if img.get_height() else 1
                target_height = max(16, int(target_width / aspect))
                img = pygame.transform.smoothscale(img, (target_width, target_height))
            except Exception:
                pass
            if facing < 0:
                img = pygame.transform.flip(img, True, False)
                pivot = (img.get_width(), img.get_height() // 2)
            else:
                pivot = (0, img.get_height() // 2)
                
            if angle != 0:
                # original center of image relative to pivot
                cx = img.get_width() / 2 - pivot[0]
                cy = img.get_height() / 2 - pivot[1]
                
                # rotate this vector (pygame rotates CCW for positive angle)
                rad = math.radians(-angle)
                rx = cx * math.cos(rad) - cy * math.sin(rad)
                ry = cx * math.sin(rad) + cy * math.cos(rad)
                
                rotated_img = pygame.transform.rotate(img, angle)
                
                # center of the rotated image will be at (x + rx, y + ry)
                dest_x = x + rx - rotated_img.get_width() / 2
                dest_y = y + ry - rotated_img.get_height() / 2
                surface.blit(rotated_img, (dest_x, dest_y))
            else:
                dest_x = x - pivot[0]
                dest_y = y - pivot[1]
                surface.blit(img, (dest_x, dest_y))
            return

        color = self.color or GRAY
        direction = 1 if facing >= 0 else -1

        temp = pygame.Surface((80, 80), pygame.SRCALPHA)
        cx_pos, cy_pos = 40, 40

        def tx(dx):
            return cx_pos + dx * direction

        if self.name == "Stick":
            points = [(tx(0), cy_pos), (tx(4), cy_pos - 6), (tx(32), cy_pos - 4), (tx(32), cy_pos + 4)]
            pygame.draw.polygon(temp, BROWN, points)
            pygame.draw.polygon(temp, BLACK, points, 2)
        elif self.name == "Sword":
            blade = pygame.Rect(min(tx(6), tx(24)), cy_pos - 3, abs(tx(24) - tx(6)), 6)
            pygame.draw.rect(temp, color, blade)
            pygame.draw.rect(temp, BLACK, blade, 2)
            pygame.draw.line(temp, BLACK, (tx(8), cy_pos), (tx(16), cy_pos), 3)
        elif self.name == "Hammer":
            handle = pygame.Rect(min(tx(0), tx(12)), cy_pos + 2, abs(tx(12) - tx(0)), 4)
            pygame.draw.rect(temp, BROWN, handle)
            head = pygame.Rect(min(tx(12), tx(26)), cy_pos - 8, abs(tx(26) - tx(12)), 16)
            pygame.draw.rect(temp, color, head)
            pygame.draw.rect(temp, BLACK, head, 2)
        elif self.name == "Spear":
            shaft = pygame.Rect(min(tx(0), tx(24)), cy_pos + 1, abs(tx(24) - tx(0)), 4)
            pygame.draw.rect(temp, color, shaft)
            tip = [(tx(24), cy_pos - 4), (tx(32), cy_pos + 2), (tx(24), cy_pos + 8)]
            pygame.draw.polygon(temp, color, tip)
            pygame.draw.polygon(temp, BLACK, tip, 2)
        elif self.name == "Axe":
            handle = pygame.Rect(min(tx(0), tx(18)), cy_pos + 3, abs(tx(18) - tx(0)), 4)
            pygame.draw.rect(temp, BROWN, handle)
            blade = [(tx(16), cy_pos - 8), (tx(28), cy_pos - 2), (tx(16), cy_pos + 10)]
            pygame.draw.polygon(temp, color, blade)
            pygame.draw.polygon(temp, BLACK, blade, 2)
        elif self.name == "Dagger":
            blade = pygame.Rect(min(tx(0), tx(18)), cy_pos + 1, abs(tx(18) - tx(0)), 4)
            pygame.draw.rect(temp, color, blade)
            tip = [(tx(18), cy_pos - 4), (tx(26), cy_pos + 3), (tx(18), cy_pos + 10)]
            pygame.draw.polygon(temp, color, tip)
            pygame.draw.polygon(temp, BLACK, tip, 2)
        else:
            rect = pygame.Rect(min(tx(0), tx(18)), cy_pos + 2, abs(tx(18) - tx(0)), 6)
            pygame.draw.rect(temp, color, rect)
            pygame.draw.rect(temp, BLACK, rect, 2)

        if angle != 0:
            rotated_temp = pygame.transform.rotate(temp, angle)
            # The center of temp was (40, 40). We pivot at (40,40), so cx=0, cy=0 relative to pivot!
            # So rotated_temp's center is exactly at (x, y).
            dest_x = x - rotated_temp.get_width() / 2
            dest_y = y - rotated_temp.get_height() / 2
            surface.blit(rotated_temp, (dest_x, dest_y))
        else:
            dest_x = x - temp.get_width() / 2
            dest_y = y - temp.get_height() / 2
            surface.blit(temp, (dest_x, dest_y))


class LootDrop:
    SIZE = 18

    def __init__(self, x, y, kind, data=None):
        self.x = x
        self.y = y
        self.kind = kind
        self.data = data
        self.rect = pygame.Rect(x, y, self.SIZE, self.SIZE)

    def draw(self, surface, cam_x):
        rx = self.x - cam_x
        img = LOOT_IMAGES.get(self.kind)
        if img is not None:
            surface.blit(img, (rx, self.y))
            return
        kind_color = {"weapon": GOLD, "health": RED, "score": BLUE, "invincibility": YELLOW, "double_damage": ORANGE}.get(self.kind)
        if kind_color:
            pygame.draw.rect(surface, kind_color, (rx, self.y, self.SIZE, self.SIZE))
            pygame.draw.rect(surface, WHITE, (rx, self.y, self.SIZE, self.SIZE), 2)
            font = pygame.font.SysFont(None, 14)
            label = {"weapon": "W", "health": "H", "score": "S", "invincibility": "I", "double_damage": "D"}[self.kind]
            txt = font.render(label, True, BLACK)
            surface.blit(txt, (rx + 4, self.y + 3))


class Enemy:
    def __init__(self, x, y, health, damage, speed, detection, color, score_value):
        self.x = float(x)
        self.y = float(y)
        self.w = 34
        self.h = 34
        self.health = health
        self.max_health = health
        self.damage = damage
        self.speed = speed
        self.detection = detection
        self.color = color
        self.score_value = score_value
        self.alive = True
        self.facing = 1
        self.patrol_dir = 1
        self.patrol_dist = 0
        self.max_patrol = 120
        self.hit_flash = 0

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)

    def take_damage(self, dmg):
        self.health -= dmg
        self.hit_flash = 8
        if self.health <= 0:
            self.alive = False

    def _dist_to_player(self, px, py):
        return math.hypot(self.x - px, self.y - py)

    def draw_health_bar(self, surface, cam_x):
        rx = int(self.x) - cam_x
        bw = self.w
        fill = int(bw * max(0, self.health / self.max_health))
        pygame.draw.rect(surface, DGRAY, (rx, int(self.y) - 8, bw, 5))
        pygame.draw.rect(surface, RED, (rx, int(self.y) - 8, fill, 5))

    def draw_eyes(self, surface, cam_x):
        rx = int(self.x) - cam_x
        ex = rx + (self.w - 16) if self.facing > 0 else rx + 4
        ey = int(self.y) + 6
        pygame.draw.circle(surface, WHITE, (ex, ey), 4)
        pygame.draw.circle(surface, WHITE, (ex + 8, ey), 4)
        pygame.draw.circle(surface, BLACK, (ex + 1, ey), 2)
        pygame.draw.circle(surface, BLACK, (ex + 9, ey), 2)


class InsectEnemy(Enemy):
    def __init__(self, x, y, level_index=0, stage=1):
        if stage == 3:
            health = ENEMY_HEALTH_STAGE3[level_index][0] if level_index < len(ENEMY_HEALTH_STAGE3) else 30
            damage = round(round(10 * 1.27) * 1.7)
        elif stage == 2:
            health = ENEMY_HEALTH_STAGE2[level_index][0] if level_index < len(ENEMY_HEALTH_STAGE2) else 30
            damage = round(10 * 1.27)
        else:
            health = ENEMY_HEALTH[level_index][0] if level_index < len(ENEMY_HEALTH) else 30
            damage = 10
        super().__init__(x, y, health=health, damage=damage, speed=1.8, detection=220, color=YELLOW, score_value=100)
        self.base_y = float(y)
        self.wave_t = random.uniform(0, math.pi * 2)
        self.wave_amp = 22
        self.anim_tick = 0

    def update(self, platforms, player_x, player_y):
        if not self.alive:
            return
        dist = self._dist_to_player(player_x, player_y)
        self.wave_t += 0.06
        self.anim_tick = (self.anim_tick + 1) % 24

        if dist < self.detection:
            dx = player_x - self.x
            dy = player_y - self.y
            length = max(1, math.hypot(dx, dy))
            self.x += (dx / length) * self.speed * 1.4
            self.y += (dy / length) * self.speed * 0.8
            self.facing = 1 if dx > 0 else -1
        else:
            self.x += self.patrol_dir * self.speed
            self.patrol_dist += self.speed
            if self.patrol_dist >= self.max_patrol:
                self.patrol_dir *= -1
                self.patrol_dist = 0
                self.facing = self.patrol_dir

        self.y = self.base_y + math.sin(self.wave_t) * self.wave_amp
        if self.hit_flash > 0:
            self.hit_flash -= 1

    def draw(self, surface, cam_x):
        if not self.alive:
            return
        rx = int(self.x) - cam_x
        ry = int(self.y)
        frame = _animation_frame(BEE_FRAMES, self.anim_tick // 6)
        if frame is None:
            frame = BEE_STATIC
        if frame is not None:
            if self.facing < 0:
                frame = pygame.transform.flip(frame, True, False)
            surface.blit(frame, (rx, ry))
            self.draw_health_bar(surface, cam_x)
            return

        col = WHITE if self.hit_flash % 2 == 1 else self.color
        pygame.draw.ellipse(surface, col, (rx, ry, self.w, self.h))
        pygame.draw.ellipse(surface, BLACK, (rx, ry, self.w, self.h), 2)
        pygame.draw.ellipse(surface, (180, 220, 255), (rx - 10, ry + 4, 14, 10))
        pygame.draw.ellipse(surface, (180, 220, 255), (rx + self.w - 4, ry + 4, 14, 10))
        self.draw_eyes(surface, cam_x)
        self.draw_health_bar(surface, cam_x)


class ReptileEnemy(Enemy):
    def __init__(self, x, y, level_index=0, stage=1):
        if stage == 3:
            health = ENEMY_HEALTH_STAGE3[level_index][1] if level_index < len(ENEMY_HEALTH_STAGE3) else 50
            damage = round(round(15 * 1.27) * 1.7)
        elif stage == 2:
            health = ENEMY_HEALTH_STAGE2[level_index][1] if level_index < len(ENEMY_HEALTH_STAGE2) else 50
            damage = round(15 * 1.27)
        else:
            health = ENEMY_HEALTH[level_index][1] if level_index < len(ENEMY_HEALTH) else 50
            damage = 15
        super().__init__(x, y, health=health, damage=damage, speed=1.4, detection=260, color=GREEN, score_value=150)
        self.stage = stage
        self.vy = 0
        self.on_ground = False
        self.anim_tick = 0

    def _has_support_ahead(self, platforms, next_x, direction):
        # Probe a short distance (15 px) ahead at feet level to ensure support
        probe_offset = 15
        if direction > 0:
            probe_x = next_x + self.w // 2 + probe_offset
        else:
            probe_x = next_x + self.w // 2 - probe_offset
        probe_y = self.y + self.h + 4
        for plat in platforms:
            if not getattr(plat, "is_solid_ground", True):
                continue
            # check if platform is under the probe point (a small vertical tolerance)
            if plat.rect.left - 2 <= probe_x <= plat.rect.right + 2:
                if plat.rect.top - 2 <= probe_y <= plat.rect.top + 10:
                    return True
        return False

    def _has_barrier_ahead(self, platforms, next_x, direction, current_platform=None):
        # Side-wall barriers removed: do not block reptile movement at platform edges.
        return False

    def update(self, platforms, player_x, player_y):
        if not self.alive:
            return
        dist = self._dist_to_player(player_x, player_y)
        current_platform = None
        if self.on_ground:
            foot_x = self.x + self.w / 2
            for plat in platforms:
                if plat.rect.left <= foot_x <= plat.rect.right and abs(self.rect.bottom - plat.rect.top) <= 8:
                    current_platform = plat
                    break

        if dist < self.detection:
            dx = player_x - self.x
            move_dir = 1 if dx > 0 else -1
            next_x = self.x + move_dir * self.speed * 1.2
            if self.on_ground and current_platform:
                # reverse if a side-wall barrier is reached, or if no support ahead
                if self._has_barrier_ahead(platforms, next_x, move_dir, current_platform) or not self._has_support_ahead(platforms, next_x, move_dir):
                    self.patrol_dir *= -1
                    self.facing = self.patrol_dir
                else:
                    prev_x = self.x
                    self.x = next_x
                    self.facing = move_dir
                    # if we accidentally overlap a barrier, revert and reverse
                    for plat in platforms:
                        if not getattr(plat, 'is_solid_ground', True) and getattr(plat, 'blocks_enemy', False):
                            if self.rect.colliderect(plat.rect):
                                self.x = prev_x
                                self.patrol_dir *= -1
                                self.facing = self.patrol_dir
                                break
            else:
                self.x = next_x
                self.facing = move_dir
        else:
            move_dir = self.patrol_dir
            next_x = self.x + move_dir * self.speed
            if self.on_ground and current_platform:
                # reverse if a side-wall barrier is reached, or if no support ahead
                if self._has_barrier_ahead(platforms, next_x, move_dir, current_platform) or not self._has_support_ahead(platforms, next_x, move_dir):
                    self.patrol_dir *= -1
                    self.facing = self.patrol_dir
                else:
                    prev_x = self.x
                    self.x = next_x
                    # if overlapping barrier after move, revert and reverse
                    for plat in platforms:
                        if not getattr(plat, 'is_solid_ground', True) and getattr(plat, 'blocks_enemy', False):
                            if self.rect.colliderect(plat.rect):
                                self.x = prev_x
                                self.patrol_dir *= -1
                                self.facing = self.patrol_dir
                                break
            else:
                self.x = next_x
            self.patrol_dist += self.speed
            if self.patrol_dist >= self.max_patrol:
                self.patrol_dir *= -1
                self.patrol_dist = 0
                self.facing = self.patrol_dir

        if not self.on_ground:
            self.vy += GRAVITY
        self.y += self.vy
        self.on_ground = False
        self.anim_tick = (self.anim_tick + 1) % 40

        for plat in platforms:
            pr = self.rect
            if pr.colliderect(plat.rect) and getattr(plat, 'blocks_enemy', True):
                if self.vy > 0 or (self.vy == 0 and pr.bottom <= plat.rect.top + 5):
                    self.y = plat.rect.top - self.h
                    self.vy = 0
                    self.on_ground = True

        if self.hit_flash > 0:
            self.hit_flash -= 1

        # Reptile fall death: if it falls past the bottom bound, mark permanently dead.
        # This counts as a defeated enemy for objectives (enemies_alive) but does
        # NOT award the player score (score is only added when player attacks).
        if self.y > SCREEN_HEIGHT + 50:
            self.alive = False
            self.health = 0
            return

    def draw(self, surface, cam_x):
        if not self.alive:
            return
        rx = int(self.x) - cam_x
        ry = int(self.y)
        frame = _animation_frame(LIZARD_FRAMES, self.anim_tick // 10)
        if frame is None:
            frame = LIZARD_STATIC
        if frame is not None:
            if self.facing < 0:
                frame = pygame.transform.flip(frame, True, False)
            surface.blit(frame, (rx, ry))
            self.draw_health_bar(surface, cam_x)
            return

        col = WHITE if self.hit_flash % 2 == 1 else self.color
        pygame.draw.rect(surface, col, (rx, ry, self.w, self.h))
        pygame.draw.rect(surface, BLACK, (rx, ry, self.w, self.h), 2)
        for i in range(3):
            sy = ry + 6 + i * 8
            pygame.draw.line(surface, (20, 120, 30), (rx + 4, sy), (rx + self.w - 4, sy), 1)
        self.draw_eyes(surface, cam_x)
        self.draw_health_bar(surface, cam_x)

class BatEnemy(Enemy):
    def __init__(self, x, y, level_index=0, stage=1):
        if stage == 3:
            health = ENEMY_HEALTH_STAGE3[level_index][0] if level_index < len(ENEMY_HEALTH_STAGE3) else 25
            damage = round(12 * 1.27 * 1.7)
        else:
            health = 25
            damage = 12
        super().__init__(x, y, health=health, damage=damage, speed=2.5, detection=300, color=(100, 50, 150), score_value=120)
        self.base_y = float(y)
        self.wave_t = random.uniform(0, math.pi * 2)
        self.wave_amp = 15
        self.anim_tick = 0

    def update(self, platforms, player_x, player_y):
        if not self.alive:
            return
        dist = self._dist_to_player(player_x, player_y)
        self.wave_t += 0.08
        self.anim_tick = (self.anim_tick + 1) % 24

        if dist < self.detection:
            dx = player_x - self.x
            dy = player_y - self.y
            length = max(1, math.hypot(dx, dy))
            self.x += (dx / length) * self.speed * 1.8
            self.y += (dy / length) * self.speed * 1.2
            self.facing = 1 if dx > 0 else -1
        else:
            self.x += self.patrol_dir * self.speed
            self.patrol_dist += self.speed
            if self.patrol_dist >= self.max_patrol:
                self.patrol_dir *= -1
                self.patrol_dist = 0
                self.facing = self.patrol_dir
            self.y = self.base_y + math.sin(self.wave_t) * self.wave_amp

        if self.hit_flash > 0:
            self.hit_flash -= 1

    def draw(self, surface, cam_x):
        if not self.alive:
            return
        rx = int(self.x) - cam_x
        ry = int(self.y)
        col = WHITE if self.hit_flash % 2 == 1 else self.color
        pygame.draw.polygon(surface, col, [(rx, ry + self.h // 2), (rx + self.w // 2, ry + self.h), (rx + self.w, ry + self.h // 2), (rx + self.w // 2, ry)])
        pygame.draw.polygon(surface, BLACK, [(rx, ry + self.h // 2), (rx + self.w // 2, ry + self.h), (rx + self.w, ry + self.h // 2), (rx + self.w // 2, ry)], 2)
        self.draw_eyes(surface, cam_x)
        self.draw_health_bar(surface, cam_x)

class ArmoredReptile(ReptileEnemy):
    def __init__(self, x, y, level_index=0, stage=1):
        super().__init__(x, y, level_index, stage)
        self.health = int(self.health * 1.5)
        self.max_health = self.health
        self.color = (100, 100, 100)
        self.score_value = 200
        self.speed = 1.0

    def draw(self, surface, cam_x):
        if not self.alive:
            return
        rx = int(self.x) - cam_x
        ry = int(self.y)
        frame = _animation_frame(LIZARD_FRAMES, self.anim_tick // 10)
        if frame is None:
            frame = LIZARD_STATIC
        if frame is not None:
            if self.facing < 0:
                frame = pygame.transform.flip(frame, True, False)
            tinted = tint_surface(frame, (100, 100, 100))
            surface.blit(tinted if tinted else frame, (rx, ry))
            self.draw_health_bar(surface, cam_x)
            return

        col = WHITE if self.hit_flash % 2 == 1 else self.color
        pygame.draw.rect(surface, col, (rx, ry, self.w, self.h))
        pygame.draw.rect(surface, BLACK, (rx, ry, self.w, self.h), 2)
        for i in range(3):
            sx = rx + 6 + i * 10
            pygame.draw.polygon(surface, (50, 50, 50), [(sx, ry), (sx + 4, ry - 6), (sx + 8, ry)])
            pygame.draw.polygon(surface, BLACK, [(sx, ry), (sx + 4, ry - 6), (sx + 8, ry)], 1)
        self.draw_eyes(surface, cam_x)
        self.draw_health_bar(surface, cam_x)

class Player:
    W = 28
    H = 46

    def __init__(self, x, y, skin, hair, shirt, pants, stage=1, hard_mode=False):
        self.x = float(x)
        self.y = float(y)
        self.vx = 0.0
        self.vy = 0.0
        self.on_ground = False
        self.jumps_left = 2
        self.ground_platform = None
        self.skin = skin
        self.hair = hair
        self.shirt = shirt
        self.pants = pants
        self.hard_mode = hard_mode
        if stage == 3:
            self.max_health = int(round(156 * 0.8)) if hard_mode else 156
        elif stage == 2:
            self.max_health = 120
        else:
            self.max_health = 100
        self.health = self.max_health
        self.score = 0
        self.alive = True
        self.facing = 1
        self.slots = [Weapon(FIST), None]
        self.active_slot = 0
        self.attacking = False
        self.attack_timer = 0
        self.attack_rect = None
        self.attack_cooldown = 0
        self.knockback_timer = 0
        self.invincible = 0
        self.double_damage_timer = 0
        self.anim_tick = 0
        self.walk_tick = 0
        self.attack_frame_tick = 0
        self.multiplier_base = 2.0 if hard_mode and stage == 3 else 1.0

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.W, self.H)

    @property
    def weapon(self):
        w = self.slots[self.active_slot]
        return w if w and not w.is_broken() else Weapon(FIST)

    @property
    def score_multiplier(self):
        return self.multiplier_base + 0.5 * (self.score // 1000)

    def equip_weapon(self, wdata):
        for i, s in enumerate(self.slots):
            if s is None or s.is_broken():
                self.slots[i] = Weapon(wdata)
                return
        self.slots[self.active_slot] = Weapon(wdata)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self._jump()
            if event.key == pygame.K_1:
                self.active_slot = 0
            if event.key == pygame.K_2:
                self.active_slot = 1
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._attack()

    def _jump(self):
        if self.knockback_timer > 0:
            return
        if self.jumps_left == 2:
            self.vy = -13.5
            self.jumps_left = 1
            self.on_ground = False
        elif self.jumps_left == 1:
            self.vy = -8.0
            self.jumps_left = 0

    def _attack(self):
        if self.attack_cooldown > 0:
            return
        self.attacking = True
        self.attack_timer = 12
        self.attack_cooldown = 22
        w = self.weapon
        w.use()
        if self.facing > 0:
            hand_x = self.x + self.W + 10
        else:
            hand_x = self.x - 10
        hand_y = self.y + 18
        if self.facing > 0:
            ax = hand_x
        else:
            ax = hand_x - w.range
        self.attack_rect = pygame.Rect(int(ax), int(hand_y), int(w.range), 18)

    def apply_knockback(self, enemy_x):
        direction = -1 if enemy_x > self.x else 1
        self.vx = direction * 7
        self.vy = -4
        self.knockback_timer = 18
        self.invincible = 60

    def update(self, platforms, keys, level_width=None):
        speed = 4.5
        accel = 0.9
        decel = 0.75

        if self.knockback_timer > 0:
            self.knockback_timer -= 1
        else:
            if keys[pygame.K_a]:
                self.vx = max(self.vx - accel, -speed)
                self.facing = -1
            elif keys[pygame.K_d]:
                self.vx = min(self.vx + accel, speed)
                self.facing = 1
            else:
                self.vx *= decel
                if abs(self.vx) < 0.2:
                    self.vx = 0

        self.vy = min(self.vy + GRAVITY, 18)
        self.x += self.vx
        lw = level_width if level_width is not None else LEVEL_WIDTH
        self.x = max(0, min(self.x, lw - self.W))

        # Horizontal collision
        for plat in platforms:
            if not getattr(plat, 'blocks_player', True):
                continue
            pr = self.rect
            if pr.colliderect(plat.rect):
                if self.vx > 0:
                    self.x = plat.rect.left - self.W
                    self.vx = 0
                elif self.vx < 0:
                    self.x = plat.rect.right
                    self.vx = 0

        self.y += self.vy
        self.on_ground = False
        self.ground_platform = None

        # Vertical collision
        for plat in platforms:
            if not getattr(plat, 'blocks_player', True):
                continue
            pr = self.rect
            if pr.colliderect(plat.rect):
                if self.vy > 0 or (self.vy == 0 and pr.bottom <= plat.rect.top + 5):
                    # Landing on top
                    bounciness = getattr(plat, 'bounciness', None)
                    if bounciness is not None:
                        self.vy = bounciness
                        self.on_ground = False
                        self.y = plat.rect.top - self.H - 1
                    else:
                        if hasattr(plat, 'breaking') and not plat.breaking:
                            plat.breaking = True
                        self.y = plat.rect.top - self.H
                        self.vy = 0
                        self.on_ground = True
                        self.jumps_left = 2
                        self.ground_platform = plat
                elif self.vy < 0:
                    # Hitting head on bottom
                    self.y = plat.rect.bottom
                    self.vy = 0

        if self.on_ground and self.ground_platform is not None:
            if getattr(self.ground_platform, 'axis', None) == 'horizontal':
                self.x += self.ground_platform.vx
                lw = level_width if level_width is not None else LEVEL_WIDTH
                self.x = max(0, min(self.x, lw - self.W))
                
                # Re-check horizontal collision if moving with platform
                for plat in platforms:
                    if plat is self.ground_platform or not getattr(plat, 'blocks_player', True):
                        continue
                    pr = self.rect
                    if pr.colliderect(plat.rect):
                        if self.ground_platform.vx > 0:
                            self.x = plat.rect.left - self.W
                        elif self.ground_platform.vx < 0:
                            self.x = plat.rect.right
                        
            elif getattr(self.ground_platform, 'axis', None) == 'vertical':
                self.y += self.ground_platform.vy

        if self.y > SCREEN_HEIGHT + 50:
            self.alive = False

        if self.on_ground and abs(self.vx) > 0.3 and self.knockback_timer == 0:
            self.walk_tick = (self.walk_tick + 1) % 24
        else:
            self.walk_tick = 0

        if self.attack_timer > 0:
            self.attack_timer -= 1
            self.attack_frame_tick = (self.attack_frame_tick + 1) % 12
            if self.attack_timer == 0:
                self.attacking = False
                self.attack_rect = None
                self.attack_frame_tick = 0

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        if self.invincible > 0:
            self.invincible -= 1
        if self.double_damage_timer > 0:
            self.double_damage_timer -= 1

    def _render_sprite_frame(self, surface, rx, ry, sprite):
        base_surface = None
        if sprite is not None:
            base_surface = sprite.copy()
        else:
            for mask in PLAYER_MASKS.values():
                if mask is not None:
                    base_surface = pygame.Surface(mask.get_size(), pygame.SRCALPHA)
                    break
            if base_surface is None:
                return False

        for part_name, color in [("skin", self.skin), ("hair", self.hair), ("shirt", self.shirt), ("pants", self.pants)]:
            mask = PLAYER_MASKS.get(part_name)
            if mask is not None:
                tinted = tint_surface(mask, color)
                if tinted is not None:
                    base_surface.blit(tinted, (0, 0))

        surface.blit(base_surface, (rx, ry))
        return True

    def draw(self, surface, cam_x):
        rx = int(self.x) - cam_x
        ry = int(self.y)

        # Flashing effect when invincible, but only if less than a second left or taking knockback
        if self.invincible > 0:
            if (self.invincible < 60 or self.knockback_timer > 0) and self.invincible % 6 < 3:
                return

        walking = self.on_ground and abs(self.vx) > 0.3
        sprite = None
        if self.attacking:
            frames = PLAYER_ATTACK.get(self.facing, [])
            sprite = _animation_frame(frames, self.attack_frame_tick // 6)
        elif not self.on_ground:
            sprite = PLAYER_JUMP if self.vy < 0 else PLAYER_FALL
        elif walking:
            frames = PLAYER_WALK.get(self.facing, [])
            sprite = _animation_frame(frames, self.walk_tick // 8)
        else:
            sprite = PLAYER_STAND.get(self.facing)

        if sprite is not None and self._render_sprite_frame(surface, rx, ry, sprite):
            w = self.weapon
            if w.name != "Fist" and w.color:
                if self.facing > 0:
                    wx = rx + 32
                else:
                    wx = rx - 4
                    
                angle = 0
                if self.attacking:
                    # Timer goes from 12 down to 0 (default attack timer)
                    progress = 1.0 - (self.attack_timer / 12.0)
                    # Swing from +90 degrees down to -45 degrees
                    swing = 90 - (progress * 135)
                    angle = -swing if self.facing > 0 else swing
                    
                w.draw(surface, wx, ry + 22, self.facing, angle)
            if self.attacking:
                if self.facing > 0:
                    arm_x = rx + 24
                else:
                    arm_x = rx - 4
                pygame.draw.rect(surface, self.skin, (arm_x, ry + 14, 8, 16))
            if self.attack_rect:
                ar = pygame.Rect(self.attack_rect.x - cam_x, self.attack_rect.y, self.attack_rect.w, self.attack_rect.h)
                s = pygame.Surface((ar.w, ar.h), pygame.SRCALPHA)
                s.fill((255, 255, 100, 60))
                surface.blit(s, (ar.x, ar.y))
            if self.double_damage_timer > 0:
                pygame.draw.circle(surface, ORANGE, (rx + self.W // 2, ry + self.H // 2), 25, 2)
            if self.invincible > 60:
                pygame.draw.circle(surface, YELLOW, (rx + self.W // 2, ry + self.H // 2), 28, 2)
            return

        shoulder_rect = pygame.Rect(rx + 4, ry + 18, 20, 10)
        body_rect = pygame.Rect(rx + 6, ry + 28, 16, 16)
        arm_left = pygame.Rect(rx - 4, ry + 18, 8, 16)
        arm_right = pygame.Rect(rx + 24, ry + 18, 8, 16)

        if walking:
            walk_phase = self.walk_tick < 8
            left_leg = (rx + 6, ry + (32 if walk_phase else 30), 7, 14)
            right_leg = (rx + 15, ry + (30 if walk_phase else 32), 7, 14)
        else:
            left_leg = (rx + 6, ry + 30, 7, 16)
            right_leg = (rx + 15, ry + 30, 7, 16)

        pygame.draw.rect(surface, self.pants, left_leg)
        pygame.draw.rect(surface, self.pants, right_leg)
        pygame.draw.rect(surface, self.shirt, shoulder_rect)
        pygame.draw.rect(surface, self.shirt, body_rect)
        pygame.draw.rect(surface, self.skin, arm_left)
        pygame.draw.rect(surface, self.skin, arm_right)
        pygame.draw.circle(surface, self.skin, (rx + 14, ry + 8), 10)
        pygame.draw.rect(surface, self.hair, (rx + 4, ry, 20, 7))

        ex = rx + 18 if self.facing > 0 else rx + 4
        pygame.draw.circle(surface, WHITE, (ex, ry + 8), 3)
        pygame.draw.circle(surface, BLACK, (ex + 1, ry + 8), 1)

        w = self.weapon
        if w.name != "Fist" and w.color:
            if self.facing > 0:
                wx = rx + 32
            else:
                wx = rx - 4
                
            angle = 0
            if self.attacking:
                progress = 1.0 - (self.attack_timer / 12.0)
                swing = 90 - (progress * 135)
                angle = -swing if self.facing > 0 else swing
                
            w.draw(surface, wx, ry + 22, self.facing, angle)
        if self.attacking:
            if self.facing > 0:
                arm_x = rx + 24
            else:
                arm_x = rx - 4
            pygame.draw.rect(surface, self.skin, (arm_x, ry + 14, 8, 16))

        if self.attack_rect:
            ar = pygame.Rect(self.attack_rect.x - cam_x, self.attack_rect.y, self.attack_rect.w, self.attack_rect.h)
            s = pygame.Surface((ar.w, ar.h), pygame.SRCALPHA)
            s.fill((255, 255, 100, 60))
            surface.blit(s, (ar.x, ar.y))
            
        if self.double_damage_timer > 0:
            pygame.draw.circle(surface, ORANGE, (rx + self.W // 2, ry + self.H // 2), 25, 2)
        if self.invincible > 60:
            pygame.draw.circle(surface, YELLOW, (rx + self.W // 2, ry + self.H // 2), 28, 2)
