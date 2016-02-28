def capitalize(val_list=None):
    for value in val_list:
        value = value.replace('_', ' ')
        yield value.title()

