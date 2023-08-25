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
    
    def print_polynomial(coeffs, degrees):
        s = ""
        for i in range(len(coeffs)):
            if i == len(coeffs) - 1:
                s += str(coeffs[i]) + "x^" + (str(degrees[i]) if not i >= len(degrees) else str(0))
            else:
                s += str(coeffs[i]) + "x^" + (str(degrees[i]) if not i >= len(degrees) else str(0)) + " + "

        print(s)

    def get_degree(self):
        print(self.degrees[0])
        return self.degrees[0]

    def get_coeff(self):
        print(self.coeffs)
        return self.coeffs