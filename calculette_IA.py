import math
def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero.")
    return a / b

def display_result(result):
    print("Le résultat est:", result)

def calculate():
    while True:
        op1 = float(input("Saisissez le premier opérande : "))
        op2 = float(input("Saisissez le deuxième opérande : "))
        operation = input("Saisissez l'opération (addition, soustraction, multiplication, division) : ")

        if operation == "addition":
            result = add(op1, op2)
        elif operation == "soustraction":
            result = subtract(op1, op2)
        elif operation == "multiplication":
            result = multiply(op1, op2)
        elif operation == "division":
            result = divide(op1, op2)
        else:
            print("Opération invalide. Veuillez réessayer.")
            continue

        display_result(result)

        choice = input("Voulez-vous continuer ? (oui/non) : ")
        if choice.lower() != "oui":
            break
calculate()