def addition(a, b):
    """Fonction pour effectuer une addition"""
    return a + b

def soustraction(a, b):
    """Fonction pour effectuer une soustraction"""
    return a - b

def multiplication(a, b):
    """Fonction pour effectuer une multiplication"""
    return a * b

def division(a, b):
    """Fonction pour effectuer une division"""
    if b == 0:
        raise ValueError("Division par zéro non autorisée")
    return a / b

def calculatrice():
    """Fonction principale pour lancer la calculatrice"""
    while True:
        print("Calculatrice")
        print("1. Addition")
        print("2. Soustraction")
        print("3. Multiplication")
        print("4. Division")
        print("5. Quitter")

        choix = input("Choisissez une opération : ")

        if choix == '1':
            op = addition
        elif choix == '2':
            op = soustraction
        elif choix == '3':
            op = multiplication
        elif choix == '4':
            op = division
        else:
            print("Opération invalide. Veuillez réessayer.")
            continue

        try:
            opérande_1 = float(input("Saisissez le premier opérande : "))
            opérande_2 = float(input("Saisissez le deuxième opérande : "))
        except ValueError:
            print("Valeur invalide. Veuillez réessayer.")
            continue

        try:
            resultat = op(opérande_1, opérande_2)
            print(f"Le résultat est: {resultat}")
        except ValueError as e:
            print(e)

        choix_continuer = input("Voulez-vous continuer ? (oui/non) : ")
        if choix_continuer.lower() != 'oui':
            break

calculatrice()