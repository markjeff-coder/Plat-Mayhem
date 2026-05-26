import pygame
import os
import random
from constants import SCREEN_HEIGHT, SCREEN_WIDTH, LEVEL_WIDTH, LEVEL_TEMPLATES, THEMES, GOLD, GRAY, LGRAY, LBROWN, BROWN, RED, BLUE, WHITE, BLACK, WEAPON_POOL, WEAPON_POOL_STAGE3, ORANGE, TEAL
from entities import LootDrop, ReptileEnemy, InsectEnemy

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


def _tile_texture(surface, texture, rx, y, width):
    if texture is None:
        return False
    tile_w = texture.get_width()
    if tile_w <= 0:
        return False
    x = rx
    end_x = rx + width
    while x < end_x:
        surface.blit(texture, (x, y))
        x += tile_w
    return True


CRATE_IMG = load_image_scaled("Crate.png", (36, 36))
DOOR_LOCKED_IMG = load_image_scaled("DoorLocked.png", (50, 80))
DOOR_OPEN_IMG = load_image_scaled("DoorOpen.png", (50, 80))
LOOT_IMAGES = {
    "weapon": load_image_scaled("LootWeapon.png", (18, 18)),
    "health": load_image_scaled("LootHealth.png", (18, 18)),
    "score": load_image_scaled("LootScore.png", (18, 18)),
}
PLATFORM_TILE_IMG = load_image("PlatformTile.png")
PLATFORM_GROUND_IMG = load_image("PlatformGround.png")
PLATFORM_MOVING_IMG = load_image("PlatformMoving.png")


