# # import json
# from loguru import logger
# from fake_useragent import UserAgent
# import json
# from cellfunctions_ import *


# def read_headers_from_json(
#     cookie_json_filepath="cookies.json", headers_example="_headers_ example.json"
# ) -> dict:
#     logger.debug("尝试从cookies.json获取headers 的cookie.......")
#     with open(cookie_json_filepath, encoding="utf-8") as f:
#         try:
#             # dread = dict(json.load(f))
#             d_list: list = json.load(f)
#             # dict().keys()
#             # print(list(dread.keys())[0])
#             headers_cookie = "; ".join([f'{d["name"]}={d["value"]}' for d in d_list])
#             with open(headers_example, encoding="utf-8") as h:
#                 headers = dict(json.load(h))
#                 headers["cookie"] = headers_cookie
#             # print(headers)
#         except Exception as e:
#             # raise e
#             # raise NameError("Not found headers") from e
#             logger.warning("失败,将用函数get_headers()采用playwright无头模式下自动获取headers.......")
#             headers = get_headers()
#             # headers = {}

#         logger.success("获取headers成功......")

#         return headers


# print(read_headers_from_json())
