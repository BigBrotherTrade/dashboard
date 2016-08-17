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
import ujson as json
from collections import defaultdict
import redis
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
        inst_dict, inst_set = get_newest_inst()
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
    pass


def get_newest_inst():
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


def calc_main_inst(inst):
    main_inst = None
    updated = False
    return main_inst, updated


def check_rollover(inst):
    pass


def calc_signal(inst):
    pass
