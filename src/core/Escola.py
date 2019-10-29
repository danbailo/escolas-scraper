from bs4 import BeautifulSoup
from multiprocessing.pool import ThreadPool
import requests

class Escola:
    def __init__(self,url):
        self.__url = url
        self.__base_url = "https://www.escol.as"
        self.__cities = []

    def __get_states(self):
        response = requests.get(self.__url)
        soup = BeautifulSoup(response.text, "html.parser")
        links = [link.find("a")["href"] for link in soup.findAll("div", attrs={"class":"state"})]
        return links

    # def handler_cities(self, state):
    #     if state:
    #         response = requests.get(self.__base_url+state)
    #         soup = BeautifulSoup(response.text, "html.parser")
    #         for link in soup.findAll("div", attrs={"class":"city"}):
    #             self.__cities.append(link.find("a")["href"])        
    
    def get_cities(self):
        all_links = []
        for state in self.__get_states():
            if state:
                response = requests.get(self.__base_url+state)
                soup = BeautifulSoup(response.text, "html.parser")
                for link in soup.findAll("div", attrs={"class":"city"}):
                    all_links.append(link.find("a")["href"])
        return all_links
         
    # def handler(self):
    #     links = self.get_cities()
    #     for link in links:
    #         response = requests.get(self.__base_url+link)
    #         soup = BeautifulSoup(response.text, "html.parser")
    #         links = [link.find("a")["href"] for link in soup.findAll("li", attrs={"class":"school-category-item"})]
    #     return links

    # def get_school_category(self):
    #     pool = ThreadPool(32)
    #     pool.imap(hand)
    
    # def get_school(self):
    #     links = self.get_school_category()
    #     print(links)
    