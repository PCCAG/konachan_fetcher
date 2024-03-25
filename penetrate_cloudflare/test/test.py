import re
from read_head_cookie import read_headers_from_json
import httpx


test_url = r"https://konachan.com/post/show/374584"
http_proxy = "http://127.0.0.1:62333"
proxies = {"http://": http_proxy, "https://": http_proxy}
headers = read_headers_from_json()
with httpx.Client(proxies=proxies, headers=headers) as c:  # type: ignore
    re = c.get(test_url)
    print(re.status_code)
    with open("reponse.html", "w", errors="ignore", encoding="UTF-8") as f:
        f.write(re.text)
