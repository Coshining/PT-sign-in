# -*- coding: utf-8 -*-
"""
cron: 0 30 04 * * *
new Env('PT_SIGN_CONFIG');
"""

# from sendNotify import send  # 调试

from notify import send  # 导入青龙后自动有这个文件
import json
import requests
import re
import os
import time

requests.packages.urllib3.disable_warnings()


def sign(url: str, cookie: str) -> tuple[bool, str]:
    """
    签到单个PT站点
    """
    # 基础变量
    max_retries = 3
    retries = 0
    msg = ""
    is_success = False

    # 正式请求
    while retries < max_retries:
        try:
            print(f"\t第{retries + 1}次执行签到")
            sign_in_url = url + "/attendance.php"
            headers = {
                "Cookie": cookie,
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "accept-language": "zh-CN,zh;q=0.9,und;q=0.8",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
            }

            rsp = requests.get(
                url=sign_in_url, headers=headers, timeout=15, verify=False
            )

            rsp_text = rsp.text
            success = False
            if "这是您的第" in rsp_text:
                # 先匹配当前魔力值信息
                magic_value = (
                    re.search(r"魔力值.*?(\d+(\,\d+)?(\.\d+)?)", rsp_text)
                    .group(1)
                    .replace(",", "")
                )
                msg += "当前魔力值为: " + magic_value + " 。"
                # 匹配当前签到提示
                pattern = r"这是您的第 <b>(\d+)</b>[\s\S]*?今日签到排名：<b>(\d+)</b>"
                result = re.search(pattern, rsp_text)
                result = result.group()
                # 剔除多余字符
                result = result.replace("<b>", "")
                result = result.replace("</b>", "")
                result = result.replace("点击白色背景的圆点进行补签。", "")
                result = result.replace('<span style="float:right">', "")
                msg += result
                success = True
                is_success = True

            if success:
                print("\t签到结果: ", msg)
                break  # 成功执行签到，跳出循环
            elif retries >= max_retries:
                print("\t达到最大重试次数，签到失败。")
                break
            else:
                retries += 1
                print("\t签到失败，等待20秒后进行重试...")
                time.sleep(20)
        except Exception as e:
            print("\t签到失败，失败原因:" + str(e))
            retries += 1
            if retries >= max_retries:
                print("\t达到最大重试次数，签到失败。")
                break
            else:
                print("\t等待20秒后进行重试...")
                time.sleep(20)

    return is_success, msg


if __name__ == "__main__":
    config = os.getenv("PT_SIGN_CONFIG")
    # config = open("example.json", "r", encoding="utf-8").read()
    sites = json.loads(config)["pt site config"]

    rep = {"success": [], "fail": []}
    for site in sites:
        name = site["name"]
        url = site["url"]
        cookie = site["cookie"]

        print(f"PT站 {name} {url} 开始签到...")

        res = sign(url, cookie)

        rep["success" if res[0] else "fail"].append(f"{name} {res[1]}")

        print(f"PT站 {name} {url} 签到结束！\n")

    send(
        "PT站 签到结果",
        f"成功站点：{'\n'.join(rep['success'])}\n失败站点：{'\n'.join(rep['fail'])}。",
    )
