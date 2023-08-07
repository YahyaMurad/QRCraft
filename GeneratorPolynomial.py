from copy import copy

def remove_elements(original_list, indices_to_remove):
    # Create a new list without the elements at the specified indices
    return [element for index, element in enumerate(original_list) if index not in indices_to_remove]


class Term:
    def __init__(self, part_alpha, part_x):
        self.part_alpha = part_alpha
        self.part_x = part_x
        self.GF256 = [1, 2, 4, 8, 16, 32, 64, 128, 29, 58, 116, 232, 205, 135, 19, 38, 76, 152, 45, 90, 180, 117, 234, 201, 143, 3, 6, 12, 24, 48, 96, 192, 157, 39, 78, 156, 37, 74, 148, 53, 106, 212, 181, 119, 238, 193, 159, 35, 70, 140, 5, 10, 20, 40, 80, 160, 93, 186, 105, 210, 185, 111, 222, 161, 95, 190, 97, 194, 153, 47, 94, 188, 101, 202, 137, 15, 30, 60, 120, 240, 253, 231, 211, 187, 107, 214, 177, 127, 254, 225, 223, 163, 91, 182, 113, 226, 217, 175, 67, 134, 17, 34, 68, 136, 13, 26, 52, 104, 208, 189, 103, 206, 129, 31, 62, 124, 248, 237, 199, 147, 59, 118, 236, 197, 151, 51, 102, 204, 133, 23, 46, 92, 184, 109, 218, 169, 79, 158, 33, 66, 132, 21, 42, 84, 168, 77, 154, 41, 82, 164, 85, 170, 73, 146, 57, 114, 228, 213, 183, 115, 230, 209, 191, 99, 198, 145, 63, 126, 252, 229, 215, 179, 123, 246, 241, 255, 227, 219, 171, 75, 150, 49, 98, 196, 149, 55, 110, 220, 165, 87, 174, 65, 130, 25, 50, 100, 200, 141, 7, 14, 28, 56, 112, 224, 221, 167, 83, 166, 81, 162, 89, 178, 121, 242, 249, 239, 195, 155, 43, 86, 172, 69, 138, 9, 18, 36, 72, 144, 61, 122, 244, 245, 247, 243, 251, 235, 203, 139, 11, 22, 44, 88, 176, 125, 250, 233, 207, 131, 27, 54, 108, 216, 173, 71, 142, 1]

    def __str__(self):
        s = ""
        s += "a^" + str(self.part_alpha) + "x^" + str(self.part_x)
        return s
    
    def multiply(self, term):
        # print("(" + str(self) + " * " + str(term) + ")", end=" = ")
        result = Term(0, 0)
        result.part_alpha = self.part_alpha + term.part_alpha
        result.part_x = self.part_x + term.part_x
        # print("result", result)
        if result.part_alpha > 255:
            # print("\n\n***************Decreasing Alpha***************\n\n")
            result.part_alpha %= 255

        return result
    
    def combine_terms(self, term):
        result = Term(0, 0)
        index = self.GF256[self.part_alpha] ^ self.GF256[term.part_alpha]
        result.part_alpha = self.GF256.index(index if index <= 255 else index % 255)
        # result.part_alpha = self.GF256.index(self.GF256[self.part_alpha] + self.GF256[term.part_alpha])
        result.part_x = self.part_x

        return result

class Polynomial:
    def __init__(self):
        self.terms = []

    def add_term(self, term):
        self.terms.append(term)

    def __str__(self):
        s = ""
        if len(self.terms) == 2:
            s += str(self.terms[0]) + " - " + str(self.terms[1])
        else:
            for i in range(len(self.terms)):
                if i == len(self.terms) - 1:
                    s += str(self.terms[i])
                else:
                    s += str(self.terms[i]) + " + "

        return s
    
    def multiply(self, poly):
        result = Polynomial()
        for term in self.terms:
            for term2 in poly.terms:
                result_term = term.multiply(term2)
                # print(result_term)
                result.add_term(result_term)

        return result
    
    def copy_poly(self, from_poly, to_poly):
        for term in from_poly.terms:
            to_poly.add_term(term)

        return to_poly

    def combine_like_terms(self):
        result = Polynomial()
        terms_to_add = []
        terms_to_remove = []
        result = self.copy_poly(self, result)
        changed = False
        for i in range(len(self.terms)):
            for j in range(i, len(self.terms)):
                if i != j:
                    if self.terms[i].part_x == self.terms[j].part_x:
                        # print("Inside Combine", result)
                        # print("Combining", self.terms[i], self.terms[j])
                        new_term = self.terms[i].combine_terms(self.terms[j])
                        # print("Combined", new_term)
                        result.terms.pop(j)
                        result.terms[i] = new_term
                        # result.terms.append(new_term)
                        # result.terms.remove(self.terms[i])
                        # terms_to_add.append(new_term)
                        # terms_to_remove.append(j)
                        # terms_to_remove.append(i)
                        changed = True
                        return result, changed

        # result.terms = remove_elements(result.terms, terms_to_remove)

        # for term in terms_to_add:
        #     result.terms.append(term)
        
        return result, changed

        
