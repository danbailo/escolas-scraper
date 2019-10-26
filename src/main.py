from core import Escola

if __name__ == "__main__":
    escola = Escola("https://www.escol.as/estados/19-rio-de-janeiro")

    print(escola.get_cities())
    # escola.get_school_category()