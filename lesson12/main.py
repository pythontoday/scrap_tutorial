import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import time
import re
from urllib.parse import unquote
import random
import json

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36"
}


def get_source_html(url):
    
    driver = webdriver.Chrome(
        executable_path="driver_path"
    )
    
    driver.maximize_window()
    
    try:
        driver.get(url=url)
        time.sleep(3)
        
        while True:
            find_more_element = driver.find_element_by_class_name("catalog-button-showMore")
            
            if driver.find_elements_by_class_name("hasmore-text"):
                with open("lesson12/source-page.html", "w") as file:
                    file.write(driver.page_source)
                    
                break
            else:
                actions = ActionChains(driver)
                actions.move_to_element(find_more_element).perform()
                time.sleep(3)
    except Exception as _ex:
        print(_ex)
    finally:
        driver.close()
        driver.quit()
        
        
def get_items_urls(file_path):
    with open(file_path) as file:
        src = file.read()
        
    soup = BeautifulSoup(src, "lxml")
    items_divs = soup.find_all("div", class_="service-description")
    
    urls = []
    for item in items_divs:
        item_url = item.find("div", class_="H3").find("a").get("href")
        urls.append(item_url)
        
    with open("lesson12/items_urls2.txt", "w") as file:
        for url in urls:
            file.write(f"{url}\n")
            
    return "[INFO] Urls collected successfully!"


def get_data(file_path):
    with open(file_path) as file:
        # urls_list = file.readlines()
        
        # clear_urls_list = []
        # for url in urls_list:
        #     url = url.strip()
        #     clear_urls_list.append(url)
        # print(clear_urls_list)
        
        urls_list = [url.strip() for url in file.readlines()]
        
    result_list = []
    urls_count = len(urls_list)
    count = 1
    for url in urls_list:
        response = requests.get(url=url, headers=headers)
        soup = BeautifulSoup(response.text, "lxml")
        
        try:
            item_name = soup.find("span", {"itemprop": "name"}).text.strip()
        except Exception as _ex:
            item_name = None
            
        item_phones_list = []
        try:
            item_phones = soup.find("div", class_="service-phones-list").find_all("a", class_="js-phone-number")
            
            for phone in item_phones:
                item_phone = phone.get("href").split(":")[-1].strip()
                item_phones_list.append(item_phone)
        except Exception as _ex:
            item_phones_list = None
            
        try:
            item_address = soup.find("address", class_="iblock").text.strip()
        except Exception as _ex:
            item_address = None
            
        try:
            item_site = soup.find(text=re.compile("Сайт|Официальный сайт")).find_next().text.strip()
        except Exception as _ex:
            item_site = None
            
        social_networks_list = []
        try:
            item_social_networks = soup.find(text=re.compile("Страница в соцсетях")).find_next().find_all("a")
            for sn in item_social_networks:
                sn_url = sn.get("href")
                sn_url = unquote(sn_url.split("?to=")[1].split("&")[0])
                social_networks_list.append(sn_url)
        except Exception as _ex:
            social_networks_list = None
            
        result_list.append(
            {
                "item_name": item_name,
                "item_url": url,
                "item_phones_list": item_phones_list,
                "item_address": item_address,
                "item_site": item_site,
                "social_networks_list": social_networks_list
            }
        )
        
        time.sleep(random.randrange(2, 5))
        
        if count%10 == 0:
            time.sleep(random.randrange(5, 9))
            
        print(f"[+] Processed: {count}/{urls_count}")
            
        count += 1
        
    with open("lesson12/result.json", "w") as file:
        json.dump(result_list, file, indent=4, ensure_ascii=False)
        
    return "[INFO] Data collected successfully!"
        

def main():
    get_source_html(url="https://spb.zoon.ru/medical/?search_query_form=1&m%5B5200e522a0f302f066000055%5D=1&center%5B%5D=59.91878264665887&center%5B%5D=30.342586983263384&zoom=10")
    # print(get_items_urls(file_path="file_path"))
    # print(get_data(file_path="file_path"))
    
    
if __name__ == "__main__":
    main()
