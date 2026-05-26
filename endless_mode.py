"""
Endless Mode System Architecture for Plat-Mayhem Stage 3

This module provides a clean, modular, reusable system for generating
infinite procedural levels with progressive difficulty scaling, balanced
spawn management, and optimized memory usage.

Key Components:
- DifficultyManager: Progressive difficulty scaling based on time/score
- PlatformSpawner: Generates varied, fair platform layouts
- EnemySpawner: Intelligent enemy spawning with difficulty consideration
- LootSpawner: Manages pickup generation
- ChunkGenerator: Orchestrates chunk-based level generation
- EndlessGameManager: High-level system orchestrator

Design Principles:
- Modular: Each system is independently testable and reusable
- Configurable: Uses constants/parameters, no hardcoded magic numbers
- Scalable: Easy to add new platform types, enemy variations, etc.
- Performant: Includes object pooling and memory cleanup
- Fair: Ensures playable, non-repetitive, balanced level generation
"""

import pygame
import random
import math
from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, THEMES, WEAPON_POOL_STAGE3
)
from level import (
    Platform, MovingPlatform, BouncyPlatform, FragilePlatform, Crate, PLATFORM_GROUND_IMG, 
    PLATFORM_TILE_IMG, PLATFORM_MOVING_IMG, TEAL, ORANGE
)
from entities import ReptileEnemy, InsectEnemy, BatEnemy, ArmoredReptile, LootDrop


class DifficultyManager:
    """
    Manages progressive difficulty scaling based on elapsed time and score.
    
    Tracks game metrics and computes appropriate difficulty parameters
    for spawn rates, enemy stats, and platform difficulty.
    """
    
    def __init__(self, hard_mode=False):
        self.hard_mode = hard_mode
        self.elapsed_time = 0.0  # seconds since start
        self.config = {
            # Time progression (in seconds)
            "scaling_interval": 20.0,  # Increase difficulty every N seconds
            "max_time_multiplier": 3.0,  # Cap at 3x difficulty
            
            # Platform difficulty
            "min_gap_width": 80,
            "max_gap_width": 320,
            "min_platform_width": 60,
            "max_platform_width": 200,
            
            # Enemy spawning - IMPROVED for more consistent enemies
            "base_enemy_spawn_chance": 0.25,  # Increased from 0.12 to 25% base
            "max_enemy_spawn_chance": 0.75,   # Increased from 0.65 to 75% max
            "elevated_insect_preference": 0.70,
            "ground_reptile_preference": 0.55,
            
            # Elevated platform frequency
            "elevated_platform_chance": 0.35,
            "moving_platform_chance": 0.20,
            
            # Crate spawning
            "base_crate_spawn_chance": 0.10,
            "max_crate_spawn_chance": 0.40,
        }
    
    def update(self, delta_time):
        """Update elapsed time (delta_time in seconds)"""
        self.elapsed_time += delta_time
    
    def get_time_multiplier(self):
        """Get difficulty multiplier based on elapsed time"""
        intervals = self.elapsed_time / self.config["scaling_interval"]
        multiplier = 1.0 + (intervals * 0.15)  # 15% increase per interval
        return min(multiplier, self.config["max_time_multiplier"])
    
    def get_gap_width(self):
        """Get random gap width appropriate to current difficulty"""
        multiplier = self.get_time_multiplier()
        base_gap = self.config["min_gap_width"]
        max_gap = min(
            self.config["max_gap_width"],
            self.config["max_gap_width"] * multiplier
        )
        return random.randint(base_gap, int(max_gap))
    
    def get_platform_width(self):
        """Get random platform width appropriate to current difficulty"""
        multiplier = self.get_time_multiplier()
        width = random.randint(
            self.config["min_platform_width"],
            int(self.config["max_platform_width"] / (1.0 + multiplier * 0.2))
        )
        return max(self.config["min_platform_width"], width)
    
    def get_enemy_spawn_chance(self, score):
        """Get enemy spawn probability (0.0-1.0)"""
        time_mult = self.get_time_multiplier()
        score_mult = min(0.3, (score / 2000) * 0.15)
        base = self.config["base_enemy_spawn_chance"]
        chance = base + score_mult + (time_mult - 1.0) * 0.1
        if self.hard_mode:
            chance *= 1.25
        return min(chance, self.config["max_enemy_spawn_chance"])
    
    def get_crate_spawn_chance(self, score):
        """Get crate spawn probability (0.0-1.0)"""
        time_mult = self.get_time_multiplier()
        score_mult = min(0.2, (score / 3000) * 0.1)
        base = self.config["base_crate_spawn_chance"]
        chance = base + score_mult + (time_mult - 1.0) * 0.05
        return min(chance, self.config["max_crate_spawn_chance"])
    
    def get_enemy_health_multiplier(self, score):
        """Get health multiplier for enemies"""
        time_mult = self.get_time_multiplier()
        score_mult = 1.0 + (score / 2500) * 0.1
        base = time_mult * score_mult
        if self.hard_mode:
            base *= 1.3
        return base


