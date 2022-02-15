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
from django.contrib import admin
from django.conf.locale.zh_Hans import formats as zh_formats

from .forms import BrokerForm
from .models import *

zh_formats.DATETIME_FORMAT = "Y-m-d H:i:s"


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'type', 'operator')


@admin.register(Broker)
class BrokerAdmin(admin.ModelAdmin):
    list_display = ('name', 'contract_type', 'trade_address', 'market_address',
                    'identify', 'username', 'fake', 'cash', 'pre_balance', 'current')
    form = BrokerForm


@admin.register(Strategy)
class StrategyAdmin(admin.ModelAdmin):
    list_display = ('name', 'broker', 'get_instruments', 'get_force_opens')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('instrument', 'price', 'direction', 'offset_flag', 'status', 'send_time', 'update_time')


@admin.register(Instrument)
class InstrumentAdmin(admin.ModelAdmin):
    list_display = ('exchange', 'section', 'name', 'product_code', 'night_trade', 'main_code',
                    'last_main', 'change_time', 'up_limit_ratio',
                    'margin_rate', 'fee_money', 'fee_volume', 'price_tick')
    ordering = ['-exchange', 'section']


@admin.register(MainBar)
class MainBarAdmin(admin.ModelAdmin):
    list_display = ('product_code', 'code', 'time', 'open', 'high', 'low', 'close',
                    'volume', 'open_interest', 'basis')
    search_fields = ('product_code', 'code', 'time',)


@admin.register(DailyBar)
class DailyBarAdmin(admin.ModelAdmin):
    list_display = ('exchange', 'code', 'time', 'open', 'high', 'low', 'close', 'volume', 'open_interest')


@admin.register(Trade)
class TradeAdmin(admin.ModelAdmin):
    list_display = (
        'broker', 'strategy', 'instrument', 'code', 'shares', 'direction', 'open_time', 'close_time',
        'avg_entry_price', 'avg_exit_price', 'profit', 'frozen_margin', 'cost')


@admin.register(Param)
class ParamAdmin(admin.ModelAdmin):
    list_display = (
        'strategy', 'update_time', 'code', 'str_value', 'int_value', 'float_value')
    search_fields = ('code',)


@admin.register(Signal)
class SignalAdmin(admin.ModelAdmin):
    list_display = (
        'strategy', 'instrument', 'code', 'type', 'trigger_value', 'price', 'volume',
        'trigger_time', 'priority', 'processed')
    search_fields = ('instrument',)


@admin.register(Performance)
class PerformanceAdmin(admin.ModelAdmin):
    list_display = (
        'broker', 'day', 'capital', 'unit_count', 'NAV', 'accumulated', 'dividend', 'used_margin')
    search_fields = ('day',)
