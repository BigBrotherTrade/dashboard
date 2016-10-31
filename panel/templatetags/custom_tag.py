# coding=utf-8

from django import template

register = template.Library()


@register.filter
def number(obj):
    return '%g' % obj


@register.filter
def change_strategy(request, new):
    return request.get_full_path().replace(
        'strategy={}'.format(request.GET['strategy']), 'strategy={}'.format(new))


@register.filter
def in_group(user, group_name):
    return user.groups.filter(name=group_name).exists()


@register.filter
def format_query_string(request):
    variables = request.GET.copy()
    if 'page' in variables:
        del variables['page']
    return '&{0}'.format(variables.urlencode())


@register.filter
def all_query_param(request):
    return request.GET.urlencode()


@register.filter
def left_bar(request):
    left_open = request.COOKIES.get("open", "false")
    if left_open == "true":
        return "nav-md"
    return "nav-sm"


@register.filter
def can_edit(db_obj, user):
    return db_obj.has_edit_perm(user)


@register.filter
def split_ip(ip):
    return "<br>".join(ip.split(","))