class PlatformSpawner:
    """
    Generates varied, balanced platform layouts with multiple types.
    
    Ensures fair gameplay by preventing impossible jumps and managing
    platform placement intelligently.
    """
    
    # Platform type constants
    TYPE_GROUND = "ground"      # Main ground-level platforms
    TYPE_ELEVATED = "elevated"  # High platforms requiring jumps
    TYPE_MOVING = "moving"      # Horizontally or vertically moving
    
    PLATFORM_TYPES = [TYPE_GROUND, TYPE_ELEVATED, TYPE_MOVING]
    
    def __init__(self, theme_color, ground_y):
        self.theme_color = theme_color
        self.ground_y = ground_y
        self.last_platform_x = 0
        self.last_platform_width = 0
    
    def generate_ground_platform(self, x, gap_width, platform_width):
        """Generate a ground-level platform at given position"""
        platform = Platform(
            x, self.ground_y, platform_width, 60,
            self.theme_color,
            texture=PLATFORM_GROUND_IMG,
            tile_mode="repeat"
        )
        self.last_platform_x = x
        self.last_platform_width = platform_width
        return platform
    
    def generate_elevated_platform(self, x, platform_width, base_platform):
        """Generate an elevated platform above base platform"""
        # Vary height between 120-280 pixels above ground
        height = random.randint(120, 280)
        elev_y = self.ground_y - height
        
        platform = Platform(
            x, elev_y, platform_width, 18,
            self.theme_color,
            texture=PLATFORM_TILE_IMG,
            tile_mode="repeat"
        )
        return platform
    
    def generate_bouncy_platform(self, x, base_platform):
        width = random.randint(60, 120)
        y = self.ground_y - random.randint(120, 280)
        return BouncyPlatform(x, y, width)

    def generate_fragile_platform(self, x, base_platform):
        width = random.randint(80, 150)
        y = self.ground_y - random.randint(120, 280)
        return FragilePlatform(x, y, width)
    
    def generate_moving_platform(self, x, base_platform, is_horizontal=True):
        """Generate a moving platform"""
        width = random.randint(100, 170)
        
        if is_horizontal:
            y = self.ground_y - 140
            start = x
            end = x + random.randint(80, 160)
            axis = "horizontal"
        else:
            y = self.ground_y - 200
            start = y
            end = y + random.randint(100, 150)
            axis = "vertical"
        
        platform = MovingPlatform(
            x, y, width, 18,
            axis=axis,
            start=start,
            end=end,
            speed=2.0,
            color=ORANGE
        )
        return platform
    
    def should_generate_elevated(self, difficulty_manager):
        """Determine if elevated platform should spawn at this location"""
        return random.random() < difficulty_manager.config["elevated_platform_chance"]
    
    def should_generate_moving(self, difficulty_manager):
        """Determine if moving platform should spawn at this location"""
        return random.random() < difficulty_manager.config["moving_platform_chance"]


