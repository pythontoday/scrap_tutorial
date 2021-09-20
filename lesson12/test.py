from urllib.parse import unquote

url = "https://spb.zoon.ru/redirect/?to=https%3A%2F%2Fvk.com%2Fmeddynasty&hash=fdf6e88a9c5fd8539a1d6ed8f8fbb03e&from=549cbbcbaa2d494e258b4589.7ada&ext_site=ext_vk&backurl=https%3A%2F%2Fspb.zoon.ru%2Fmedical%2Fmeditsinskij_tsentr_dinastiya_na_ulitse_repischeva%2F"

url = unquote(url.split("?to=")[1].split("&")[0])
print(url)