from src.utils.structs import CHANNEL_CATEGORIES


def human_format(num):
    num = float('{:.3g}'.format(num))
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 'T'][magnitude])


def format_channel_cat(category: str):
    return CHANNEL_CATEGORIES[category]


def map_vars_list(variables):
    mapping = []

    for var in variables:
        mapping.append({'label': format_var_names(var), 'value': var})

    return mapping


def format_var_names(var : str):
    if var is not None:
        var = var.replace('_', ' ')
        var = var.replace('avg', 'avg.')
        var = var.title()
    else:
        var = ''

    return var
