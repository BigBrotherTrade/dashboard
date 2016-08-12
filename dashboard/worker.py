import ujson as json
import os
import asyncio
from collections import defaultdict

import aioredis
import django
import sys
import redis

sys.path.append('/Users/jeffchen/Documents/gitdir/dashboard')
os.environ["DJANGO_SETTINGS_MODULE"] = "dashboard.settings"
django.setup()

from panel.models import *

async def instrument_reader(chanel: aioredis.Channel, fut: asyncio.Future):
    inst_set = defaultdict(set)
    inst_dict = defaultdict(dict)
    print('wait for data...')
    while await chanel.wait_message():
        print('got msg!')
        chs, msg = await chanel.get(encoding='utf-8')
        print('chs=', chs)
        inst = json.loads(msg)
        print('inst=', inst)
        if not inst['empty']:
            if inst['IsTrading'] == 1:
                inst_set[inst['ProductID']].add(inst['InstrumentID'])
                inst_dict[inst['ProductID']]['exchange'] = inst['ExchangeID']
                inst_dict[inst['ProductID']]['product_code'] = inst['ProductID']
        if inst['bIsLast']:
            print('inst_dict len={}'.format(len(inst_dict)))
            for code, data in inst_dict.items():
                Instrument.objects.update_or_create(product_code=code, defaults={
                    'exchange': data['exchange'],
                    'all_inst': ','.join(inst_set[code])
                })
            fut.set_result(inst_set)


async def test():
    loop = asyncio.get_event_loop()
    sub_client = await aioredis.create_redis(('10.211.55.2', 6379))
    ch = await sub_client.subscribe('MSG:CTP:RSP:TRADE:OnRspQryInstrument:1')
    cb = loop.create_future()
    task = asyncio.ensure_future(instrument_reader(ch, cb), loop=loop)
    print('waiting...')
    rst = await asyncio.wait_for(cb, 5)
    print('wait done! rst=', rst)
    await sub_client.unsubscribe('MSG:CTP:RSP:TRADE:OnRspQryInstrument:1')
    print('punsubscribe done!')
    sub_client.close()
    loop.run_until_complete(asyncio.wait(task, loop=loop))


def redis_cb(*args, **kwargs):
    print(args)
    print(kwargs)


if __name__ == '__main__':
    inst_set = defaultdict(set)
    inst_dict = defaultdict(dict)
    r = redis.StrictRedis()
    p = r.pubsub()
    p.psubscribe('MSG:CTP:RSP:TRADE:OnRspQryInstrument:*')
    for message in p.listen():
        if message['type'] != 'pmessage':
            continue
        inst = json.loads(message['data'].decode('utf8'))
        if not inst['empty']:
            if inst['IsTrading'] == 1:
                inst_set[inst['ProductID']].add(inst['InstrumentID'])
                inst_dict[inst['ProductID']]['exchange'] = inst['ExchangeID']
                inst_dict[inst['ProductID']]['product_code'] = inst['ProductID']
                inst_dict[inst['ProductID']]['name'] = inst['InstrumentName']

        if inst['bIsLast']:
            print('inst_dict len={}'.format(len(inst_dict)))
            for code, data in inst_dict.items():
                Instrument.objects.update_or_create(product_code=code, defaults={
                    'exchange': data['exchange'],
                    'name': data['name'],
                    'all_inst': ','.join(inst_set[code])
                })
            break
    print('done!')
    # asyncio.get_event_loop().create_task(test())
    # asyncio.get_event_loop().run_forever()
    # print('done!')
