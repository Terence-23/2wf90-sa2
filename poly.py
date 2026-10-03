

class Polynomial:
    vals = []
    modulus = 0
    
    def format(self , var: str = "x") -> str:
        self.reduce()
        coeffs =self.vals
        if coeffs == [0]:
            return "0"

        terms = []
        # Process terms from highest degree down to constant term
        for degree in range(len(coeffs) - 1, -1, -1):
            coeff = coeffs[degree]
            if coeff == 0:
                continue

            abs_coeff = abs(coeff)
            
            # Build variable string
            if degree == 0:
                var_part = ""
            elif degree == 1:
                var_part = var
            else:
                var_part = f"{var}^{degree}"

            # Build coefficient string (omit '1' unless it's the constant term)
            if abs_coeff == 1 and degree > 0:
                coeff_part = ""
            else:
                coeff_part = f"{int(abs_coeff) if abs_coeff.is_integer() else abs_coeff}"

            term = f"{coeff_part}{var_part}"

            # Determine sign and formatting
            if not terms:  # Leading term
                sign = "-" if coeff < 0 else ""
                terms.append(f"{sign}{term}")
            else:
                sign = " - " if coeff < 0 else " + "
                terms.append(f"{sign}{term}")

        return "".join(terms)
    __str__ = lambda self: self.format('x')

    def __init__(self, poly: list[int], modulus: int):
        self.vals = poly
        self.modulus = modulus
    
    def reduce(self):
        vals = [x%self.modulus for x in self.vals]
        while len(vals) > 1 and vals[-1] == 0:
            vals.pop()

        self.vals = vals

    def add(self, oth):
        l = max(len(self.vals), len(oth.vals))
        pad_self = self.vals + [0] * (l-len(self.vals))
        pad_oth =  oth.vals + [0]* (l-len(oth.vals))

        res = Polynomial([x+y for x, y in zip(pad_self, pad_oth)], self.modulus)
        res.reduce()
        return res

    def __neg__(self):
        vals = [ self.modulus-x for x in self.vals]
        return Polynomial(vals, self.modulus)

    __add__ = add
    def __sub__(self, oth):
        return self + (-oth)

    def mul(self, oth):
        vals = [0] * (len(self.vals) + len(oth.vals) + 1)
        for i,x in enumerate(self.vals):
            for j, y in enumerate(oth.vals):
                vals[i+j] += x*y

        res = Polynomial(vals, self.modulus)
        res.reduce()
        return res

    def int_mul(self, x):
        vals = [a*x for a in self.vals]
        res = Polynomial(vals, self.modulus)
        res.reduce()
        return res
    __mul__  = mul 
    
    def clone(self):
        return Polynomial(self.vals[::], self.modulus)

    def pow(self, exp: int):
        base = self.clone()
        res = Polynomial([1], self.modulus)
        while exp > 0:
            if exp %2 != 0:
                res = base * res
            exp //=2
            base = base*base
        return res
    __pow__ = pow

    def _mod_conversion(self):
        res = self.clone()
        res.reduce()
        x = res.vals.pop()
        res = (-res).int_mul(pow(x, -1, res.modulus))
        res.reduce()
        return res
            
    def poly_mod(self, modulus):
        sub = modulus._mod_conversion()
        deg_m = len(modulus.vals)
        v = self.clone()
        while len(v.vals) >= deg_m:
            deg_p = len(v.vals)
            coeff = v.vals.pop()
            v = v + Polynomial([0]*(deg_p - deg_m) + sub.int_mul(coeff).vals, v.modulus)
            v.reduce()
        return v