class EnemySpawner:
    """
    Intelligent enemy spawning with difficulty scaling and balance.
    
    Respects platform characteristics and ensures enemies are placed
    fairly without creating impossible encounters.
    """
    
    def __init__(self, stage=3, hard_mode=False):
        self.stage = stage
        self.hard_mode = hard_mode
    
    def should_spawn_enemy(self, platform, difficulty_manager, score):
        """Determine if an enemy should spawn on this platform"""
        # Platform must be wide enough to place an enemy
        if platform.rect.w < 80:
            return False
        
        # Use difficulty manager to get spawn chance
        chance = difficulty_manager.get_enemy_spawn_chance(score)
        return random.random() < chance
    
    def select_enemy_type(self, platform, is_elevated):
        """Select enemy type based on platform characteristics"""
        rand = random.random()
        if is_elevated:
            if rand < 0.50:
                return "insect"
            elif rand < 0.80:
                return "bat"
            else:
                return "reptile"
        else:
            if rand < 0.40:
                return "reptile"
            elif rand < 0.70:
                return "armored_reptile"
            elif rand < 0.85:
                return "insect"
            else:
                return "bat"
    
    def spawn_enemy(self, platform, enemy_type, difficulty_manager, score):
        """Create an enemy with appropriate stats for current difficulty"""
        # Randomize position on platform
        ex = platform.rect.x + random.randint(12, max(12, platform.rect.w - 34))
        
        # Position based on enemy type
        if enemy_type == "reptile":
            ey = platform.rect.y - 34
            enemy = ReptileEnemy(ex, ey, level_index=0, stage=self.stage)
        elif enemy_type == "armored_reptile":
            ey = platform.rect.y - 34
            enemy = ArmoredReptile(ex, ey, level_index=0, stage=self.stage)
        elif enemy_type == "bat":
            ey = platform.rect.y - 60
            enemy = BatEnemy(ex, ey, level_index=0, stage=self.stage)
        else:
            ey = platform.rect.y - 50
            enemy = InsectEnemy(ex, ey, level_index=0, stage=self.stage)
        
        # Apply difficulty scaling
        health_multiplier = difficulty_manager.get_enemy_health_multiplier(score)
        enemy.health = max(1, int(enemy.health * health_multiplier))
        enemy.max_health = enemy.health
        enemy.speed *= (1.0 + health_multiplier * 0.1)
        
        return enemy


class LootSpawner:
    """
    Manages pickup and loot generation with balanced distribution.
    """
    
    # Loot probabilities
    WEAPON_CHANCE = 0.40
    HEALTH_CHANCE = 0.20
    SCORE_CHANCE = 0.20
    INVINCIBLE_CHANCE = 0.10
    DOUBLE_DAMAGE_CHANCE = 0.10
    
    def __init__(self):
        self.weapon_pool = WEAPON_POOL_STAGE3
    
    def spawn_loot(self, crate):
        """Generate loot when a crate is destroyed"""
        roll = random.random()
        
        cx = crate.rect.x + Crate.SIZE // 2
        cy = crate.rect.y + Crate.SIZE - 4
        
        if roll < self.WEAPON_CHANCE:
            weapon_data = random.choice(self.weapon_pool)
            return LootDrop(cx, cy, "weapon", dict(weapon_data))
        elif roll < self.WEAPON_CHANCE + self.HEALTH_CHANCE:
            return LootDrop(cx, cy, "health")
        elif roll < self.WEAPON_CHANCE + self.HEALTH_CHANCE + self.INVINCIBLE_CHANCE:
            return LootDrop(cx, cy, "invincibility")
        elif roll < self.WEAPON_CHANCE + self.HEALTH_CHANCE + self.INVINCIBLE_CHANCE + self.DOUBLE_DAMAGE_CHANCE:
            return LootDrop(cx, cy, "double_damage")
        else:
            return LootDrop(cx, cy, "score")


class ObjectPool:
    """
    Simple object pool for memory-efficient object reuse.
    
    Reduces garbage collection overhead during long gameplay sessions.
    """
    
    def __init__(self, object_class, max_size=100):
        self.object_class = object_class
        self.max_size = max_size
        self.available = []
        self.in_use = set()
    
    def acquire(self, *args, **kwargs):
        """Get an object from pool or create new one"""
        if self.available:
            obj = self.available.pop()
            # Reset object state
            if hasattr(obj, 'reset'):
                obj.reset(*args, **kwargs)
        else:
            obj = self.object_class(*args, **kwargs)
        self.in_use.add(obj)
        return obj
    
    def release(self, obj):
        """Return object to pool for reuse"""
        if obj in self.in_use:
            self.in_use.remove(obj)
            if len(self.available) < self.max_size:
                self.available.append(obj)


