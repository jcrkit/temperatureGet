from django.urls import resolve
from django.conf import settings
from django.shortcuts import HttpResponse, render, redirect
from tempAPP.permissions.permission_list import perm_list


def perm_check(*args, **kwargs):
    req = args[0]
    solve_url = resolve(req.path)
    current_url = solve_url.url_name
    result = None
    permission_key = None
    # if req.user.is_authenticated is False:
    #     return redirect(settings.LOGIN_URL)
    for permission_key, permission_val in perm_list.items():
        per_url_name = permission_val[0]
        per_method = permission_val[1]
        per_args = permission_val[2]
        per_kwargs = permission_val[3]
        per_hook = permission_val[4] if len(permission_val) > 4 else None
        print(current_url, per_url_name)
        if req.user.is_authenticated is True:
            if req.user.is_superuser is True:
                result = True
            else:
                if current_url == per_url_name:
                    if per_method == req.method:
                        arg_flag = True
                        if len(per_args) > 0:
                            for arg in per_args:
                                req_method_func = getattr(req, req.method)
                                if req_method_func.get(arg, None):
                                    arg_flag = True
                                else:
                                    arg_flag = False
                        else:
                            arg_flag = True
                        kwarg_flag = True
                        if len(per_kwargs) > 0:
                            for k, v in per_kwargs.items():
                                req_method_func = getattr(req, req.method)
                                kwarg_val = req_method_func.get(k, None)
                                if kwarg_val == str(v):
                                    kwarg_flag = True
                                else:
                                    kwarg_flag = False
                        else:
                            kwarg_flag = True

                        hook_flag = True
                        if per_hook:
                            hook_flag = per_hook(req)

                        print(arg_flag, kwarg_flag, hook_flag)
                        if arg_flag is True and kwarg_flag is True and hook_flag is True:
                            result = True
                            break
        else:
            print(323)
            result = True

    if result is True:
        app_name, *per_name = permission_key.split('_')
        per_obj = '{}.{}'.format(app_name, permission_key)
        if req.user.is_authenticated is True:
            if req.user.is_superuser is False:
                if req.user.has_perm(per_obj):
                    return True
                else:
                    return False
            else:
                return True
        else:
            return True
    else:
        print(req.user.is_superuser)
        print('re', result)
        return False


def check_permission(func):
    def inner(*args, **kwargs):
        print(perm_check(*args, **kwargs))
        if perm_check(*args, **kwargs) is True:
            return func(*args, **kwargs)
        else:
            return HttpResponse('无权限')
    return inner
