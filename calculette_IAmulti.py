def calculatrice_priorites():
    """
    Fonction pour effectuer des calculs en respectant les priorités des opérations
    """
    operations = []
    priorites = {'+': 1, '-': 1, '*': 2, '/': 2}

    while True:
        print("Calculatrice - Opérations avec priorités")
        print("1. Saisir une opération")
        print("2. Afficher le résultat")
        print("3. Quitter")

        choix = input("Choisissez une option : ")

        if choix == '1':
            op = input("Saisissez l'opération (addition, soustraction, multiplication, division) : ")
            opérande_1 = float(input("Saisissez le premier opérande : "))
            opérande_2 = float(input("Saisissez le deuxième opérande : "))

            if op in priorites:
                while operations and operations[-1][0] in priorites and priorites[op] <= priorites[operations[-1][0]]:
                    resultat = calculer(operations.pop())
                    operations.append((resultat, None, None))

            operations.append((op, opérande_1, opérande_2))
        elif choix == '2':
            if len(operations) == 0:
                print("Aucune opération saisie. Veuillez en saisir une.")
                continue

            while len(operations) > 1:
                resultat = calculer(operations.pop())
                operations.append((resultat, None, None))

            print(f"Le résultat est: {operations[0][0]}")
            operations = []
        elif choix == '3':
            break

def calculer(operande):
    """
    Fonction pour effectuer le calcul avec les opérations fournies
    """
    op, opérande_1, opérande_2 = operande
    if op == '+':
        return opérande_1 + opérande_2
    elif op == '-':
        return opérande_1 - opérande_2
    elif op == '*':
        return opérande_1 * opérande_2
    elif op == '/':
        if opérande_2 == 0:
            print("Division par zéro non autorisée.")
            return None
        return opérande_1 / opérande_2

calculatrice_priorites()