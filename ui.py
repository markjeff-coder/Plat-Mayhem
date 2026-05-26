import pygame
import sys
import os
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, GOLD, WHITE, BLACK, DGRAY, LGRAY, GRAY, GREEN, RED, YELLOW
from entities import Player

AUDIO_DIR = os.path.join(os.path.dirname(__file__), "musicNsound")
_CURRENT_MUSIC_FILE = None


def _music_path(filename):
    if not filename:
        return None
    path = os.path.join(AUDIO_DIR, filename)
    return path if os.path.isfile(path) else None


def stop_music():
    try:
        pygame.mixer.music.stop()
    except Exception:
        pass


def play_music(filename, volume=0.6):
    global _CURRENT_MUSIC_FILE
    path = _music_path(filename)
    if path is None:
        return
    try:
        if _CURRENT_MUSIC_FILE == filename and pygame.mixer.music.get_busy():
            pygame.mixer.music.set_volume(volume)
            return
        pygame.mixer.music.stop()
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(-1)
        _CURRENT_MUSIC_FILE = filename
    except Exception:
        pass


class UI:
    def __init__(self):
        self.font_big = pygame.font.SysFont(None, 28)
        self.font_small = pygame.font.SysFont(None, 20)

    def draw(self, surface, player, total_enemies, enemies_left):
        bx, by, bw, bh = 14, 14, 180, 18
        pygame.draw.rect(surface, DGRAY, (bx, by, bw, bh))
        fill = int(bw * max(0, player.health / player.max_health))
        hp_col = RED if player.health < 30 else (220, 180, 0) if player.health < 60 else (50, 200, 80)
        pygame.draw.rect(surface, hp_col, (bx, by, fill, bh))
        pygame.draw.rect(surface, WHITE, (bx, by, bw, bh), 2)
        hp_txt = self.font_small.render(f"HP  {player.health}/{player.max_health}", True, WHITE)
        surface.blit(hp_txt, (bx + 4, by + 2))

        sc = self.font_big.render(f"Score: {player.score}", True, WHITE)
        surface.blit(sc, (14, 40))

        ec = self.font_small.render(f"Enemies: {enemies_left}/{total_enemies}", True, YELLOW)
        surface.blit(ec, (14, 66))

        if getattr(player, "stage", None) == 3:
            multiplier = getattr(player, "score_multiplier", 1.0)
            mult_txt = self.font_small.render(f"Multiplier: x{multiplier:.1f}", True, WHITE)
            surface.blit(mult_txt, (14, 90))

        for i, slot in enumerate(player.slots):
            sx = SCREEN_WIDTH - 170 + i * 85
            sy = 14
            pygame.draw.rect(surface, (60, 60, 80), (sx, sy, 78, 44))
            border = GOLD if i == player.active_slot else DGRAY
            pygame.draw.rect(surface, border, (sx, sy, 78, 44), 2)
            label = f"[{i+1}]"
            lt = self.font_small.render(label, True, LGRAY)
            surface.blit(lt, (sx + 4, sy + 2))
            if slot and not slot.is_broken():
                name_t = self.font_small.render(slot.name, True, WHITE)
                surface.blit(name_t, (sx + 4, sy + 18))
                dur = "∞" if slot.durability is None else str(slot.durability)
                dur_t = self.font_small.render(f"Dur:{dur}", True, LGRAY)
                surface.blit(dur_t, (sx + 4, sy + 30))
            else:
                empty = self.font_small.render("Empty", True, GRAY)
                surface.blit(empty, (sx + 12, sy + 14))

        hints = "A/D Move  |  Space Jump  |  LClick Attack  |  1/2 Swap Weapon"
        ht = self.font_small.render(hints, True, (160, 160, 160))
        surface.blit(ht, (SCREEN_WIDTH // 2 - ht.get_width() // 2, SCREEN_HEIGHT - 20))


def run_customization(screen, clock, stage=None):
    play_music("ScreenBGmusic.mp3", volume=0.6)
    font_title = pygame.font.SysFont(None, 52)
    font_cat = pygame.font.SysFont(None, 28)
    font_btn = pygame.font.SysFont(None, 36)
    font_small = pygame.font.SysFont(None, 16)

    categories = [
        ["Skin", [255, 220, 170]],
        ["Hair", [40, 30, 20]],
        ["Shirt", [50, 80, 200]],
        ["Pants", [40, 40, 100]],
    ]

    START_X = 40
    START_Y = 120
    ROW_H = 135
    SLIDER_W = 280
    SLIDER_H = 16
    SLIDER_GAP = 12
    LABEL_W = 50
    SWATCH_SIZE = 24
    PREVIEW_X = 520
    PREVIEW_Y = START_Y
    PREVIEW_BOX_W = 240
    PREVIEW_BOX_H = 300
    btn_rect = pygame.Rect(PREVIEW_X + PREVIEW_BOX_W // 2 - 90, PREVIEW_Y + PREVIEW_BOX_H + 10, 180, 50)
    back_rect = pygame.Rect(btn_rect.x, btn_rect.y + btn_rect.h + 12, btn_rect.w, 48)
    hard_mode_rect = pygame.Rect(btn_rect.x, back_rect.y + back_rect.h + 12, btn_rect.w, 36)
    hard_mode = False

    visible_height = SCREEN_HEIGHT - START_Y - 40
    content_height = len(categories) * ROW_H
    LEFT_PANEL_WIDTH = SLIDER_W + LABEL_W + 90
    scroll_area_rect = pygame.Rect(START_X, START_Y, LEFT_PANEL_WIDTH, visible_height)
    scroll_offset = 0
    slider_rects = []
    active_slider = None

    def draw_preview(surf, cx, cy, skin, hair, shirt, pants):
        preview = Player(cx - Player.W // 2, cy - Player.H // 2 + 20, skin, hair, shirt, pants, stage=1)
        preview.slots = [None, None]
        preview.active_slot = 0
        preview.draw(surf, 0)

    def draw_button(rect, text, hovered, active=True):
        color = GREEN if active else DGRAY
        if hovered and active:
            color = LGRAY
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, WHITE, rect, 2)
        label = font_btn.render(text, True, BLACK if active else LGRAY)
        screen.blit(label, (rect.x + rect.w // 2 - label.get_width() // 2, rect.y + rect.h // 2 - label.get_height() // 2))

    def clamp_color(value):
        return max(0, min(255, int(value)))

    def slider_value_to_x(value, x):
        return x + int((SLIDER_W - 10) * value / 255)

    def draw_slider(surf, x, y, value, color):
        track = pygame.Rect(x, y, SLIDER_W, SLIDER_H)
        pygame.draw.rect(surf, (50, 50, 60), track)
        fill = pygame.Rect(x, y, slider_value_to_x(value, x) - x, SLIDER_H)
        pygame.draw.rect(surf, color, fill)
        pygame.draw.rect(surf, WHITE, track, 2)
        knob_x = slider_value_to_x(value, x)
        pygame.draw.circle(surf, WHITE, (knob_x, y + SLIDER_H // 2), 8)
        pygame.draw.circle(surf, BLACK, (knob_x, y + SLIDER_H // 2), 4)
        return track

    def clamp_scroll(offset):
        min_offset = min(0, visible_height - content_height)
        return max(min_offset, min(0, offset))

    def get_colors():
        return tuple(tuple(cat[1]) for cat in categories)

    running = True
    while running:
        screen.fill((20, 22, 35))
        t = font_title.render("Customize Your Character", True, GOLD)
        screen.blit(t, (SCREEN_WIDTH // 2 - t.get_width() // 2, 30))
        sub = font_cat.render("Use the RGB sliders to choose each color", True, LGRAY)
        screen.blit(sub, (SCREEN_WIDTH // 2 - sub.get_width() // 2, 88))

        pygame.draw.rect(screen, (25, 28, 40), scroll_area_rect)
        pygame.draw.rect(screen, WHITE, scroll_area_rect, 2)

        slider_rects.clear()
        scroll_offset = clamp_scroll(scroll_offset)
        old_clip = screen.get_clip()
        screen.set_clip(scroll_area_rect)
        for ci, (cat_name, rgb) in enumerate(categories):
            base_y = START_Y + ci * ROW_H + scroll_offset
            label = font_cat.render(cat_name + ":", True, WHITE)
            screen.blit(label, (START_X, base_y))

            swatch_x = START_X + label.get_width() + 12
            swatch_y = base_y + 2
            swatch_rect = pygame.Rect(swatch_x, swatch_y, SWATCH_SIZE, SWATCH_SIZE)
            pygame.draw.rect(screen, tuple(rgb), swatch_rect)
            pygame.draw.rect(screen, WHITE, swatch_rect, 2)

            for channel, channel_name in enumerate(["R", "G", "B"]):
                slider_y = base_y + 36 + channel * (SLIDER_H + SLIDER_GAP)
                text = font_small.render(f"{channel_name}: {rgb[channel]}", True, WHITE)
                screen.blit(text, (START_X + 8, slider_y))
                color = [(255, 80, 80), (80, 255, 80), (80, 160, 255)][channel]
                track = draw_slider(screen, START_X + LABEL_W, slider_y, rgb[channel], color)
                slider_rects.append((track, ci, channel))
        screen.set_clip(old_clip)

        skin, hair, shirt, pants = get_colors()
        pygame.draw.rect(screen, (35, 38, 55), (PREVIEW_X - 10, PREVIEW_Y - 10, PREVIEW_BOX_W + 20, PREVIEW_BOX_H + 20))
        pygame.draw.rect(screen, DGRAY, (PREVIEW_X - 10, PREVIEW_Y - 10, PREVIEW_BOX_W + 20, PREVIEW_BOX_H + 20), 2)
        lbl = font_cat.render("Preview", True, LGRAY)
        screen.blit(lbl, (PREVIEW_X + PREVIEW_BOX_W // 2 - lbl.get_width() // 2, PREVIEW_Y))
        draw_preview(screen, PREVIEW_X + PREVIEW_BOX_W // 2, PREVIEW_Y + PREVIEW_BOX_H // 2 + 10, skin, hair, shirt, pants)

        mouse_pos = pygame.mouse.get_pos()
        if stage == 3:
            hover_hard = hard_mode_rect.collidepoint(mouse_pos)
            hard_color = GREEN if hard_mode else DGRAY
            hard_border = LGRAY if hover_hard else WHITE
            pygame.draw.rect(screen, hard_color, hard_mode_rect)
            pygame.draw.rect(screen, hard_border, hard_mode_rect, 2)
            txt = font_small.render(f"Hard Mode: {'ON' if hard_mode else 'OFF'}", True, BLACK if hard_mode else WHITE)
            screen.blit(txt, (hard_mode_rect.x + hard_mode_rect.w // 2 - txt.get_width() // 2, hard_mode_rect.y + hard_mode_rect.h // 2 - txt.get_height() // 2))

        # draw custom scrollbar if needed
        if content_height > visible_height:
            bar_x = START_X + SLIDER_W + 60
            bar_y = START_Y
            pygame.draw.rect(screen, (40, 40, 40), (bar_x, bar_y, 10, visible_height))
            thumb_h = int(max(40, visible_height * visible_height / content_height))
            thumb_range = visible_height - thumb_h
            thumb_y = bar_y + int((scroll_offset * -1) / (content_height - visible_height) * thumb_range) if content_height > visible_height else bar_y
            scroll_thumb_rect = pygame.Rect(bar_x, thumb_y, 10, thumb_h)
            pygame.draw.rect(screen, LGRAY, scroll_thumb_rect)
        else:
            scroll_thumb_rect = None

        mouse_pos = pygame.mouse.get_pos()
        hover_start = btn_rect.collidepoint(mouse_pos)
        hover_back = back_rect.collidepoint(mouse_pos)
        draw_button(btn_rect, "▶  Start Game", hover_start, True)
        draw_button(back_rect, "Back", hover_back, True)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                if btn_rect.collidepoint(mx, my):
                    if stage == 3:
                        return (*get_colors(), hard_mode)
                    return get_colors()
                if back_rect.collidepoint(mx, my):
                    return None
                if stage == 3 and hard_mode_rect.collidepoint(mx, my):
                    hard_mode = not hard_mode
                for rect, ci, channel in slider_rects:
                    if rect.collidepoint(mx, my):
                        active_slider = (ci, channel)
                        break
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                active_slider = None
            elif event.type == pygame.MOUSEMOTION and active_slider is not None:
                mx, _ = event.pos
                ci, channel = active_slider
                track_x = START_X + LABEL_W
                value = int(255 * (mx - track_x) / (SLIDER_W - 10))
                categories[ci][1][channel] = clamp_color(value)
            elif event.type == pygame.MOUSEWHEEL:
                scroll_offset += event.y * 40
                scroll_offset = clamp_scroll(scroll_offset)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button in (4, 5):
                scroll_offset += 40 if event.button == 4 else -40
                scroll_offset = clamp_scroll(scroll_offset)

        clock.tick(FPS)

    return get_colors()


def show_end_screen(screen, clock, won, score, save_callback=None, stage=None, scoreboard=None):
    play_music("ScreenBGmusic.mp3", volume=0.6)
    font_big = pygame.font.SysFont(None, 72)
    font_mid = pygame.font.SysFont(None, 40)
    stages_rect = pygame.Rect(SCREEN_WIDTH // 2 - 110, SCREEN_HEIGHT // 2 + 20, 220, 52)
    save_rect = pygame.Rect(stages_rect.x, stages_rect.y + stages_rect.h + 12, stages_rect.w, 44)

    while True:
        screen.fill((15, 10, 25) if not won else (10, 25, 15))
        msg = "YOU WIN!" if won else "GAME OVER"
        color = GOLD if won else RED
        t1 = font_big.render(msg, True, color)
        screen.blit(t1, (SCREEN_WIDTH // 2 - t1.get_width() // 2, SCREEN_HEIGHT // 2 - 120))
        t2 = font_mid.render(f"Final Score: {score}", True, WHITE)
        screen.blit(t2, (SCREEN_WIDTH // 2 - t2.get_width() // 2, SCREEN_HEIGHT // 2 - 30))

        pygame.draw.rect(screen, GREEN, stages_rect)
        pygame.draw.rect(screen, WHITE, stages_rect, 2)
        st = font_mid.render("Stages", True, BLACK)
        screen.blit(st, (stages_rect.x + stages_rect.w // 2 - st.get_width() // 2, stages_rect.y + 10))

        pygame.draw.rect(screen, GREEN, save_rect)
        pygame.draw.rect(screen, WHITE, save_rect, 2)
        sv = font_mid.render("Save and Quit", True, BLACK)
        screen.blit(sv, (save_rect.x + save_rect.w // 2 - sv.get_width() // 2, save_rect.y + 10))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if stages_rect.collidepoint(event.pos):
                    return run_stage_select(screen, clock, scoreboard)
                if save_rect.collidepoint(event.pos):
                    if save_callback and stage in (1, 2, 3):
                        save_callback(stage, score)
                    pygame.quit()
                    sys.exit()


def draw_pause_menu(screen, level_index):
    play_music("ScreenBGmusic.mp3", volume=0.6)
    font_title = pygame.font.SysFont(None, 64)
    font_btn = pygame.font.SysFont(None, 34)
    font_text = pygame.font.SysFont(None, 24)

    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    screen.blit(overlay, (0, 0))

    title = font_title.render("Paused", True, WHITE)
    title_x = SCREEN_WIDTH // 2 - title.get_width() // 2
    title_y = SCREEN_HEIGHT // 2 - 140
    screen.blit(title, (title_x, title_y))

    level_label = font_text.render(f"Level {level_index + 1}", True, WHITE)
    screen.blit(level_label, (SCREEN_WIDTH // 2 - level_label.get_width() // 2, title_y + 70))

    btn_w = 240
    btn_h = 50
    btn_x = SCREEN_WIDTH // 2 - btn_w // 2
    btn_y = SCREEN_HEIGHT // 2 - 20
    spacing = 16

    resume_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
    restart_rect = pygame.Rect(btn_x, btn_y + btn_h + spacing, btn_w, btn_h)
    quit_rect = pygame.Rect(btn_x, btn_y + 2 * (btn_h + spacing), btn_w, btn_h)

    mouse_pos = pygame.mouse.get_pos()
    for rect, text in [(resume_rect, "Resume"), (restart_rect, "Restart Level"), (quit_rect, "Quit")]:
        hovered = rect.collidepoint(mouse_pos)
        color = LGRAY if hovered else DGRAY
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, WHITE, rect, 2)
        label = font_btn.render(text, True, WHITE if hovered else BLACK)
        screen.blit(label, (rect.x + rect.w // 2 - label.get_width() // 2, rect.y + rect.h // 2 - label.get_height() // 2))

    return resume_rect, restart_rect, quit_rect


def run_stage_select(screen, clock, scoreboard=None, skip_customization=False):
    play_music("ScreenBGmusic.mp3", volume=0.6)
    font_title = pygame.font.SysFont(None, 52)
    font_btn = pygame.font.SysFont(None, 32)
    font_small = pygame.font.SysFont(None, 20)
    card_w = 260
    card_h = 90
    card_x = 80
    card_gap = 40
    content_top = 140
    content_height = 3 * (card_h + card_gap) + 120
    visible_height = SCREEN_HEIGHT - 200
    scroll_offset = 0
    dragging_slider = False
    scroll_drag_offset = 0
    slider_track = pygame.Rect(SCREEN_WIDTH - 44, 120, 24, visible_height)
    back_rect = pygame.Rect(40, SCREEN_HEIGHT - 80, 160, 48)

    def clamp_scroll(offset):
        max_offset = 0
        min_offset = min(0, SCREEN_HEIGHT - 160 - content_height)
        return max(min_offset, min(max_offset, offset))

    def draw_stage_card(y, label, active, show_coming_soon=False, single_circle=False):
        title_rect = pygame.Rect(card_x, y, card_w, card_h)
        base_color = GREEN if active else DGRAY
        pygame.draw.rect(screen, base_color, title_rect)
        pygame.draw.rect(screen, WHITE, title_rect, 2)
        label_txt = font_btn.render(label, True, BLACK if active else LGRAY)
        screen.blit(label_txt, (title_rect.x + 16, title_rect.y + title_rect.h // 2 - label_txt.get_height() // 2))

        line_y = y + card_h // 2
        line_start = (title_rect.right + 100, line_y)
        line_end = (line_start[0] + 240, line_y)
        circle_count = 1 if show_coming_soon or single_circle else 3
        if not show_coming_soon and not single_circle:
            pygame.draw.line(screen, WHITE if active else LGRAY, line_start, line_end, 3)

        for idx in range(circle_count):
            cx = line_start[0] + idx * 120
            cy = line_y
            circle_color = WHITE if active else LGRAY
            radius = 22
            if active:
                pygame.draw.circle(screen, circle_color, (cx, cy), radius)
                pygame.draw.circle(screen, BLACK, (cx, cy), radius, 2)
            else:
                pygame.draw.circle(screen, BLACK, (cx, cy), radius, 2)
            num_txt = font_btn.render(str(idx + 1), True, BLACK if active else LGRAY)
            screen.blit(num_txt, (cx - num_txt.get_width() // 2, cy - num_txt.get_height() // 2))

        if show_coming_soon:
            note = font_small.render("Coming Soon", True, LGRAY)
            screen.blit(note, (title_rect.x + title_rect.w - note.get_width() - 12, title_rect.y + title_rect.h - note.get_height() - 10))
        return title_rect

    def draw_scrollbar(offset):
        pygame.draw.rect(screen, (40, 40, 40), slider_track)
        content_span = max(content_height, visible_height)
        thumb_h = int(max(40, visible_height * visible_height / content_span))
        thumb_range = visible_height - thumb_h
        thumb_y = 120 + int((offset * -1) / (content_height - visible_height) * thumb_range) if content_height > visible_height else 120
        thumb_rect = pygame.Rect(slider_track.x + 4, thumb_y, slider_track.w - 8, thumb_h)
        pygame.draw.rect(screen, LGRAY, thumb_rect)
        pygame.draw.rect(screen, WHITE, thumb_rect, 2)
        return thumb_rect

    running = True
    while running:
        screen.fill((20, 22, 35))
        title = font_title.render("Stage Levels", True, GOLD)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 40))

        max_offset = min(0, SCREEN_HEIGHT - 160 - content_height)
        scroll_offset = clamp_scroll(scroll_offset)
        stage_y = content_top + scroll_offset

        first_rect = draw_stage_card(stage_y, "First Stage", active=True)
        second_rect = draw_stage_card(stage_y + card_h + card_gap, "Second Stage", active=True, show_coming_soon=False)
        third_rect = draw_stage_card(stage_y + 2 * (card_h + card_gap), "Third Stage", active=True, show_coming_soon=False, single_circle=True)

        # Draw saved scores next to each stage
        if scoreboard is None:
            scoreboard = {"first": [0, 0, 0, 0], "second": [0, 0, 0, 0], "third": [0, 0, 0, 0]}
        score_x = slider_track.x - 90

        def draw_stage_scores(score_list, base_y):
            last_score = score_list[0] if len(score_list) > 0 else 0
            top_scores = score_list[1:4] if len(score_list) > 1 else [0, 0, 0]
            while len(top_scores) < 3:
                top_scores.append(0)

            txt_last = font_small.render(f"Score: {last_score}", True, WHITE)
            screen.blit(txt_last, (score_x, base_y))
            for i in range(3):
                ty = base_y + 22 + i * (font_small.get_height() + 2)
                rank = "1st" if i == 0 else "2nd" if i == 1 else "3rd"
                txt = font_small.render(f"{rank}: {top_scores[i]}", True, LGRAY)
                screen.blit(txt, (score_x + 8, ty))

        fs_y = stage_y + card_h // 2 - font_small.get_height() // 2
        draw_stage_scores(scoreboard.get("first", [0, 0, 0, 0]), fs_y)
        ss_y = stage_y + card_h + card_gap + card_h // 2 - font_small.get_height() // 2
        draw_stage_scores(scoreboard.get("second", [0, 0, 0, 0]), ss_y)
        ts_y = stage_y + 2 * (card_h + card_gap) + card_h // 2 - font_small.get_height() // 2
        draw_stage_scores(scoreboard.get("third", [0, 0, 0, 0]), ts_y)

        thumb_rect = draw_scrollbar(scroll_offset)

        mouse_pos = pygame.mouse.get_pos()
        hover_back = back_rect.collidepoint(mouse_pos)
        back_color = LGRAY if hover_back else DGRAY
        pygame.draw.rect(screen, back_color, back_rect)
        pygame.draw.rect(screen, WHITE, back_rect, 2)
        back_label = font_btn.render("Back", True, BLACK)
        screen.blit(back_label, (back_rect.x + back_rect.w // 2 - back_label.get_width() // 2, back_rect.y + back_rect.h // 2 - back_label.get_height() // 2))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if first_rect.collidepoint(event.pos):
                    if skip_customization:
                        defaults = (255, 220, 170), (40, 30, 20), (50, 80, 200), (40, 40, 100)
                        return (*defaults, 1)
                    result = run_customization(screen, clock, stage=1)
                    if result is None:
                        break
                    return (*result, 1)
                if second_rect.collidepoint(event.pos):
                    if skip_customization:
                        defaults = (255, 220, 170), (40, 30, 20), (50, 80, 200), (40, 40, 100)
                        return (*defaults, 2)
                    result = run_customization(screen, clock, stage=2)
                    if result is None:
                        break
                    return (*result, 2)
                if third_rect.collidepoint(event.pos):
                    if skip_customization:
                        defaults = (255, 220, 170), (40, 30, 20), (50, 80, 200), (40, 40, 100)
                        return (*defaults, False, 3)
                    result = run_customization(screen, clock, stage=3)
                    if result is None:
                        break
                    return (*result, 3)
                if back_rect.collidepoint(event.pos):
                    return None
                if thumb_rect.collidepoint(event.pos):
                    dragging_slider = True
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                dragging_slider = False
            elif event.type == pygame.MOUSEMOTION and dragging_slider:
                _, my = event.pos
                thumb_h = thumb_rect.h
                thumb_range = visible_height - thumb_h
                new_thumb_y = max(120, min(120 + thumb_range, my - thumb_h // 2))
                if thumb_range > 0:
                    scroll_offset = -int((new_thumb_y - 120) / thumb_range * (content_height - visible_height))
            elif event.type == pygame.MOUSEWHEEL:
                scroll_offset += event.y * 40
                scroll_offset = clamp_scroll(scroll_offset)

        clock.tick(FPS)

    return None


def run_start_screen(screen, clock, scoreboard=None, reset_callback=None):
    play_music("ScreenBGmusic.mp3", volume=0.6)
    font_title = pygame.font.SysFont(None, 72)
    font_btn = pygame.font.SysFont(None, 36)
    font_note = pygame.font.SysFont(None, 18)
    btn_w = 260
    btn_h = 60
    btn_x = SCREEN_WIDTH // 2 - btn_w // 2
    btn_spacing = 20
    total_height = 3 * btn_h + 2 * btn_spacing
    first_y = SCREEN_HEIGHT // 2 - total_height // 2

    start_rect = pygame.Rect(btn_x, first_y, btn_w, btn_h)
    controls_rect = pygame.Rect(btn_x, first_y + btn_h + btn_spacing, btn_w, btn_h)
    quit_rect = pygame.Rect(btn_x, first_y + 2 * (btn_h + btn_spacing), btn_w, btn_h)
    back_rect = pygame.Rect(SCREEN_WIDTH // 2 - 110, SCREEN_HEIGHT - 100, 220, 52)

    def draw_button(rect, text, hovered, active=True, note_text=None):
        if active:
            color = LGRAY if hovered else DGRAY
            text_color = WHITE if hovered else BLACK
        else:
            color = (45, 45, 55)
            text_color = LGRAY
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, WHITE, rect, 2)
        label = font_btn.render(text, True, text_color)
        screen.blit(label, (rect.x + rect.w // 2 - label.get_width() // 2, rect.y + rect.h // 2 - label.get_height() // 2 - (10 if note_text else 0)))
        if note_text:
            note = font_note.render(note_text, True, GRAY)
            screen.blit(note, (rect.x + rect.w // 2 - note.get_width() // 2, rect.y + rect.h - note.get_height() - 10))

    def show_controls_screen():
        while True:
            mouse_pos = pygame.mouse.get_pos()
            hovered_back = back_rect.collidepoint(mouse_pos)
            screen.fill((20, 22, 35))
            title = font_title.render("Controls", True, GOLD)
            screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 60))
            controls = [
                "A/D = Move",
                "Space = Jump",
                "Left Click = Attack",
                "1/2 = Switch Weapon",
            ]
            for i, line in enumerate(controls):
                txt = pygame.font.SysFont(None, 28).render(line, True, WHITE)
                screen.blit(txt, (SCREEN_WIDTH // 2 - txt.get_width() // 2, 180 + i * 45))
            draw_button(back_rect, "Back", hovered_back)
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if back_rect.collidepoint(event.pos):
                        return
            clock.tick(FPS)

    while True:
        mouse_pos = pygame.mouse.get_pos()
        hover_start = start_rect.collidepoint(mouse_pos)
        hover_controls = controls_rect.collidepoint(mouse_pos)
        hover_quit = quit_rect.collidepoint(mouse_pos)
        screen.fill((20, 22, 35))
        title = font_title.render("Plat-Mayhem", True, GOLD)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))
        draw_button(start_rect, "Start Game", hover_start, active=True)
        draw_button(controls_rect, "Controls", hover_controls, active=True)
        draw_button(quit_rect, "Quit", hover_quit, active=True)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if start_rect.collidepoint(event.pos):
                    if reset_callback:
                        reset_callback()
                    return run_stage_select(screen, clock, scoreboard, skip_customization=False)
                if controls_rect.collidepoint(event.pos):
                    show_controls_screen()
                if quit_rect.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()
        clock.tick(FPS)
