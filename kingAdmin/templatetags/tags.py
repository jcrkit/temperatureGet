from datetime import datetime, timedelta
from django import template
from django.core.exceptions import FieldDoesNotExist
from django.utils.safestring import mark_safe
from kingAdmin import kingAdmin

register = template.Library()


@register.simple_tag
def get_table_name(admin):
    return admin.model._meta.verbose_name


@register.simple_tag
def get_table_objs(app_name, table_name, query_sets):
    print(app_name, table_name)
    admin = kingAdmin.enabled_admins[app_name][table_name]
    row = ''

    for col in query_sets:
        row += '<tr>'

        for index, field in enumerate(admin.list_display):
            print(index, field)
            try:
                if len(col._meta.get_field(field).choices) == 0:
                    if type(getattr(col, field)).__name__ == 'datetime':
                        row += '<td>{}</td>'.format(getattr(col, field).strftime('%Y-%m-%d %H:%M:%S'))
                    else:
                        if index == 0:
                            row += '<td><input tag="ids" name="selected_ids" value="{num}" type="checkbox"></td>'.\
                                format(num=getattr(col, field))
                            row += '<td><a href="{num}/change">{num}</a></td>'.\
                                format(num=getattr(col, field))
                        else:
                            row += '<td>{}</td>'.format(getattr(col, field))
                else:
                    print('ccc', col._meta.get_field(field).choices)
                    row += '<td>{}</td>'.format(getattr(col, 'get_{}_display'.format(field))())
            except FieldDoesNotExist:
                if hasattr(admin, field):
                    field_func = getattr(admin, field)
                    row += '<td>{}</td>'.format(field_func(admin))
                else:
                    row += '<td>未设置</td>'
        row += '</tr>'
    return mark_safe(row)


@register.simple_tag
def get_temp_objs(app_name, table_name, query_sets):
    print(app_name, table_name)
    admin = kingAdmin.enabled_admins[app_name][table_name]
    row = ''

    for col in query_sets:
        row += '<tr>'

        for index, field in enumerate(admin.list_display):
            print(index, field)
            try:
                if len(col._meta.get_field(field).choices) == 0:
                    if type(getattr(col, field)).__name__ == 'datetime':
                        row += '<td>{}</td>'.format(getattr(col, field).strftime('%Y-%m-%d %H:%M:%S'))
                    else:
                        if index == 0:
                            row += '<td><input tag="ids" name="selected_ids" value="{num}" type="checkbox"></td>'.\
                                format(num=getattr(col, field))
                            row += '<td>{num}</td>'.\
                                format(num=getattr(col, field))
                        else:
                            row += '<td>{}</td>'.format(getattr(col, field))
                else:
                    print('ccc', col._meta.get_field(field).choices)
                    row += '<td>{}</td>'.format(getattr(col, 'get_{}_display'.format(field))())
            except FieldDoesNotExist:
                if hasattr(admin, field):
                    field_func = getattr(admin, field)
                    row += '<td>{}</td>'.format(field_func(admin))
                else:
                    row += '<td>未设置</td>'
        row += '</tr>'
    return mark_safe(row)


# @register.simple_tag
# def build_paginator(query_sets):
#     page_btn = ''
#     for page_num in query_sets.paginator.page_range:
#         if query_sets.number == page_num:
#             ele_class = 'active'
#         else:
#             ele_class = ''
#         page_btn += '<li class="{}"><a href="?page={}">{}</a></li>'.format(
#             ele_class, page_num, page_num
#         )
#     return mark_safe(page_btn)


@register.simple_tag
def build_paginator(query_sets, filter_conditions, orderBy, search):
    page_btn = ''
    filters = ''
    for k, v in filter_conditions.items():
        filters += '{}={}'.format(k, v)
    flag = False
    for page_num in query_sets.paginator.page_range:
        if page_num < 3 or page_num >query_sets.paginator.num_pages - 2 or abs(query_sets.number - page_num) <= 1:
            ele_class = ''
            if query_sets.number == page_num:
                flag = False
                ele_class = 'active'
            page_btn += '<li class="{}"><a href="?page={}{}&o={}&_q={}">{}</a></li>'.format(
                ele_class, page_num, filters, orderBy, search, page_num
            )
        else:
            if not flag:
                page_btn += '<li><a>...</a></li>'
                flag = True
    # if query_sets.paginator.count < 8:
    #     for page_num in query_sets.paginator.page_range:
    #         if query_sets.number == page_num:
    #             ele_class = 'active'
    #         else:
    #             ele_class = ''
    #         page_btn += '<li class="{}"><a href="?page={}">{}</a></li>'.format(
    #             ele_class, page_num, page_num
    #         )
    # else:
    #     for page_num in query_sets.paginator.page_range:
    #         if query_sets.number == page_num:
    #             ele_class = 'active'
    #         else:
    #             ele_class = ''
    #         if query_sets.number < 3:
    #             page_btn += '<li class="{}"><a href="?page={}">{}</a></li>'.format(
    #                 ele_class, page_num, page_num
    #             )
    #         elif query_sets.number < query_sets.paginator.count-3:
    #             page_btn += '<li class="{}"><a href="?page={}">{}</a></li>'.format(
    #                 ele_class, page_num, page_num
    #             )

    return mark_safe(page_btn)


