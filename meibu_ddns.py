import datetime
import logging
import os.path
import re
import subprocess
from time import sleep

import requests

logging.basicConfig(filename=f"{os.path.splitext(os.path.basename(__file__))[0]}.log", level=logging.DEBUG,
                    format='%(asctime)s|%(funcName)s|%(levelname)s|%(message)s')


def write_ipv6(ipv6: str):
    logging.info("开始写入IPv6地址到ipv6.ini文件")
    f = open('ipv6.ini', 'w')
    f.write(ipv6)
    f.flush()
    f.close()
    logging.info("写入成功")


def read_ipv6():
    logging.info("读取上次记录的IPv6地址")
    if os.path.exists('ipv6.ini'):
        with open('ipv6.ini', 'r') as f:
            ipv6 = f.read()
            logging.info(f"读取成功，最后一次记录的地址为: {ipv6}")
            return ipv6
    else:
        logging.warning("不存在历史记录，写入空文件")
        write_ipv6('')
        return ''


def submit_ipv6() -> bool:
    logging.info("开始提交IPv6地址变更")
    resp = requests.get('http://v6.meibu.com/v6.asp?name=域名&pwd=密码')
    logging.info(f"请求成功，状态码:->{resp.status_code}<-,请求头:->{resp.headers}<-,内容:->{resp.text}<-")
    if resp.text == "ok":
        logging.info("更新成功")
        return True
    else:
        logging.error("更新失败")
        return False


def get_ipv6_address():
    ifconfig_result = subprocess.Popen(["ifconfig", "enp6s0"], stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE, text=True)
    grep_result = subprocess.Popen(['grep', '240e'], stdin=ifconfig_result.stdout, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, text=True)
    grep_output, grep_error = grep_result.communicate()
    # 打印结果
    ipv6_pattern = r"\b((?:[\da-fA-F]{0,4}:[\da-fA-F]{0,4}){2,7})(?:[\/\\%](\d{1,3}))?\b"
    if grep_output:
        ipv6 = re.findall(ipv6_pattern, grep_output)
        logging.info(f"执行ssh命令成功,执行结果:{grep_output}".strip())
        if ipv6.__len__() == 0:
            logging.error(f"解析IPv6地址失败,解析结果:{ipv6}")
            return None
        else:
            logging.info(f"解析IPv6地址成功,解析结果:{ipv6[0][0]}")
            return ipv6[0][0]
    if grep_error:
        logging.error(f"执行ssh命令失败,信息:{grep_error}")
        return None


if __name__ == '__main__':
    while True:
        sleep(60)
        last_ip = read_ipv6()
        cur_ip = get_ipv6_address()
        if cur_ip is not None:
            if last_ip == cur_ip:
                logging.info(f"与上次地址相同,上次ip:{last_ip},当前ip:{cur_ip}.\n")
                ...
            else:
                logging.info(f"与上次地址不相同,上次ip:{last_ip},当前ip:{cur_ip}\n")
                write_ipv6(cur_ip)
                submit_ipv6()
                logging.info(f"{datetime.datetime.now()}完成更新")
