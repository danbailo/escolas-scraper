from bs4 import BeautifulSoup
from multiprocessing.pool import ThreadPool
import requests

class Escola:
    def __init__(self,url):
        self.base_url = "https://www.escol.as"
        self.url = url
    
    def get_cities(self):
        response = requests.get(self.url)
        soup = BeautifulSoup(response.text, "html.parser")
        links = [link.find("a")["href"] for link in soup.findAll("div", attrs={"class":"city"})]
        return links

    def get_school_category(self):
        links = self.get_cities()
        for link in links:
            response = requests.get(self.base_url+link)
            soup = BeautifulSoup(response.text, "html.parser")
            links = [link.find("a")["href"] for link in soup.findAll("li", attrs={"class":"school-category-item"})]
        return links
    
    def get_school(self):
        links = self.get_school_category()
        print(links)
    