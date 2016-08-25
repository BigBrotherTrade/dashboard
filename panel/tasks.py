# coding=utf-8
#
# Copyright 2016 timercrack
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
import logging
import re
import datetime

import pytz
from collections import defaultdict
import xml.etree.ElementTree as ET

import ujson as json
import redis
import requests
from bs4 import BeautifulSoup
from django.db.models import Max

from dashboard import app
from panel.models import *

logger = logging.getLogger('panel.tasks')


@app.task(bind=True)
def collect_quote(_):
    """
    各品种的交易合约更新（ctp，新浪）
    各品种的主联合约：计算基差，主联合约复权（新浪）
    资金曲线（ctp）
    各品种换月标志
    各品种开仓价格
    各品种平仓价格
    微信报告
    """
    logger.info('start collect_quote')
    try:
        if not is_trading_day():
            logger.info('今日是非交易日, 不计算任何数据。')
            return
        fetch_today_bars()
        inst_dict, inst_set = get_newest_inst()
        update_inst_margin_fee(inst_set)
        for code, data in inst_dict.items():
            inst_obj, created = Instrument.objects.update_or_create(product_code=code, defaults={
                'exchange': data['exchange'],
                'name': data['name'],
                'all_inst': ','.join(sorted(inst_set[code]))
            })
            main_inst, updated = calc_main_inst(inst_obj)
            if updated:
                check_rollover(inst_obj)
            calc_signal(inst_obj)
    except Exception as e:
        logger.error('collect_quote failed: %s', e, exc_info=True)
    logger.info('collect_quote done!')


def update_inst_margin_fee(inst_set):
    """
    更新每一个合约的保证金和手续费
    :param inst_set:
    :return:
    """
    pass


def get_newest_inst():
    """
    从CTP获取正在交易的所有合约
    :return: 品种信息, 每个品种的正在交易的合约集合
    """
    inst_set = defaultdict(set)
    inst_dict = defaultdict(dict)
    redis_client = redis.StrictRedis()
    pubs = redis_client.pubsub()
    pubs.psubscribe('MSG:CTP:RSP:TRADE:OnRspQryInstrument:1')
    regex = re.compile('(.*?)([0-9]+)$')
    redis_client.publish('MSG:CTP:REQ:ReqQryInstrument', json.dumps({
        'RequestID': 1,
    }))
    for message in pubs.listen():
        if message['type'] != 'pmessage':
            continue
        inst = json.loads(message['data'].decode('utf8'))
        if not inst['empty']:
            if inst['IsTrading'] == 1:
                inst_set[inst['ProductID']].add(inst['InstrumentID'])
                inst_dict[inst['ProductID']]['exchange'] = inst['ExchangeID']
                inst_dict[inst['ProductID']]['product_code'] = inst['ProductID']
                if 'name' not in inst_dict[inst['ProductID']]:
                    inst_dict[inst['ProductID']]['name'] = regex.match(inst['InstrumentName']).group(1)
        if inst['bIsLast']:
            break
    return inst_dict, inst_set


def calc_main_inst(inst: Instrument, day: datetime.datetime):
    """
    [["2016-07-18","2116.000","2212.000","2106.000","2146.000","34"],...]
    """
    main_inst = None
    updated = False
    check = DailyBar.objects.filter(
        exchange=inst.exchange, code__startswith=inst.product_code, expire_date__gte=day.strftime('%y%m'),
        time=day, volume__gte=10000, open_interest__gte=10000).order_by('-volume').first()
    if check is None:
        check = DailyBar.objects.filter(exchange=inst.exchange, code__startswith=inst.product_code,).values('time', 'code').annotate(Max('volume'))
    if inst.main_code is None and check1 is not None:
        inst.main_code = check1.code
        inst.save(update_fields=['main_code'])
    for inst_code in inst.all_inst.split(','):
        rst = requests.get(
            'http://stock2.finance.sina.com.cn/futures/api/json.php/IndexService.getInnerFuturesDailyKLine?symbol={}'.format(inst_code))
        for day_bar in rst.json():
            pass

    return main_inst, updated


def check_rollover(inst):
    pass


def calc_signal(inst):
    pass


