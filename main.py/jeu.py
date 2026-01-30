"""
======================== main.py ========================

Petit jeu de plateformes verticales en Python / Pygame
------------------------------------------------------

Comment lancer
--------------
1) Installer Python 3.x
2) Installer pygame :
       pip install pygame
3) Lancer le jeu :
       python main.py

Par défaut, la fenêtre fait 800x600.

Au lancement :
- Un premier écran attend que tu appuies sur la barre d'espace.
- Quand tu appuies sur ESPACE, le niveau apparaît, le joueur est posé
  sur une plateforme, mais le niveau est figé.
- Le niveau ne commence vraiment (gravité + scroll + plateformes) que
  lorsque tu appuies sur une touche de déplacement (flèches) ou de saut.

Règles
------
- Tu contrôles un petit monstre rose.
- Tu peux te déplacer à gauche / droite.
- Tu peux sauter avec la flèche haut.
- La caméra monte en continu (le monde descend) une fois le niveau lancé.
- Des plateformes sont générées au lancement du niveau, puis régénérées
  au-dessus pour garder l'écran rempli :
    * NORMAL      : tu peux te poser dessus.
    * TRAP        : tu peux te poser dessus, mais la plateforme
                    disparaît 0.5 seconde après que tu aies marché dessus.
                    (pas de perte de vie directe, mais tu peux tomber ensuite)
    * TRAMPOLINE  : tu rebondis avec un saut plus fort (x1.5).
- Si tu tombes en dehors de l'écran par le bas, tu perds 1 vie.
- Tu as 3 vies au début de chaque niveau.
- Il y a 3 niveaux. En haut de chaque niveau, un "soleil" à toucher.
  Le toucher te fait passer au niveau suivant et remet tes vies à 3.
- Après le niveau 3, un écran "Bravo" s'affiche avec le temps de
  chaque niveau.

Couleur des plateformes
-----------------------
- Plateforme NORMAL      : vert (100, 200, 100)
- Plateforme TRAP        : rouge (200, 60, 60)
- Plateforme TRAMPOLINE  : bleu clair (80, 180, 220)
- Joueur (monstre)       : rose (255, 105, 180)
- Soleil (objectif)      : jaune (255, 220, 0)

Commandes
---------
- Flèche gauche  : se déplacer à gauche
- Flèche droite  : se déplacer à droite
- Flèche haut    : sauter
- Barre d'espace : démarrer la partie (depuis l'écran d'attente)
- Échap          : quitter le jeu

Dépendances
-----------
- pygame uniquement

=========================================================
"""

from __future__ import annotations

import sys
import random
import time
from enum import Enum, auto
from typing import List, Tuple, Dict, Optional

import pygame


# =========================================================
#                 CONSTANTES EXPLICITES
# =========================================================

# Physique et déplacements
GRAVITY: float = 0.5
RUN_SPEED: float = 4.0
JUMP_FORCE: float = 10.0
SCROLL_SPEED: float = 1.0  # demandé : SCROLL_SPEED = 1
TRAMPOLINE_MULTIPLIER: float = 3.0  # demandé
# Gameplay : trampoline = saut x1.5
TRAMPOLINE_GAME_FACTOR: float = 1.5

# Fenêtre
SCREEN_WIDTH: int = 800
SCREEN_HEIGHT: int = 600

# Police
FONT_SIZE: int = 24

# Couleurs (R, G, B)
COLORS: Dict[str, Tuple[int, int, int]] = {
    "background": (20, 20, 40),
    "player": (255, 105, 180),      # Rose
    "platform_normal": (100, 200, 100),
    "platform_trap": (200, 60, 60),
    "platform_trampoline": (80, 180, 220),
    "hud_text": (255, 255, 255),
    "sun": (255, 220, 0),
    "game_over": (255, 80, 80),
    "victory": (80, 255, 120),
}

# Répartition des types de plateformes (en pourcentage)
PLATFORM_NORMAL_PERCENT: float = 0.70
PLATFORM_TRAP_PERCENT: float = 0.15
PLATFORM_TRAMPOLINE_PERCENT: float = 0.15

