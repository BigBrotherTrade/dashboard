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
from django.conf.urls import url

from .views import *

urlpatterns = [
    url(r'^status$', StatusView.as_view(
        template_name='panel/status.html'), name="status_view"),
    url(r'^status_data', status_data, name='get_status_data'),

    url(r'^performance$', PerformanceView.as_view(
        template_name='panel/performance.html'), name="performance_view"),
    url(r'^nav_data', nav_data, name='get_nav_data'),

    url(r'^instrument$', InstrumentView.as_view(
        template_name='panel/instrument.html'), name='instrument_view'),
    url(r'^bar_data', bar_data, name='get_bar_data'),

    url(r'^correlation$', CorrelationView.as_view(
        template_name='panel/correlation.html'), name="correlation_view"),
    url(r'^corr_data', corr_data, name='get_corr_data'),


]
