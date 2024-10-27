from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
import time
import requests
from PIL import Image

class LEDMatrixDashboard:
  def __init__(self):
    options = RGBMatrixOptions()
    options.rows = 64
    options.cols = 64
    options.gpio_slowdown = 4
    options.disable_hardware_pulsing = True
    options.hardware_mapping = 'regular'

    self.matrix = RGBMatrix(options=options)
    self.weather = self.get_weather('Chicago')
    self.default_color = graphics.Color(0, 255, 255)
    self.offscreen_canvas = self.matrix.CreateFrameCanvas()

  def run(self):
    while True:
      self.offscreen_canvas.Clear()
      self.display_weather()

      time.sleep(0.05)
      self.offscreen_canvas = self.matrix.SwapOnVSync(self.offscreen_canvas)

  # draws belo pos_x instead of above which is default behavior for graphics.drawText()
  def draw_text(self, font_height, pos_x, pos_y, text, text_color = graphics.Color(0, 255, 255)):
    font_files = {
      7: "../../../fonts/5x7.bdf",
      20: "../../../fonts/10x20.bdf",
      24: "../../../fonts/12x24.bdf"
    }

    if font_height not in font_files:
      raise ValueError(f"Invalid font height: {font_height}")

    font = graphics.Font()
    font.LoadFont(font_files[font_height])
    graphics.DrawText(self.offscreen_canvas, font, pos_x, pos_y + font_height, text_color, text)
  
  def get_weather(self, location = 'Santa Barbara'):
      api_key = '623331e648e44cbd97970459242710'
      url = f'http://api.weatherapi.com/v1/current.json?key={api_key}&q={location}'
      response = requests.get(url)
      if response.status_code == 200:
          weather_data = response.json()
          return weather_data
      else:
          return 'Error fetching weather'
      
  def display_weather(self):  
    location = self.weather['location']['name']
    self.draw_text(7, 5, 10, location)
    weather_message = f"{self.weather['current']['temp_c']} C"
    self.draw_text(7, 5, 20, weather_message)
    icon_url = self.weather['current']['condition']['icon']
    icon_response = requests.get(f"http:{icon_url}")
    if icon_response.status_code == 200:
      with open("/tmp/weather_icon.png", "wb") as icon_file:
        icon_file.write(icon_response.content)
      
      self.draw_image("/tmp/weather_icon.png", 20, 20, 5, 30)
    else:
      self.draw_text(7, 5, 40, "No icon")

  def draw_image(self, icon_path, width, height, pos_x, pos_y):
    image = Image.open(icon_path)
    image = image.resize((width, height))  # Resize the image to fit the matrix
    image = image.convert('RGB')

    for x in range(image.width):
      for y in range(image.height):
        r, g, b = image.getpixel((x, y))
        graphics.Color(r, g, b)
        self.offscreen_canvas.SetPixel(pos_x + x, pos_y + y, r, g, b)

  # untested
  def scroll_text(self):
    pos = self.offscreen_canvas.width
    while True:
      len = self.draw_text(self.offscreen_canvas, 7, pos, 20, 'hello world')
      pos -= 1
      if (pos + len < 0):
        pos = self.offscreen_canvas.width

      time.sleep(0.05)
      self.offscreen_canvas = self.matrix.SwapOnVSync(self.offscreen_canvas)

if __name__ == "__main__":
  dashboard = LEDMatrixDashboard()
  dashboard.run()