import pygame

from config import Constants
from system.SwarmSystem import SwarmSystem


# --- ЗАПУСК ПРИЛОЖЕНИЯ ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((Constants.WIDTH, Constants.HEIGHT))
    pygame.display.set_caption("Swarm Intelligence Simulation")
    clock = pygame.time.Clock()

    swarm = SwarmSystem(Constants.NUM_DRONES)

    running = True
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # Обработка нажатий клавиатуры
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_v:  # Нажата клавиша 'V'
                    swarm.toggle_vision()

        # Tracking mouse position as target
        target_pos = pygame.mouse.get_pos()
        swarm.update(target_pos)

        # Drawing elements on screen
        screen.fill(Constants.BG_COLOR)
        pygame.draw.circle(screen, Constants.TARGET_COLOR, target_pos, 10, 2)
        swarm.draw(screen)

        # Setting frame rate and updating display state
        pygame.display.flip()
        clock.tick(Constants.FPS)

    pygame.quit()


if __name__ == "__main__":
    main()