import random
import unittest

from poly import Polynomial

# ---------------------------------------------------------------------------
# ADAPTERS: the only place that knows your class's API. Edit these if needed.
# I assumed: coefficients in `.vals`, and operators +, -, *, % for the
# four operations. Change the lambdas if your methods are named differently
# (e.g. a.add(b), a.mod(x)).
# ---------------------------------------------------------------------------
def make(vals, p):
    return Polynomial(list(vals), p)


def coeffs(poly):
    """Coefficients, lowest degree first, high-degree zeros stripped."""
    v = list(poly.vals)
    while v and v[-1] == 0:
        v.pop()
    return v


def add(a, b):
    return a + b


def sub(a, b):
    return a - b


def mul(a, b):
    return a * b


def mod(y, x):
    return y.poly_mod(x)


# ---------------------------------------------------------------------------
# Independent reference implementations on plain lists
# ---------------------------------------------------------------------------
def strip(v):
    v = list(v)
    while v and v[-1] == 0:
        v.pop()
    return v


def ref_add(a, b, p):
    n = max(len(a), len(b))
    a = a + [0] * (n - len(a))
    b = b + [0] * (n - len(b))
    return strip((x + y) % p for x, y in zip(a, b))


def ref_sub(a, b, p):
    n = max(len(a), len(b))
    a = a + [0] * (n - len(a))
    b = b + [0] * (n - len(b))
    return strip((x - y) % p for x, y in zip(a, b))


def ref_mul(a, b, p):
    if not a or not b:
        return []
    out = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i + j] = (out[i + j] + x * y) % p
    return strip(out)


def ref_mod(y, x, p):
    """Schoolbook long division; returns the remainder only."""
    y, x = strip(c % p for c in y), strip(c % p for c in x)
    inv = pow(x[-1], -1, p)
    while len(y) >= len(x):
        q = y[-1] * inv % p
        shift = len(y) - len(x)
        for i, c in enumerate(x):
            y[shift + i] = (y[shift + i] - q * c) % p
        y = strip(y)
    return y


def rand_poly(p, max_len):
    return strip(random.randrange(p) for _ in range(random.randint(0, max_len)))


PRIMES = [2, 3, 5, 7, 13, 101]


class TestAddition(unittest.TestCase):
    def test_known(self):
        # (1 + 2x + 3x^2) + (4 + 4x + 4x^2) over F5 = x + 2x^2
        r = add(make([1, 2, 3], 5), make([4, 4, 4], 5))
        self.assertEqual(coeffs(r), [0, 1, 2])

    def test_different_lengths(self):
        r = add(make([1], 5), make([0, 0, 3], 5))
        self.assertEqual(coeffs(r), [1, 0, 3])

    def test_leading_terms_cancel(self):
        r = add(make([1, 2, 3], 5), make([0, 0, 2], 5))
        self.assertEqual(coeffs(r), [1, 2])

    def test_zero_identity(self):
        a = make([1, 2, 3], 7)
        self.assertEqual(coeffs(add(a, make([], 7))), [1, 2, 3])

    def test_commutative(self):
        for p in PRIMES:
            for _ in range(30):
                a, b = rand_poly(p, 8), rand_poly(p, 8)
                self.assertEqual(coeffs(add(make(a, p), make(b, p))),
                                 coeffs(add(make(b, p), make(a, p))))

    def test_inputs_not_mutated(self):
        a, b = make([1, 2, 3], 5), make([4, 4], 5)
        add(a, b)
        self.assertEqual(list(a.vals), [1, 2, 3])
        self.assertEqual(list(b.vals), [4, 4])

    def test_random_vs_reference(self):
        for p in PRIMES:
            for _ in range(50):
                a, b = rand_poly(p, 8), rand_poly(p, 8)
                self.assertEqual(coeffs(add(make(a, p), make(b, p))),
                                 ref_add(a, b, p))


class TestSubtraction(unittest.TestCase):
    def test_known_wraps_negative(self):
        # [1,2,3] - [4,4,4] over F5 = [-3,-2,-1] = [2,3,4]
        r = sub(make([1, 2, 3], 5), make([4, 4, 4], 5))
        self.assertEqual(coeffs(r), [2, 3, 4])

    def test_self_is_zero(self):
        a = make([3, 1, 4, 1], 7)
        self.assertEqual(coeffs(sub(a, make([3, 1, 4, 1], 7))), [])

    def test_leading_terms_cancel(self):
        r = sub(make([1, 2, 3], 5), make([0, 0, 3], 5))
        self.assertEqual(coeffs(r), [1, 2])

    def test_add_then_sub_roundtrip(self):
        for p in PRIMES:
            for _ in range(30):
                a, b = rand_poly(p, 8), rand_poly(p, 8)
                s = add(make(a, p), make(b, p))
                self.assertEqual(coeffs(sub(s, make(b, p))), a)

    def test_random_vs_reference(self):
        for p in PRIMES:
            for _ in range(50):
                a, b = rand_poly(p, 8), rand_poly(p, 8)
                self.assertEqual(coeffs(sub(make(a, p), make(b, p))),
                                 ref_sub(a, b, p))


