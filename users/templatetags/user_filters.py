from django import template
# В template.Library зарегистрированы все теги и фильтры шаблонов
register = template.Library()


@register.filter 
def addclass(field, css):
        return field.as_widget(attrs={"class": css})