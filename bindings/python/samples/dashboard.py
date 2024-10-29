from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
import sys
import time
import requests
import os
from PIL import Image

class LEDMatrixDashboard:
    def __init__(self, location = "Santa Barbara"):
        options = RGBMatrixOptions()
        options.rows = 64
        options.cols = 64
        options.gpio_slowdown = 4
        options.disable_hardware_pulsing = True
        options.hardware_mapping = 'regular'

        self.matrix = RGBMatrix(options=options)
        self.location = location
        self.weather = self.get_weather()
        self.default_color = graphics.Color(0, 255, 255)
        self.offscreen_canvas = self.matrix.CreateFrameCanvas()

    def run(self):
        self.display_loading()
        while True:
            self.offscreen_canvas.Clear()
            self.display_weather()

            time.sleep(0.05)
            self.offscreen_canvas = self.matrix.SwapOnVSync(self.offscreen_canvas)

    # draws belo pos_x instead of above which is default behavior for graphics.drawText()
    def draw_text(self, font_height, pos_x, pos_y, text, text_color = graphics.Color(0, 255, 255)):
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        fonts = {
            7: "../../../fonts/5x7.bdf",
            8: "../../../fonts/5x8.bdf",
            9: "../../../fonts/6x9.bdf",
            10: "../../../fonts/6x10.bdf",
            12: "../../../fonts/6x12.bdf",
            14: "../../../fonts/7x14.bdf",
            18: "../../../fonts/9x18.bdf",
        }
        if font_height not in fonts:
            raise ValueError(f"Invalid font height: {font_height}")

        font = graphics.Font()
        font.LoadFont(fonts[font_height])

        graphics.DrawText(self.offscreen_canvas, font, pos_x, pos_y + font_height, text_color, text)

    def get_weather(self):
        api_key = '623331e648e44cbd97970459242710'
        url = f'http://api.weatherapi.com/v1/current.json?key={api_key}&q={self.location}'
        response = requests.get(url)
        if response.status_code == 200:
            weather_data = response.json()
            return weather_data
        else:
            return 'Error fetching weather'

    def display_weather(self):
        self.offscreen_canvas.Clear()
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

    def display_loading(self, duration = 3):
        frames = ['|', '/', '-', '\\']
        start_time = time.time()
        frame_index = 0

        while time.time() - start_time < duration:
            self.offscreen_canvas.Clear()
            self.draw_text(10, 30, 30, frames[frame_index], self.default_color)
            self.offscreen_canvas = self.matrix.SwapOnVSync(self.offscreen_canvas)
            frame_index = (frame_index + 1) % len(frames)
            time.sleep(0.1)

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
    location = sys.argv[1] if len(sys.argv) > 1 else "Chicago"
    dashboard = LEDMatrixDashboard(location)
    dashboard.run()
