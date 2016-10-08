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
import datetime
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.utils import timezone
from django.views.generic import TemplateView
import logging
import pytz

from panel.models import *

logger = logging.getLogger('panel.view')


class PerformanceView(LoginRequiredMixin, TemplateView):
    pass


class CorrelationView(LoginRequiredMixin, TemplateView):
    pass


class InstrumentView(LoginRequiredMixin, TemplateView):
    def get_context_data(self, **kwargs):
        context = super(InstrumentView, self).get_context_data(**kwargs)
        context['object_list'] = Strategy.objects.get(name='大哥2.0').instruments.all().order_by('exchange')
        return context


def nav_data(request):
    q = Performance.objects.filter(broker__strategy__name='大哥2.0').order_by('-day').values_list('day', 'NAV')
    rst = []
    for day, val in q:
        rst.append([day.isoformat(), float(val)])
    return JsonResponse(rst, safe=False)


def bar_data(request):
    try:
        inst_id = request.GET['inst']
        inst = Instrument.objects.get(id=inst_id)
        break_n = Strategy.objects.first().param_set.get(code='BreakPeriod').int_value + 1
        q = MainBar.objects.filter(product_code=inst.product_code).order_by('time').values_list(
            'time', 'open', 'close', 'low', 'high')
        rst = {'up': [], 'down': [], 'k': [], 'x': [], 'trade': [], 'title': str(inst)}
        for day, oo, cc, ll, hh in q:
            rst['x'].append(day.isoformat())
            rst['k'].append([float(oo), float(cc), float(ll), float(hh)])
            rst['up'].append(max(x[2] for x in rst['k'][-break_n:]))
            rst['down'].append(min(x[2] for x in rst['k'][-break_n:]))
        for t in Trade.objects.filter(instrument_id=inst_id).order_by('open_time'):
            if t.close_time is None:
                close_price = rst['k'][-1][1]
                close_time = rst['x'][-1]
                if t.profit is None:
                    continue
            else:
                close_price = t.avg_exit_price
                close_time = timezone.localtime(t.close_time, pytz.FixedOffset(480)).date().isoformat()
            rst['trade'].append([
                {
                    'name': '{}至{} {}仓{}手'.format(
                        t.open_time, close_time, t.direction, t.shares),
                    'coord': [timezone.localtime(t.open_time, pytz.FixedOffset(480)).date().isoformat(),
                              t.avg_entry_price],
                    'lineStyle': {
                        'normal': {
                            'color': '#00f' if t.profit > 0 else '#fff'
                        }
                    },
                },
                {
                    'coord': [close_time, close_price]
                }])
        return JsonResponse(rst, safe=False)
    except Exception as e:
        logger.error('bar_data failed: %s', e, exc_info=True)


def corr_data(request):
    try:
        day = datetime.datetime.today()
        price_dict = dict()
        begin_day = day.replace(year=day.year - 1)
        category = list()
        for inst in Strategy.objects.get(name='大哥2.0').instruments.all():
            category.append(inst.name)
            price_dict[inst.product_code] = to_df(MainBar.objects.filter(
                time__gte=begin_day.date(), exchange=inst.exchange,
                product_code=inst.product_code).order_by('time').values_list('time', 'close'))
            price_dict[inst.product_code].index = pd.DatetimeIndex(price_dict[inst.product_code].time)
            price_dict[inst.product_code]['price'] = price_dict[inst.product_code].close.pct_change()
        corr_pd = pd.DataFrame({k: v.price for k, v in price_dict.items()}).corr()
        length = corr_pd.shape[0]
        return JsonResponse({
            'index': category,
            'title': '各品种{}至{}的相关性分析'.format(begin_day.date(), day.date()),
            'data': [[i, j, corr_pd.iloc[i, j]] for i in list(range(length)) for j in list(range(length))]
        }, safe=False)
    except Exception as e:
        logger.error('bar_data failed: %s', e, exc_info=True)
