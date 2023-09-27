from PIL import Image
import re
import random
import colorsys
from MessagePolynomial import MessagePolynomial
from GeneratorPolynomial import GeneratorPolynomial

def is_alphanumeric(data):
    pattern = r'^[A-Z\s$%*+\-./:0-9]+$'
    match = re.match(pattern, data)
    
    return match is not None

class QRCode:
    def __init__(
        self, version: int = None, error_correction: int = None, mask: int = None
    ):
        self.data = ""
        self.version = version
        self.error_correction = error_correction
        self.mask = mask
        self.quiet_zone = 4
        self.data_type = None
        self.valid_error_correction = ["L", "M", "Q", "H"]
        self.character_count = []
        self.mode_indicator = []
        self.modules = []
        self.encoded_data = []
        self.error_codewords = []
        self.GF256 = [1, 2, 4, 8, 16, 32, 64, 128, 29, 58, 116, 232, 205, 135, 19, 38, 76, 152, 45, 90, 180, 117, 234, 201, 143, 3, 6, 12, 24, 48, 96, 192, 157, 39, 78, 156, 37, 74, 148, 53, 106, 212, 181, 119, 238, 193, 159, 35, 70, 140, 5, 10, 20, 40, 80, 160, 93, 186, 105, 210, 185, 111, 222, 161, 95, 190, 97, 194, 153, 47, 94, 188, 101, 202, 137, 15, 30, 60, 120, 240, 253, 231, 211, 187, 107, 214, 177, 127, 254, 225, 223, 163, 91, 182, 113, 226, 217, 175, 67, 134, 17, 34, 68, 136, 13, 26, 52, 104, 208, 189, 103, 206, 129, 31, 62, 124, 248, 237, 199, 147, 59, 118, 236, 197, 151, 51, 102, 204, 133, 23, 46, 92, 184, 109, 218, 169, 79, 158, 33, 66, 132, 21, 42, 84, 168, 77, 154, 41, 82, 164, 85, 170, 73, 146, 57, 114, 228, 213, 183, 115, 230, 209, 191, 99, 198, 145, 63, 126, 252, 229, 215, 179, 123, 246, 241, 255, 227, 219, 171, 75, 150, 49, 98, 196, 149, 55, 110, 220, 165, 87, 174, 65, 130, 25, 50, 100, 200, 141, 7, 14, 28, 56, 112, 224, 221, 167, 83, 166, 81, 162, 89, 178, 121, 242, 249, 239, 195, 155, 43, 86, 172, 69, 138, 9, 18, 36, 72, 144, 61, 122, 244, 245, 247, 243, 251, 235, 203, 139, 11, 22, 44, 88, 176, 125, 250, 233, 207, 131, 27, 54, 108, 216, 173, 71, 142, 1]

        if self.version is not None:
            self.size = (21 + (self.version - 1) * 4)
            self.image = [[-1 for _ in range(21 + (self.version - 1) * 4)] for _ in range(21 + (self.version - 1) * 4)]
            self.evaluation_image = [[-1 for _ in range(21 + (self.version - 1) * 4)] for _ in range(21 + (self.version - 1) * 4)]

        self.occupied_pixels = []
        self.mask_lambdas = [
            lambda x, y: (x + y) % 2 == 0,
            lambda x, y: x % 2 == 0,
            lambda x, y: y % 3 == 0,
            lambda x, y: (x + y) % 3 == 0,
            lambda x, y: ((x // 2) + (y // 3)) % 2 == 0,
            lambda x, y: ((x * y) % 2) + ((x * y) % 3) == 0,
            lambda x, y: (((x * y) % 2) + ((x * y) % 3)) % 2 == 0,
            lambda x, y: (((x + y) % 2) + ((x * y) % 3)) % 2 == 0
        ]

        self.needed_error_codewords = {
            '1L': 7, '1M': 10, '1Q': 13, '1H': 17,
            '2L': 10, '2M': 16, '2Q': 22, '2H': 28,
            '3L': 15, '3M': 26, '3Q': 18, '3H': 22,
            '4L': 20, '4M': 18, '4Q': 26, '4H': 16,
            '5L': 26, '5M': 24, '5Q': 18, '5H': 22,
            '6L': 18, '6M': 16, '6Q': 24, '6H': 28,
            '7L': 20, '7M': 18, '7Q': 18, '7H': 26,
            '8L': 24, '8M': 22, '8Q': 22, '8H': 26,
            '9L': 30, '9M': 22, '9Q': 20, '9H': 24,
            '10L': 18, '10M': 26, '10Q': 24, '10H': 28,
            '11L': 20, '11M': 30, '11Q': 28, '11H': 24,
            '12L': 24, '12M': 22, '12Q': 26, '12H': 26,
            '13L': 26, '13M': 22, '13Q': 24, '13H': 22,
            '14L': 30, '14M': 24, '14Q': 20, '14H': 24,
            '15L': 22, '15M': 24, '15Q': 30, '15H': 24,
            '16L': 24, '16M': 28, '16Q': 24, '16H': 30,
            '17L': 28, '17M': 28, '17Q': 22, '17H': 28,
            '18L': 30, '18M': 26, '18Q': 28, '18H': 28,
            '19L': 28, '19M': 26, '19Q': 26, '19H': 26,
            '20L': 28, '20M': 26, '20Q': 30, '20H': 28,
        }
    
    def print_image(self):
        for i in range(len(self.image)):
            for j in range(len(self.image[i])):
                print("{:4}".format(self.image[i][j]), end=" ")
            print()

    def show(self, image=None):
        image = self.image if image == None else image
        enlarged_image = self.enlarge_image(image)
        enlarged_image.show()

    def determine_data_type(self, data):
        if data.isdigit():
            self.mode_indicator = [0, 0, 0, 1]
            return "numeric"
        elif is_alphanumeric(data):
            self.mode_indicator = [0, 0, 1, 0]
            return "alphanumeric"
        else:
            self.mode_indicator = [0, 1, 0, 0]
            return "byte"

    def add_data_type(self, data_type):
        if data_type == "numeric":
            self.modules.extend([0, 0, 0, 1])
        elif data_type == "alphanumeric":
            self.modules.extend([0, 0, 1, 0])
        elif data_type == "byte":
            self.modules.extend([0, 1, 0, 0])

    def determine_version(self, data, data_type, error_correction):
        data_capacity = len(data)
        capacity_table = {
            "numeric": {
                'L': [41, 77, 127, 187, 255, 322, 370, 461, 552, 652, 772, 883, 1022, 1101, 1250, 1408, 1548, 1725, 1903, 2061],
                'M': [34, 63, 101, 149, 202, 255, 293, 365, 432, 513, 604, 691, 796, 871, 991, 1082, 1156, 1258, 1364, 1474],
                'Q': [27, 48, 77, 111, 144, 178, 207, 259, 312, 364, 427, 492, 557, 610, 672, 744, 779, 864, 938, 1016],
                'H': [17, 34, 58, 82, 106, 139, 154, 202, 235, 288, 331, 374, 427, 468, 530, 602, 674, 746, 813, 919]
            },
            "alphanumeric": {
                'L': [25, 47, 77, 114, 154, 195, 224, 279, 335, 395, 468, 535, 619, 667, 758, 854, 938, 1046, 1153, 1249],
                'M': [20, 38, 61, 90, 122, 154, 178, 221, 262, 311, 366, 419, 483, 528, 600, 656, 734, 816, 909, 970],
                'Q': [16, 29, 47, 67, 87, 108, 125, 157, 189, 221, 259, 296, 352, 376, 426, 470, 531, 574, 644, 702],
                'H': [10, 20, 35, 50, 64, 84, 93, 122, 143, 174, 200, 227, 259, 283, 321, 365, 408, 452, 493, 557]
            },
            "byte": {
                'L': [17, 32, 53, 78, 106, 134, 154, 192, 230, 271, 321, 367, 425, 458, 520, 586, 644, 718, 792, 858],
                'M': [14, 26, 42, 62, 84, 106, 122, 152, 180, 213, 251, 287, 331, 362, 412, 450, 504, 560, 624, 666],
                'Q': [11, 20, 32, 46, 60, 74, 86, 108, 130, 151, 177, 203, 241, 258, 292, 322, 364, 394, 442, 482],
                'H': [7, 14, 24, 34, 44, 58, 64, 84, 98, 119, 137, 155, 177, 194, 220, 250, 280, 310, 338, 382]
            },
            "kanji": {
                'L': [10, 20, 32, 48, 65, 82, 95, 118, 141, 167, 198, 226, 262, 282, 320, 361, 397, 442, 488, 528],
                'M': [8, 16, 26, 38, 52, 65, 75, 93, 111, 131, 155, 177, 204, 223, 254, 277, 310, 345, 384, 410],
                'Q': [7, 12, 20, 29, 37, 45, 53, 66, 80, 93, 109, 125, 149, 159, 180, 198, 224, 243, 272, 297],
                'H': [4, 8, 15, 22, 28, 36, 43, 53, 63, 74, 85, 96, 109, 120, 136, 154, 173, 191, 209, 235]
            }
        }

        capacities = capacity_table[data_type][error_correction]

        for version, capacity in enumerate(capacities, start=1):
            if capacity >= data_capacity:
                return version

        return None

    def check_version(self, version):
        if version == None:
            raise Exception("Data exceeds highest version's encoding limit")
        
        if type(version) != int:
            raise TypeError("Version must be an integer")
        
        if version < 1 or version > 20:
            raise Exception("Version must be between 1-20")
        
        determined_version = self.determine_version(self.data, self.data_type, self.error_correction)

        if version < determined_version:
            raise Exception("Version can not contain data size - version has to at least be " + str(determined_version))

        return True
        
    def check_error_correction(self, error_correction):
        if type(error_correction) != str:
            raise TypeError("Error correction must be a string")
        
        if error_correction.upper() in self.valid_error_correction:
            return True
        else:
            raise Exception("Invalid error correction value entered - Valid values: [\"L\", \"M\", \"Q\", \"H\"]")

    def check_mask(self, data, version, error_correction, mask):
        pass
    
    def pad(self, binary, length):
        return "0" * (length - len(binary)) + binary

    def pad_right(self, binary, length):
        return binary + "0" * (length - len(binary))

    def pad_modules(self, data, version, error_correction):
        data_codewords = {
            "1L": 19, "1M": 16, "1Q": 13, "1H": 9,
            "2L": 34, "2M": 28, "2Q": 22, "2H": 16,
            "3L": 55, "3M": 44, "3Q": 34, "3H": 26,
            "4L": 80, "4M": 64, "4Q": 48, "4H": 36,
            "5L": 108, "5M": 86, "5Q": 62, "5H": 46,
            "6L": 136, "6M": 108, "6Q": 76, "6H": 60,
            "7L": 156, "7M": 124, "7Q": 88, "7H": 66,
            "8L": 194, "8M": 154, "8Q": 110, "8H": 86,
            "9L": 232, "9M": 182, "9Q": 132, "9H": 100,
            "10L": 274, "10M": 216, "10Q": 154, "10H": 122,
            "11L": 324, "11M": 254, "11Q": 180, "11H": 140,
            "12L": 370, "12M": 290, "12Q": 206, "12H": 158,
            "13L": 428, "13M": 334, "13Q": 244, "13H": 180,
            "14L": 461, "14M": 365, "14Q": 261, "14H": 197,
            "15L": 523, "15M": 415, "15Q": 295, "15H": 223,
            "16L": 589, "16M": 453, "16Q": 325, "16H": 253,
            "17L": 647, "17M": 507, "17Q": 367, "17H": 283,
            "18L": 721, "18M": 563, "18Q": 397, "18H": 313,
            "19L": 795, "19M": 627, "19Q": 445, "19H": 341,
            "20L": 861, "20M": 669, "20Q": 485, "20H": 385
        }
        needed_bytes = data_codewords[str(version) + error_correction]
        needed_bits = needed_bytes * 8
        zeros = 0
        while zeros < 4 and len(self.modules) < needed_bits:
            self.modules.append(0)
            zeros += 1
        
        if len(self.modules) >= needed_bits:
            return True
        
        while len(self.modules) % 8 != 0:
            self.modules.append(0)
            
        if len(self.modules) >= needed_bits:
            return True
        
        pad_bits = [
            [1, 1, 1, 0, 1, 1, 0, 0], 
            [0, 0, 0, 1, 0, 0, 0, 1]
        ]
        x = 0
        while len(self.modules) < needed_bits:
            self.modules.extend(pad_bits[x])
            x ^= 1
    
        
    def add_character_count(self, data, data_type, version):
        data_capacity = len(data)
        binary_capacity = bin(data_capacity)[2:]
        if 1 <= version <= 9:
            if data_type == "numeric":
                padded_capacity = self.pad(binary_capacity, 10)
            elif data_type == "alphanumeric":
                padded_capacity = self.pad(binary_capacity, 9)
            elif data_type == "byte":
                padded_capacity = self.pad(binary_capacity, 8)
        elif 10 <= version <= 26:
            if data_type == "numeric":
                padded_capacity = self.pad(binary_capacity, 12)
            elif data_type == "alphanumeric":
                padded_capacity = self.pad(binary_capacity, 11)
            elif data_type == "byte":
                padded_capacity = self.pad(binary_capacity, 16)
        else:
            raise Exception("Error occurred")
        
        self.character_count = padded_capacity
        self.modules.extend([int(i) for i in padded_capacity])

    def add_data(self, data, data_type):
        if data_type == "numeric":
            for i in range(0, len(data), 3):
                group = data[i:i+3]
                int_group = int(data[i:i+3])
                bin_group = bin(int_group)[2:]
                
                if len(str(int_group)) == 3:
                    bin_group = self.pad(bin_group, 10)
                elif len(str(int_group)) == 2:
                    bin_group = self.pad(bin_group, 7)
                elif len(str(int_group)) == 1:
                    bin_group = self.pad(bin_group, 4)

                self.encoded_data.extend([int(i) for i in bin_group])
                self.modules.extend([int(i) for i in bin_group])

        elif data_type == "alphanumeric":
            for i in range(0, len(data), 2):
                allowed_characters = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ $%*+-./:"
                group = data[i:i+2]

                if len(group) == 2:
                    ch1 = allowed_characters.index(group[0])
                    ch2 = allowed_characters.index(group[1])
                    int_group = 45 * ch1 + ch2
                    bin_group = bin(int_group)[2:]
                    bin_group = self.pad(bin_group, 11)
                else:
                    ch1 = allowed_characters.index(group[0])
                    int_group = ch1
                    bin_group = bin(int_group)[2:]
                    bin_group = self.pad(bin_group, 6)

                self.encoded_data.extend([int(i) for i in bin_group])
                self.modules.extend([int(i) for i in bin_group])

        elif data_type == "byte":
            for i in range(len(data)):
                bin_r = bin(ord(data[i]))[2:]
                bin_r = self.pad(bin_r, 8)
                self.encoded_data.extend([int(i) for i in bin_r])
                self.modules.extend([int(i) for i in bin_r])
        else:
            raise Exception("Error occurred")

    def generate_message_polynomial(self, modules):
        msg = MessagePolynomial()
        msg_coeffs, msg_degrees = msg.generate_polynomial(modules)
        return msg_coeffs, msg_degrees
    
    def generate_generator_polynomial(self, error_codewords):
        gen = GeneratorPolynomial()
        gen_coeffs, gen_degrees = gen.generate_polynomial(error_codewords)
        return gen_coeffs, gen_degrees

    def division(self, msg_coeffs, msg_degrees, gen_coeffs, gen_degrees, error_codewords_count):
        # Used to increase degree of generator polynomial later
        initial_degree = msg_degrees[0]

        # Increase degree of message polynomial by number of codewords
        msg_degrees = [x + error_codewords_count for x in msg_degrees]

        # Used to reset generator polynomial
        tmp_gen_degrees = gen_degrees
        tmp_gen_coeffs = gen_coeffs
        
        # Loop variable
        n = len(msg_coeffs)
        for i in range(n):
            # Reset the generator polynomial
            gen_degrees = tmp_gen_degrees
            gen_coeffs = tmp_gen_coeffs

            # Increase degree of generator polynomial by initial degree - i
            gen_degrees = [x + initial_degree - i for x in gen_degrees]

            # Get the lead term of the message polynomial
            lead_term = msg_coeffs[0]
            if lead_term == 0:
                alpha_lead_term = 1
            else:
                alpha_lead_term = self.GF256.index(lead_term)

            # Multiply the generator polynomial by the lead term
            gen_coeffs = [(x + alpha_lead_term) % 255 if x + alpha_lead_term > 255 else x + alpha_lead_term for x in gen_coeffs]

            # Remove lead term early
            msg_coeffs.pop(0)
            msg_degrees.pop(0)
            gen_coeffs.pop(0)
            gen_degrees.pop(0)

            # Divide the message polynomial by the generator polynomial
            for j in range(len(gen_coeffs)):
                if j < len(msg_coeffs):
                    msg_coeffs[j] = msg_coeffs[j] ^ self.GF256[gen_coeffs[j]]
                else:
                    msg_coeffs.append( 0 ^ self.GF256[gen_coeffs[j]])

            # Maintain needed length
            if len(msg_coeffs) < error_codewords_count:
                print("Maintaining length")
                msg_coeffs.append(0 ^ self.GF256[gen_coeffs[-1]])
            
        return msg_coeffs
            

    def add_error_correction(self, msg_coeffs):
        for coeff in msg_coeffs:
            bin_coeff = bin(coeff)[2:]
            bin_coeff = self.pad(bin_coeff, 8)
            bin_coeff = list(bin_coeff)
            bin_coeff = [int(i) for i in bin_coeff]
            self.modules.extend(bin_coeff)

    def place_finder(self, x, y):
        r = 7
        f = 1
        while r >= 3:
            for i in range(r):
                for j in range(r):
                    self.occupied_pixels.append((y + i, x + j))
                    self.image[y + i][x + j] = f
            r -= 2
            x += 1
            y += 1
            f ^= 1

    def place_separator(self, x, y):
        for i in range(8):
            for j in range(8):
                self.occupied_pixels.append((y + i, x + j))
                self.image[y + i][x + j] = 0

    def draw_finder_patterns(self, version):
        finder_locations = [(0, 0), ((((version - 1) * 4) + 21) - 7, 0), (0, (((version - 1) * 4) + 21) - 7)]
        
        for location in finder_locations:
            self.place_separator(location[0] - (1 if location[0] - 1 >= 0 else 0), location[1] - (1 if location[1] - 1 >= 0 else 0))

        for location in finder_locations:
            self.place_finder(location[0], location[1])

    def draw_timing_patterns(self, version):
        pixel = 1
        for i in range(6, (((version - 1) * 4) + 21) - 7):
            self.occupied_pixels.append((i, 6))
            self.occupied_pixels.append((6, i))
            self.image[i][6] = pixel
            self.image[6][i] = pixel

            pixel ^= 1

    def draw_dark_module(self, version):
        self.image[(4 * version) + 9][8] = 1

    def reserve_location(self, x, y):
        if x == 0 and y == 0:
            for i in range(9):
                for j in range(9):
                    if self.image[y + i][x + j] == -1:
                        self.occupied_pixels.append((y + i, x + j))
                        self.image[y + i][x + j] = -2

        elif x != 0 and y == 0:
            for i in range(9):
                for j in range(1, 9):
                    if self.image[y + i][x + j] == -1:
                        self.occupied_pixels.append((y + i, x + j))
                        self.image[y + i][x + j] = -2

        elif x == 0 and y != 0:
            for i in range(1, 9):
                for j in range(9):
                    if self.image[y + i][x + j] == -1:
                        self.occupied_pixels.append((y + i, x + j))
                        self.image[y + i][x + j] = -2

    def reserve_format_information(self, version):
        reserve_locations = [(0, 0), ((((version-1) * 4) + 21) - 9, 0), (0, (((version - 1) * 4) + 21) - 9)]

        for location in reserve_locations:
            self.reserve_location(location[0], location[1])

    def place_point(self, point, data, direction, ind):
        x, y = point[0], point[1]
        status = True
        placed = False
        if self.image[x][y] == -1:
            self.image[x][y] = data
        else:
            status = False

        if y - 1 == 6 and x == 0:
            y -= 1

        if direction == 0:
            if y - 1 >= 0:
                return (x, y - 1), status, 1
            else:
                print("There is a problem, y takes me out to the left")
        elif direction == 1:
            if x - 1 >= 0:
                if y + 1 < len(self.image):
                    return (x - 1, y + 1), status, 0
                else:
                    print("There is a problem, y takes me out to the right")
            else:
                return (x, y - 1), status, 2
        elif direction == 2:
            if y - 1 >= 0:
                return (x, y - 1), status, 3
            else:
                print("There is a problem, y takes me out to the left")
        elif direction == 3:
            if x + 1 < len(self.image):
                if y + 1 < len(self.image):
                    return (x + 1, y + 1), status, 2
                else:
                    print("There is a problem, y takes me out to the right")
            else:
                return (x, y - 1), status, 0


    def place_data(self):
        # print(self.modules)
        print(len(self.modules))
        point = (len(self.image) - 1, len(self.image) - 1)
        direction = 0
        status = False
        for i in range(0, len(self.modules)):
            status = False
            data = int(self.modules[i])
            while not status:
                point, status, direction = self.place_point(point, data, direction, i)
                if status == True:
                    break

    def place_format_information(self, error_correction, mask):
        error_correction_bits = 0
        if error_correction == "L":
            error_correction_bits = ["0", "1"]
        elif error_correction == "M":
            error_correction_bits = ["0", "0"]
        elif error_correction == "Q":
            error_correction_bits = ["1", "1"]
        elif error_correction == "H":
            error_correction_bits = ["1", "0"]

        mask_bits = bin(mask)[2:]
        
        format_string = str("".join(error_correction_bits)) + str(mask_bits)
        format_error_correction = self.format_error_correction(format_string)

        complete_format = str(format_string) + str(format_error_correction)
        complete_format = self.pad_right(complete_format, 15)

        xor_mask = "101010000010010"
        final_format = int(complete_format, 2) ^ int(xor_mask, 2)
        final_format = bin(final_format)[2:]

        final_format = self.pad(final_format, 15)

        pixels = {
            0: [(8, 0), (-1, 8)],
            1: [(8, 1), (-2, 8)],
            2: [(8, 2), (-3, 8)],
            3: [(8, 3), (-4, 8)],
            4: [(8, 4), (-5, 8)],
            5: [(8, 5), (-6, 8)],
            6: [(8, 7), (-7, 8)],
            7: [(8, 8), (8, -8)],
            8: [(7, 8), (8, -7)],
            9: [(5, 8), (8, -6)],
            10: [(4, 8), (8, -5)],
            11: [(3, 8), (8, -4)],
            12: [(2, 8), (8, -3)],
            13: [(1, 8), (8, -2)],
            14: [(0, 8), (8, -1)],
        }
        for i in range(len(final_format)):
            for pixel in pixels[i]:
                x, y = pixel
                self.image[x][y] = int(final_format[i])

    def format_error_correction(self, format_string):
        format_string = self.pad_right(format_string, 15)

        while len(format_string) >= 11:
            generator_string = "10100110111"    
            format_string = str(int(format_string))
            generator_string = self.pad_right(generator_string, len(format_string))
            
            format_string = int(format_string, 2) ^ int(generator_string, 2)
            format_string = bin(format_string)[2:]

        format_string = self.pad(format_string, 10)

        return format_string
    
    def copy_image(self, copy_to, copy_from):
        for x in range(len(copy_from)):
            for y in range(len(copy_from[x])):
                copy_to[x][y] = copy_from[x][y]
        return copy_to

    def evaluate_mask(self, error_correction):
        masks = {
            0: -1,
            1: -1,
            2: -1,
            3: -1,
            4: -1,
            5: -1,
            6: -1,
            7: -1
        }
        for mask in range(0, 8):
            self.place_format_information(error_correction, mask)
            self.evaluation_image = self.copy_image(self.evaluation_image, self.image)
            penalty = self.calculate_penalty(mask)
            masks[mask] += penalty
        
        mask = min(masks, key=masks.get)

        self.mask = mask
        return mask 
    
    def mask_image(self, mask, image):
        for x in range(len(image)):
            for y in range(len(image[x])):
                if (x, y) not in self.occupied_pixels:
                    mask_lambda = self.mask_lambdas[mask]
                    if mask_lambda(x, y):
                        image[x][y] ^= 1

    def first_condition(self, image=None):
        image = self.evaluation_image if image == None else image
        penalty = 0

        prev_color = image[0][0]
        for x in range(len(image)):
            run = 1
            for y in range(1, len(image)):
                if image[x][y] == prev_color:
                    run += 1
                    if y == len(image) - 1:
                        if run >= 5:
                            run -= 5
                            penalty += 3
                            penalty += run
                else:
                    if run >= 5:
                        run -= 5
                        penalty += 3
                        penalty += run
                    run = 1
                prev_color = image[x][y]

        prev_color = image[0][0]
        for y in range(len(image[0])):
            run = 1
            for x in range(1, len(image)):
                if image[x][y] == prev_color:
                    run += 1
                    if x == len(image) - 1:
                        if run >= 5:
                            run -= 5
                            penalty += 3
                            penalty += run
                else:
                    if run >= 5:
                        run -= 5
                        penalty += 3
                        penalty += run
                    run = 1
                prev_color = image[x][y]
        
        return penalty

    def second_condition(self, image=None):
        image = self.evaluation_image if image == None else image
        penalty = 0

        for x in range(len(image) - 2):
            for y in range(len(image) - 2):
                if image[x][y] == image[x][y + 1] == image[x + 1][y] == image[x + 1][y + 1]:
                    penalty += 3

        return penalty
    
    def third_condition(self, image=None):
        image = self.evaluation_image if image == None else image
        penalty = 0

        pattern1 = [1, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0]
        pattern2 = [0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 1]

        for x in range(len(image)):
            for y in range(len(image) - len(pattern1)):
                if image[x][y:y+len(pattern1)] == pattern1 or image[x][y:y+len(pattern2)] == pattern2:
                    penalty += 40

        for y in range(len(image)):
            for x in range(len(image) - len(pattern1)):
                if [image[i][y] for i in range(x, x + len(pattern1))] == pattern1 or [image[i][y] for i in range(x, x + len(pattern2))] == pattern2:
                    penalty += 40

        return penalty

    def fourth_condition(self, image=None):
        image = self.evaluation_image if image == None else image
        penalty = 0

        dark_count = 0
        for x in range(len(image)):
            for y in range(len(image)):
                if image[x][y] == 1:
                    dark_count += 1
        
        ratio = (dark_count / (len(image) ** 2)) * 100
        
        lower_percent = ratio // 1
        upper_percent = ratio // 1

        while lower_percent % 5 != 0:
            lower_percent -= 1

        while upper_percent % 5 != 0:
            upper_percent += 1

        lower_percent = abs(lower_percent - 50)
        upper_percent = abs(upper_percent - 50)

        result = min(lower_percent // 5, upper_percent // 5) * 10

        penalty += result
        return penalty

    def calculate_penalty(self, mask):
        self.mask_image(mask, self.evaluation_image)
        penalty = 0

        penalty += self.first_condition()
        penalty += self.second_condition()
        penalty += self.third_condition()
        penalty += self.fourth_condition()

        return penalty

    def draw_alignment_patterns(self, version):
        alignment_positions = {
            2: [6, 18],
            3: [6, 22],
            4: [6, 26],
            5: [6, 30],
            6: [6, 34],
            7: [6, 22, 38],
            8: [6, 24, 42],
            9: [6, 26, 46],
            10: [6, 28, 50],
            11: [6, 30, 54],
            12: [6, 32, 58],
            13: [6, 34, 62],
            14: [6, 26, 46, 66],
            15: [6, 26, 48, 70],
            16: [6, 26, 50, 74],
            17: [6, 30, 54, 78],
            18: [6, 30, 56, 82],
            19: [6, 30, 58, 86],
            20: [6, 34, 62, 90]
        }
        position = alignment_positions[version]
        for i in range(len(position)):
            for j in range(len(position)):
                self.place_alignment_pattern(position[i], position[j])

    def place_alignment_pattern(self, x, y):
        needed_pixels = []
        # x and y are the center of the alignment pattern
        # find the pixels that are needed if a 3x3 square is drawn around the center
        for i in range(3):
            for j in range(3):
                needed_pixels.append((x + i - 2, y + j - 2))

        # check if the needed pixels are occupied
        for pixel in needed_pixels:
            if pixel in self.occupied_pixels:
                return False
            
        # if not occupied, place the pattern
        for i in range(5):
            for j in range(5):
                self.occupied_pixels.append((x + i - 2, y + j - 2))
                self.image[x + i - 2][y + j - 2] = 1

        for i in range(3):
            for j in range(3):
                self.occupied_pixels.append((x + i - 1, y + j - 1))
                self.image[x + i - 1][y + j - 1] = 0

        self.occupied_pixels.append((x, y))
        self.image[x][y] = 1
    
    def generate_images(self):
        self.size = 21 + (self.version - 1) * 4
        self.image = [[-1 for _ in range(self.size)] for _ in range(self.size)]
        self.evaluation_image = [[-1 for _ in range(self.size)] for _ in range(self.size)]

    def add_remainder_bits(self):
        required_remainder_bits = {
            1: 0,
            2: 7,
            3: 7,
            4: 7,
            5: 7,
            6: 7,
            7: 0,
            8: 0,
            9: 0,
            10: 0,
            11: 0,
            12: 0,
            13: 0,
            14: 3,
            15: 3,
            16: 3,
            17: 3,
            18: 3,
            19: 3,
            20: 3
        }

        for i in range(required_remainder_bits[self.version]):
            self.modules.append(0)

    def break_into_blocks(self, version, error_correction):
        grouping = (
            # 1
            (1, 26, 19),
            (1, 26, 16),
            (1, 26, 13),
            (1, 26, 9),
            # 2
            (1, 44, 34),
            (1, 44, 28),
            (1, 44, 22),
            (1, 44, 16),
            # 3
            (1, 70, 55),
            (1, 70, 44),
            (2, 35, 17),
            (2, 35, 13),
            # 4
            (1, 100, 80),
            (2, 50, 32),
            (2, 50, 24),
            (4, 25, 9),
            # 5
            (1, 134, 108),
            (2, 67, 43),
            (2, 33, 15, 2, 34, 16),
            (2, 33, 11, 2, 34, 12),
            # 6
            (2, 86, 68),
            (4, 43, 27),
            (4, 43, 19),
            (4, 43, 15),
            # 7
            (2, 98, 78),
            (4, 49, 31),
            (2, 32, 14, 4, 33, 15),
            (4, 39, 13, 1, 40, 14),
            # 8
            (2, 121, 97),
            (2, 60, 38, 2, 61, 39),
            (4, 40, 18, 2, 41, 19),
            (4, 40, 14, 2, 41, 15),
            # 9
            (2, 146, 116),
            (3, 58, 36, 2, 59, 37),
            (4, 36, 16, 4, 37, 17),
            (4, 36, 12, 4, 37, 13),
            # 10
            (2, 86, 68, 2, 87, 69),
            (4, 69, 43, 1, 70, 44),
            (6, 43, 19, 2, 44, 20),
            (6, 43, 15, 2, 44, 16),
            # 11
            (4, 101, 81),
            (1, 80, 50, 4, 81, 51),
            (4, 50, 22, 4, 51, 23),
            (3, 36, 12, 8, 37, 13),
            # 12
            (2, 116, 92, 2, 117, 93),
            (6, 58, 36, 2, 59, 37),
            (4, 46, 20, 6, 47, 21),
            (7, 42, 14, 4, 43, 15),
            # 13
            (4, 133, 107),
            (8, 59, 37, 1, 60, 38),
            (8, 44, 20, 4, 45, 21),
            (12, 33, 11, 4, 34, 12),
            # 14
            (3, 145, 115, 1, 146, 116),
            (4, 64, 40, 5, 65, 41),
            (11, 36, 16, 5, 37, 17),
            (11, 36, 12, 5, 37, 13),
            # 15
            (5, 109, 87, 1, 110, 88),
            (5, 65, 41, 5, 66, 42),
            (5, 54, 24, 7, 55, 25),
            (11, 36, 12, 7, 37, 13),
            # 16
            (5, 122, 98, 1, 123, 99),
            (7, 73, 45, 3, 74, 46),
            (15, 43, 19, 2, 44, 20),
            (3, 45, 15, 13, 46, 16),
            # 17
            (1, 135, 107, 5, 136, 108),
            (10, 74, 46, 1, 75, 47),
            (1, 50, 22, 15, 51, 23),
            (2, 42, 14, 17, 43, 15),
            # 18
            (5, 150, 120, 1, 151, 121),
            (9, 69, 43, 4, 70, 44),
            (17, 50, 22, 1, 51, 23),
            (2, 42, 14, 19, 43, 15),
            # 19
            (3, 141, 113, 4, 142, 114),
            (3, 70, 44, 11, 71, 45),
            (17, 47, 21, 4, 48, 22),
            (9, 39, 13, 16, 40, 14),
            # 20
            (3, 135, 107, 5, 136, 108),
            (3, 67, 41, 13, 68, 42),
            (15, 54, 24, 5, 55, 25),
            (15, 43, 15, 10, 44, 16),
        )

        error_correction_offset = {
            "L": 0,
            "M": 1,
            "Q": 2,
            "H": 3 
        }
        # self.print_modules()

        offset = error_correction_offset[error_correction]
        version_grouping = grouping[(version - 1) * 4 + offset]

        blocks = []
        error_codewords = []

        # Copy self.modules to another list
        self.modules_copy = []
        for i in range(len(self.modules)):
            self.modules_copy.append(self.modules[i])

        for i in range(0, len(version_grouping), 3):
            blocks.append([])
            error_codewords.append([])
            count, total_count, data_count = version_grouping[i : i + 3]
            for _ in range(count):
                bits = data_count * 8
                blocks[-1].append(self.modules[:bits])
                self.modules = self.modules[bits:]
                error_codewords[-1].append([])

        return blocks, error_codewords

    def reserve_version_information(self, version):
        pass

    def place_version_information(self, version):
        pass

    def print_blocks(self, blocks):
        block_counter = 1
        group_counter = 1
        for block in blocks:
            print(f"Block {block_counter}", "\n")
            for group in block:
                print(f"Group {group_counter}", group, "\n")
                group_counter += 1
            block_counter += 1

    def interleave_blocks(self, blocks, groups):
        modules = []
        block1_size = int(len(blocks[0][0]) / 8)
        block2_size = int(len(blocks[1][0]) / 8)

        for i in range(0, min(block1_size, block2_size)):
            for idx in range(len(groups)):
                for j in range(8):
                    modules.append(groups[idx][j])

        if block1_size > block2_size:
            for i in range(block2_size, block1_size):
                for j in range(len(blocks[0])):
                    for k in range(8):
                        modules.append(blocks[0][j][k])

        elif block2_size > block1_size:
            for i in range(block1_size, block2_size):
                for j in range(len(blocks[1])):
                    for k in range(8):
                        modules.append(blocks[1][j][k])

        return modules
    
    def interleave_groups(self, groups):
        modules = []
        for i in range(len(groups)):
            print(i)
            for idx in range(len(groups)):
                for j in range(8):
                    modules.append(groups[idx][j])

        return modules

    def interleave_error_blocks(self, error_codewords, error_groups):
        modules = []

        error_block1_size = int(len(error_codewords[0][0]))
        error_block2_size = int(len(error_codewords[1][0]))
        for i in range(0, min(error_block1_size, error_block2_size)):
            for idx in range(4):
                for j in range(8):
                    modules.append(error_groups[idx][j])

        if error_block1_size > error_block2_size:
            for i in range(error_block2_size, error_block1_size):
                for j in range(len(error_codewords[0])):
                    for k in range(8):
                        modules.append(error_codewords[0][j][k])
        
        elif error_block2_size > error_block1_size:
            for i in range(error_block1_size, error_block2_size):
                for j in range(len(error_codewords[1])):
                    for k in range(8):
                        modules.append(error_codewords[1][j][k])

        return modules
    
    def interleave_error_groups(self, error_groups):
        modules = []
        for i in range(len(error_groups[0])):
            print(i)
            for idx in range(len(error_groups)):
                for j in range(8):
                    modules.append(error_groups[idx][j])

        return modules

    def interleave_modules(self, blocks, error_codewords):
        # self.print_blocks(blocks)
        # self.print_blocks(blocks)
        # self.print_blocks(error_codewords)
        
        modules = []
        groups = [inner_array for outer_array in blocks for inner_array in outer_array]

        error_groups = [inner_array for outer_array in error_codewords for inner_array in outer_array]
        error_groups = [
            [int(digit) for num in sublist for digit in format(num, '08b')]
            for sublist in error_groups
        ]

        if len(blocks) > 1:
            print("MULTIPLE BLOCKS")
            data_modules = self.interleave_blocks(blocks, groups)
            error_modules = self.interleave_error_blocks(error_codewords, error_groups)
        else:
            print("SINGLE BLOCK")
            for i in groups:
                print(len(i), i)
            for i in error_groups:
                print(len(i), i)
            data_modules = self.interleave_groups(groups)
            error_modules = self.interleave_error_groups(error_groups)

        modules.extend(data_modules)
        modules.extend(error_modules)

        print(len(modules))

        return modules

    def create(self, data, version=None, error_correction=None, mask=None):
        self.data = data
        self.data_type = self.determine_data_type(self.data)

        self.error_correction = error_correction if error_correction != None else self.error_correction if self.error_correction != None else "H"
        self.check_error_correction(self.error_correction)

        self.version = version if version != None else self.version if self.version != None else self.determine_version(self.data, self.data_type, self.error_correction) 
        self.check_version(self.version)
        self.generate_images()

        self.add_data_type(self.data_type)
        self.add_character_count(self.data, self.data_type, self.version)
        self.add_data(self.data, self.data_type)

        self.pad_modules(self.data, self.version, self.error_correction)

        self.blocks, self.error_codewords = self.break_into_blocks(self.version, self.error_correction)

        for b in range(len(self.blocks)):
            for g in range(len(self.blocks[b])):
                # print(self.blocks[b][g], end="\n\n")
                needed_error = self.needed_error_codewords[str(self.version) + str(self.error_correction)]
                msg_coeffs, msg_degrees = self.generate_message_polynomial(self.blocks[b][g])
                gen_coeffs, gen_degrees = self.generate_generator_polynomial(needed_error)
                self.error_codewords[b][g] = self.division(msg_coeffs, msg_degrees, gen_coeffs, gen_degrees, needed_error)

        self.modules = self.interleave_modules(self.blocks, self.error_codewords)

        self.add_remainder_bits()

        self.draw_finder_patterns(self.version)

        if self.version >= 2:
            self.draw_alignment_patterns(self.version)

        self.draw_timing_patterns(self.version)

        self.draw_dark_module(self.version)

        self.reserve_format_information(self.version)

        if self.version >= 7:
            self.reserve_version_information(self.version)

        self.place_data()

        # self.mask = mask if mask != None else self.mask if self.mask != None else self.determine_mask(data, self.version, self.error_correction)
        self.mask = self.evaluate_mask(self.error_correction)
        self.mask = 4
        self.mask_image(self.mask, self.image)

        self.place_format_information(self.error_correction, self.mask)

        if self.version >= 7:
            self.place_version_information(self.version)
        
        self.add_quite_zone()

    def fill_empty_space(self):
        random.seed(1)

        for x in range(len(self.image)):
            for y in range(len(self.image[x])):
                random_bit = random.randint(0, 1)
                if self.image[x][y] == -1 or self.image[x][y] == -2:
                    self.image[x][y] = random_bit

    def print_modules(self):
        print(len(self.modules))
        for i in range(len(self.modules)):
            print(self.modules[i], end="")
            if (i + 1) % 8 == 0 and i != len(self.modules) - 1:
                print()

    def add_quite_zone(self):
        l = [0] * self.size
        for i in range(self.quiet_zone):
            self.image = [l] + self.image + [l]

        for i in range(len(self.image)):
            self.image[i] = [0] * self.quiet_zone + self.image[i] + [0] * self.quiet_zone

    def enlarge_image(self, image=None):
        image = self.image if image == None else image
        scale = 20
        enlarged_size = (len(image[0]) * scale, len(image) * scale)
        
        enlarged_image = Image.new("RGB", enlarged_size, "white")
        pixels = enlarged_image.load()

        for y in range(len(image)):
            for x in range(len(image[y])):
                if image[x][y] == -3:
                    color = "red"
                elif image[y][x] == -1:
                    color = "gray"
                elif image[y][x] == 1:
                    color = "black"
                elif image[y][x] == -2:
                    color = "blue"
                else:
                    color = "white"

                for i in range(scale):
                    for j in range(scale):
                        c = (0, 0, 0)
                        if color == "blue":
                            c = (30, 144, 255)
                        elif color == "white":
                            c = (255, 255, 255)
                        elif color == "gray":
                            c = (128, 128, 128)
                        elif color == "red":
                            c = (255, 160, 122)
                        pixels[x * scale + i, y * scale + j] = (c)

        return enlarged_image


qr = QRCode(version=5)
qr.create("HELLO WORLD", error_correction="Q")
qr.show()
