from PIL import Image

class qrcode:
    def __init__(self):
        self.version = 1
        self.size = 21
        self.quiet_zone = 4
        self.code = [[0 for i in range(self.size)] for j in range(self.size)]

    # def show(self):
    #     for i in range(len(self.code)):
    #         for j in range(len(self.code[i])):
    #             print(self.code[i][j], end=" ")
    #         print()

    def show(self):
        enlarged_image = self.enlarge_image()
        enlarged_image.show()

    def create(self, data, filename):
        self.add_position()
        self.add_timeline()
        self.add_quite_zone()
        pass

    def add_timeline(self):
        f = 1
        x = 6
        y = 8
        for i in range(5):
            self.code[x][y + i] = f
            f ^= 1

        f = 1
        x = 8
        y = 6
        for i in range(5):
            self.code[x + i][y] = f
            f ^= 1
        pass

    def add_position(self):
        self.draw_position_marker(0, 0)
        self.draw_position_marker(0, 14)
        self.draw_position_marker(14, 0)

    def draw_position_marker(self, x, y):
        r = 7
        f = 1
        while r >= 3:
            for i in range(r):
                for j in range(r):
                    self.code[y + i][x + j] = f
            r -= 2
            x += 1
            y += 1
            f ^= 1
            
    def add_quite_zone(self):
        l = [0] * self.size
        for i in range(self.quiet_zone):
            self.code = [l] + self.code + [l]
            
        for i in range(len(self.code)):
            self.code[i] = [0] * self.quiet_zone + self.code[i] + [0] * self.quiet_zone

    def read(self, filename):
        pass

    def enlarge_image(self):
        scale = 20  # Scaling factor for visualization
        enlarged_size = (len(self.code[0]) * scale, len(self.code) * scale)
        enlarged_image = Image.new("RGB", enlarged_size, "white")
        pixels = enlarged_image.load()

        for y in range(len(self.code)):
            for x in range(len(self.code[y])):
                color = "black" if self.code[y][x] == 1 else "white"
                for i in range(scale):
                    for j in range(scale):
                        pixels[x * scale + i, y * scale + j] = (0, 0, 0) if color == "black" else (255, 255, 255)

        return enlarged_image
        

qr = qrcode()
qr.create("Hello World", "hello.png")
qr.show()