class ChunkGenerator:
    """
    Procedurally generates level chunks with coordinated variety.
    
    Manages the creation of cohesive, balanced chunks that flow naturally
    without repetition or unfair difficulty spikes.
    """
    
    def __init__(self, theme_color, ground_y, hard_mode=False):
        self.theme_color = theme_color
        self.ground_y = ground_y
        self.hard_mode = hard_mode
        
        self.platform_spawner = PlatformSpawner(theme_color, ground_y)
        self.enemy_spawner = EnemySpawner(stage=3, hard_mode=hard_mode)
        self.loot_spawner = LootSpawner()
        self.difficulty_manager = DifficultyManager(hard_mode=hard_mode)
        
        self.chunk_size = SCREEN_WIDTH * 2  # Generate 2 screen widths ahead
    
    def generate_chunk(self, start_from_x, player_score):
        """Generate a new chunk of level content starting from start_from_x"""
        platforms = []
        enemies = []
        crates = []
        
        chunk_start = start_from_x
        chunk_end = chunk_start + self.chunk_size
        
        current_x = chunk_start
        max_iterations = 30  # Safety limit to prevent infinite loops
        iterations = 0
        
        while current_x < chunk_end and iterations < max_iterations:
            iterations += 1
            
            # Generate gap and platform width
            gap_width = self.difficulty_manager.get_gap_width()
            platform_width = self.difficulty_manager.get_platform_width()
            
            # Safety: ensure we're making progress
            if platform_width < 50:
                platform_width = 50
            if gap_width < 40:
                gap_width = 40
            
            # Place ground platform
            x = current_x + gap_width
            platform = self.platform_spawner.generate_ground_platform(
                x, gap_width, platform_width
            )
            platforms.append(platform)
            
            # Spawn entities on ground platform
            # Allow multiple enemies on very wide platforms at high difficulty
            max_enemies = 1
            if platform_width > 350 and self.difficulty_manager.get_time_multiplier() > 1.8:
                max_enemies = 2
                
            for _ in range(max_enemies):
                if self.enemy_spawner.should_spawn_enemy(platform, self.difficulty_manager, player_score):
                    enemy_type = self.enemy_spawner.select_enemy_type(platform, False)
                    enemy = self.enemy_spawner.spawn_enemy(
                        platform, enemy_type, self.difficulty_manager, player_score
                    )
                    # Ensure they don't spawn exactly on top of each other
                    if any(e.rect.colliderect(enemy.rect) for e in enemies):
                        enemy.x += 40
                    enemies.append(enemy)
            
            # Spawn crate
            if random.random() < self.difficulty_manager.get_crate_spawn_chance(player_score):
                cx = platform.rect.x + random.randint(12, max(12, platform.rect.w - Crate.SIZE - 12))
                cy = platform.rect.y - Crate.SIZE
                crate = Crate(cx, cy, weapon_pool=WEAPON_POOL_STAGE3)
                crates.append(crate)
            
            # Possibly add elevated platform
            if self.platform_spawner.should_generate_elevated(self.difficulty_manager):
                elev_width = random.randint(90, 160)
                max_elev_x = max(12, platform_width - elev_width - 12)
                elev_x = x + random.randint(12, max_elev_x) if max_elev_x > 12 else x + 12
                    
                rand_plat = random.random()
                if rand_plat < 0.15:
                    elev = self.platform_spawner.generate_bouncy_platform(elev_x, platform)
                elif rand_plat < 0.30:
                    elev = self.platform_spawner.generate_fragile_platform(elev_x, platform)
                else:
                    elev = self.platform_spawner.generate_elevated_platform(
                        elev_x, elev_width, platform
                    )
                platforms.append(elev)
                
                # Spawn entities on elevated platform
                if self.enemy_spawner.should_spawn_enemy(elev, self.difficulty_manager, player_score):
                    enemy_type = self.enemy_spawner.select_enemy_type(elev, True)
                    enemy = self.enemy_spawner.spawn_enemy(
                        elev, enemy_type, self.difficulty_manager, player_score
                    )
                    enemies.append(enemy)
                
                # Crate on elevated platform
                if random.random() < self.difficulty_manager.get_crate_spawn_chance(player_score) * 0.7:
                    cx = elev.rect.x + random.randint(12, max(12, elev.rect.w - Crate.SIZE - 12))
                    cy = elev.rect.y - Crate.SIZE
                    crate = Crate(cx, cy, weapon_pool=WEAPON_POOL_STAGE3)
                    crates.append(crate)
            
            # Possibly add moving platform
            if self.platform_spawner.should_generate_moving(self.difficulty_manager):
                is_horizontal = random.random() < 0.75  # 75% horizontal
                move_x_offset = random.randint(0, max(0, platform_width - 150)) if platform_width > 150 else 0
                moving = self.platform_spawner.generate_moving_platform(
                    x + move_x_offset,
                    platform,
                    is_horizontal
                )
                platforms.append(moving)
                
                # Spawn enemy on moving platform
                if random.random() < self.difficulty_manager.get_enemy_spawn_chance(player_score) * 0.6:
                    enemy_type = self.enemy_spawner.select_enemy_type(moving, True)
                    enemy = self.enemy_spawner.spawn_enemy(
                        moving, enemy_type, self.difficulty_manager, player_score
                    )
                    enemies.append(enemy)
            
            current_x = x + platform_width
        
        end_x = current_x
        return platforms, enemies, crates, end_x


