from bs4 import BeautifulSoup
from multiprocessing.pool import ThreadPool
from time import time
import requests
import xlsxwriter

class Escola:
    def __init__(self,url):
        self.__url = url
        self.__base_url = "https://www.escol.as"
        self.__cities = []
        self.__public = []
        self.__private = []
        self.__all_pages_public = []
        self.__all_pages_private = []
        self.__schools_links_public = []
        self.__schools_links_private = []
        self.__data = []

    def __get_states(self):
        response = requests.get(self.__url)
        soup = BeautifulSoup(response.text, "html.parser")
        links = [link.find("a")["href"] for link in soup.findAll("div", attrs={"class":"state"})]
        return links

    def handler_cities(self, state):
        while True:
            try:
                response = requests.get(self.__base_url+state)
                soup = BeautifulSoup(response.text, "html.parser")
                break
            except Exception:
                pass
        for link in soup.findAll("div", attrs={"class":"city"}):
            self.__cities.append(link.find("a")["href"])        
    
    def get_cities(self):
        pool = ThreadPool(16)
        list(pool.imap(self.handler_cities, self.__get_states()))
         
    def handler_categories(self, city):
        while True:
            try:
                response = requests.get(self.__base_url+city)
                soup = BeautifulSoup(response.text, "html.parser")
                break
            except Exception:
                pass
        school_categories = soup.findAll("div", attrs={"class":"col-md-6"})
        if len(school_categories) == 1:
            public_schools = school_categories[0]
            for link in public_schools("li", attrs={"class":"school-category-item"}):
                self.__public.append(link.find("a")["href"])                
        elif len(school_categories) == 2:
            public_schools = school_categories[0]
            private_schools = school_categories[1]                
            for link in public_schools("li", attrs={"class":"school-category-item"}):
                self.__public.append(link.find("a")["href"])
            for link in private_schools("li", attrs={"class":"school-category-item"}):
                self.__private.append(link.find("a")["href"])                

    def get_school_category(self):
        pool = ThreadPool(64)
        list(pool.imap(self.handler_categories, self.__cities))

    def handler_all_links_public(self, initial_url):
        url = initial_url
        while True:
            while True:
                try:
                    response = requests.get(self.__base_url+url)
                    soup = BeautifulSoup(response.text, "html.parser")
                    break
                except Exception:
                    pass
            pagination = soup.find("ul",attrs={"class":"pagination"})
            if pagination is None: break
            next_page = pagination.find("li", attrs={"class":"next_page"})
            if next_page is None: break
            for link in next_page:
                try:
                    self.__all_pages_public.append(link["href"])
                    url = link["href"]
                except Exception:
                    pass

    def get_all_links_public(self):
        pool = ThreadPool(64)
        list(pool.imap(self.handler_all_links_public, self.__public))

    def handler_all_links_private(self, initial_url):
        url = initial_url
        while True:
            while True:
                try:
                    response = requests.get(self.__base_url+url)
                    soup = BeautifulSoup(response.text, "html.parser")
                    break
                except Exception:
                    pass
            pagination = soup.find("ul",attrs={"class":"pagination"})
            if pagination is None: break
            next_page = pagination.find("li", attrs={"class":"next_page"})
            if next_page is None: break
            for link in next_page:
                try:
                    self.__all_pages_private.append(link["href"])
                    url = link["href"]
                except Exception:
                    pass                      

    def get_all_links_private(self):
        pool = ThreadPool(64)
        list(pool.imap(self.handler_all_links_private, self.__private))

    def handler_schools_public(self,school):
        while True:
            try:
                response = requests.get(self.__base_url+school)
                soup = BeautifulSoup(response.text, "html.parser")
                break
            except Exception:
                pass            
        for link in soup.find("div", attrs={"class":"schools clearfix"}).findAll("a"):
            self.__schools_links_public.append(link["href"])
            
    def get_schools_public(self,iterable):
        pool = ThreadPool(64)
        list(pool.imap(self.handler_schools_public, iterable))

    def handler_schools_private(self,school):
        while True:
            try:
                response = requests.get(self.__base_url+school)
                soup = BeautifulSoup(response.text, "html.parser")
                break
            except Exception:
                pass
        for link in soup.find("div", attrs={"class":"schools clearfix"}).findAll("a"):
            self.__schools_links_private.append(link["href"])
            
    def get_schools_private(self,iterable):
        pool = ThreadPool(64)
        list(pool.imap(self.handler_schools_private, iterable))

    def handler_data_public(self, url):
        while True:
            try:
                response = requests.get(self.__base_url+url)
                soup = BeautifulSoup(response.text, "html.parser")
                break
            except:
                pass
        school = soup.find("div", attrs={"class":"school"})
        if not school: return False
        address = school.find("table",attrs={"itemprop":"address"})
        if not address: return False

        state = "null"
        city = "null"
        neighborhood = "null"
        school_name = "null"
        telephone = "null"
        email = "null"
        streetAddress = "Sem endereço"

        temp_state = address.find("span",attrs={"itemprop":"addressRegion"})
        if temp_state: state = temp_state.text
        temp_city = address.find("span",attrs={"itemprop":"addressLocality"})
        if temp_city: city = temp_city.text[:-3]
        temp_neighborhood = address.find("strong")
        if temp_neighborhood: neighborhood = temp_neighborhood.text
        temp_school_name = school.find("h1", attrs={"class":"school-name"})
        if temp_school_name: school_name = temp_school_name.text
        temp_telephone = address.find("a",attrs={"itemprop":"telephone"})
        if temp_telephone: telephone = temp_telephone.text
        temp_email = address.find("td", attrs={"itemprop":"email"})
        if temp_email: email = temp_email.text
        temp_streetAddress = address.find("span",attrs={"itemprop":"streetAddress"})
        if temp_streetAddress: streetAddress = temp_streetAddress.text

        self.__data.append((state, city, neighborhood, school_name, "Escola Pública", telephone, email, streetAddress))

    def get_data_public(self):
        pool = ThreadPool(64)
        list(pool.imap(self.handler_data_public, self.__schools_links_public))

    def handler_data_private(self, url):
        while True:
            try:
                response = requests.get(self.__base_url+url)
                soup = BeautifulSoup(response.text, "html.parser")
                break
            except:
                pass
        school = soup.find("div", attrs={"class":"school"})
        if not school: return False
        address = school.find("table",attrs={"itemprop":"address"})
        if not address: return False
        
        state = "null"
        city = "null"
        neighborhood = "null"
        school_name = "null"
        telephone = "null"
        email = "null"
        streetAddress = "Sem endereço"

        temp_state = address.find("span",attrs={"itemprop":"addressRegion"})
        if temp_state: state = temp_state.text
        temp_city = address.find("span",attrs={"itemprop":"addressLocality"})
        if temp_city: city = temp_city.text[:-3]
        temp_neighborhood = address.find("strong")
        if temp_neighborhood: neighborhood = temp_neighborhood.text
        temp_school_name = school.find("h1", attrs={"class":"school-name"})
        if temp_school_name: school_name = temp_school_name.text
        temp_telephone = address.find("a",attrs={"itemprop":"telephone"})
        if temp_telephone: telephone = temp_telephone.text
        temp_email = address.find("td", attrs={"itemprop":"email"})
        if temp_email: email = temp_email.text
        temp_streetAddress = address.find("span",attrs={"itemprop":"streetAddress"})
        if temp_streetAddress: streetAddress = temp_streetAddress.text

        self.__data.append((state, city, neighborhood, school_name, "Escola Privada", telephone, email, streetAddress))

    def get_data_private(self):
        pool = ThreadPool(64)
        list(pool.imap(self.handler_data_private, self.__schools_links_private))

    def write_sheet(self):
        workbook = xlsxwriter.Workbook("Escolas_v2.xlsx")
        worksheet = workbook.add_worksheet()
        bold = workbook.add_format({'bold': True})

        worksheet.write(0, 0, "Estado",bold)
        worksheet.write(0, 1, "Cidade",bold)
        worksheet.write(0, 2, "Bairro",bold)
        worksheet.write(0, 3, "Nome da Instituição",bold)
        worksheet.write(0, 4, "Tipo",bold)
        worksheet.write(0, 5, "Telefone",bold)
        worksheet.write(0, 6, "Email",bold)
        worksheet.write(0, 7, "Endereço",bold)

        for row_number, info in enumerate(self.__data):
            worksheet.write(row_number+1, 0, info[0])
            worksheet.write(row_number+1, 1, info[1])
            worksheet.write(row_number+1, 2, info[2])
            worksheet.write(row_number+1, 3, info[3])
            worksheet.write(row_number+1, 4, info[4])
            worksheet.write(row_number+1, 5, info[5])
            worksheet.write(row_number+1, 6, info[6])
            worksheet.write(row_number+1, 7, info[7])
        workbook.close() 

    def write_links(self, data, name):
        with open(name,"w") as file:
            for link in data:
                file.write(link+"\n")              

    def work(self):
        self.get_cities()
        print("\nCidades coletadas!")
        print("{cities} cidades foram coletadas!\n".format(cities=len(self.__cities)))

        self.get_school_category()
        print("Escolas coletadas!")
        print("{public} escolas públicas foram coletadas! (OBS: Página 1)".format(public=len(self.__public)))
        print("{private} escolas privadas foram coletadas! (OBS: Página 1)\n".format(private=len(self.__private)))
        self.get_all_links_public()
        self.get_all_links_private()
        print("{all_pages_public} páginas restantes das escolas públicas foram coletadas!".format(all_pages_public=len(self.__all_pages_public)))
        print("{all_pages_private} páginas restantes das escolas privadas foram coletadas!\n".format(all_pages_private=len(self.__all_pages_private)))

        new_public = self.__public + self.__all_pages_public
        new_private = self.__private + self.__all_pages_private
        print("{new_public} páginas contendo escolas públicas foram coletadas no total!".format(new_public=len(new_public)))
        print("{new_private} páginas contendo escolas privadas foram coletadas no total!\n".format(new_private=len(new_private)))

        self.get_schools_public(new_public)
        self.get_schools_private(new_private)        
        print("{schools_links_public} links de escolas públicas foram coletados!".format(schools_links_public=len(self.__schools_links_public)))
        print("{schools_links_private} links de escolas privadas foram coletados!\n".format(schools_links_private=len(self.__schools_links_private)))
        
        self.get_data_public()
        self.get_data_private()
        print("{data} foram coletados e gravados na planilha com sucesso!".format(data=len(self.__data)))
        self.write_sheet()

        #Links das primeiras páginas de cada categoria e cidade.
        self.write_links(self.__public, "initial_links_public.txt")
        self.write_links(self.__private, "initial_links_private.txt")

        #Links das páginas seguintes, pg2, pg3, etc.
        self.write_links(self.__all_pages_public, "all_pages_public.txt")
        self.write_links(self.__all_pages_private, "all_pages_private.txt")

        #Somatório dos links das primeiras páginas com as seguintes.
        self.write_links(new_public, "new_public.txt")
        self.write_links(new_private, "new_private.txt")
        
        #Links de todas as escolas, públicas e privadas.
        self.write_links(self.__schools_links_public, "schools_links_public.txt")
        self.write_links(self.__schools_links_private, "schools_links_private.txt")
        