def fetch_daily_bar(day: datetime.datetime, market: str):
    error_data = None
    try:
        day = day.replace(tzinfo=pytz.FixedOffset(480))
        day_str = day.strftime('%Y%m%d')
        if market == ExchangeType.SHFE:
            rst = requests.get('http://www.shfe.com.cn/data/dailydata/kx/kx{}.dat'.format(day_str))
            rst_json = rst.json()
            for inst_data in rst_json['o_curinstrument']:
                """
    {'OPENINTERESTCHG': -11154, 'CLOSEPRICE': 36640, 'SETTLEMENTPRICE': 36770, 'OPENPRICE': 36990,
    'PRESETTLEMENTPRICE': 37080, 'ZD2_CHG': -310, 'DELIVERYMONTH': '1609', 'VOLUME': 51102,
    'PRODUCTSORTNO': 10, 'ZD1_CHG': -440, 'OPENINTEREST': 86824, 'ORDERNO': 0, 'PRODUCTNAME': '铜                  ',
    'LOWESTPRICE': 36630, 'PRODUCTID': 'cu_f    ', 'HIGHESTPRICE': 37000}
                """
                error_data = inst_data
                if inst_data['DELIVERYMONTH'] == '小计' or inst_data['PRODUCTID'] == '总计':
                    continue
                if '_' not in inst_data['PRODUCTID']:
                    continue
                DailyBar.objects.update_or_create(
                    code=inst_data['PRODUCTID'].split('_')[0] + inst_data['DELIVERYMONTH'],
                    exchange=market, time=day, defaults={
                        'expire_date': inst_data['DELIVERYMONTH'],
                        'open': inst_data['OPENPRICE'] if inst_data['OPENPRICE'] else inst_data['CLOSEPRICE'],
                        'high': inst_data['HIGHESTPRICE'] if inst_data['HIGHESTPRICE'] else
                        inst_data['CLOSEPRICE'],
                        'low': inst_data['LOWESTPRICE'] if inst_data['LOWESTPRICE']
                        else inst_data['CLOSEPRICE'],
                        'close': inst_data['CLOSEPRICE'],
                        'volume': inst_data['VOLUME'] if inst_data['VOLUME'] else 0,
                        'open_interest': inst_data['OPENINTEREST'] if inst_data['OPENINTEREST'] else 0})
        elif market == ExchangeType.DCE:
            rst = requests.post('http://www.dce.com.cn/PublicWeb/MainServlet', {
                'action': 'Pu00011_result', 'Pu00011_Input.trade_date': day_str, 'Pu00011_Input.variety': 'all',
                'Pu00011_Input.trade_type': 0})
            soup = BeautifulSoup(rst.text, 'lxml')
            for tr in soup.select("tr")[2:-4]:
                inst_data = list(tr.stripped_strings)
                error_data = inst_data
                """
    [0'商品名称', 1'交割月份', 2'开盘价', 3'最高价', 4'最低价', 5'收盘价', 6'前结算价', 7'结算价', 8'涨跌', 9'涨跌1', 10'成交量', 11'持仓量', 12'持仓量变化', 13'成交额']
    ['豆一', '1609', '3,699', '3,705', '3,634', '3,661', '3,714', '3,668', '-53', '-46', '5,746', '5,104', '-976', '21,077.13']
                """
                if '小计' in inst_data[0]:
                    continue
                DailyBar.objects.update_or_create(
                    code=DCE_NAME_CODE[inst_data[0]] + inst_data[1],
                    exchange=market, time=day, defaults={
                        'expire_date': inst_data[1],
                        'open': inst_data[2].replace(',', '') if inst_data[2] != '-' else inst_data[5].replace(',', ''),
                        'high': inst_data[3].replace(',', '') if inst_data[3] != '-' else inst_data[5].replace(',', ''),
                        'low': inst_data[4].replace(',', '') if inst_data[4] != '-' else inst_data[5].replace(',', ''),
                        'close': inst_data[5].replace(',', ''),
                        'volume': inst_data[10].replace(',', ''),
                        'open_interest': inst_data[11].replace(',', '')})
        elif market == ExchangeType.CZCE:
            rst = requests.get(
                'http://www.czce.com.cn/portal/DFSStaticFiles/Future/{}/{}/FutureDataDaily.txt'.format(
                    day.year, day_str))
            if rst.status_code == 404:
                rst = requests.get(
                    'http://www.czce.com.cn/portal/exchange/{}/datadaily/{}.txt'.format(
                        day.year, day_str))
            for lines in rst.content.decode('gbk').split('\r\n')[1:-3]:
                if '小计' in lines or '品种' in lines:
                    continue
                inst_data = [x.strip() for x in lines.split('|' if '|' in lines else ',')]
                error_data = inst_data
                """
[0'品种月份', 1'昨结算', 2'今开盘', 3'最高价', 4'最低价', 5'今收盘', 6'今结算', 7'涨跌1', 8'涨跌2', 9'成交量(手)', 10'空盘量', 11'增减量', 12'成交额(万元)', 13'交割结算价']
['CF601', '11,970.00', '11,970.00', '11,970.00', '11,800.00', '11,870.00', '11,905.00', '-100.00',
'-65.00', '13,826', '59,140', '-10,760', '82,305.24', '']
                """
                expire_date = int(re.findall('\d+', inst_data[0])[0])
                if expire_date < 1000:
                    expire_date += 1000
                DailyBar.objects.update_or_create(
                    code=inst_data[0],
                    exchange=market, time=day, defaults={
                        'expire_date': expire_date,
                        'open': inst_data[2].replace(',', '') if float(inst_data[2].replace(',', '')) > 0.1
                        else inst_data[5].replace(',', ''),
                        'high': inst_data[3].replace(',', '') if float(inst_data[3].replace(',', '')) > 0.1
                        else inst_data[5].replace(',', ''),
                        'low': inst_data[4].replace(',', '') if float(inst_data[4].replace(',', '')) > 0.1
                        else inst_data[5].replace(',', ''),
                        'close': inst_data[5].replace(',', ''),
                        'volume': inst_data[9].replace(',', ''),
                        'open_interest': inst_data[10].replace(',', '')})
        elif market == ExchangeType.CFFEX:
            rst = requests.get('http://www.cffex.com.cn/fzjy/mrhq/{}/index.xml'.format(
                day.strftime('%Y%m/%d')))
            tree = ET.fromstring(rst.text)
            for inst_data in tree.getchildren():
                """
<dailydata>
<instrumentid>IC1609</instrumentid>
<tradingday>20160824</tradingday>
<openprice>6336.8</openprice>
<highestprice>6364.4</highestprice>
<lowestprice>6295.6</lowestprice>
<closeprice>6314.2</closeprice>
<openinterest>24703.0</openinterest>
<presettlementprice>6296.6</presettlementprice>
<settlementpriceIF>6317.6</settlementpriceIF>
<settlementprice>6317.6</settlementprice>
<volume>10619</volume>
<turnover>1.3440868E10</turnover>
<productid>IC</productid>
<delta/>
<segma/>
<expiredate>20160919</expiredate>
</dailydata>
                """
                error_data = list(inst_data.itertext())
                DailyBar.objects.update_or_create(
                    code=inst_data.findtext('instrumentid').strip(),
                    exchange=market, time=day, defaults={
                        'expire_date': inst_data.findtext('expiredate')[2:6],
                        'open': inst_data.findtext('openprice').replace(',', '') if inst_data.findtext('openprice') else inst_data.findtext('closeprice').replace(',', ''),
                        'high': inst_data.findtext('highestprice').replace(',', '') if inst_data.findtext('highestprice') else inst_data.findtext('closeprice').replace(',', ''),
                        'low': inst_data.findtext('lowestprice').replace(',', '') if inst_data.findtext('lowestprice') else inst_data.findtext('closeprice').replace(',', ''),
                        'close': inst_data.findtext('closeprice').replace(',', ''),
                        'volume': inst_data.findtext('volume').replace(',', ''),
                        'open_interest': inst_data.findtext('openinterest').replace(',', '')})

    except Exception as e:
        logger.error('%s, row=%s', repr(e), error_data, exc_info=True)


def fetch_today_bars():
    if is_trading_day():
        day = datetime.datetime.today()
        fetch_daily_bar(day, 'SHFE')
        fetch_daily_bar(day, 'DCE')
        fetch_daily_bar(day, 'CZCE')
        fetch_daily_bar(day, 'CFFEX')
        return True


def is_trading_day():
    """
    判断今天是否是交易日, 方法是从中金所获取今日的K线数据,判断http的返回码(如果出错会返回302重定向至404页面),
    因为开市前也可能返回302, 所以适合收市后(下午)使用
    :return: bool
    """
    day = datetime.datetime.today()
    rst = requests.get('http://www.cffex.com.cn/fzjy/mrhq/{}/index.xml'.format(day.strftime('%Y%m/%d')))
    return rst.status_code != 302
