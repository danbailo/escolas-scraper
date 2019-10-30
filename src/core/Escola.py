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
        # print(*self.__cities, sep="\n")
        # print(end)
         
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
        # print(*self.__categories, sep="\n")
        # print(end)

    def handler_all_links(self, initial_url):
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
                    self.__all_pages.append(link["href"])
                    url = link["href"]
                except Exception:
                    pass        

    def get_all_links(self):
        pool = ThreadPool(64)
        start = time()
        list(pool.imap(self.handler_all_links, self.__categories))
        end = time() - start
        print(*self.__all_pages, sep="\n")
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
    
    def test(self):        
        url = "/cidades/3829-sao-paulo/categories/1-creche"
        while True:
            response = requests.get(self.__base_url+url)
            soup = BeautifulSoup(response.text, "html.parser")
            pagination = soup.find("ul",attrs={"class":"pagination"})
            if pagination is None: break
            next_page = pagination.find("li", attrs={"class":"next_page"})
            if next_page is None: break
            for link in next_page:
                try:
                    print(link["href"])
                    self.__all_pages.append(link["href"])
                    url = link["href"]
                except Exception:
                    pass        
    
    def work(self):
        self.get_cities()
        self.get_school_category()
        # with open("shools.txt","w") as file:
        #     for link in self.__categories:
        #         file.write(link+"\n")
        self.get_all_links()
        # with open("shools_NEXT.txt","w") as file:
        #     for link in self.__all_pages:
        #         file.write(link+"\n")
        pages = self.__categories + self.__all_pages
        pages_sorted = sorted(pages)
        with open("all_pages.txt","w") as file:
            for link in pages_sorted:
                file.write(link+"\n")        
        # self.get_shools()
        