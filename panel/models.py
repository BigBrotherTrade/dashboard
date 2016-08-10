from django.db import models

from dashboard.const import *


class Address(models.Model):
    name = models.CharField(verbose_name='名称', max_length=64)
    url = models.CharField(verbose_name='地址', max_length=128)
    type = models.CharField(verbose_name='类型', max_length=16, choices=AddressType.choices)
    operator = models.CharField(verbose_name='运营商', max_length=16, choices=OperatorType.choices)


class Broker(models.Model):
    name = models.CharField(verbose_name='名称', max_length=64)
    market_type = models.CharField(verbose_name='市场', max_length=32, choices=MarketType.choices)
    trade_address = models.ForeignKey(Address, on_delete=models.CASCADE)
    market_address = models.ForeignKey(Address, on_delete=models.CASCADE)
    identify = models.CharField(verbose_name='唯一标志', max_length=32)
    username = models.CharField(verbose_name='用户名', max_length=32)
    password = models.CharField(verbose_name='密码', max_length=32)


class Strategy(models.Model):
    broker = models.ForeignKey(Broker, on_delete=models.CASCADE)
    name = models.CharField(verbose_name='名称', max_length=64)


class Order(models.Model):
    broker = models.ForeignKey(Broker, on_delete=models.CASCADE)


class Trade(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)

