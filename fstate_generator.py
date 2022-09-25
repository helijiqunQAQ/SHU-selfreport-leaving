import base64
import datetime as dt
import json
import re
from pathlib import Path

from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont


def _generate_fstate_base64(fstate):
    fstate_json = json.dumps(fstate, ensure_ascii=False)
    fstate_bytes = fstate_json.encode("utf-8")
    return base64.b64encode(fstate_bytes).decode()


def generate_fstate_day(BaoSRQ, ShiFSH, JinXXQ, ShiFZX, XiaoQu,
                        ddlSheng, ddlShi, ddlXian, ddlJieDao, XiangXDZ, ShiFZJ,
                        SuiSM, XingCM):
    with open(Path(__file__).resolve().parent.joinpath('fstate_day.json'), encoding='utf8') as f:
        fstate = json.loads(f.read())

    fstate['p1_BaoSRQ']['Text'] = BaoSRQ
    fstate['p1_P_GuoNei_ShiFSH']['SelectedValue'] = ShiFSH
    fstate['p1_P_GuoNei_JinXXQ']['SelectedValueArray'][0] = JinXXQ
    fstate['p1_P_GuoNei_ShiFZX']['SelectedValue'] = ShiFZX
    fstate['p1_P_GuoNei_XiaoQu']['SelectedValue'] = XiaoQu
    fstate['p1_ddlSheng']['F_Items'] = [[ddlSheng, ddlSheng, 1, '', '']]
    fstate['p1_ddlSheng']['SelectedValueArray'] = [ddlSheng]
    fstate['p1_ddlShi']['F_Items'] = [[ddlShi, ddlShi, 1, '', '']]
    fstate['p1_ddlShi']['SelectedValueArray'] = [ddlShi]
    fstate['p1_ddlXian']['F_Items'] = [[ddlXian, ddlXian, 1, '', '']]
    fstate['p1_ddlXian']['SelectedValueArray'] = [ddlXian]
    fstate['p1_ddlJieDao']['F_Items'] = [[ddlJieDao, ddlJieDao, 1, '', '']]
    fstate['p1_ddlJieDao']['SelectedValueArray'] = [ddlJieDao]
    fstate['p1_XiangXDZ']['Text'] = XiangXDZ
    fstate['p1_ShiFZJ']['SelectedValue'] = ShiFZJ
    # fstate['p1_P_GuoNei_pImages_HFimgSuiSM']['Text'] = SuiSM
    # fstate['p1_P_GuoNei_pImages_HFimgXingCM']['Text'] = XingCM

    fstate_base64 = _generate_fstate_base64(fstate)
    t = len(fstate_base64) // 2
    fstate_base64 = fstate_base64[:t] + 'F_STATE' + fstate_base64[t:]

    return fstate_base64


def _html_to_json(html):
    return json.loads(html[html.find('=') + 1:])


def get_ShouJHM(sess):
    ShouJHM = '111111111'

    r = sess.get(f'https://selfreport.shu.edu.cn/PersonInfo.aspx')
    t = re.findall(r'^.*//\]', r.text, re.MULTILINE)[0]
    htmls = t.split(';var ')
    for i, h in enumerate(htmls):
        try:
            if 'ShouJHM' in h:
                print('-ShouJHM-')
                ShouJHM = _html_to_json(htmls[i - 1])['Text']
        except:

    return ShouJHM