# Autres constantes de gameplay
INITIAL_LIVES: int = 3
MAX_LEVEL: int = 3

# Espacement vertical entre plateformes (en pixels) — demandé : [40..50]
PLATFORM_MIN_GAP: int = 40
PLATFORM_MAX_GAP: int = 50

# Nombre de plateformes à maintenir à l'écran
MIN_PLATFORMS: int = 16
MAX_PLATFORMS: int = 20

# Taille des plateformes
PLATFORM_WIDTH: int = 100
PLATFORM_HEIGHT: int = 20

# Taille du joueur
PLAYER_WIDTH: int = 40
PLAYER_HEIGHT: int = 50

# Taille du "soleil" (objectif en haut)
SUN_RADIUS: int = 30

# Durée avant disparition d'un piège après qu'on ait marché dessus (en secondes)
TRAP_LIFETIME_AFTER_STEP: float = 0.5


# =========================================================
#                 ENUM ET CLASSES DE BASE
# =========================================================

class PlatformType(Enum):
    """Type de plateforme dans le jeu."""
    NORMAL = auto()
    TRAP = auto()
    TRAMPOLINE = auto()


class Platform:
    """Représente une plateforme sur laquelle le joueur peut interagir."""

    def __init__(self, x: float, y: float, width: int, height: int, p_type: PlatformType) -> None:
        """
        Crée une nouvelle plateforme.

        :param x: Position horizontale (gauche) de la plateforme.
        :param y: Position verticale (haut) de la plateforme.
        :param width: Largeur de la plateforme.
        :param height: Hauteur de la plateforme.
        :param p_type: Type de la plateforme (NORMAL, TRAP, TRAMPOLINE).
        """
        self.rect: pygame.Rect = pygame.Rect(int(x), int(y), width, height)
        self.type: PlatformType = p_type

        # Pour les plateformes TRAP : moment où le joueur a marché dessus.
        # None = jamais déclenchée.
        self.trigger_time: Optional[float] = None

    def update(self, scroll_speed: float) -> None:
        """
        Met à jour la position de la plateforme en fonction du défilement vertical.

        :param scroll_speed: Vitesse de défilement vers le bas (caméra qui monte).
        """
        self.rect.y += int(scroll_speed)

    def trigger_trap(self) -> None:
        """
        Marque un piège comme déclenché (le joueur a marché dessus).
        La plateforme disparaîtra après un certain temps.
        """
        if self.type == PlatformType.TRAP and self.trigger_time is None:
            self.trigger_time = time.time()

    def should_disappear(self) -> bool:
        """
        Indique si une plateforme TRAP doit disparaître (0.5 seconde après déclenchement).

        :return: True si la plateforme doit être supprimée.
        """
        if self.type != PlatformType.TRAP:
            return False
        if self.trigger_time is None:
            return False
        return (time.time() - self.trigger_time) >= TRAP_LIFETIME_AFTER_STEP

    def draw(self, surface: pygame.Surface) -> None:
        """
        Dessine la plateforme sur l'écran.

        :param surface: Surface pygame sur laquelle dessiner.
        """
        if self.type == PlatformType.NORMAL:
            color = COLORS["platform_normal"]
        elif self.type == PlatformType.TRAP:
            color = COLORS["platform_trap"]
        else:
            color = COLORS["platform_trampoline"]

        pygame.draw.rect(surface, color, self.rect)


