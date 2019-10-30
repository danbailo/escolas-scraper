import bs4
from bs4 import BeautifulSoup
from multiprocessing.pool import ThreadPool
from multiprocessing import Pool
import requests
from time import time

class Escola:
    def __init__(self,url):
        self.__url = url
        self.__base_url = "https://www.escol.as"
        self.__cities = []
        
        self.__categories = []
        self.__all_pages = []

        self.__public = []
        self.__private = []
        self.__all_pages_public = []
        self.__all_pages_private = []



        self.__file_links = []
        self.__schools_links = []

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

    def handler_schools(self,school):
        if school:
            response = requests.get(self.__base_url+school)
            soup = BeautifulSoup(response.text, "html.parser")
            for link in soup.find("div", attrs={"class":"schools clearfix"}).findAll("a"):
                self.__schools_links.append(link["href"])
            
    def get_schools(self,iterable):
        pool = ThreadPool(64)
        list(pool.imap(self.handler_schools, iterable))

    def read_pages(self):
        with open("all_pages.txt") as file:
            for line in file:
                self.__file_links.append(line[:-1])

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

    def work_aux(self):
        with open("public_schools.txt") as file:
            for line in file:
                self.__public.append(line[:-1])

        with open("private_schools.txt") as file:
            for line in file:
                self.__private.append(line[:-1])                        

        self.get_all_links_public()
        self.get_all_links_private()

        public_pages = self.__public + self.__all_pages_public
        with open("all_pages_public.txt","w") as file:
            for link in public_pages:
                file.write(link+"\n")
                 
        private_pages = self.__private + self.__all_pages_private
        with open("all_pages_private.txt","w") as file:
            for link in private_pages:
                file.write(link+"\n")

        # self.read_pages()
        # self.get_schools(self.__file_links)
        # with open("school_link.txt","w") as file:
        #     for link in self.__schools_links:
        #         file.write(link+"\n")    

    def test(self):
        response = requests.get("https://www.escol.as/67448-ideal-da-crianca-creche")
        soup = BeautifulSoup(response.text, "html.parser")
        # print(soup)
        school = soup.find("div", attrs={"class":"school"})
        school_name = school.find("h1", attrs={"class":"school-name"}).text
       
        address = school.find("table",attrs={"itemprop":"address"})
        telephone = address.find("a",attrs={"itemprop":"telephone"}).text
        streetAddress = address.find("span",attrs={"itemprop":"streetAddress"}).text
        neighborhood = address.find("strong").text
        addressLocality = address.find("span",attrs={"itemprop":"addressLocality"}).text
        addressRegion = address.find("span",attrs={"itemprop":"addressRegion"}).text
        postalCode = address.find("span",attrs={"itemprop":"postalCode"}).text

        print(school)

        print(school_name)
        print(telephone)
        print(streetAddress)
        print(neighborhood)
        print(addressLocality)
        print(addressRegion)
        print(postalCode)