import re
import ujson as json
import os
from collections import defaultdict

import django
import sys
import redis

sys.path.append('/Users/jeffchen/Documents/gitdir/dashboard')
os.environ["DJANGO_SETTINGS_MODULE"] = "dashboard.settings"
django.setup()

from panel.models import *


if __name__ == '__main__':
    inst_set = defaultdict(set)
    inst_dict = defaultdict(dict)
    r = redis.StrictRedis()
    p = r.pubsub()
    p.psubscribe('MSG:CTP:RSP:TRADE:OnRspQryInstrument:*')
    r = re.compile('(.*?)([0-9]+)$')
    for message in p.listen():
        if message['type'] != 'pmessage':
            continue
        inst = json.loads(message['data'].decode('utf8'))
        if not inst['empty']:
            if inst['IsTrading'] == 1:
                inst_set[inst['ProductID']].add(inst['InstrumentID'])
                inst_dict[inst['ProductID']]['exchange'] = inst['ExchangeID']
                inst_dict[inst['ProductID']]['product_code'] = inst['ProductID']
                if 'name' not in inst_dict[inst['ProductID']]:
                    inst_dict[inst['ProductID']]['name'] = r.match(inst['InstrumentName']).group(1)

        if inst['bIsLast']:
            print('inst_dict len={}'.format(len(inst_dict)))
            for code, data in inst_dict.items():
                Instrument.objects.update_or_create(product_code=code, defaults={
                    'exchange': data['exchange'],
                    'name': data['name'],
                    'all_inst': ','.join(sorted(inst_set[code]))
                })
            break
    print('done!')
    # http://finance.sina.com.cn/iframe/futures_info_cff.js 合约数据
    # asyncio.get_event_loop().create_task(test())
    # asyncio.get_event_loop().run_forever()
    # print('done!')
