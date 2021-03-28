# This is the way
# Author: pythontoday
# YouTube: https://www.youtube.com/c/PythonToday/videos

import json
import os
import random
import re
import time
import requests
from bs4 import BeautifulSoup


def get_data(url):
    headers = {
        "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Mobile Safari/537.36"
    }

    projects_data_list = []
    iteration_count = 23
    print(f"Всего итераций: #{iteration_count}")

    for item in range(1, 24):
        req = requests.get(url + f"&PAGEN_1={item}&PAGEN_2={item}", headers)

        folder_name = f"data/data_{item}"

        if os.path.exists(folder_name):
            print("Папка уже существует!")
        else:
            os.mkdir(folder_name)

        with open(f"{folder_name}/projects_{item}.html", "w") as file:
            file.write(req.text)

        with open(f"{folder_name}/projects_{item}.html") as file:
            src = file.read()

        soup = BeautifulSoup(src, "lxml")
        articles = soup.find_all("article", class_="ib19")

        projects_urls = []
        for article in articles:
            project_url = "http://www.edutainme.ru" + article.find("div", class_="txtBlock").find("a").get("href")
            projects_urls.append(project_url)

        for project_url in projects_urls:
            req = requests.get(project_url, headers)
            project_name = project_url.split("/")[-2]

            with open(f"{folder_name}/{project_name}.html", "w") as file:
                file.write(req.text)

            with open(f"{folder_name}/{project_name}.html") as file:
                src = file.read()

            soup = BeautifulSoup(src, "lxml")
            project_data = soup.find("div", class_="inside")

            try:
                project_logo = "http://www.edutainme.ru" + project_data.find("div", class_="Img logo").find("img").get("src")
            except Exception:
                project_logo = "No project logo"

            try:
                project_name = project_data.find("div", class_="txt").find("h1").text
            except Exception:
                project_name = "No project name"

            try:
                project_short_description = project_data.find("div", class_="txt").find("h4", class_="head").text
            except Exception:
                project_short_description = "No project short description"

            try:
                project_website = project_data.find("div", class_="txt").find("p").find("a").text
            except Exception:
                project_website = "No project website"

            try:
                project_full_description = project_data.find("div", class_="textWrap").find("div", class_="rBlock").text
            except Exception:
                project_full_description = "No project full description"

            def replace_string(string):
                return ''.join(re.sub(r'(<p>|</p>)', "", string))
            project_full_description = replace_string(project_full_description)

            # rep = ["<p>", "</p>"]
            # for s in rep:
            #     if s in project_full_description:
            #         project_full_description = project_full_description.replace(s, "")

            projects_data_list.append(
                {
                    "Имя проекта": project_name,
                    "URL логотипа проекта": project_logo,
                    "Короткое описание проекта": project_short_description,
                    "Сайт проекта": project_website,
                    "Полное описание проекта": project_full_description.strip()
                }
            )

        iteration_count -= 1
        print(f"Итерация #{item} завершена, осталось итераций #{iteration_count}")
        if iteration_count == 0:
            print("Сбор данных завершен")
        time.sleep(random.randrange(2, 4))

    with open("data/projects_data.json", "a", encoding="utf-8") as file:
        json.dump(projects_data_list, file, indent=4, ensure_ascii=False)


def main():
    get_data("http://www.edutainme.ru/edindex/ajax.php?params=%7B%22LETTER%22%3Anull%2C%22RESTART%22%3A%22N%22%2C%22CHECK_DATES%22%3Afalse%2C%22arrWHERE%22%3A%5B%22iblock_startaps%22%5D%2C%22arrFILTER%22%3A%5B%22iblock_startaps%22%5D%2C%22startups%22%3A%22Y%22%2C%22SHOW_WHERE%22%3Atrue%2C%22PAGE_RESULT_COUNT%22%3A9%2C%22CACHE_TYPE%22%3A%22A%22%2C%22CACHE_TIME%22%3A0%2C%22TAGS_SORT%22%3A%22NAME%22%2C%22TAGS_PAGE_ELEMENTS%22%3A%22999999999999999999%22%2C%22TAGS_PERIOD%22%3A%22%22%2C%22TAGS_URL_SEARCH%22%3A%22%22%2C%22TAGS_INHERIT%22%3A%22Y%22%2C%22SHOW_RATING%22%3A%22Y%22%2C%22FONT_MAX%22%3A%2214%22%2C%22FONT_MIN%22%3A%2214%22%2C%22COLOR_NEW%22%3A%22000000%22%2C%22COLOR_OLD%22%3A%22C8C8C8%22%2C%22PERIOD_NEW_TAGS%22%3A%22%22%2C%22DISPLAY_TOP_PAGER%22%3A%22N%22%2C%22DISPLAY_BOTTOM_PAGER%22%3A%22N%22%2C%22SHOW_CHAIN%22%3A%22Y%22%2C%22COLOR_TYPE%22%3A%22Y%22%2C%22WIDTH%22%3A%22100%25%22%2C%22USE_LANGUAGE_GUESS%22%3A%22N%22%2C%22PATH_TO_USER_PROFILE%22%3A%22%23SITE_DIR%23people%5C%2Fuser%5C%2F%23USER_ID%23%5C%2F%22%2C%22SHOW_WHEN%22%3Afalse%2C%22PAGER_TITLE%22%3A%22%5Cu0420%5Cu0435%5Cu0437%5Cu0443%5Cu043b%5Cu044c%5Cu0442%5Cu0430%5Cu0442%5Cu044b+%5Cu043f%5Cu043e%5Cu0438%5Cu0441%5Cu043a%5Cu0430%22%2C%22PAGER_SHOW_ALWAYS%22%3Atrue%2C%22USE_TITLE_RANK%22%3Afalse%2C%22PAGER_TEMPLATE%22%3A%22%22%2C%22DEFAULT_SORT%22%3A%22rank%22%2C%22noTitle%22%3A%22Y%22%7D")


if __name__ == "__main__":
    main()
