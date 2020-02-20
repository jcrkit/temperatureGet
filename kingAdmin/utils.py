from django.db.models import Q


def table_filter(req, admin_class):
    filter_conditions = {}
    keywords = ['page', '_q', 'o']

    for k, v in req.GET.items():
        print('k', k, 'v', v)
        if k in keywords:
            continue
        if v:
            filter_conditions[k] = v
    print('condition', filter_conditions)
    print('ss', admin_class.model.objects.filter(**filter_conditions))
    return admin_class.model.objects.filter(**filter_conditions).\
        order_by('-{}'.format(admin_class.ordering) if admin_class.ordering else '-id'), filter_conditions


def table_search(req, admin_class, object_list):
    search_key = req.GET.get('_q', '')
    q_obj = Q()
    q_obj.connector = 'OR'
    for col in admin_class.search_fields:
        q_obj.children.append(('{}__contains'.format(col), search_key))
    print('Q', q_obj)
    res = object_list.filter(q_obj)
    return res


def table_sort(req, admin_class, objs):
    print(admin_class)
    orderByKey = req.GET.get('o')
    if orderByKey:
        res = objs.order_by(orderByKey)
        if orderByKey.startswith('-'):
            orderByKey = orderByKey.strip('-')
        else:
            orderByKey = '-{}'.format(orderByKey)
    else:
        res = objs
    return res, orderByKey
