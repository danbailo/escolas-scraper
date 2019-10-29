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
        self.__schools = []

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
        start = time()
        list(pool.imap(self.handler_cities, self.__get_states()))
        end = time() - start
        print(*self.__cities, sep="\n")
        print(end)
         
    def handler_categories(self, city):
        if city:
            response = requests.get(self.__base_url+city)
            soup = BeautifulSoup(response.text, "html.parser")
            for link in soup.findAll("li", attrs={"class":"school-category-item"}):
                self.__categories.append(link.find("a")["href"])

    def get_school_category(self):
        pool = ThreadPool(64)
        start = time()
        list(pool.imap(self.handler_categories, self.__cities))
        end = time() - start
        print(*self.__categories, sep="\n")
        print(end)

    # def handler_schools(self,school):
    #     if school:
    #         response = requests.get(self.__base_url+school)
    #         soup = BeautifulSoup(response.text, "html.parser")
    #         for link in soup.findAll("div", attrs={"class":"schools clearfix"}):
    #             self.__schools.append(link.find("a")["href"])
            

    # def get_shools(self):
    #     pool = ThreadPool(64)
    #     start = time()
    #     list(pool.imap(self.handler_schools, self.__categories))
    #     end = time() - start
    #     print(*self.__schools, sep="\n")
    #     print(end)
        
    
    def work(self):
        self.get_cities()
        self.get_school_category()
        # self.get_shools()
    
    def test(self):
        url = "https://www.escol.as/cidades/3907-votorantim/categories/1-creche"
        while True:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, "html.parser")
            next_page = soup.find("ul",attrs={"class":"pagination"}).find("li", attrs={"class":"next_page"})
            if next_page is None: break
            for link in next_page:
                try:
                    print(link["href"])
                    url = self.__base_url+link["href"]
                except Exception:
                    pass
        