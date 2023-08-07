class MessagePolynomial:
    def __init__(self):
        self.coeffs = []
        self.degrees = []

    def generate_polynomial(self, modules):
        degree = 0
        for i in range(0, len(modules), 8):
            byte = ""
            for i in modules[i:i+8]:
                byte += str(i)
            decimal_byte = int(byte, 2)
            self.coeffs.append(decimal_byte)

            self.degrees.append(degree)
            degree += 1
        
        self.degrees.reverse()

        return self.coeffs, self.degrees

    
    def print_polynomial(self):
        for coeff, degree in zip(self.coeffs, self.degrees):
            if degree != 0:
                print(f"{coeff}x^{degree}", end=" + ")
            else:
                print(f"{coeff}")

    def get_degree(self):
        print(self.degrees[0])
        return self.degrees[0]

    def get_coeff(self):
        print(self.coeffs)
        return self.coeffs