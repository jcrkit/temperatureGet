from django.utils.translation import ugettext as _
from django.forms import ModelForm, ValidationError
from kingAdmin import kingAdmin


def create_model_form(req, app_name, table_name):
    admin_class = kingAdmin.enabled_admins[app_name][table_name]

    def __new__(cls, *args, **kwargs):
        print('base', cls.base_fields)
        for k, v in cls.base_fields.items():
            v.widget.attrs['class'] = 'form-control'
            if k in admin_class.readonly_fields and not admin_class.is_add_form:
                v.widget.attrs['disabled'] = 'disabled'
            if admin_class.readonly_table is True and not admin_class.is_add_form:
                v.widget.attrs['disabled'] = 'disabled'
            if hasattr(admin_class, 'clean_{}'.format(k)):
                clean_field_func = getattr(admin_class, 'clean_{}'.format(k))
                setattr(cls, 'clean_{}'.format(k), clean_field_func)
        return ModelForm.__new__(cls)

    def default_validation_clean(obj):
        print(obj)
        print(obj.instance)
        error_list = []
        if admin_class.readonly_fields and obj.instance.id:
            for field in admin_class.readonly_fields:
                # print('kkk', type(getattr(obj.instance, field)))
                if hasattr(getattr(obj.instance, field), 'select_related'):
                    m2m_field = getattr(obj.instance, field).select_related()
                    field_front = obj.cleaned_data.get(field)
                    flag = True
                    field_obj = m2m_field
                    if field_front and m2m_field:
                        for i in field_front:
                            print('iiii', i)
                            for f in m2m_field:
                                if i == f:
                                    break
                            else:
                                field_obj = m2m_field
                                flag = False
                            if flag:
                                field_obj = field_front
                                break

                    print('kkk', m2m_field)
                elif hasattr(getattr(obj.instance, field), 'strftime'):
                    field_obj = getattr(obj.instance, field).strftime('%Y-%m-%d %H:%M:%S')
                    if hasattr(obj.cleaned_data.get(field), 'strftime'):
                        field_front = obj.cleaned_data.get(field).strftime('%Y-%m-%d %H:%M:%S')
                    else:
                        field_front = None
                else:
                    field_obj = getattr(obj.instance, field)
                    field_front = obj.cleaned_data.get(field)
                print('---------------------------', dir(field_obj))
                print('=')
                print('---------------------------', obj.cleaned_data.get(field))

                print(field_obj, field_front)
                if field_obj != field_front:
                    error_list.append(ValidationError(
                        _('Readonly field %(value)s , it can not change'),
                        code='invalid1',
                        params={'value': field},
                    ))
        if admin_class.readonly_table is True and obj.instance.id:
            raise ValidationError(
                _('readonly table, you can just go back'),
                code='invalid2',
            )

        user_validation = admin_class.default_form_validation_clean(obj)
        if user_validation:
            error_list.append(user_validation)
        if error_list:
            raise ValidationError(error_list)

    class Meta:
        model = admin_class.model
        fields = '__all__'
        # todo exclude = ['last_login']

    model_form_class = type('dy', (ModelForm,), {'Meta': Meta})
    setattr(model_form_class, '__new__', __new__)
    setattr(model_form_class, 'clean', default_validation_clean)
    return model_form_class
