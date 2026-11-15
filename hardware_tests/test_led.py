from gpiozero import PWMLED
from time import sleep

red = PWMLED(13)
green = PWMLED(6)
blue = PWMLED(5)

def set_rgb(r, g, b):
    red.value = r / 255.0
    green.value = g / 255.0
    blue.value = b / 255.0


try:
    while True:
        text = input("RGB (0-255) or q: ").strip()

        if text.lower() == "q":
            break

        try:
            r, g, b = [int(x) for x in text.split()]
            set_rgb(r, g, b)
            print(f"RGB = ({r}, {g}, {b})")
        except ValueError:
            print("Enter three numbers, e.g. 255 120 20")

finally:
    red.close()
    green.close()
    blue.close()

