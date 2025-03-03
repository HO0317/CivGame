# building.py
import pygame

RESIDENCE_POP_INCREASE = 1000
BARRACKS_TRAIN_COST = 500

def building_menu(screen, font):
    # "Capital" 옵션 제거 – 수도는 자동으로 생성됨
    options = ["Residence", "Barracks", "Igluvijaq"]
    option_rects = []
    menu_width = 300
    menu_height = 180
    menu_x = (screen.get_width() - menu_width) // 2
    menu_y = (screen.get_height() - menu_height) // 2
    menu_rect = pygame.Rect(menu_x, menu_y, menu_width, menu_height)
    pygame.draw.rect(screen, (50, 50, 50), menu_rect)
    option_height = 40
    for i, option in enumerate(options):
        rect = pygame.Rect(menu_x + 20, menu_y + 20 + i * (option_height + 10), menu_width - 40, option_height)
        pygame.draw.rect(screen, (100, 100, 100), rect)
        txt = font.render(option, True, (255, 255, 255))
        txt_rect = txt.get_rect(center=rect.center)
        screen.blit(txt, txt_rect)
        option_rects.append((rect, option))
    pygame.display.flip()
    chosen = None
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                for rect, opt in option_rects:
                    if rect.collidepoint(mx, my):
                        chosen = opt
                        waiting = False
                        break
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    waiting = False
        pygame.time.delay(50)
    return chosen
