from bs4 import BeautifulSoup
from multiprocessing.pool import ThreadPool
from time import time
import requests
import xlsxwriter

#SE EU FOR REMODELAR O CODIGO, QND EU PEGAR OS LINKS EU COLOCO UMA FLAG PRA DIZER SE É PUBLICA OU PRIVADA, ASSIM VOU ECONOMIZAR MTO CODIGO!

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

        self.__data = {}
        self.__key = 0

    def __get_states(self):
        response = requests.get(self.__url)
        soup = BeautifulSoup(response.text, "html.parser")
        links = [link.find("a")["href"] for link in soup.findAll("div", attrs={"class":"state"})]
        return links

    def handler_cities(self, state):
        if state:
            response = requests.get(self.__base_url+state)
            soup = BeautifulSoup(response.text, "html.parser")
            for link in soup.findAll("div", attrs={"class":"city"}):
                self.__cities.append(link.find("a")["href"])        
    
    def get_cities(self):
        pool = ThreadPool(16)
        list(pool.imap(self.handler_cities, self.__get_states()))
         
    def handler_categories(self, city):
        if city:
            response = requests.get(self.__base_url+city)
            soup = BeautifulSoup(response.text, "html.parser")
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
            response = requests.get(self.__base_url+url)
            soup = BeautifulSoup(response.text, "html.parser")
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

    def handler_all_links_private(self, initial_url):
        url = initial_url
        while True:
            response = requests.get(self.__base_url+url)
            soup = BeautifulSoup(response.text, "html.parser")
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

    def get_all_links_public(self):
        pool = ThreadPool(64)
        list(pool.imap(self.handler_all_links_public, self.__public))

    def get_all_links_private(self):
        pool = ThreadPool(64)
        list(pool.imap(self.handler_all_links_public, self.__private))

    def handler_schools_public(self,school):
        if school:
            response = requests.get(self.__base_url+school)
            soup = BeautifulSoup(response.text, "html.parser")
            for link in soup.find("div", attrs={"class":"schools clearfix"}).findAll("a"):
                self.__schools_links_public.append(link["href"])
            
    def get_schools_public(self,iterable):
        pool = ThreadPool(64)
        list(pool.imap(self.handler_schools_public, iterable))

    def handler_schools_private(self,school):
        if school:
            response = requests.get(self.__base_url+school)
            soup = BeautifulSoup(response.text, "html.parser")
            for link in soup.find("div", attrs={"class":"schools clearfix"}).findAll("a"):
                self.__schools_links_private.append(link["href"])
            
    def get_schools_private(self,iterable):
        pool = ThreadPool(64)
        list(pool.imap(self.handler_schools_private, iterable))

    def handler_data_public(self, url):
        response = requests.get(self.__base_url+url)
        soup = BeautifulSoup(response.text, "html.parser")
        
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
        # postalCode = address.find("span",attrs={"itemprop":"postalCode"}).text

        self.__data[self.__key] = state, city, neighborhood, school_name, "Escola Pública", telephone, email, streetAddress
        self.__key += 1
        # print(state)
        # print(city[:-3])
        # print(neighborhood)
        # print(school_name)
        # print(telephone)
        # print(email)
        # print(streetAddress)

        # print(postalCode)      

    def get_data_public(self):
        pool = ThreadPool(64)
        list(pool.imap(self.handler_data_public, self.__schools_links_public))

    def handler_data_private(self, url):
        response = requests.get(self.__base_url+url)
        soup = BeautifulSoup(response.text, "html.parser")
        
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
        # postalCode = address.find("span",attrs={"itemprop":"postalCode"}).text

        self.__data[self.__key] = state, city, neighborhood, school_name, "Escola Particular", telephone, email, streetAddress
        self.__key += 1
        # print(state)
        # print(city[:-3])
        # print(neighborhood)
        # print(school_name)
        # print(telephone)
        # print(email)
        # print(streetAddress)
        
        # print(postalCode)    

    def get_data_private(self):
        pool = ThreadPool(64)
        list(pool.imap(self.handler_data_private, self.__schools_links_private))

    def work_aux(self):
        # with open("public_schools.txt") as file:
        #     for line in file:
        #         self.__public.append(line[:-1])

        # with open("private_schools.txt") as file:
        #     for line in file:
        #         self.__private.append(line[:-1])                        

        # self.get_all_links_public()
        # self.get_all_links_private()

        # public_pages = self.__public + self.__all_pages_public
        # with open("all_pages_public.txt","w") as file:
        #     for link in public_pages:
        #         file.write(link+"\n")
                 
        # private_pages = self.__private + self.__all_pages_private
        # with open("all_pages_private.txt","w") as file:
        #     for link in private_pages:
        #         file.write(link+"\n")

        # with open("all_pages_public.txt") as file:
        #     for line in file:
        #         self.__all_pages_public.append(line[:-1])

        # with open("all_pages_private.txt") as file:
        #     for line in file:
        #         self.__all_pages_private.append(line[:-1])  

        # self.get_schools_public(self.__all_pages_public)
        # self.get_schools_private(self.__all_pages_private)

        # with open("schools_links_public.txt","w") as file:
        #     for link in self.__schools_links_public:
        #         file.write(link+"\n")
        # with open("schools_links_private.txt","w") as file:
        #     for link in self.__schools_links_private:
        #         file.write(link+"\n")        
        #     

        with open("schools_links_public.txt") as file:
            for line in file:
                self.__schools_links_public.append(line[:-1])

        with open("schools_links_private.txt") as file:
            for line in file:
                self.__schools_links_private.append(line[:-1])
                
        self.get_data_public()
        self.get_data_private()
        self.write_sheet()

    def work(self):
        self.get_cities()
        self.get_school_category()

        with open("public_schools.txt","w") as file:
            for link in self.__public:
                file.write(link+"\n")          

        with open("private_schools.txt","w") as file:
            for link in self.__private:
                file.write(link+"\n")   
        # self.get_all_links()
        # pages = self.__categories + self.__all_pages
        # pages_sorted = sorted(pages)
        # with open("all_pages.txt","w") as file:
        #     for link in pages_sorted:
        #         file.write(link+"\n")        
        # self.get_schools()                

    def write_sheet(self):
        workbook = xlsxwriter.Workbook("escolas.xlsx")
        worksheet = workbook.add_worksheet()
        bold = workbook.add_format({'bold': True})

        values = list(self.__data.values())
        worksheet.write(0, 0, "Estado",bold)
        worksheet.write(0, 1, "Cidade",bold)
        worksheet.write(0, 2, "Bairro",bold)
        worksheet.write(0, 3, "Nome da Instituição",bold)
        worksheet.write(0, 4, "Tipo",bold)
        worksheet.write(0, 5, "Telefone",bold)
        worksheet.write(0, 6, "Email",bold)
        worksheet.write(0, 7, "Endereço",bold)

        for row_number, info in enumerate(values):
            worksheet.write(row_number+1, 0, info[0])
            worksheet.write(row_number+1, 1, info[1])
            worksheet.write(row_number+1, 2, info[2])
            worksheet.write(row_number+1, 3, info[3])
            worksheet.write(row_number+1, 4, info[4])
            worksheet.write(row_number+1, 5, info[5])
            worksheet.write(row_number+1, 6, info[6])
            worksheet.write(row_number+1, 7, info[7])
        workbook.close()

    def test(self):
        response = requests.get("https://www.escol.as/279496-pingo-de-gente-creche-centro-de-educacao-infantil")
        soup = BeautifulSoup(response.text, "html.parser")
        school = soup.find("div", attrs={"class":"school"})
        address = school.find("table",attrs={"itemprop":"address"})
        
        state = address.find("span",attrs={"itemprop":"addressRegion"}).text
        city = address.find("span",attrs={"itemprop":"addressLocality"}).text[:-3]
        neighborhood = address.find("strong").text
        school_name = school.find("h1", attrs={"class":"school-name"}).text
        telephone = address.find("a",attrs={"itemprop":"telephone"}).text
        email = address.find("td", attrs={"itemprop":"email"}).text
        streetAddress = address.find("span",attrs={"itemprop":"streetAddress"}).text
        # postalCode = address.find("span",attrs={"itemprop":"postalCode"}).text

        self.__data[self.__key] = state, city, neighborhood, school_name, "public", telephone, email
        self.__key += 1
        print(state)
        print(city)
        print(neighborhood)
        print(school_name)
        print(telephone)
        print(email)
        print(streetAddress)
        # print(postalCode)        