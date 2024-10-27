from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
import time

class LEDMatrixDashboard:
  def __init__(self):
    options = RGBMatrixOptions()
    options.rows = 64
    options.columns = 64
    options.gpio_slowdown = 4
    options.disable_hardware_pulsing = False
    options.hardware_mapping = 'regular'

    self.matrix = RGBMatrix(options=options)

  def run(self):
    offscreen_canvas = self.matrix.CreateFrameCanvas()
    font = graphics.Font()
    font.LoadFont("../../../fonts/7x13.bdf")
    text_color = graphics.Color(255, 255, 0)
    pos = offscreen_canvas.width

    while True:
      offscreen_canvas.Clear()
      len = graphics.DrawText(offscreen_canvas, font, pos, 20, text_color, self.message)
      pos -= 1
      if (pos + len < 0):
        pos = offscreen_canvas.width

      time.sleep(0.05)
      offscreen_canvas = self.matrix.SwapOnVSync(offscreen_canvas)

if __name__ == "__main__":
  dashboard = LEDMatrixDashboard(message="Welcome to the LED Matrix Dashboard!")
  dashboard.run()