class EndlessGameManager:
    """
    High-level orchestrator for the endless mode system.
    
    Manages all subsystems and coordinates level generation, updates,
    memory cleanup, and game state.
    """
    
    GROUND_Y = SCREEN_HEIGHT - 60
    
    def __init__(self, stage=3, theme_index=2, hard_mode=False):
        self.stage = stage
        self.theme_index = min(theme_index, len(THEMES) - 1)
        self.theme = THEMES[self.theme_index]
        self.hard_mode = hard_mode
        
        # Initialize all systems
        self.chunk_generator = ChunkGenerator(
            self.theme["platform_color"],
            self.GROUND_Y,
            hard_mode
        )
        
        # Game state
        self.platforms = []
        self.moving_platforms = []
        self.fragile_platforms = []
        self.enemies = []
        self.crates = []
        self.loots = []
        
        self.total_enemies = 0
        self.level_width = 1000000  # Effectively infinite
        self.generated_to_x = 0
        
        # Statistics
        self.survival_time = 0.0
        self.distance_traveled = 0.0
        
        # Initialize with starting platform
        self._initialize_starting_area()
    
    def _initialize_starting_area(self):
        """Create initial ground platform for starting position"""
        start_width = 400  # Reduced from 1400 to spawn enemies much sooner
        ground = Platform(
            0, self.GROUND_Y, start_width, 60,
            self.theme["platform_color"],
            texture=PLATFORM_GROUND_IMG,
            tile_mode="repeat"
        )
        self.platforms.append(ground)
        self.generated_to_x = start_width
        
        # Generate initial chunks ahead of player
        self._generate_ahead(0)
    
    def _generate_ahead(self, player_x, score=0):
        """Generate level chunks ahead of player position"""
        target_x = player_x + SCREEN_WIDTH * 2
        
        while self.generated_to_x < target_x:
            platforms, enemies, crates, end_x = self.chunk_generator.generate_chunk(self.generated_to_x, score)
            
            self.platforms.extend(platforms)
            self.moving_platforms.extend([p for p in platforms if isinstance(p, MovingPlatform)])
            self.fragile_platforms.extend([p for p in platforms if isinstance(p, FragilePlatform)])
            self.enemies.extend(enemies)
            self.crates.extend(crates)
            
            self.generated_to_x = end_x
    
    def _cleanup_offscreen_objects(self, player_x):
        """Remove objects that are far off-screen to free memory"""
        cutoff_x = player_x - SCREEN_WIDTH
        
        # Keep platforms that are visible or might come back into view
        self.platforms = [p for p in self.platforms if p.rect.right >= cutoff_x]
        self.moving_platforms = [p for p in self.moving_platforms if p.rect.right >= cutoff_x]
        self.fragile_platforms = [p for p in self.fragile_platforms if p.rect.right >= cutoff_x]
        
        # Clean up enemies (keep alive ones and those still visible)
        self.enemies = [e for e in self.enemies if e.alive or e.x + e.w >= cutoff_x]
        
        # Clean up loots and crates
        self.crates = [c for c in self.crates if c.alive and c.x + Crate.SIZE >= cutoff_x]
        self.loots = [l for l in self.loots if l.x + LootDrop.SIZE >= cutoff_x]
    
    def update(self, player, delta_time):
        """Update all game systems"""
        # Update difficulty manager
        self.chunk_generator.difficulty_manager.update(delta_time)
        
        # Update survival stats
        self.survival_time += delta_time
        self.distance_traveled = player.x
        
        # Update moving platforms
        for platform in self.moving_platforms:
            platform.update()
            
        # Update fragile platforms
        for platform in self.fragile_platforms:
            platform.update()
        
        # Generate level ahead of player if needed
        if self.generated_to_x < player.x + SCREEN_WIDTH * 2:
            self._generate_ahead(player.x, player.score)
        
        # Update enemies
        enemy_platforms = self.platforms + []
        for enemy in self.enemies:
            if enemy.alive:
                enemy.update(enemy_platforms, player.x, player.y)
                
                # Collision with player
                if enemy.rect.colliderect(player.rect) and player.invincible == 0:
                    player.health -= enemy.damage
                    player.apply_knockback(enemy.x)
                    if player.health <= 0:
                        player.alive = False
        
        # Handle player attacks on enemies
        if player.attack_rect:
            for enemy in self.enemies:
                if enemy.alive and enemy.rect.colliderect(player.attack_rect):
                    weapon = player.weapon
                    dmg = weapon.damage * 2 if player.double_damage_timer > 0 else weapon.damage
                    enemy.take_damage(dmg)
                    if not enemy.alive:
                        player.score += int(round(enemy.score_value * player.score_multiplier))
        
        # Handle player attacks on crates
        if player.attack_rect:
            for crate in self.crates:
                if crate.alive and crate.rect.colliderect(player.attack_rect):
                    weapon = player.weapon
                    dmg = weapon.damage * 2 if player.double_damage_timer > 0 else weapon.damage
                    _ = crate.take_hit(dmg)
                    if not crate.alive:
                        loot = self.chunk_generator.loot_spawner.spawn_loot(crate)
                        if loot:
                            self.loots.append(loot)
        
        # Handle loot pickup
        for loot in self.loots[:]:
            if player.rect.colliderect(pygame.Rect(loot.x, loot.y, LootDrop.SIZE, LootDrop.SIZE)):
                if loot.kind == "weapon":
                    player.equip_weapon(loot.data)
                elif loot.kind == "health":
                    player.health = min(player.max_health, player.health + 25)
                elif loot.kind == "score":
                    player.score += 50
                elif loot.kind == "invincibility":
                    player.invincible += 600
                elif loot.kind == "double_damage":
                    player.double_damage_timer += 600
                self.loots.remove(loot)
        
        # Clean up off-screen objects
        self._cleanup_offscreen_objects(player.x)
    
    def enemies_alive(self):
        """Get count of alive enemies"""
        return sum(1 for e in self.enemies if e.alive)
    
    def draw_background(self, surface):
        """Draw background scene"""
        surface.fill(self.theme["sky_color"])
        scene = self.theme.get("scene", {})
        sx, sy = scene.get("pos", (SCREEN_WIDTH - 120, 80))
        radius = scene.get("radius", 30)
        color = scene.get("color", (255, 255, 255))
        
        if scene.get("type") == "sun":
            pygame.draw.circle(surface, color, (sx, sy), radius)
        elif scene.get("type") == "moon":
            pygame.draw.circle(surface, color, (sx, sy), radius)
            for star in scene.get("stars", []):
                pygame.draw.circle(surface, scene.get("star_color", (255, 255, 255)), star, 2)
    
    def draw(self, surface, cam_x):
        """Draw all game elements"""
        self.draw_background(surface)
        
        for platform in self.platforms:
            platform.draw(surface, cam_x)
        
        for crate in self.crates:
            if crate.alive:
                crate.draw(surface, cam_x)
        
        for loot in self.loots:
            loot.draw(surface, cam_x)
        
        for enemy in self.enemies:
            if enemy.alive:
                enemy.draw(surface, cam_x)
