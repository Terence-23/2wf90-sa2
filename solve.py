##
# 2WF90 Algebra for Security -- Software Assignment 2
# Polynomial and Finite Field Arithmetic
# solve.py
#
#
# Group number: 51
# group_number 
#
# Author names and student IDs:
# author_name_1 (author_student_ID_1) 
# Grace Borrebach (2255111)
# author_name_3 (author_student_ID_3)
# author_name_4 (author_student_ID_4)
##

# Import built-in json library for handling input/output 
import json
from poly import Polynomial

def solve_exercise(exercise_location : str, answer_location : str):
    """
    solves an exercise specified in the file located at exercise_location and
    writes the answer to a file at answer_location. Note: the file at
    answer_location might not exist yet and, hence, might still need to be created.
    """
    
    # Open file at exercise_location for reading.
    with open(exercise_location, "r") as exercise_file:
        # Deserialize JSON exercise data present in exercise_file to corresponding Python exercise data 
        exercise = json.load(exercise_file)
        

    ### Parse and solve ###

    # Check type of exercise
    if exercise["type"] == "polynomial_arithmetic":
        # Check what task within the polynomial arithmetic tasks we need to perform
        p = exercise["integer_modulus"]
        f = Polynomial(exercise["f"], p) if "f" in exercise else None
        g = Polynomial(exercise["g"], p) if "g" in exercise else None

        if exercise["task"] == "addition":
            # Solve polynomial arithmetic addition exercise
            answer = {
                "answer": (f + g).vals
            }

        elif exercise["task"] == "subtraction":
            # Solve polynomial arithmetic subtraction exercise
            answer = {
                "answer": (f - g).vals
            }
        elif exercise["task"] == "multiplication":
            answer = {
                "answer": (f * g).vals
            }
        elif exercise["task"] == "long_division":
            try:
                q,r = map(lambda x: x.vals, f.divmod(g))
            except ValueError:
                q,r = [None]*2

            answer = {
                "answer-q": q,
                "answer-r": r
            }

        elif exercise["task"] == "extended_euclidean_algorithm":
            try:
                a,b,d = map(lambda x: x.vals,f.extended_gcd(g))
            except ValueError:
                a,b,d = [None]*3
            answer = {
                "answer-a": a,
                "answer-b": b,
                "answer-gcd": d
            }

        elif exercise["task"] == "irreducibility_check":
            # Solve polynomial irreducibility check exercise
            answer = {
                "answer": f.is_irreducible()
            }
            
        elif exercise["task"] == "irreducible_element_generation":
            # Solve polynomial irreducible element generation exercise
            p = exercise["integer_modulus"]
            answer = {
                "answer": Polynomial.generate_irreducible(
                    p,
                    exercise["degree"]
                )
            }

        else:
            raise ValueError(
                f"Unsupported polynomial arithmetic task: {exercise['task']}"
            )
            
    elif exercise["type"] == "finite_field_arithmetic":
        # Check what task within the finite field arithmetic tasks we need to perform
        p = exercise["integer_modulus"]
        h = Polynomial(exercise["polynomial_modulus"], p)
        # "f" and "g" are absent for some tasks (e.g. primitive_element_generation)
        f = Polynomial(exercise["f"], p) if "f" in exercise else None
        g = Polynomial(exercise["g"], p) if "g" in exercise else None

        if exercise["task"] == "addition":
            # Solve finite field arithmetic addition exercise
            answer = {
                "answer": (f + g).poly_mod(h).vals
            }
        elif exercise["task"] == "subtraction":
            answer = {
                "answer": (f - g).poly_mod(h).vals
            }

        elif exercise["task"] == "multiplication":
            answer = {
                "answer": (f * g).poly_mod(h).vals
            }

        elif exercise["task"] == "inversion":
            try:
                res = f.invert(h).vals
            except ValueError:
                res = None
            answer = {
                "answer": res
            }

        elif exercise["task"] == "division":
            try:
                res = (f * g.invert(h)).poly_mod(h).vals
            except ValueError:
                res = None
            answer = {
                "answer": res
            }

        elif exercise["task"] == "primitivity_check":
            answer = {
                "answer": f.is_primitive(h)
            }

        elif exercise["task"] == "primitive_element_generation":
            answer = {
                "answer": Polynomial.generate_primitive(h)
            }

        else:
            raise ValueError(
                f"Unsupported finite field task: {exercise['task']}"
            )

    else:
        raise ValueError(
            f"Unsupported exercise type: {exercise['type']}"
        )


    # Open file at answer_location for writing, creating the file if it does not exist yet
    # (and overwriting it if it does already exist).
    with open(answer_location, "w") as answer_file:
        # Serialize Python answer data (stored in answer) to JSON answer data and write it to answer_file
        json.dump(answer, answer_file, indent=4)



# You can call your function from here
# Please do not *run* code outside this block
# You can however define other functions or constants
if __name__ == '__main__':
    solve_exercise('Simple/Exercises/exercise0.json', 'Simple/Answers/answer0.json')
