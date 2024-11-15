import requests
import json


class BaiduErnie:
    host: str = "https://aip.baidubce.com"
    client_id: str = ""
    client_secret: str = ""
    access_token: str = ""

    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.get_access_token()

    def get_access_token(self):
        url = "https://aip.baidubce.com/oauth/2.0/token"
        payload = json.dumps("")
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        params = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }

        response = requests.request("POST", url, headers=headers, data=params)


        print("Response status code:", response.status_code)
        print("Response text:", response.text)  # 打印返回的文本内容

        if response.status_code == 200:
            result = response.json()
            self.access_token = result['access_token']
        else:
            raise Exception("获取access_token失败")

    def chat(self, messages: list, user_id: str) -> tuple:
        if not self.access_token:
            self.get_access_token()
        url = f"{self.host}/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions?access_token={self.access_token}"
        payload = json.dumps({
            "messages": messages,
            "temperature": 0.95,
            "top_p": 0.8,
            "penalty_score": 1,
            "enable_system_memory": False,
            "disable_search": False,
            "enable_citation": False,
            "response_format": "text"
        })
        headers = {
            'Content-Type': 'application/json'
        }
        # data = {"messages": messages, "user_id": user_id}
        response = requests.request("POST", url, headers=headers, data=payload)
        # response = requests.post(url, json=data)
        if response.status_code == 200:
            resp = response.json()
            print(resp)
            return resp["result"], resp
        else:
            raise Exception("请求失败")



