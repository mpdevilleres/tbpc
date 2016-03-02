def capitalize(val_list=None):
    for value in val_list:
        value = value.replace('_', ' ')
        yield value.title()

def group_sort_to_list(gp, str_list=None):
    '''
    :param gp:  # grouped by dataframe
    :param to_str:  # string equivalent
    :return:    # list of (i, count)
    '''
    result=[]
    for i in gp.groups:
        group = gp.get_group(i)
        count = len(group)
        id = i if str_list is not None else group.head(1)['contractor_id']
        result.append(
            (i, count, int(id))  #tuple
            )
    return sorted(result)