class Platform:
    def __init__(self, x, y, w, h=18, color=None, texture=None, tile_mode=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = color or (80, 120, 60)
        self.texture = texture
        self.tile_mode = tile_mode
        self.blocks_player = True
        self.blocks_enemy = True
        self.is_solid_ground = True

    def draw(self, surface, cam_x):
        rx = self.rect.x - cam_x
        if self.texture is not None and _tile_texture(surface, self.texture, rx, self.rect.y, self.rect.w):
            pygame.draw.rect(surface, BLACK, (rx, self.rect.y, self.rect.w, self.rect.h), 2)
            return
        pygame.draw.rect(surface, self.color, (rx, self.rect.y, self.rect.w, self.rect.h))
        pygame.draw.rect(surface, BLACK, (rx, self.rect.y, self.rect.w, self.rect.h), 2)


class Barrier(Platform):
    def __init__(self, x, y, w, h=12, side=None, color=(40, 40, 40)):
        super().__init__(x, y, w, h, color=color)
        self.blocks_player = False
        self.blocks_enemy = True
        self.is_solid_ground = False
        self.side = side

    def draw(self, surface, cam_x):
        rx = self.rect.x - cam_x
        # Draw a visible small wall/curb on the platform edge
        pygame.draw.rect(surface, self.color, (rx, self.rect.y, self.rect.w, self.rect.h))
        pygame.draw.rect(surface, BLACK, (rx, self.rect.y, self.rect.w, self.rect.h), 2)


class MovingPlatform(Platform):
    # Horizontal moving platforms use `start` and `end` as left-edge bounds.
    # Stage 2 templates must keep these paths fully inside the hole width
    # they cover, never extending past the cliff corner.
    def __init__(self, x, y, w, h=18, axis="horizontal", start=0, end=0, speed=2, color=None):
        super().__init__(x, y, w, h, color or ORANGE, texture=PLATFORM_MOVING_IMG, tile_mode="repeat")
        self.axis = axis
        self.start = start
        self.end = end
        self.speed = speed
        self.direction = 1
        self.vx = speed if axis == "horizontal" else 0
        self.vy = speed if axis == "vertical" else 0

    def update(self):
        if self.axis == "horizontal":
            self.rect.x += self.vx * self.direction
            if self.direction > 0 and self.rect.x >= self.end:
                self.rect.x = self.end
                self.direction = -1
            elif self.direction < 0 and self.rect.x <= self.start:
                self.rect.x = self.start
                self.direction = 1
            self.vx = self.speed * self.direction
            self.vy = 0
        else:
            self.rect.y += self.vy * self.direction
            if self.direction > 0 and self.rect.y >= self.end:
                self.rect.y = self.end
                self.direction = -1
            elif self.direction < 0 and self.rect.y <= self.start:
                self.rect.y = self.start
                self.direction = 1
            self.vy = self.speed * self.direction
            self.vx = 0

        if hasattr(self, "barriers"):
            for barrier in self.barriers:
                # keep barrier sitting on top edge of moving platform
                barrier.rect.y = self.rect.y - barrier.rect.height
                if barrier.side == "left":
                    barrier.rect.x = self.rect.left - barrier.rect.width
                else:
                    barrier.rect.x = self.rect.right


class Crate:
    SIZE = 36

    def __init__(self, x, y, weapon_pool=None):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x, y, self.SIZE, self.SIZE)
        self.health = 3
        self.alive = True
        self.weapon_pool = weapon_pool

    def take_hit(self):
        self.health -= 1
        if self.health <= 0:
            self.alive = False
            return self._drop_loot()
        return None

    def _drop_loot(self):
        roll = random.random()
        cx = self.x + self.SIZE // 2
        cy = self.y + self.SIZE - 4
        if roll < 0.50:
            wdata = random.choice(self.weapon_pool or WEAPON_POOL)
            return LootDrop(cx, cy, "weapon", dict(wdata))
        elif roll < 0.75:
            return LootDrop(cx, cy, "health")
        else:
            return LootDrop(cx, cy, "score")

    def draw(self, surface, cam_x):
        rx = self.x - cam_x
        if CRATE_IMG is not None:
            surface.blit(CRATE_IMG, (rx, self.y))
            return
        pygame.draw.rect(surface, LBROWN, (rx, self.y, self.SIZE, self.SIZE))
        pygame.draw.rect(surface, BLACK, (rx, self.y, self.SIZE, self.SIZE), 2)
        cx = rx + self.SIZE // 2
        cy = self.y + self.SIZE // 2
        pygame.draw.line(surface, BROWN, (rx, self.y), (rx + self.SIZE, self.y + self.SIZE), 2)
        pygame.draw.line(surface, BROWN, (rx + self.SIZE, self.y), (rx, self.y + self.SIZE), 2)
        pygame.draw.rect(surface, LGRAY, (cx - 5, cy - 5, 10, 10))
        pygame.draw.rect(surface, BLACK, (cx - 5, cy - 5, 10, 10), 1)
        for i in range(self.health):
            pygame.draw.circle(surface, RED, (rx + 6 + i * 10, self.y + 4), 3)


