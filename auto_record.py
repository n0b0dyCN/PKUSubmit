import requests
import os
import json
import re
import datetime
import argparse

USERNAME = os.getenv("PKU_USERNAME")
PASSWORD = os.getenv("PKU_PASSWORD")

DATA_OUT = {
    "sqbh":"",
    "sqlb":"出校",
    "szxq":"",
    "email":"",
    "lxdh":"",
    "crxsy":"",
    "cxrq":"",
    "cxcs":1,
    "cxxm":"",
    "cxxdgj":"",
    "sfqdhxrq":"",
    "rxrq":"",
    "rxcs":1,
    "rxxm":"",
    "cxmdd":"北京",
    "rxjzd":"北京",
    "jzdbjqx":"08",
    "jzdbjjd":"燕园街道",
    "jzdbjyzzj14":"",
    "jzdbjdjrq":"",
    "jzdjwgjdq":"156",
    "jzdjwssdm":"",
    "jzdjwdjsdm":"",
    "jzdjwdjrq":"",
    "sfqdcxrq":"",
    "dfx14qrbz":"y",
    "sfyxtycj":"",
    "tjbz":"",
    "shbz":"",
    "sfkcx":True
}

DATA_IN = {
    "sqbh":"",
    "sqlb":"入校",
    "szxq":"燕园",
    "email":"",
    "lxdh":"",
    "crxsy":"",
    "cxrq":"",
    "cxcs":1,
    "cxxm":"",
    "cxxdgj":"",
    "sfqdhxrq":"",
    "rxrq":"",
    "rxcs":1,
    "rxxm":"",
    "cxmdd":"北京",
    "rxjzd":"北京",
    "jzdbjqx":"08",
    "jzdbjjd":"燕园街道",
    "jzdbjyzzj14":"y",
    "jzdbjdjrq":"",
    "jzdjwgjdq":"156",
    "jzdjwssdm":"",
    "jzdjwdjsdm":"",
    "jzdjwdjrq":"",
    "sfqdcxrq":"",
    "dfx14qrbz":"y",
    "sfyxtycj":"",
    "tjbz":"",
    "shbz":"",
    "sfkcx":True
}

headers={
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
    "Origin": "https://iaaa.pku.edu.cn"
}

LOG = "```"
def log(s):
    global LOG
    LOG += s + "\n"

def logv(vname, v):
    global LOG
    LOG += vname + " " + str(v) + "\n"

def fail(reason, msg):
    log(reason)
    log(msg)
    raise Exception(f"""{reason}\n\n{msg}\n""")

def finish_log():
    global LOG
    LOG += "```\n\n"

def oauth_login(sess):
    post_data = {
        "appid": "portal2017",
        "userName": USERNAME,
        "password": PASSWORD,
        "redirUrl": "https://portal.pku.edu.cn/portal2017/ssoLogin.do"
    }
    login_url = "https://iaaa.pku.edu.cn/iaaa/oauthlogin.do"
    resp = sess.post(login_url, data=post_data, headers=headers)
    j = json.loads(resp.text)
    if not j["success"]:
        fail("Fail in login:", resp.text)
    return j["token"]

def sso_login(sess, token):
    url = f"https://portal.pku.edu.cn/portal2017/ssoLogin.do?_rand=0.6444242332881047&token={token}"
    resp = sess.get(url, headers=headers)

def getSimsoToken(sess):
    url = "https://portal.pku.edu.cn/portal2017/util/appSysRedir.do?appId=stuCampusExEn"
    resp = sess.get(url, allow_redirects=False, headers=headers)
    found = re.findall(r'token=([a-z0-9]+)&', resp.headers['Location'])
    if len(found) != 1:
        fail("Fail in getSimsoToken: no token in `Location`", resp.headers['Location'])
    return found[0]

def simsoLogin(sess, token):
    url = f"https://simso.pku.edu.cn/ssapi/simsoLogin?token={token}"
    resp = sess.get(url, headers=headers)
    j = json.loads(resp.text)
    if not j["success"]:
        fail("Fail in simsoLogin", resp.text)
    return j

def get_apply_status(sess, sid):
    url = f"https://simso.pku.edu.cn/ssapi/stuaffair/epiAccess/getSqzt?sid={sid}&_sk={USERNAME}"
    resp = sess.get(url, headers=headers)
    return json.loads(resp.text)