@register.simple_tag
def render_filter_ele(filter_field, admin_class, filter_conditions):
    select_ele = '''<select class="form-control" name='{filter_field}' ><option value=''>----</option>'''
    field_obj = admin_class.model._meta.get_field(filter_field)
    if field_obj.choices:
        selected = ''
        for choices_item in field_obj.choices:
            if filter_conditions.get(filter_field) == str(choices_item[0]):
                selected = 'selected'
            select_ele += '<option value="{}" {}>{}</option>'.format(choices_item[0], selected, choices_item[1])
            print(select_ele)
            selected = ''

    if type(field_obj).__name__ == 'ForeignKey':
        selected = ''
        for choices_item in field_obj.get_choices()[1:]:
            if filter_conditions.get(filter_field) == str(choices_item[0]):
                selected = 'selected'
            select_ele += '<option value="{}" {}>{}</option>'.format(choices_item[0], selected, choices_item[1])
            selected = ''

    if type(field_obj).__name__ in ['DateTimeField', 'DateField']:
        date_els = []
        today_ele = datetime.now().date()
        date_els.append(['今天', datetime.now().date()])
        date_els.append(['昨天', today_ele - timedelta(days=1)])
        date_els.append(['近7天', today_ele - timedelta(days=7)])
        date_els.append(['本月', today_ele.replace(day=1)])
        date_els.append(['近30天', today_ele - timedelta(days=30)])
        date_els.append(['近90天', today_ele - timedelta(days=90)])
        date_els.append(['近180天', today_ele - timedelta(days=180)])
        date_els.append(['本年', today_ele.replace(month=1, day=1)])
        date_els.append(['近1年', today_ele - timedelta(days=365)])

        selected = ''
        for item in date_els:
            select_ele += '<option value="{}" {}>{}</option>'.format(item[1], selected, item[0])

        filter_field_name = '{}__gte'.format(filter_field)
    else:
        filter_field_name = filter_field

    select_ele += '</select>'
    select_ele = select_ele.format(filter_field=filter_field_name)

    return mark_safe(select_ele)


@register.simple_tag
def table_header(req, field, orderByKey, filter_conditions, admin_class):
    filters = ''
    for k, v in filter_conditions.items():
        filters += '&{}={}'.format(k, v)
    print('a', filters)
    if orderByKey:
        if orderByKey.startswith('-'):
            sort_icon = '<span class="glyphicon glyphicon-chevron-up"></span>'
        else:
            sort_icon = '<span class="glyphicon glyphicon-chevron-down"></span>'

        if orderByKey.strip('-') == field:
            orderByKey = orderByKey
        else:
            orderByKey = field
            sort_icon = ''
    else:
        orderByKey = field
        sort_icon = ''
    try:
        name = admin_class.model._meta.get_field(field).verbose_name.upper()
    except FieldDoesNotExist:
        name = field
        if hasattr(admin_class, field):
            func = getattr(admin_class, field)
            if hasattr(func, 'verbose_name'):
                name = getattr(func, 'verbose_name').upper()
        return mark_safe('<th><a href="javascript:void(0);">{}</a></th>'.format(name))
    return mark_safe('<th><a href="?{}&o={}">{}</a>{}</th>'.format(filters, orderByKey, name, sort_icon))


@register.simple_tag
def get_m2m_list(admin_class, field_obj, form_obj):
    m2m_field_name = field_obj.name
    field = getattr(admin_class.model, m2m_field_name)
    # field.rel.to.objects.all()
    # 所有字段
    all_field = field.rel.model.objects.all()
    # 该对象已选中字段
    if form_obj.instance.id:   # 判断是否存在
        # 需先有model form对象才能调用m2m对象
        selected_field = getattr(form_obj.instance, m2m_field_name).all()
    else:
        return all_field
    wait_field = []
    for f in all_field:
        if f in selected_field:
            continue
        wait_field.append(f)

    return wait_field


@register.simple_tag
def get_m2m_selected_list(form_obj, obj_name):
    if form_obj.instance.id:
        return getattr(form_obj.instance, obj_name).all()
    else:
        return []


