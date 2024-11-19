from xpander import Xpander

PLC = Xpander()

# Helper function to draw a circle from a given position with a given radius
# This is an implementation of the midpoint circle algorithm,
# see https://en.wikipedia.org/wiki/Midpoint_circle_algorithm#C_example for details
def circle(xpos0, ypos0, rad, col=1):
    x = rad - 1
    y = 0
    dx = 1
    dy = 1
    err = dx - (rad << 1)
    while x >= y:
        PLC.OLED.pixel(xpos0 + x, ypos0 + y, col)
        PLC.OLED.pixel(xpos0 + y, ypos0 + x, col)
        PLC.OLED.pixel(xpos0 - y, ypos0 + x, col)
        PLC.OLED.pixel(xpos0 - x, ypos0 + y, col)
        PLC.OLED.pixel(xpos0 - x, ypos0 - y, col)
        PLC.OLED.pixel(xpos0 - y, ypos0 - x, col)
        PLC.OLED.pixel(xpos0 + y, ypos0 - x, col)
        PLC.OLED.pixel(xpos0 + x, ypos0 - y, col)
        if err <= 0:
            y += 1
            err += dy
            dy += 2
        if err > 0:
            x -= 1
            dx += 2
            err += dx - (rad << 1)

center_x = 63
center_y = 15
x_inc = 4
y_inc = 4
radius = 4


if __name__ == "__main__":
    PLC.init()
    PLC.setOLED()

    PLC.OLED.fill(0)
    PLC.OLED.show()

    while True:
        # undraw the previous circle
        circle(center_x, center_y, radius, col=0)

        # if bouncing off right
        if center_x + radius >= PLC.OLED.width:
            # start moving to the left
            x_inc = -1
        # if bouncing off left
        elif center_x - radius < 0:
            # start moving to the right
            x_inc = 1

        # if bouncing off top
        if center_y + radius >= PLC.OLED.height:
            # start moving down
            y_inc = -1
        # if bouncing off bottom
        elif center_y - radius < 0:
            # start moving up
            y_inc = 1

        center_x += x_inc
        center_y += y_inc

        circle(center_x, center_y, radius)
        PLC.OLED.show()