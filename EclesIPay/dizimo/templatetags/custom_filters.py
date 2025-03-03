from django import template

register = template.Library()

@register.filter
def sum_contributions(contributions):
    return sum(contribution['amount'] for contribution in contributions)