class GeneratorPolynomial:
    def __init__(self):
        self.GF256 = [1, 2, 4, 8, 16, 32, 64, 128, 29, 58, 116, 232, 205, 135, 19, 38, 76, 152, 45, 90, 180, 117, 234, 201, 143, 3, 6, 12, 24, 48, 96, 192, 157, 39, 78, 156, 37, 74, 148, 53, 106, 212, 181, 119, 238, 193, 159, 35, 70, 140, 5, 10, 20, 40, 80, 160, 93, 186, 105, 210, 185, 111, 222, 161, 95, 190, 97, 194, 153, 47, 94, 188, 101, 202, 137, 15, 30, 60, 120, 240, 253, 231, 211, 187, 107, 214, 177, 127, 254, 225, 223, 163, 91, 182, 113, 226, 217, 175, 67, 134, 17, 34, 68, 136, 13, 26, 52, 104, 208, 189, 103, 206, 129, 31, 62, 124, 248, 237, 199, 147, 59, 118, 236, 197, 151, 51, 102, 204, 133, 23, 46, 92, 184, 109, 218, 169, 79, 158, 33, 66, 132, 21, 42, 84, 168, 77, 154, 41, 82, 164, 85, 170, 73, 146, 57, 114, 228, 213, 183, 115, 230, 209, 191, 99, 198, 145, 63, 126, 252, 229, 215, 179, 123, 246, 241, 255, 227, 219, 171, 75, 150, 49, 98, 196, 149, 55, 110, 220, 165, 87, 174, 65, 130, 25, 50, 100, 200, 141, 7, 14, 28, 56, 112, 224, 221, 167, 83, 166, 81, 162, 89, 178, 121, 242, 249, 239, 195, 155, 43, 86, 172, 69, 138, 9, 18, 36, 72, 144, 61, 122, 244, 245, 247, 243, 251, 235, 203, 139, 11, 22, 44, 88, 176, 125, 250, 233, 207, 131, 27, 54, 108, 216, 173, 71, 142, 1]

    def create_polynomial(self, degree):
        polynomial = Polynomial()

        term = Term(0, 1)
        polynomial.add_term(term)

        term = Term(degree, 0)
        polynomial.add_term(term)

        return polynomial

    def generate_polynomial(self, power):
        # result = self.create_polynomial(0).multiply(self.create_polynomial(1))
        # changed = True
        # while changed == True:
        #     result, changed = result.combine_like_terms()
    
        # result = result.multiply(self.create_polynomial(2))
        # result, changed = result.combine_like_terms()
        # print(result)
        # print(result)

        polynomials = []
        for i in range(0, power):
            polynomials.append(self.create_polynomial(i))

        # result = polynomials[0].multiply(polynomials[1])
        # changed = True
        # while changed == True:
        #     result, changed = result.combine_like_terms()
        
        # result = result.multiply(polynomials[2])
        # changed = True
        # while changed == True:
        #     result, changed = result.combine_like_terms()

        # print(result)
        while len(polynomials) > 1:
            # print("Multiplying (" + str(polynomials[0]) + ") * (" + str(polynomials[1]) + ")")
            result = polynomials[0].multiply(polynomials[1])
            # print("Result", result)
            changed = True
            loops = 1
            # print("Combining like terms")
            while changed == True:
                result, changed = result.combine_like_terms()
                # print(f"After combining like terms {loops} time(s)", result)
                loops += 1
            
            polynomials.pop(0)
            polynomials.pop(0)
            polynomials.insert(0, result)
            
        # print(polynomials[0])

        return self.get_coeffs(polynomials[0]), self.get_degrees(polynomials[0])

    def get_coeffs(self, polynomial):
        ret = []
        for term in polynomial.terms:
            ret.append(term.part_alpha)

        return ret

    def get_degrees(self, polynomial):
        ret = []
        for term in polynomial.terms:
            ret.append(term.part_x)

        return ret