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
from django.db import models

from dashboard.const import *


class Address(models.Model):
    name = models.CharField(verbose_name='名称', max_length=64)
    url = models.CharField(verbose_name='地址', max_length=128)
    type = models.CharField(verbose_name='类型', max_length=16, choices=AddressType.choices)
    operator = models.CharField(verbose_name='运营商', max_length=16, choices=OperatorType.choices)

    class Meta:
        verbose_name = '前置地址'
        verbose_name_plural = '前置地址集合'

    def __str__(self):
        return '{}{}-{}'.format(self.name, self.get_operator_display(), self.get_type_display())


class Broker(models.Model):
    name = models.CharField(verbose_name='名称', max_length=64)
    contract_type = models.CharField(verbose_name='市场', max_length=32, choices=ContractType.choices)
    trade_address = models.ForeignKey(Address, verbose_name='交易前置', on_delete=models.CASCADE, related_name='trade_address')
    market_address = models.ForeignKey(Address, verbose_name='行情前置', on_delete=models.CASCADE, related_name='market_address')
    identify = models.CharField(verbose_name='唯一标志', max_length=32)
    username = models.CharField(verbose_name='用户名', max_length=32)
    password = models.CharField(verbose_name='密码', max_length=32)

    class Meta:
        verbose_name = '券商'
        verbose_name_plural = '券商集合'

    def __str__(self):
        return '{}-{}'.format(self.name, self.get_contract_type_display())


class Strategy(models.Model):
    broker = models.ForeignKey(Broker, verbose_name='券商', on_delete=models.CASCADE)
    name = models.CharField(verbose_name='名称', max_length=64)

    class Meta:
        verbose_name = '策略'
        verbose_name_plural = '策略集合'

    def __str__(self):
        return '{}'.format(self.name)


class Order(models.Model):
    broker = models.ForeignKey(Broker, verbose_name='券商', on_delete=models.CASCADE)
    strategy = models.ForeignKey(Strategy, verbose_name='策略', on_delete=models.SET_NULL, null=True, blank=True)
    order_ref = models.CharField('报单号', max_length=13)
    instrument = models.CharField('品种代码', max_length=8)
    front = models.IntegerField('前置编号')
    session = models.IntegerField('会话编号')
    price = models.FloatField('报单价格')
    direction = models.CharField('方向', max_length=8, choices=DirectionType.choices)
    offset_flag = models.CharField('开平', max_length=8, choices=OffsetFlag.choices)
    status = models.CharField('状态', max_length=16, choices=OrderStatus.choices)
    send_time = models.DateTimeField('发送时间')
    update_time = models.DateTimeField('更新时间')

    class Meta:
        verbose_name = '报单'
        verbose_name_plural = '报单集合'

    def __str__(self):
        return '{}-{}'.format(self.instrument, self.get_offset_flag_display())


class Instrument(models.Model):
    exchange = models.CharField('交易所', max_length=8, choices=ExchangeType.choices)
    product_code = models.CharField('品种代码', max_length=16, unique=True)
    all_inst = models.CharField('合约月份汇总', max_length=32)
    main_code = models.CharField('主力合约', max_length=16)
    last_main = models.CharField('上个主力合约', max_length=16)
    change_time = models.DateTimeField('切换时间')

    class Meta:
        verbose_name = '合约'
        verbose_name_plural = '合约集合'

    def __str__(self):
        return '{}.{}'.format(self.exchange, self.main_code)


class DailyBar(models.Model):
    exchange = models.CharField('交易所', max_length=8, choices=ExchangeType.choices)
    code = models.CharField('合约代码', max_length=8)
    time = models.DateField('时间')
    open = models.FloatField('开盘价')
    high = models.FloatField('最高价')
    low = models.FloatField('最低价')
    close = models.FloatField('收盘价')
    volume = models.IntegerField('成交量')
    open_interest = models.IntegerField('持仓量')

    class Meta:
        verbose_name = '日K线'
        verbose_name_plural = '日K线集合'

    def __str__(self):
        return '{}.{}'.format(self.exchange, self.code)


class Trade(models.Model):
    broker = models.ForeignKey(Broker, verbose_name='券商', on_delete=models.CASCADE)
    strategy = models.ForeignKey(Strategy, verbose_name='策略', on_delete=models.SET_NULL, null=True, blank=True)
    open_order = models.ForeignKey(Order, verbose_name='开仓报单', on_delete=models.CASCADE, related_name='open_order')
    close_order = models.ForeignKey(Order, verbose_name='平仓报单', on_delete=models.CASCADE, related_name='close_order', null=True, blank=True)
    exchange = models.CharField('交易所', max_length=8, choices=ExchangeType.choices)
    instrument = models.CharField('品种代码', max_length=8)
    direction = models.CharField('方向', max_length=8, choices=DirectionType.choices)
    open_time = models.DateTimeField('开仓日期')
    close_time = models.DateTimeField('平仓日期', null=True, blank=True)
    shares = models.IntegerField('手数', blank=True)
    filled_shares = models.IntegerField('已成交手数', null=True, blank=True)
    avg_entry_price = models.FloatField('持仓均价')
    avg_exit_price = models.FloatField('平仓均价', null=True, blank=True)
    profit = models.FloatField('持仓盈亏')
    frozen_margin = models.FloatField('冻结保证金')
    cost = models.FloatField('手续费')

    class Meta:
        verbose_name = '交易记录'
        verbose_name_plural = '交易记录集合'

    def __str__(self):
        return '{}-{}手'.format(self.instrument, self.shares)
