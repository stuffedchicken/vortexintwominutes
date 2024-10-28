import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Get screen dimensions for fullscreen
screen_info = pygame.display.Info()
SCREEN_WIDTH, SCREEN_HEIGHT = screen_info.current_w, screen_info.current_h
WINDOW_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)

# Set full-screen display
window = pygame.display.set_mode(WINDOW_SIZE, pygame.FULLSCREEN)
pygame.display.set_caption("VORTEX IN TWOOOOOOOO MINUTES")

# pygame.time.wait(5000)  # Wait 5000 milliseconds (5 seconds)
# This is only here because fuckin' obs took too long to figure out where the window was when full-screen, so it was mising the beginning. Uncomment it if you have the same problem.


# Calculate radius for the large circle to fill the screen
LARGE_CIRCLE_RADIUS = min(SCREEN_WIDTH, SCREEN_HEIGHT) // 2 - 10  # Fit within screen edges
SMALL_CIRCLE_RADIUS = 40  # Initial small circle radius
INCREASE_SIZE = 1.1  # Size increase factor
SPEED = 5  # Initial speed of the small circle
GRAVITY = 1.3  # Gravitational acceleration
BOUNCE_MULTIPLIER = 198.5  # Multiplier for vertical bounce strength
MAX_RADIUS = LARGE_CIRCLE_RADIUS - 10  # Cap for small circle radius
FPS = 30  # Frames per second
MAX_VELOCITY = 35  # Maximum velocity for the small circle
DAMPING_FACTOR = 0.8  # Damping factor to reduce velocity after bounces
COLOR_SHIFT_AMOUNT = 30  # Amount to shift hue on each bounce
TRAIL_LENGTH = 0  # Maximum number of trail segments to keep
AFTER_IMAGE_FRAMES = 1  # Frames between after-images

# Load the bounce sound and sprite image
bounce_sound = pygame.mixer.Sound('bounce_sound.wav')
sprite_image = pygame.image.load("sprite.png").convert_alpha()
original_sprite = pygame.transform.scale(sprite_image, (SMALL_CIRCLE_RADIUS * 2, SMALL_CIRCLE_RADIUS * 2))

# Define the small circle's initial position and velocity
small_circle_pos = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2]
initial_velocity = [random.choice([-1, 1]) * SPEED * random.random(),
                    random.choice([-1, 1]) * SPEED * random.random()]
small_circle_velocity = initial_velocity.copy()

# Initialize color in HSV
hue = 0
color = pygame.Color(0)  # Initialize color

# List to store trail positions and colors
trail = []

# Frame counter for after-image
frame_count = 0

# Create a surface for the textured large circle
def draw_textured_circle():
    texture_surface = pygame.Surface(WINDOW_SIZE, pygame.SRCALPHA)
    for r in range(LARGE_CIRCLE_RADIUS, 0, -1):  # Draw circles from the outside in
        color_value = int(255 * (r / LARGE_CIRCLE_RADIUS))  # Gradient effect
        pygame.draw.circle(texture_surface, (color_value, color_value, 255), (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), r)
        pygame.draw.circle(texture_surface, (0, 0, 0), (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), r, 1)  # Black outline
    return texture_surface

# Create the textured circle once
textured_circle_surface = draw_textured_circle()

# Main game loop
running = True
clock = pygame.time.Clock()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:  # Press ESC to exit full-screen
                running = False

    # Apply gravity to vertical velocity
    small_circle_velocity[1] += GRAVITY

    # Update position
    small_circle_pos[0] += small_circle_velocity[0]
    small_circle_pos[1] += small_circle_velocity[1]

    # Check for collisions with the large circle
    distance_from_center = math.sqrt(
        (small_circle_pos[0] - SCREEN_WIDTH // 2) ** 2 +
        (small_circle_pos[1] - SCREEN_HEIGHT // 2) ** 2
    )

    # Check if the small circle is colliding with the edge of the large circle
    if distance_from_center + SMALL_CIRCLE_RADIUS > LARGE_CIRCLE_RADIUS:
        bounce_sound.play()

        # Check if growing would exceed the max radius allowed
        if SMALL_CIRCLE_RADIUS * INCREASE_SIZE <= MAX_RADIUS:
            SMALL_CIRCLE_RADIUS *= INCREASE_SIZE
            original_sprite = pygame.transform.scale(sprite_image, (int(SMALL_CIRCLE_RADIUS * 2), int(SMALL_CIRCLE_RADIUS * 2)))

        hue = (hue + COLOR_SHIFT_AMOUNT) % 360
        color.hsva = (hue, 100, 100)

        # Calculate the normal at the point of collision
        normal_x = (small_circle_pos[0] - SCREEN_WIDTH // 2) / distance_from_center
        normal_y = (small_circle_pos[1] - SCREEN_HEIGHT // 2) / distance_from_center

        # Reflect the velocity based on the normal
        dot_product = small_circle_velocity[0] * normal_x + small_circle_velocity[1] * normal_y
        small_circle_velocity[0] -= 2 * dot_product * normal_x
        small_circle_velocity[1] -= 2 * dot_product * normal_y

        # Apply bounce multiplier for a stronger bounce effect
        if small_circle_velocity[1] < 0:
            small_circle_velocity[1] = -abs(small_circle_velocity[1]) * BOUNCE_MULTIPLIER

        small_circle_velocity[0] += random.uniform(-1, 1)

        overlap = (distance_from_center + SMALL_CIRCLE_RADIUS) - LARGE_CIRCLE_RADIUS
        if overlap > 0:
            small_circle_pos[0] -= overlap * normal_x
            small_circle_pos[1] -= overlap * normal_y

        # Apply damping to the velocity
        small_circle_velocity[0] *= DAMPING_FACTOR
        small_circle_velocity[1] *= DAMPING_FACTOR

        # Clamp the velocity
        small_circle_velocity[0] = max(min(small_circle_velocity[0], MAX_VELOCITY), -MAX_VELOCITY)
        small_circle_velocity[1] = max(min(small_circle_velocity[1], MAX_VELOCITY), -MAX_VELOCITY)

    # Fill the window with black
    window.fill((0, 0, 0))

    # Draw the textured large circle
    window.blit(textured_circle_surface, (0, 0))

    # Draw the trail
    for pos, col, radius in trail:
        pygame.draw.circle(window, (0, 0, 0), (int(pos[0]), int(pos[1])), int(radius))  # Draw black outline
        pygame.draw.circle(window, col, (int(pos[0]), int(pos[1])), int(radius - 1))

    # Increment frame counter
    frame_count += 1

    # IF YOU WANT THE TRAIL TO COME BACK, UNCOMMENT THIS PART OUT LOL.
    
    # if frame_count % AFTER_IMAGE_FRAMES == 0:
    #     if len(trail) >= TRAIL_LENGTH:
    #         trail.pop(0)
    #     trail.append((small_circle_pos.copy(), (color.r, color.g, color.b), SMALL_CIRCLE_RADIUS))

    # Calculate the angle of rotation
    angle = math.degrees(math.atan2(small_circle_velocity[1], small_circle_velocity[0])) - 90

    # Rotate the sprite to face the direction of movement
    rotated_sprite = pygame.transform.rotate(original_sprite, angle)

    # Get the new rect for centered positioning
    sprite_rect = rotated_sprite.get_rect(center=(int(small_circle_pos[0]), int(small_circle_pos[1])))

    # Draw the rotated sprite
    window.blit(rotated_sprite, sprite_rect.topleft)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
