from flask import Flask, request
import requests
import xml.etree.ElementTree as ET

app = Flask(__name__)

# ====== 改成你的信息 ======
WX_TOKEN = "1230"
WX_CORPID = "ww684d0184d559d00e"
WX_AGENTID = "1000002"
WX_SECRET = "dNNxQrIcPxeiIz4NKOatjoy3BUTDoJ7VlJYOeCxX9hw"
DEEPSEEK_API_KEY = "sk-23f55ae7ccae452c948ea25f4071343c"
# ==========================

def get_wx_token():
    url = f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={WX_CORPID}&corpsecret={WX_SECRET}"
    resp = requests.get(url).json()
    return resp.get("access_token")

def call_deepseek(msg):
    headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "你是群聊百科全书，知识渊博、说话像朋友聊天，简洁易懂。"},
            {"role": "user", "content": msg}
        ]
    }
    resp = requests.post("https://api.deepseek.com/chat/completions", headers=headers, json=data, timeout=30)
    return resp.json()["choices"][0]["message"]["content"]

def reply_to_wechat(user_id, content):
    token = get_wx_token()
    url = f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={token}"
    data = {"touser": user_id, "msgtype": "text", "agentid": WX_AGENTID, "text": {"content": content}}
    requests.post(url, json=data)

@app.route("/wechat", methods=["GET", "POST"])
def wechat():
    if request.method == "GET":
        return request.args.get("echostr", "")
    xml_data = request.data
    root = ET.fromstring(xml_data)
    msg_type = root.find("MsgType").text
    content = root.find("Content").text
    user_id = root.find("FromUserName").text
    if msg_type == "text":
        reply = call_deepseek(content)
        reply_to_wechat(user_id, reply)
    return "ok"

@app.route("/")
def home():
    return "DeepSeek 机器人运行中..."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
