import pygame

pygame.init()
pygame.joystick.init()

if pygame.joystick.get_count() == 0:
    raise SystemExit("No controller detected")

stik = pygame.joystick.Joystick(0)
print("Controller:", stik.get_name())
print("Axes:", stik.get_numaxes(), "| Buttons:", stik.get_numbuttons(), "| Hats:", stik.get_numhats())

clock = pygame.time.Clock()
while True:
    pygame.event.pump()
    axis = [round(stik.get_axis(i), 2) for i in range(stik.get_numaxes())]
    tombol = [i for i in range(stik.get_numbuttons()) if stik.get_button(i)]
    print("axes:", axis, "buttons pressed:", tombol)
    clock.tick(10)