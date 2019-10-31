from bs4 import BeautifulSoup
from multiprocessing.pool import ThreadPool
from time import time
import requests
import xlsxwriter

base_url = "https://www.escol.as"

public = []
all_pages_public = []
schools_links_public = []

private = []
all_pages_private = []
schools_links_private = []

data = []

def handler_all_links_public(initial_url):
    url = initial_url
    while True:
        while True:
            try:
                response = requests.get(base_url+url)
                soup = BeautifulSoup(response.text, "html.parser")
                break
            except Exception:
                print("exception")                
        pagination = soup.find("ul",attrs={"class":"pagination"})
        if pagination is None: break
        next_page = pagination.find("li", attrs={"class":"next_page"})
        if next_page is None: break
        for link in next_page:
            try:
                all_pages_public.append(link["href"])
                url = link["href"]
            except Exception:
                pass        

def get_all_links_public():
    pool = ThreadPool(64)
    list(pool.imap(handler_all_links_public, public))

def handler_schools_public(school):
    while True:
        try:
            response = requests.get(base_url+school)
            soup = BeautifulSoup(response.text, "html.parser")
            break       
        except Exception:
            print("exception")
            pass
    for link in soup.find("div", attrs={"class":"schools clearfix"}).findAll("a"):
        schools_links_public.append(link["href"])
        
def get_schools_public(iterable):
    pool = ThreadPool(64)
    list(pool.imap(handler_schools_public, iterable))    

def handler_data_public(url):
    while True:
        try:
            response = requests.get(base_url+url)
            soup = BeautifulSoup(response.text, "html.parser")
            break
        except Exception:
            print("exception")
            pass

    school = soup.find("div", attrs={"class":"school"})
    if not school: 
        print("entrei no school")
        return False
    
    address = school.find("table",attrs={"itemprop":"address"})
    if not address: 
        print("entrei no address")
        return False

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

    data.append((state, city, neighborhood, school_name, "Escola Pública", telephone, email, streetAddress))
    # print(state)
    # print(city[:-3])
    # print(neighborhood)
    # print(school_name)
    # print(telephone)
    # print(email)
    # print(streetAddress)   

def get_data_public():
    pool = ThreadPool(64)
    list(pool.imap(handler_data_public, schools_links_public))

def handler_all_links_private( initial_url):
    url = initial_url
    while True:
        while True:
            try:
                response = requests.get(base_url+url)
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
                all_pages_private.append(link["href"])
                url = link["href"]
            except Exception:
                pass                      

def get_all_links_private():
    pool = ThreadPool(64)
    list(pool.imap(handler_all_links_private, private))
def handler_schools_private(school):
    while True:
        try:
            response = requests.get(base_url+school)
            soup = BeautifulSoup(response.text, "html.parser")
            break
        except Exception:
            pass
    for link in soup.find("div", attrs={"class":"schools clearfix"}).findAll("a"):
        schools_links_private.append(link["href"])
        
def get_schools_private(iterable):
    pool = ThreadPool(64)
    list(pool.imap(handler_schools_private, iterable))
def handler_data_private( url):
    while True:
        try:
            response = requests.get(base_url+url)
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
    # postalCode = address.find("span",attrs={"itemprop":"postalCode"}).text

    data.append((state, city, neighborhood, school_name, "Escola Privada", telephone, email, streetAddress))
    # print(state)
    # print(city[:-3])
    # print(neighborhood)
    # print(school_name)
    # print(telephone)
    # print(email)
    # print(streetAddress)
    
    # print(postalCode)    

def get_data_private():
    pool = ThreadPool(64)
    list(pool.imap(handler_data_private, schools_links_private))    

def write_sheet(data):
    workbook = xlsxwriter.Workbook("araruama_test.xlsx")
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

    for row_number, info in enumerate(data):
        worksheet.write(row_number+1, 0, info[0])
        worksheet.write(row_number+1, 1, info[1])
        worksheet.write(row_number+1, 2, info[2])
        worksheet.write(row_number+1, 3, info[3])
        worksheet.write(row_number+1, 4, info[4])
        worksheet.write(row_number+1, 5, info[5])
        worksheet.write(row_number+1, 6, info[6])
        worksheet.write(row_number+1, 7, info[7])
    workbook.close()

if __name__ == "__main__":

    response = requests.get("https://www.escol.as/cidades/3177-araruama")
    soup = BeautifulSoup(response.text, "html.parser")
    school_categories = soup.findAll("div", attrs={"class":"col-md-6"})
    if len(school_categories) == 1:
        public_schools = school_categories[0]
        for link in public_schools("li", attrs={"class":"school-category-item"}):
            public.append(link.find("a")["href"])                
    elif len(school_categories) == 2:
        public_schools = school_categories[0]
        private_schools = school_categories[1]                
        for link in public_schools("li", attrs={"class":"school-category-item"}):
            public.append(link.find("a")["href"])
        for link in private_schools("li", attrs={"class":"school-category-item"}):
            private.append(link.find("a")["href"])
    
    get_all_links_public()    
    new_public = public + all_pages_public
    get_schools_public(new_public)

    get_all_links_private()
    new_private = private + all_pages_private
    get_schools_private(new_private)

    print("\n")
    get_data_public()
    get_data_private()
    print(*data, sep="\n")
    print(len(data))
    # print(private)
    write_sheet(data)