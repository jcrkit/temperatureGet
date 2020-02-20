from django.contrib.auth import authenticate
from django.shortcuts import render, redirect
from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required
from django.core.paginator import PageNotAnInteger, EmptyPage, Paginator
from kingAdmin import kingAdmin, forms
from kingAdmin.utils import table_filter, table_search, table_sort
from django.contrib.auth.hashers import (
    make_password,
)
from tempAPP.permissions.permission import check_permission


# Create your views here.

@check_permission
@login_required
def king_index(req, app_name, table_name):
    admin_class = kingAdmin.enabled_admins[app_name][table_name]
    if req.method == 'POST':
        action_name = req.POST.get('action')
        selected_ids = req.POST.get('selected_ids')
        print(action_name, selected_ids)
        # if hasattr(admin_class, action_name) is False:
        #     raise KeyError('没选操作或未定义相关动作')
        if selected_ids:
            selected_objs = admin_class.model.objects.filter(id__in=selected_ids.split(','))
            print('selected_objs', selected_objs)
            if hasattr(admin_class, action_name) is False:
                raise KeyError('没选操作或未定义相关动作')
            else:
                action_func = getattr(admin_class, action_name)
                req.admin_action = action_name
                return action_func(admin_class, req, selected_objs)
        else:
            raise KeyError('没选项目')

    object_list, filter_conditions = table_filter(req, admin_class)
    object_list = table_search(req, admin_class, object_list)
    object_list, orderByKey = table_sort(req, admin_class, object_list)
    print('order', orderByKey)
    paginator = Paginator(object_list, admin_class.list_per_page)
    page = req.GET.get('page')
    try:
        query_sets = paginator.page(page)
    except PageNotAnInteger:
        query_sets = paginator.page(1)
    except EmptyPage:
        query_sets = paginator.page(paginator.num_pages)
    return render(req, 'kingAdmin/kingAdmin.html', {'req': req,
                                                    'app_name': app_name,
                                                    'table_name': table_name,
                                                    'admin_class': admin_class,
                                                    'query_sets': query_sets,
                                                    'filter_conditions': filter_conditions,
                                                    'orderByKey': orderByKey,
                                                    'orderBy': req.GET.get('o', ''),
                                                    'search': req.GET.get('_q', '')
                                                    })


@check_permission
@login_required
def king_table(req):
    return render(req, 'kingAdmin/adminTable.html', {'req': req,
                                                     'table_list': kingAdmin.enabled_admins})


@login_required
def king_change(req, app_name, table_name, obj_id):
    model_form = forms.create_model_form(req, app_name, table_name)
    admin_class = kingAdmin.enabled_admins[app_name][table_name]
    admin_class.is_add_form = False
    obj = admin_class.model.objects.get(id=obj_id)
    if req.method == 'POST':
        form_obj = model_form(req.POST, instance=obj)  # 更新
        print(form_obj)
        if form_obj.is_valid():
            form_obj.save()
    else:
        form_obj = model_form(instance=obj)
    return render(req, 'kingAdmin/tableChange.html', {'req': req,
                                                      'model_form': model_form,
                                                      'form_obj': form_obj,
                                                      'admin_class': admin_class,
                                                      })


@check_permission
@login_required
def password_reset(req, app_name, table_name, obj_id):
    admin_class = kingAdmin.enabled_admins[app_name][table_name]
    obj = admin_class.model.objects.get(id=obj_id)
    error_list = {}
    if req.method == 'POST':
        old_pass = req.POST.get('old_pass')
        _password1 = req.POST.get('password1')
        _password2 = req.POST.get('password2')
        user = authenticate(req, username=obj.email, password=old_pass)
        if user and _password1 == _password2 and len(_password2) > 6:
            obj.set_password(_password2)
            obj.save()
        else:
            if len(_password2) <= 6:
                error_list['invalid password3'] = '密码太短啦'
            if user is None:
                error_list['invalid password1'] = '旧密码输入错误'
            if _password1 != _password2:
                error_list['invalid password2'] = '两次密码不一致'
    return render(req, 'kingAdmin/passwordReset.html', {'req': req,
                                                        'obj': obj,
                                                        'error': error_list.items()})


@check_permission
@login_required
def king_delete(req, app_name, table_name, obj_id):
    admin_class = kingAdmin.enabled_admins[app_name][table_name]
    path = req.path.replace('delete', 'change')
    obj = admin_class.model.objects.get(id=obj_id)
    error = ''
    if req.method == 'POST':
        if admin_class.readonly_table is True:
            error = _('{} is readonly_table, you can just go back'.format(table_name)),
        else:
            obj.delete()
            return redirect('/kingAdmin/{}/{}/'.format(app_name, table_name))
    return render(req, 'kingAdmin/tableDelete.html', {'obj': obj,
                                                      'admin_class': admin_class,
                                                      'req': req,
                                                      'path': path,
                                                      'errors': error})

    # 创建新记录
    # if req.method == 'POST':
    #     form_obj = model_form(req.POST)
    #     if form_obj.is_valid():
    #         form_obj.save()


@check_permission
@login_required
def king_add(req, app_name, table_name):
    admin_class = kingAdmin.enabled_admins[app_name][table_name]
    admin_class.is_add_form = True
    model_form = forms.create_model_form(req, app_name, table_name)
    if req.method == 'POST':
        obj = model_form(req.POST)
        if obj.is_valid():
            if 'password' in obj.cleaned_data:
                password = make_password(obj.cleaned_data['password'])
                print('pass', password)
                obj.cleaned_data['password'] = password
                obj = model_form(obj.cleaned_data)
                print(obj)
                obj.save()
            else:
                obj.save()
            return redirect(req.path.replace('/add/', '/'))
    else:
        obj = model_form()

    return render(req, 'kingAdmin/tableAdd.html', {'req': req,
                                                   'form_obj': obj,
                                                   'admin_class': admin_class})
# todo 错误优化
# todo 模板必填区分
# todo 模板关联