@register.simple_tag
def delete_path(ch_path):
    return ch_path.replace('change', 'delete')


# 递归单条数据删除的关联表
def recursive_related_objs_lookup(obj):
    obj_list = '<ul style="color: red;">'
    li_ele = '<li>{}:{}</li>'.format(obj._meta.verbose_name, obj.__str__())
    obj_list += li_ele

    for m2m_filed in obj._meta.local_many_to_many:
        sub_ul_ele = '<ul'
        m2m_filed_obj = getattr(obj, m2m_filed.name)
        print(m2m_filed_obj.select_related())
        for o in m2m_filed_obj.select_related():
            li_ele = '<li>{}: {}</li>'.format(m2m_filed.verbose_name, o.__str__())
            sub_ul_ele += li_ele
        sub_ul_ele += '</ul>'
        obj_list += sub_ul_ele

    for related_obj in obj._meta.related_objects:
        print(related_obj.__repr__())
        print(getattr(obj, related_obj.get_accessor_name()))
        if 'ManyToOneRel' in related_obj.__repr__():

            if hasattr(obj, related_obj.get_accessor_name()):
                accessor_obj = getattr(obj, related_obj.get_accessor_name())
                print('many to one rel', accessor_obj, related_obj.get_accessor_name())
                if hasattr(accessor_obj, 'select_related'):
                    target_objs = accessor_obj.select_related()
                    if len(target_objs) > 0:
                        nodes = recursive_related_obj_lookup(target_objs)
                        obj_list += nodes

    print(obj._meta.verbose_name)
    print(obj._meta.local_many_to_many)  # m2m list
    print(obj._meta.related_objects) # many to one
    # print(obj._meta.fields_map)
    # print(dir(obj._meta.model.objects))
    print(obj._meta.many_to_many)  # m2m  tuple

    obj_list += '</ul>'
    return obj_list


def recursive_related_obj_lookup(target_objs):
    obj_list = ''
    for obj in target_objs:
        li_ele = '<li>{}:{}</li>'.format(obj._meta.verbose_name, obj.__str__())
        obj_list += li_ele

        for m2m_filed in obj._meta.local_many_to_many:
            sub_ul_ele = '<ul>'
            m2m_filed_obj = getattr(obj, m2m_filed.name)
            print(m2m_filed_obj.select_related())
            for o in m2m_filed_obj.select_related():
                li_ele = '<li>{}: {}</li>'.format(m2m_filed.verbose_name, o.__str__())
                sub_ul_ele += li_ele
            sub_ul_ele += '</ul>'
            obj_list += sub_ul_ele

        for related_obj in obj._meta.related_objects:
            print(related_obj.__repr__())
            print(getattr(obj, related_obj.get_accessor_name()))
            if 'ManyToOneRel' in related_obj.__repr__():

                if hasattr(obj, related_obj.get_accessor_name()):
                    accessor_obj = getattr(obj, related_obj.get_accessor_name())
                    print('many to one rel', accessor_obj, related_obj.get_accessor_name())
                    if hasattr(accessor_obj, 'select_related'):
                        target_objs = accessor_obj.select_related()
                        sub_ul_ele = '<ul style="color:red">'
                        for o in target_objs:
                            li_ele = '<li>{}:{}</li>'.format(o._meta.verbose_name, o.__str__())
                            sub_ul_ele += li_ele
                        sub_ul_ele += '</ul>'
                        obj_list += sub_ul_ele
                    elif hasattr(obj, related_obj.get_accessor_name()):
                        accessor_obj = getattr(obj, related_obj.get_accessor_name())
                        if hasattr(accessor_obj, 'select_related'):
                            target_objs = accessor_obj.select_related()
                        else:
                            print('one?', accessor_obj)
                            target_objs = accessor_obj
                        if len(target_objs) > 0:
                            nodes = recursive_related_obj_lookup(target_objs)
                            obj_list += nodes

        print(obj._meta.verbose_name)
        print(obj._meta.local_many_to_many)  # m2m list
        print(obj._meta.related_objects)  # many to one
        # print(obj._meta.fields_map)
        # print(dir(obj._meta.model.objects))
        print(obj._meta.many_to_many)  # m2m  tuple
    return obj_list


@register.simple_tag
def display_obj_related(obj):
    return mark_safe(recursive_related_objs_lookup(obj))


@register.simple_tag
def display_objs_related(obj):
    return mark_safe(recursive_related_obj_lookup(obj))


@register.simple_tag
def get_action_verbose_name(action, admin_class):
    print('action', action)
    action_func = getattr(admin_class, action)
    return getattr(action_func, 'display_name') if hasattr(action_func, 'display_name') else action

