

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

    
    def divmod(self, oth):
        """Return quotient q and remainder r."""
        if self.modulus != oth.modulus:
            raise ValueError("Moduli must match")

        p = self.modulus
        f = self.clone()
        g = oth.clone()
        f.reduce()
        g.reduce()

        if g.vals == [0]:
            raise ZeroDivisionError("Division by zero polynomial")

        quotient = [0] * max(1, len(f.vals) - len(g.vals) + 1)
        remainder = f.vals[:]
        inv_lc = pow(g.vals[-1], -1, p)

        while remainder != [0] and len(remainder) >= len(g.vals):
            shift = len(remainder) - len(g.vals)
            factor = remainder[-1] * inv_lc % p
            quotient[shift] = factor

            for i, coeff in enumerate(g.vals):
                remainder[i + shift] = (
                    remainder[i + shift] - factor * coeff
                ) % p

            while len(remainder) > 1 and remainder[-1] == 0:
                remainder.pop()

        q = Polynomial(quotient, p)
        r = Polynomial(remainder, p)
        q.reduce()
        r.reduce()
        return q, r

    __divmod__ = divmod

    def is_irreducible(self):
        self.reduce()
        p = self.modulus
        n = len(self.vals) - 1

        if n < 1:
            return False

        if n == 1:
            return True

        # Make the polynomial monic.
        f = self.int_mul(pow(self.vals[-1], -1, p))
        f.reduce()

        x = Polynomial([0, 1], p)

        def power_mod(base, exponent):
            result = Polynomial([1], p)
            base = base.poly_mod(f)

            while exponent > 0:
                if exponent % 2 == 1:
                    result = (result * base).poly_mod(f)

                base = (base * base).poly_mod(f)
                exponent //= 2

            result.reduce()
            return result

        # Check x^(p^n) = x mod f.
        if power_mod(x, p ** n).vals != x.vals:
            return False

        # Find the distinct prime divisors of n.
        number = n
        divisor = 2
        prime_divisors = []

        while divisor * divisor <= number:
            if number % divisor == 0:
                prime_divisors.append(divisor)
                while number % divisor == 0:
                    number //= divisor

            divisor += 1

        if number > 1:
            prime_divisors.append(number)

        # Check gcd(f, x^(p^(n/q)) - x) = 1.
        for q in prime_divisors:
            test = power_mod(x, p ** (n // q)) - x
            _, _, gcd = f.extended_gcd(test)

            gcd.reduce()

            if gcd.vals != [1]:
                return False

        return True
        
    @classmethod
    def generate_irreducible(cls, modulus, degree):
        if degree < 1:
            raise ValueError("Degree must be positive")

        # Every degree-one polynomial is irreducible.
        if degree == 1:
            return [0, 1]

        # Enumerate monic polynomials
        for number in range(modulus ** degree):
            coefficients = []

            for _ in range(degree):
                coefficients.append(number % modulus)
                number //= modulus

            candidate = coefficients + [1]

            if cls(candidate, modulus).is_irreducible():
                return candidate

        raise RuntimeError(
            "Could not generate an irreducible polynomial"
        )

    def extended_gcd(self, oth):
        """Return a, b, d such that a*self + b*oth = d."""
        if self.modulus != oth.modulus:
            raise ValueError("Moduli must match")

        p = self.modulus
        r0, r1 = self.clone(), oth.clone()
        r0.reduce()
        r1.reduce()

        if r0.vals == [0] and r1.vals == [0]:
            raise ValueError("GCD of two zero polynomials is undefined")

        a0, a1 = Polynomial([1], p), Polynomial([0], p)
        b0, b1 = Polynomial([0], p), Polynomial([1], p)

        while r1.vals != [0]:
            q, r2 = r0.divmod(r1)
            r0, r1 = r1, r2
            a0, a1 = a1, a0 - q * a1
            b0, b1 = b1, b0 - q * b1

        # Normalize the gcd to make it monic.
        inv_lc = pow(r0.vals[-1], -1, p)
        a0 = a0.int_mul(inv_lc)
        b0 = b0.int_mul(inv_lc)
        d = r0.int_mul(inv_lc)

        a0.reduce()
        b0.reduce()
        d.reduce()
        return a0, b0, d
