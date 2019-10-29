from core import Escola

if __name__ == "__main__":
    escola = Escola("https://www.escol.as/estados")

    for link in escola.get_cities():
        print(link)
    # escola.get_school_category