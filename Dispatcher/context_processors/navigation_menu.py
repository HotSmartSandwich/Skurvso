from django import template

from Dispatcher.models import Building

register = template.Library()


@register.inclusion_tag('base.html', takes_context=True)
def get_navigation_menu(request):
    context = {'buildings': Building.objects.all()}
    return context
