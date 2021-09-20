import requests
import json
import os
import time


headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
}


def get_data_file(headers):
    """Collect data and return a JSON file"""

    # url = "https://www.landingfolio.com/"

    # r = requests.get(url=url, headers=headers)

    # with open("index.html", "w") as file:
    #     file.write(r.text)

    offset = 0
    img_count = 0
    result_list = []

    while True:
        url = f"https://s1.landingfolio.com/api/v1/inspiration/?offset={offset}&color=%23undefined"

        response = requests.get(url=url, headers=headers)
        data = response.json()

        for item in data:
            if "description" in item:

                images = item.get("images")
                img_count += len(images)

                for img in images:
                    img.update({"url": f"https://landingfoliocom.imgix.net/{img.get('url')}"})

                result_list.append(
                    {
                        "title": item.get("title"),
                        "description": item.get("description"),
                        "url": item.get("url"),
                        "images": images
                    }
                )
            else:
                with open("result_list.json", "a") as file:
                    json.dump(result_list, file, indent=4, ensure_ascii=False)

                return f"[INFO] Work finished. Images count is: {img_count}\n{'=' * 20}"

        print(f"[+] Processed {offset}")
        offset += 1


def download_imgs(file_path):
    """Download images"""

    try:
        with open(file_path) as file:
            src = json.load(file)
    except Exception as _ex:
        print(_ex)
        return "[INFO] Check the file path!"

    items_len = len(src)
    count = 1

    for item in src[:100]:
        item_name = item.get("title")
        item_imgs = item.get("images")

        if not os.path.exists(f"data/{item_name}"):
            os.mkdir(f"data/{item_name}")

        for img in item_imgs:
            r = requests.get(url=img["url"])

            with open(f"data/{item_name}/{img['type']}.png", "wb") as file:
                file.write(r.content)

        print(f"[+] Download {count}/{items_len}")
        count += 1

    return "[INFO] Work finished!"


def main():
    start_time = time.time()

    print(get_data_file(headers=headers))
    print(download_imgs("result_list.json"))

    finish_time = time.time() - start_time
    print(f"Worked time: {finish_time}")


if __name__ == "__main__":
    main()