class Door:
    W = 50
    H = 80

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x, y, self.W, self.H)
        self.active = False

    def draw(self, surface, cam_x):
        rx = self.x - cam_x
        img = DOOR_OPEN_IMG if self.active else DOOR_LOCKED_IMG
        if img is not None:
            surface.blit(img, (rx, self.y))
            return
        color = GOLD if self.active else GRAY
        pygame.draw.rect(surface, color, (rx, self.y, self.W, self.H))
        pygame.draw.rect(surface, BLACK, (rx, self.y, self.W, self.H), 3)
        pygame.draw.circle(surface, BLACK, (rx + self.W - 10, self.y + self.H // 2), 5)
        font = pygame.font.SysFont(None, 18)
        label = "EXIT" if self.active else "LOCKED"
        txt = font.render(label, True, BLACK)
        surface.blit(txt, (rx + self.W // 2 - txt.get_width() // 2, self.y + 4))


class Level:
    GROUND_Y = SCREEN_HEIGHT - 60

    def __init__(self, template=None, theme=None, theme_index=0, level_index=0):
        self.platforms = []
        self.moving_platforms = []
        self.barriers = []
        self.enemies = []
        self.crates = []
        self.loots = []
        self.door = None
        self.total_enemies = 0
        self.template = template or LEVEL_TEMPLATES[0]
        self.stage = self.template.get("stage", 1)
        self.theme_index = theme_index
        self.level_index = level_index
        self.theme = theme or THEMES[self.theme_index]
        self.level_width = self.template.get("width", LEVEL_WIDTH)
        self._build()

    def _build(self):
        gy = self.GROUND_Y
        for x, y, w in self.template["platforms"]:
            height = 60 if y == gy else 18
            color = self.theme["platform_color"]
            texture = PLATFORM_GROUND_IMG if height > 18 or y >= self.GROUND_Y - 4 else PLATFORM_TILE_IMG
            platform = Platform(x, y, w, height, color, texture=texture, tile_mode="repeat")
            self.platforms.append(platform)
            # Side wall barriers removed: no left/right barrier objects created

        for mp in self.template.get("moving_platforms", []):
            axis = mp.get("axis", "horizontal")
            height = mp.get("height", 18)
            color = mp.get("color") or (TEAL if axis == "horizontal" else ORANGE)
            moving = MovingPlatform(
                mp["x"], mp["y"], mp["width"], height,
                axis=axis,
                start=mp["start"],
                end=mp["end"],
                speed=mp["speed"],
                color=color,
            )
            self.moving_platforms.append(moving)
            self.platforms.append(moving)
            # No side wall barriers for moving platforms either

        self.weapon_pool = self.template.get("weapon_pool", WEAPON_POOL)

        for ex, ey, etype in self.template["enemies"]:
            if etype == "reptile":
                self.enemies.append(ReptileEnemy(ex, ey, self.level_index, stage=self.stage))
            else:
                self.enemies.append(InsectEnemy(ex, ey, self.level_index, stage=self.stage))

        self.total_enemies = len(self.enemies)
        for crate in self.template["crates"]:
            if isinstance(crate, tuple):
                cx, cy = crate
            else:
                cx, cy = crate, gy - Crate.SIZE
            self.crates.append(Crate(cx, cy, weapon_pool=self.weapon_pool))

        door_x, door_y = self.template["door"]
        if door_y is None:
            door_y = gy - Door.H
        self.door = Door(door_x, door_y)

    def enemies_alive(self):
        return sum(1 for e in self.enemies if e.alive)

    def update(self, player, delta_time=None):
        """Update level (delta_time is optional, for compatibility with EndlessLevel)"""
        for moving in self.moving_platforms:
            moving.update()

        # door activation will be computed after enemy updates and attack processing

        enemy_platforms = self.platforms + self.barriers
        for e in self.enemies:
            if e.alive:
                e.update(enemy_platforms, player.x, player.y)
                if e.rect.colliderect(player.rect) and player.invincible == 0:
                    player.health -= e.damage
                    player.apply_knockback(e.x)
                    if player.health <= 0:
                        player.alive = False

        if player.attack_rect:
            for e in self.enemies:
                if e.alive and e.rect.colliderect(player.attack_rect):
                    w = player.weapon
                    e.take_damage(w.damage)
                    if not e.alive:
                        player.score += e.score_value

        if player.attack_rect:
            for c in self.crates:
                if c.alive and c.rect.colliderect(player.attack_rect):
                    loot = c.take_hit()
                    if loot:
                        self.loots.append(loot)

        for loot in self.loots[:]:
            if player.rect.colliderect(pygame.Rect(loot.x, loot.y, loot.SIZE, loot.SIZE)):
                if loot.kind == "weapon":
                    player.equip_weapon(loot.data)
                elif loot.kind == "health":
                    player.health = min(player.max_health, player.health + 25)
                elif loot.kind == "score":
                    player.score += 50
                self.loots.remove(loot)

        # Recompute alive enemies after updates and attack processing so fallen
        # reptiles (which set `alive=False` when they fall) count toward objectives
        alive_count = self.enemies_alive()
        self.door.active = alive_count == 0

    def draw_background(self, surface, theme_index):
        theme = THEMES[theme_index]
        surface.fill(theme["sky_color"])
        scene = theme.get("scene", {})
        sx, sy = scene.get("pos", (SCREEN_WIDTH - 120, 80))
        radius = scene.get("radius", 30)
        color = scene.get("color", WHITE)
        if scene.get("type") == "sun":
            pygame.draw.circle(surface, color, (sx, sy), radius)
        elif scene.get("type") == "moon":
            pygame.draw.circle(surface, color, (sx, sy), radius)
            for star in scene.get("stars", []):
                pygame.draw.circle(surface, scene.get("star_color", WHITE), star, 2)

    def draw(self, surface, cam_x):
        self.draw_background(surface, self.theme_index)
        for p in self.platforms:
            p.draw(surface, cam_x)
        for b in self.barriers:
            b.draw(surface, cam_x)
        for c in self.crates:
            if c.alive:
                c.draw(surface, cam_x)
        for loot in self.loots:
            loot.draw(surface, cam_x)
        for e in self.enemies:
            if e.alive:
                e.draw(surface, cam_x)
        self.door.draw(surface, cam_x)


class EndlessLevel:
    """
    Wrapper for the new modular endless mode system.
    
    This class maintains the same interface as the old implementation
    but uses the new EndlessGameManager for superior architecture,
    difficulty scaling, and performance.
    """
    
    GROUND_Y = SCREEN_HEIGHT - 60

    def __init__(self, stage=3, theme_index=2, hard_mode=False):
        from endless_mode import EndlessGameManager
        
        self.stage = stage
        self.theme_index = theme_index if theme_index < len(THEMES) else 0
        self.theme = THEMES[self.theme_index]
        self.hard_mode = hard_mode
        
        # Use the new modular system
        self.manager = EndlessGameManager(stage, self.theme_index, hard_mode)
        
        # Expose attributes for compatibility
        self.barriers = []
        self.level_width = self.manager.level_width
        self.total_enemies = 0
    
    @property
    def platforms(self):
        """Proxy to manager's platforms"""
        return self.manager.platforms
    
    @property
    def moving_platforms(self):
        """Proxy to manager's moving platforms"""
        return self.manager.moving_platforms
    
    @property
    def enemies(self):
        """Proxy to manager's enemies"""
        return self.manager.enemies
    
    @property
    def crates(self):
        """Proxy to manager's crates"""
        return self.manager.crates
    
    @property
    def loots(self):
        """Proxy to manager's loots"""
        return self.manager.loots
    
    def enemies_alive(self):
        """Get count of alive enemies"""
        return self.manager.enemies_alive()
    
    def update(self, player, delta_time=1.0/60.0):
        """Update game state (delta_time in seconds, default 60 FPS)"""
        self.manager.update(player, delta_time)
    
    def draw(self, surface, cam_x):
        """Draw all game elements"""
        self.manager.draw(surface, cam_x)


class LevelManager:
    def __init__(self, level_data_list, theme_list=None):
        self.level_data_list = level_data_list
        self.theme_list = theme_list if theme_list is not None else THEMES
        self.current_index = 0
        self.current_level = None

    def load_level(self, index):
        if index < 0 or index >= len(self.level_data_list):
            raise IndexError("Level index out of range")
        self.current_index = index
        theme = self.theme_list[self.current_index]
        self.current_level = Level(self.level_data_list[index], theme, self.current_index, index)
        return self.current_level

    def next_level(self):
        return self.load_level(self.current_index + 1) if self.current_index + 1 < len(self.level_data_list) else None


def fade_transition(screen, clock, duration=400):
    fade = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    fade.fill((0, 0, 0))
    steps = 12
    delay = duration // steps
    for step in range(steps):
        alpha = int(255 * (step + 1) / steps)
        fade.set_alpha(alpha)
        screen.blit(fade, (0, 0))
        pygame.display.flip()
        pygame.time.delay(delay)