def save_out(sess, sid):
    url = f"https://simso.pku.edu.cn/ssapi/stuaffair/epiAccess/saveSqxx?sid={sid}&_sk={USERNAME}"
    resp = sess.post(url, headers=headers, json=DATA_OUT)
    j = json.loads(resp.text)
    ret = j["row"]
    return ret

def save_in(sess, sid):
    url = f"https://simso.pku.edu.cn/ssapi/stuaffair/epiAccess/saveSqxx?sid={sid}&_sk={USERNAME}"
    resp = sess.post(url, headers=headers, json=DATA_IN)
    j = json.loads(resp.text)
    ret = j["row"]
    return ret

def submit_application(sess, sid, application_id):
    url = f"https://simso.pku.edu.cn/ssapi/stuaffair/epiAccess/submitSqxx?sid={sid}&sqbh={application_id}&_sk={USERNAME}"
    resp = sess.get(url, headers=headers)
    j = json.loads(resp.text)
    logv("Submit status:", j["success"])
    return j

def logout(sess, sid):
    url = f"https://simso.pku.edu.cn/ssapi/logout?sid={sid}"
    sess.get(url)
    url = f"https://portal.pku.edu.cn/portal2017/logout.do?_redir_2_webvpn=1"
    sess.get(url)

def wechat_push(key, title, message):
    url = f"https://sc.ftqq.com/{key}.send?text={title}&desp={message}"
    requests.get(url)

def run(wechat_key):
    title = "备案成功 "
    msg = ""
    try:
        sess = requests.Session()

        # Login operations
        oauth_token = oauth_login(sess)
        logv("oauth_token", oauth_token)
        sso_login(sess, oauth_token)
        simso_token = getSimsoToken(sess)
        logv("simso_token", simso_token)
        simso_meta = simsoLogin(sess, simso_token)
        sid = simso_meta["sid"]
        logv("simso_meta", simso_meta)
        sess.cookies.set("sid", sid, domain="pku.edu.cn")

        log("Out application")
        out_application_id = save_out(sess, sid)
        logv("out_application_id", out_application_id)
        status = submit_application(sess, sid, out_application_id)
        if not status["success"]:
            fail("Fail to submit OUT application", json.dumps(status))

        log("In application")
        in_application_id = save_in(sess, sid)
        logv("in_application_id", in_application_id)
        status = submit_application(sess, sid, in_application_id)
        if not status["success"]:
            fail("Fail to submit IN application", json.dumps(status))

        log("备案成功")

        # logout
        logout(sess, sid)
    except Exception as e:
        title = "备案失败"
        log(str(e))
    finish_log()

    title += datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S %f")
    msg += LOG

    if wechat_key:
        wechat_push(wechat_key, title, msg)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='自动出校备案',
        epilog=f"""Add environment variable before you use!
        PKU_USERNAME=学号 PKU_PASSWORD=密码 python3 {__file__} balabala"""
    )
    parser.add_argument('--campus', dest='campus', action='store', required=True,
                        help='校区（燕园、万柳、畅春园、圆明园、中关新园、大兴）')
    parser.add_argument('--email', dest='email', action='store', required=True,
                        help='邮箱')
    parser.add_argument('--phone', dest='phone', action='store', required=True,
                        help='电话')
    parser.add_argument('--reason', dest='reason', action='store', required=True,
                        help='出入校事由')
    parser.add_argument('--route', dest='route', action='store', required=True,
                        help='行动轨迹')
    parser.add_argument('--wechat-key', dest='wechat_key', action='store',
                        help='微信推送key，在 http://sc.ftqq.com/3.version 获取，可以妹有')
    args = parser.parse_args()
    print(args)
    
    DATA_OUT["szxq"] = args.campus
    DATA_OUT["email"] = args.email
    DATA_OUT["lxdh"] = args.phone
    DATA_OUT["crxsy"] = args.reason
    DATA_OUT["cxxdgj"] = args.route
    DATA_OUT["cxrq"] = datetime.datetime.now().strftime("%Y%m%d")

    DATA_IN["email"] = args.email
    DATA_IN["lxdh"] = args.phone
    DATA_IN["crxsy"] = args.reason
    DATA_IN["rxrq"] = datetime.datetime.now().strftime("%Y%m%d")
    wechat_key = args.wechat_key

    run(wechat_key)
    print(LOG)
