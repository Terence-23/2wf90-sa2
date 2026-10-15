

def prime_divisors(n):
    """List of distinct prime divisors of n"""
    primes = []
    divisor = 2
    while divisor ** 2 <= n:
        if n % divisor == 0:
            primes.append(divisor)

            while n % divisor == 0:
                n //= divisor

        divisor += 1

    if n > 1:
        primes.append(n)

    return primes


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

    def pow_mod(self, exp: int, h):
        """self^exp mod h by square-and-multiply, reducing every step."""
        res = Polynomial([1], self.modulus)
        base = self.poly_mod(h)

        while exp > 0:
            if exp % 2 != 0:
                res = (res * base).poly_mod(h)
            exp //= 2
            base = (base * base).poly_mod(h)
        return res

    def is_primitive(self, h):
        f = self.poly_mod(h)
        f.reduce()

        if f.vals == [0]:
            return False

        order = self.modulus ** (len(h.vals) - 1) - 1
        return all(f.pow_mod(order // r, h).vals != [1] for r in prime_divisors(order))

    @classmethod
    def generate_primitive(cls, h):
        """Return the first primitive element of Z_p[X]/(h), counting up in base p."""
        p = h.modulus
        n = len(h.vals) - 1
        for number in range(1, p ** n):
            coefficients = []
            for _ in range(n):
                coefficients.append(number % p)
                number //= p

            candidate = cls(coefficients, p)
            candidate.reduce()
            if candidate.is_primitive(h):
                return candidate.vals

        raise RuntimeError("Could not generate a primitive element")

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

        # Check x^(p^n) = x mod f.
        if x.pow_mod(p ** n, f).vals != x.vals:
            return False

        # Check gcd(f, x^(p^(n/q)) - x) = 1.
        for q in prime_divisors(n):
            test = x.pow_mod(p ** (n // q), f) - x
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

    def invert(self, h):
        f = self.poly_mod(h)
        f.reduce()
        if f.vals == [0]:
            raise ValueError("Zero polynomial has no inverse")
        a, _, d = f.extended_gcd(h)
        if d.vals != [1]:
            raise ValueError("Polynomial is not invertible modulo h")
        ret = a.poly_mod(h)
        a.reduce()
        return a
