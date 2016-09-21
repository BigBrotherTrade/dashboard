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

from panel.models import Performance


class PerformanceView(LoginRequiredMixin, TemplateView):
    pass


def nav_data(request):
    q = Performance.objects.filter(broker__strategy__name='大哥2.0').order_by('-day').values_list('day', 'NAV')
    l = []
    for day, val in q:
        l.append([day.isoformat(), float(val)])
    return JsonResponse(l, safe=False)
