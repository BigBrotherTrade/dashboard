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
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views.generic import TemplateView

from panel.models import *


class PerformanceView(LoginRequiredMixin, TemplateView):
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
    for t in Trade.objects.filter(
            instrument_id=inst_id, cost__isnull=False).order_by('open_time'):
        if t.close_time is None:
            close_price = rst['k'][-1][1]
            close_time = rst['x'][-1]
        else:
            close_price = t.avg_exit_price
            close_time = t.close_time.date().isoformat()
        rst['trade'].append([
            {
                'name': '{}至{} {}仓{}手'.format(
                    t.open_time.date(), close_time, t.direction, t.shares),
                'coord': [t.open_time.date().isoformat(), t.avg_entry_price],
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
