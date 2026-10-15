"""
Runs solve.solve_exercise on every exercise in Examples/Simple and Examples/Realistic,
compares against the provided answers, and reports timing.

Usage:
    python run_examples.py [examples_dir] [time_limit_seconds]

Defaults: examples_dir = "Examples", time_limit = 5

Expected layout (adjust EXERCISE_DIR / ANSWER_DIR below if yours differs):
    Examples/Simple/Exercises/exercise0.json      Examples/Simple/Answers/answer0.json
    Examples/Realistic/Exercises/exercise0.json   Examples/Realistic/Answers/answer0.json

Our own outputs go to Examples/<set>/Outputs/ so the provided answers are never overwritten.
"""
import json
import os
import re
import sys
import time

import solve  # your solve.py

EXERCISE_DIR = "Exercises"
ANSWER_DIR = "Answers"
OUTPUT_DIR = "Outputs"
SETS = ["Simple", "Realistic"]


def number_of(filename):
    m = re.search(r"(\d+)", filename)
    return int(m.group(1)) if m else None


def parse(s, radix):
    """Test-only helper (uses built-in int, fine outside the submission)."""
    return int(s, radix)


def eea_valid(exercise, ours):
    """Bezout coefficients aren't unique, so check a*x + b*y = gcd instead."""
    r = exercise["radix"]
    x, y = parse(exercise["x"], r), parse(exercise["y"], r)
    a, b, g = (parse(ours[k], r) for k in ("answer-a", "answer-b", "answer-gcd"))
    from math import gcd
    return g == gcd(x, y) and a * x + b * y == g


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else "Examples"
    limit = float(sys.argv[2]) if len(sys.argv) > 2 else 5.0

    total = passed = slow = errors = 0
    slowest = (0.0, "")

    for name in SETS:
        ex_dir = os.path.join(root, name, EXERCISE_DIR)
        ans_dir = os.path.join(root, name, ANSWER_DIR)
        out_dir = os.path.join(root, name, OUTPUT_DIR)
        if not os.path.isdir(ex_dir):
            print(f"[skip] {ex_dir} not found")
            continue
        os.makedirs(out_dir, exist_ok=True)

        expected = {}
        if os.path.isdir(ans_dir):
            for f in os.listdir(ans_dir):
                if f.endswith(".json"):
                    expected[number_of(f)] = os.path.join(ans_dir, f)

        files = sorted((f for f in os.listdir(ex_dir) if f.endswith(".json")),
                       key=lambda f: (number_of(f) is None, number_of(f), f))
        print(f"\n=== {name}: {len(files)} exercises ===")

        for f in files:
            n = number_of(f)
            ex_path = os.path.join(ex_dir, f)
            out_path = os.path.join(out_dir, f"answer{n}.json")
            total += 1

            t0 = time.perf_counter()
            try:
                solve.solve_exercise(ex_path, out_path)
            except BaseException as e:  # includes RecursionError
                errors += 1
                print(f"[ERROR] {name}/{f}: {type(e).__name__}: {e}")
                continue
            dt = time.perf_counter() - t0
            if dt > slowest[0]:
                slowest = (dt, f"{name}/{f}")

            with open(ex_path) as fh:
                exercise = json.load(fh)
            with open(out_path) as fh:
                ours = json.load(fh)

            status = "?"
            if n in expected:
                with open(expected[n]) as fh:
                    want = json.load(fh)
                if ours == want:
                    status = "OK"
                elif (exercise.get("operation") == "extended_euclidean_algorithm"
                      and want.get("answer-gcd") is not None
                      and ours.get("answer-gcd") == want["answer-gcd"]
                      and eea_valid(exercise, ours)):
                    status = "OK (different valid Bezout coefficients)"
                else:
                    status = "WRONG"
            else:
                status = "no expected answer"

            too_slow = dt > limit
            if too_slow:
                slow += 1
            if status.startswith("OK"):
                passed += 1

            if status == "WRONG" or too_slow or status == "no expected answer":
                flag = " TOO SLOW" if too_slow else ""
                print(f"[{status}] {name}/{f} ({exercise['task']}) {dt:.2f}s{flag}")
                if status == "WRONG":
                    print(f"    ours:     {json.dumps(ours)[:200]}")
                    print(f"    expected: {json.dumps(want)[:200]}")

    print("\n=== Summary ===")
    print(f"total: {total}, correct: {passed}, errors: {errors}, over {limit:g}s: {slow}")
    if slowest[1]:
        print(f"slowest: {slowest[1]} at {slowest[0]:.2f}s")


if __name__ == "__main__":
    main()