class TestMultiplication(unittest.TestCase):
    def test_known(self):
        # (1 + x)^2 = 1 + 2x + x^2
        r = mul(make([1, 1], 5), make([1, 1], 5))
        self.assertEqual(coeffs(r), [1, 2, 1])

    def test_known_with_wraparound(self):
        # (x + 4)(x + 1) = x^2 + 5x + 4 = x^2 + 4 over F5
        r = mul(make([4, 1], 5), make([1, 1], 5))
        self.assertEqual(coeffs(r), [4, 0, 1])

    def test_known_2(self):
        # (3 + 2x)(1 + 3x) = 3 + 11x + 6x^2 = 3 + x + x^2 over F5
        r = mul(make([3, 2], 5), make([1, 3], 5))
        self.assertEqual(coeffs(r), [3, 1, 1])

    def test_one_is_identity(self):
        a = make([1, 2, 3], 7)
        self.assertEqual(coeffs(mul(a, make([1], 7))), [1, 2, 3])

    def test_zero_annihilates(self):
        a = make([1, 2, 3], 7)
        self.assertEqual(coeffs(mul(a, make([], 7))), [])

    def test_leading_coeffs_multiply_to_zero(self):
        # over F2 nothing vanishes, but over F5: leading terms stay nonzero
        # (field => no zero divisors); degree must add exactly.
        r = mul(make([1, 2], 5), make([3, 0, 4], 5))
        self.assertEqual(len(coeffs(r)), 4)

    def test_commutative_and_distributive(self):
        for p in PRIMES:
            for _ in range(20):
                a, b, c = (make(rand_poly(p, 6), p) for _ in range(3))
                self.assertEqual(coeffs(mul(a, b)), coeffs(mul(b, a)))
                self.assertEqual(coeffs(mul(a, add(b, c))),
                                 coeffs(add(mul(a, b), mul(a, c))))

    def test_inputs_not_mutated(self):
        a, b = make([1, 2, 3], 5), make([4, 4], 5)
        mul(a, b)
        self.assertEqual(list(a.vals), [1, 2, 3])
        self.assertEqual(list(b.vals), [4, 4])

    def test_random_vs_reference(self):
        for p in PRIMES:
            for _ in range(50):
                a, b = rand_poly(p, 8), rand_poly(p, 8)
                self.assertEqual(coeffs(mul(make(a, p), make(b, p))),
                                 ref_mul(a, b, p))


class TestModularReduction(unittest.TestCase):
    def test_lower_degree_unchanged(self):
        r = mod(make([1, 2], 5), make([1, 1, 1], 5))
        self.assertEqual(coeffs(r), [1, 2])

    def test_x_cubed_mod_x2_x_1(self):
        # x^3 = 1 mod (x^2 + x + 1) over F5
        r = mod(make([0, 0, 0, 1], 5), make([1, 1, 1], 5))
        self.assertEqual(coeffs(r), [1])

    def test_x_squared_mod_x2_x_1(self):
        # x^2 = -x - 1 = 4x + 4 over F5
        r = mod(make([0, 0, 1], 5), make([1, 1, 1], 5))
        self.assertEqual(coeffs(r), [4, 4])

    def test_non_monic_modulus(self):
        # X = 2x^2 + 3 over F5 => x^2 = 1, so x^3 + x^2 = x + 1
        r = mod(make([0, 0, 1, 1], 5), make([3, 0, 2], 5))
        self.assertEqual(coeffs(r), [1, 1])

    def test_multiple_of_modulus_is_zero(self):
        p = 7
        x = make([2, 0, 1, 3], p)
        q = make([5, 1, 4], p)
        self.assertEqual(coeffs(mod(mul(x, q), x)), [])

    def test_result_degree_below_modulus(self):
        for p in PRIMES:
            for _ in range(30):
                x = rand_poly(p, 5)
                if len(x) < 2:
                    continue
                y = rand_poly(p, 12)
                r = mod(make(y, p), make(x, p))
                self.assertLess(len(coeffs(r)), len(x))

    def test_inputs_not_mutated(self):
        y, x = make([0, 0, 0, 1], 5), make([1, 1, 1], 5)
        mod(y, x)
        self.assertEqual(list(y.vals), [0, 0, 0, 1])
        self.assertEqual(list(x.vals), [1, 1, 1])

    def test_random_vs_reference(self):
        for p in PRIMES:
            for _ in range(60):
                x = rand_poly(p, 6)
                if len(x) < 2:
                    continue
                y = rand_poly(p, 14)
                self.assertEqual(coeffs(mod(make(y, p), make(x, p))),
                                 ref_mod(y, x, p),
                                 msg=f"p={p} y={y} x={x}")

    def test_reduction_respects_ring_homomorphism(self):
        # (a*b) mod X == ((a mod X) * (b mod X)) mod X
        for p in PRIMES:
            for _ in range(20):
                x = rand_poly(p, 5)
                if len(x) < 2:
                    continue
                a, b = make(rand_poly(p, 8), p), make(rand_poly(p, 8), p)
                X = make(x, p)
                lhs = mod(mul(a, b), X)
                rhs = mod(mul(mod(a, X), mod(b, X)), X)
                self.assertEqual(coeffs(lhs), coeffs(rhs))


if __name__ == "__main__":
    unittest.main()