class Player:
    """Représente le joueur (petit monstre rose)."""

    def __init__(self, x: float, y: float) -> None:
        """
        Crée un joueur à la position donnée.

        :param x: Position horizontale initiale.
        :param y: Position verticale initiale.
        """
        self.rect: pygame.Rect = pygame.Rect(int(x), int(y), PLAYER_WIDTH, PLAYER_HEIGHT)
        self.vx: float = 0.0
        self.vy: float = 0.0
        self.on_ground: bool = False

    def reset_position(self, x: float, y: float) -> None:
        """
        Replace le joueur à une position donnée et remet sa vitesse à zéro.

        :param x: Nouvelle position horizontale.
        :param y: Nouvelle position verticale.
        """
        self.rect.x = int(x)
        self.rect.y = int(y)
        self.vx = 0.0
        self.vy = 0.0
        self.on_ground = False

    def handle_input(self) -> None:
        """
        Gère les entrées clavier pour le déplacement du joueur.
        """
        keys = pygame.key.get_pressed()
        self.vx = 0.0

        if keys[pygame.K_LEFT]:
            self.vx = -RUN_SPEED
        if keys[pygame.K_RIGHT]:
            self.vx = RUN_SPEED

        if keys[pygame.K_UP]:
            # Saut autorisé uniquement si le joueur est au sol
            if self.on_ground:
                self.vy = -JUMP_FORCE
                self.on_ground = False

    def apply_gravity(self) -> None:
        """
        Applique la gravité au joueur.
        """
        self.vy += GRAVITY

    def landed(self) -> None:
        """
        Appelé lorsque le joueur atterrit sur une plateforme ou le sol.
        """
        self.on_ground = True

    def draw(self, surface: pygame.Surface) -> None:
        """
        Dessine le joueur (placeholder rose) sur l'écran.

        :param surface: Surface pygame sur laquelle dessiner.
        """
        pygame.draw.rect(surface, COLORS["player"], self.rect)


class HUD:
    """Affiche les informations de jeu (vies, niveau, temps)."""

    def __init__(self, font: pygame.font.Font) -> None:
        """
        Crée un HUD avec la police donnée.

        :param font: Police pygame utilisée pour le texte.
        """
        self.font: pygame.font.Font = font

    def format_time(self, seconds: float) -> str:
        """
        Formate un temps en secondes en chaîne mm:ss.cc.

        :param seconds: Temps en secondes.
        :return: Chaîne formatée.
        """
        minutes = int(seconds // 60)
        sec = int(seconds % 60)
        centi = int((seconds - int(seconds)) * 100)
        return f"{minutes:02d}:{sec:02d}.{centi:02d}"

    def draw(self, surface: pygame.Surface, lives: int, level: int, max_level: int, level_time: float) -> None:
        """
        Dessine le HUD en haut à gauche.

        :param surface: Surface pygame sur laquelle dessiner.
        :param lives: Nombre de vies restantes.
        :param level: Niveau actuel.
        :param max_level: Nombre total de niveaux.
        :param level_time: Temps écoulé dans le niveau actuel.
        """
        lives_text = self.font.render(f"Vies: {lives}", True, COLORS["hud_text"])
        level_text = self.font.render(f"Niveau: {level}/{max_level}", True, COLORS["hud_text"])
        time_text = self.font.render(f"Temps: {self.format_time(level_time)}", True, COLORS["hud_text"])

        surface.blit(lives_text, (10, 10))
        surface.blit(level_text, (10, 10 + FONT_SIZE + 4))
        surface.blit(time_text, (10, 10 + 2 * (FONT_SIZE + 4)))


class Level:
    """Gère la génération et la logique d'un niveau."""

    def __init__(self, level_index: int) -> None:
        """
        Crée un niveau avec une difficulté dépendant de son index.

        :param level_index: Numéro du niveau (1, 2 ou 3).
        """
        self.level_index: int = level_index
        self.platforms: List[Platform] = []

        # Difficulté progressive :
        # on augmente légèrement le scroll pour les niveaux plus hauts.
        self.scroll_speed: float = SCROLL_SPEED + (level_index - 1) * 0.5

        # Espacement demandé : [40..50]
        self.min_gap: int = PLATFORM_MIN_GAP
        self.max_gap: int = PLATFORM_MAX_GAP

        # Légère augmentation des pièges au niveau 3
        if level_index == 3:
            self.normal_percent: float = 0.60
            self.trap_percent: float = 0.25
            self.trampoline_percent: float = 0.15
        else:
            self.normal_percent = PLATFORM_NORMAL_PERCENT
            self.trap_percent = PLATFORM_TRAP_PERCENT
            self.trampoline_percent = PLATFORM_TRAMPOLINE_PERCENT

        # Pour garder un chemin praticable :
        # - éviter deux pièges d'affilée
        # - éviter que deux pièges soient au même endroit horizontalement
        self.last_platform_type: PlatformType = PlatformType.NORMAL
        self.last_trap_x: Optional[float] = None

        # Position verticale la plus haute (plus petit y) où une plateforme a été générée
        self.highest_platform_y: float = SCREEN_HEIGHT

        # Création initiale des plateformes (au lancement du niveau)
        self._create_initial_platforms()

    def _choose_platform_type(self) -> PlatformType:
        """
        Choisit un type de plateforme en fonction des pourcentages configurés.
        Évite de générer trop de pièges pour garder un chemin praticable.

        :return: Type de plateforme choisi.
        """
        r = random.random()

        # Si la dernière plateforme était un piège, on force une plateforme non-piège
        if self.last_platform_type == PlatformType.TRAP:
            if r < 0.5:
                return PlatformType.NORMAL
            else:
                return PlatformType.TRAMPOLINE

        # Cas général : tirage selon les pourcentages
        if r < self.normal_percent:
            return PlatformType.NORMAL
        elif r < self.normal_percent + self.trap_percent:
            return PlatformType.TRAP
        else:
            return PlatformType.TRAMPOLINE

    def _create_initial_platforms(self) -> None:
        """
        Crée les premières plateformes pour remplir l'écran au début du niveau.
        """
        self.platforms.clear()

        # Plateforme de départ (large et en bas)
        start_platform_y = SCREEN_HEIGHT - 80
        start_platform = Platform(
            x=(SCREEN_WIDTH - PLATFORM_WIDTH) / 2,
            y=start_platform_y,
            width=PLATFORM_WIDTH,
            height=PLATFORM_HEIGHT,
            p_type=PlatformType.NORMAL,
        )
        self.platforms.append(start_platform)
        self.highest_platform_y = start_platform_y
        self.last_platform_type = PlatformType.NORMAL

        # Générer d'autres plateformes au-dessus
        while len(self.platforms) < MIN_PLATFORMS:
            self.spawn_platform_above()

    def spawn_platform_above(self) -> None:
        """
        Génère une nouvelle plateforme au-dessus de la plus haute existante.
        Garde un chemin praticable et une possibilité d'éviter les pièges.
        """
        gap = random.randint(self.min_gap, self.max_gap)
        new_y = self.highest_platform_y - gap

        # Marge horizontale pour éviter les plateformes collées aux bords
        margin = 40
        x_min = margin
        x_max = SCREEN_WIDTH - PLATFORM_WIDTH - margin
        new_x = random.randint(x_min, x_max)

        p_type = self._choose_platform_type()

        # Si on génère un piège, on essaie de le placer loin du dernier piège
        if p_type == PlatformType.TRAP and self.last_trap_x is not None:
            if abs(new_x - self.last_trap_x) < PLATFORM_WIDTH:
                # Trop proche du dernier piège : on transforme en NORMAL
                p_type = PlatformType.NORMAL

        platform = Platform(new_x, new_y, PLATFORM_WIDTH, PLATFORM_HEIGHT, p_type)
        self.platforms.append(platform)
        self.highest_platform_y = new_y
        self.last_platform_type = p_type

        if p_type == PlatformType.TRAP:
            self.last_trap_x = new_x

    def update(self) -> None:
        """
        Met à jour toutes les plateformes (défilement) et en génère de nouvelles si besoin.
        Gère aussi la disparition des pièges déclenchés.
        """
        # Déplacer les plateformes vers le bas (caméra qui monte)
        for p in self.platforms:
            p.update(self.scroll_speed)

        # Supprimer les plateformes qui sortent par le bas
        self.platforms = [p for p in self.platforms if p.rect.top <= SCREEN_HEIGHT]

        # Supprimer les pièges qui ont été déclenchés depuis plus de TRAP_LIFETIME_AFTER_STEP
        self.platforms = [p for p in self.platforms if not p.should_disappear()]

        # Garder entre MIN_PLATFORMS et MAX_PLATFORMS
        while len(self.platforms) < MIN_PLATFORMS:
            self.spawn_platform_above()
        while len(self.platforms) > MAX_PLATFORMS:
            # Supprimer d'abord les plateformes les plus basses
            self.platforms.sort(key=lambda pl: pl.rect.y, reverse=True)
            self.platforms.pop(0)

    def draw(self, surface: pygame.Surface) -> None:
        """
        Dessine toutes les plateformes du niveau.

        :param surface: Surface pygame sur laquelle dessiner.
        """
        for p in self.platforms:
            p.draw(surface)

    def get_safe_spawn_position(self) -> Tuple[float, float]:
        """
        Retourne une position sûre pour respawn le joueur (sur la plateforme la plus basse).

        :return: Tuple (x, y) pour la position du joueur.
        """
        # On choisit la plateforme la plus basse (plus grande valeur de y)
        if not self.platforms:
            # Valeur de secours : centre de l'écran
            return SCREEN_WIDTH / 2 - PLAYER_WIDTH / 2, SCREEN_HEIGHT / 2

        lowest_platform = max(self.platforms, key=lambda p: p.rect.y)
        x = lowest_platform.rect.centerx - PLAYER_WIDTH / 2
        y = lowest_platform.rect.top - PLAYER_HEIGHT
        return float(x), float(y)


class Game:
    """Classe principale qui gère tout le jeu."""

    def __init__(self) -> None:
        """
        Initialise le jeu, la fenêtre, les niveaux et le joueur.
        """
        pygame.init()
        pygame.display.set_caption("Plateformes verticales - Python / Pygame")

        self.screen: pygame.Surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock: pygame.time.Clock = pygame.time.Clock()

        self.font: pygame.font.Font = pygame.font.SysFont("Arial", FONT_SIZE)

        self.hud: HUD = HUD(self.font)

        # Gestion des niveaux
        self.current_level_index: int = 1
        self.level: Level = Level(self.current_level_index)

        # Joueur
        spawn_x, spawn_y = self.level.get_safe_spawn_position()
        self.player: Player = Player(spawn_x, spawn_y)

        # Vies
        self.lives: int = INITIAL_LIVES

        # Gestion du temps par niveau
        self.level_start_time: float = time.time()
        self.level_times: List[float] = []

        # États de jeu
        self.running: bool = True
        self.game_over: bool = False
        self.victory: bool = False

        # État d'attente avant d'appuyer sur espace pour démarrer le jeu
        self.waiting_start: bool = True
        # État d'attente au début de chaque niveau (joueur posé, rien ne bouge)
        self.level_running: bool = False

        # Position du "soleil" (objectif) en haut de l'écran (dans la vue)
        self.sun_center: Tuple[int, int] = (SCREEN_WIDTH // 2, 80)

    def reset_level(self) -> None:
        """
        Réinitialise le niveau actuel (nouveau Level, respawn du joueur, reset des vies).
        Le niveau est figé tant qu'aucune touche de déplacement n'est pressée.
        """
        self.level = Level(self.current_level_index)
        spawn_x, spawn_y = self.level.get_safe_spawn_position()
        self.player.reset_position(spawn_x, spawn_y)
        self.lives = INITIAL_LIVES
        self.level_running = False
        self.level_start_time = time.time()

    def next_level(self) -> None:
        """
        Passe au niveau suivant ou déclenche la victoire si le dernier niveau est terminé.
        """
        # Enregistrer le temps du niveau terminé
        level_time = time.time() - self.level_start_time
        self.level_times.append(level_time)

        if self.current_level_index >= MAX_LEVEL:
            # Tous les niveaux sont terminés
            self.victory = True
            self.game_over = True
        else:
            # Passer au niveau suivant
            self.current_level_index += 1
            self.reset_level()

    def lose_life_and_respawn(self) -> None:
        """
        Retire une vie et replace le joueur à une position sûre.
        Déclenche le Game Over si plus de vies.
        Le niveau est à nouveau figé jusqu'à la prochaine touche.
        """
        self.lives -= 1
        if self.lives <= 0:
            self.game_over = True
            # Enregistrer le temps du niveau en cours (même si perdu)
            level_time = time.time() - self.level_start_time
            self.level_times.append(level_time)
        else:
            spawn_x, spawn_y = self.level.get_safe_spawn_position()
            self.player.reset_position(spawn_x, spawn_y)
            self.level_running = False
            self.level_start_time = time.time()

    def handle_vertical_collisions_and_move(self) -> None:
        """
        Teste les collisions avant de déplacer le joueur, puis applique le déplacement.

        - On applique d'abord le déplacement horizontal (avec clamp dans l'écran).
        - On prédit la position verticale future.
        - On teste la collision avec les plateformes.
        - On applique les effets (NORMAL, TRAP, TRAMPOLINE).
        - On met à jour la position verticale finale.
        """
        # Mouvement horizontal simple (sans collision avec les plateformes)
        self.player.rect.x += int(self.player.vx)
        if self.player.rect.left < 0:
            self.player.rect.left = 0
        if self.player.rect.right > SCREEN_WIDTH:
            self.player.rect.right = SCREEN_WIDTH

        # Si le joueur ne descend pas, on applique juste le mouvement vertical
        if self.player.vy <= 0:
            self.player.rect.y += int(self.player.vy)
            return

        # Prévision de la position verticale future
        proposed_rect: pygame.Rect = self.player.rect.copy()
        proposed_rect.y += int(self.player.vy)

        # On suppose qu'il n'est pas au sol tant qu'on n'a pas trouvé de plateforme
        self.player.on_ground = False

        for platform in self.level.platforms:
            if proposed_rect.colliderect(platform.rect):
                # Vérifier que le joueur arrive par le dessus
                if self.player.rect.bottom <= platform.rect.top:
                    if platform.type == PlatformType.NORMAL:
                        # On "snap" le joueur sur la plateforme
                        self.player.rect.bottom = platform.rect.top
                        self.player.vy = 0.0
                        self.player.landed()
                    elif platform.type == PlatformType.TRAP:
                        # Le piège supporte le joueur, mais disparaîtra après 0.5 seconde
                        self.player.rect.bottom = platform.rect.top
                        self.player.vy = 0.0
                        self.player.landed()
                        platform.trigger_trap()
                    elif platform.type == PlatformType.TRAMPOLINE:
                        # Rebond plus fort (x1.5)
                        self.player.rect.bottom = platform.rect.top
                        self.player.vy = -JUMP_FORCE * TRAMPOLINE_GAME_FACTOR
                        self.player.on_ground = False
                    # On a géré une collision, on sort
                    return

        # Si aucune collision, on applique le mouvement vertical prévu
        self.player.rect.y = proposed_rect.y

    def check_fall_out_of_screen(self) -> None:
        """
        Vérifie si le joueur est tombé en dehors de l'écran par le bas.
        Si oui, il perd une vie et respawn.
        """
        if self.player.rect.top > SCREEN_HEIGHT:
            self.lose_life_and_respawn()

    def check_sun_collision(self) -> None:
        """
        Vérifie si le joueur touche le "soleil" en haut de l'écran.
        Si oui, passe au niveau suivant.
        """
        sun_x, sun_y = self.sun_center
        sun_rect = pygame.Rect(
            sun_x - SUN_RADIUS,
            sun_y - SUN_RADIUS,
            SUN_RADIUS * 2,
            SUN_RADIUS * 2,
        )
        if self.player.rect.colliderect(sun_rect):
            self.next_level()

    def draw_sun(self) -> None:
        """
        Dessine le "soleil" (objectif) en haut de l'écran.
        """
        pygame.draw.circle(self.screen, COLORS["sun"], self.sun_center, SUN_RADIUS)

    def draw_start_screen(self) -> None:
        """
        Affiche l'écran d'attente avant le début de la partie.
        """
        self.screen.fill(COLORS["background"])

        title_text = self.font.render("Jeu de plateformes verticales", True, COLORS["hud_text"])
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40))
        self.screen.blit(title_text, title_rect)

        info_text = self.font.render("Appuie sur ESPACE pour commencer", True, COLORS["hud_text"])
        info_rect = info_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
        self.screen.blit(info_text, info_rect)

    def draw_game_over_screen(self) -> None:
        """
        Affiche l'écran de Game Over ou de victoire avec les temps par niveau.
        """
        self.screen.fill(COLORS["background"])

        if self.victory:
            title_text = self.font.render("Bravo ! Tu as terminé les 3 niveaux !", True, COLORS["victory"])
        else:
            title_text = self.font.render("Game Over", True, COLORS["game_over"])

        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 80))
        self.screen.blit(title_text, title_rect)

        # Affichage des temps par niveau
        y = 150
        for i, t in enumerate(self.level_times, start=1):
            label = f"Niveau {i}: {self.hud.format_time(t)}"
            time_text = self.font.render(label, True, COLORS["hud_text"])
            self.screen.blit(time_text, (SCREEN_WIDTH // 2 - 150, y))
            y += FONT_SIZE + 10

        info_text = self.font.render("Appuie sur Échap pour quitter.", True, COLORS["hud_text"])
        info_rect = info_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80))
        self.screen.blit(info_text, info_rect)

    def draw_level_scene(self, level_time: float) -> None:
        """
        Dessine la scène de jeu (niveau, joueur, HUD).

        :param level_time: Temps écoulé dans le niveau.
        """
        self.screen.fill(COLORS["background"])
        self.level.draw(self.screen)
        self.draw_sun()
        self.player.draw(self.screen)
        self.hud.draw(self.screen, self.lives, self.current_level_index, MAX_LEVEL, level_time)

        # Si le niveau n'a pas encore démarré, afficher un petit message
        if not self.level_running:
            info_text = self.font.render(
                "Appuie sur une flèche ou HAUT pour lancer le niveau",
                True,
                COLORS["hud_text"],
            )
            info_rect = info_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60))
            self.screen.blit(info_text, info_rect)

    def run(self) -> None:
        """
        Boucle principale du jeu (limitée à 60 FPS).
        """
        while self.running:
            # Limiter à 60 FPS
            self.clock.tick(60)

            # Gestion des événements
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    if self.waiting_start and event.key == pygame.K_SPACE:
                        # Sortir de l'écran d'attente général
                        self.waiting_start = False
                        # Le niveau est affiché mais figé, le chrono repart de zéro
                        self.level_running = False
                        self.level_start_time = time.time()
                    # Si on est dans un niveau affiché mais figé, la première touche de déplacement/saut le lance
                    if (not self.waiting_start) and (not self.game_over) and (not self.level_running):
                        if event.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP):
                            self.level_running = True
                            self.level_start_time = time.time()

            if self.waiting_start:
                # Écran d'attente avant le début du jeu
                self.draw_start_screen()
            elif not self.game_over:
                # Calcul du temps de niveau (0 si le niveau n'a pas encore démarré)
                if self.level_running:
                    current_time = time.time()
                    level_time = current_time - self.level_start_time
                else:
                    level_time = 0.0

                # Mise à jour du jeu uniquement si le niveau est "en cours"
                if self.level_running:
                    # Entrées + gravité
                    self.player.handle_input()
                    self.player.apply_gravity()
                    # Collision testée AVANT de déplacer verticalement
                    self.handle_vertical_collisions_and_move()

                    # Scroll des plateformes (caméra qui monte)
                    self.level.update()
                    # Vérifier chute hors écran et soleil
                    self.check_fall_out_of_screen()
                    self.check_sun_collision()
                else:
                    # Niveau figé : on lit juste les entrées pour pouvoir démarrer
                    self.player.handle_input()
                    # Pas de gravité ni de déplacement tant que le niveau n'est pas lancé.

                # Dessin de la scène de niveau
                self.draw_level_scene(level_time)
            else:
                # Écran de fin (Game Over ou Victoire)
                self.draw_game_over_screen()

            pygame.display.flip()

        pygame.quit()
        sys.exit()


def main() -> None:
    """
    Point d'entrée du programme.
    Crée le jeu et lance la boucle principale.
    """
        # Note : indentation corrigée si besoin dans votre éditeur
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
