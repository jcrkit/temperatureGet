from django.forms import ValidationError
from django.utils.translation import ugettext as _
from django.shortcuts import render, redirect, HttpResponse
from tempAPP import models

enabled_admins = {}


class BaseAdmin(object):
    list_display = []
    list_filters = []
    search_fields = []
    list_per_page = 20
    filter_horizontal = []
    ordering = None
    readonly_fields = []
    readonly_table = False
    actions = ['delete_selected_objs', ]
    modelform_exclude_fields = []

    def delete_selected_objs(self, req, query_sets):
        app_name = self.model._meta.app_label
        table_name = self.model._meta.model_name

        if req.POST.get('confirm') == 'yes':
            query_sets.delete()
            return redirect('/kingAdmin/{}/{}/'.format(app_name, table_name))
        selected_ids = ','.join([str(i.id) for i in query_sets])
        return render(req, 'kingAdmin/tableDelete.html', {'obj': query_sets,
                                                          'admin_class': self,
                                                          'selected_ids': selected_ids,
                                                          'action': req.admin_action
                                                          })

    # 自定validation的表单验证
    def default_form_validation_clean(self):
        pass


class CustomerAdmin(BaseAdmin):
    list_display = ['id', 'qq', 'name', 'consultant', 'status', 'date', 'buy']
    list_per_page = 2
    list_filters = ['consultant', 'status', 'date']
    ordering = 'id'
    search_fields = ['name', 'qq', 'id', 'consultant__name']
    filter_horizontal = ['tag', ]
    actions = ['delete_selected_objs', 'test']
    readonly_fields = ['qq', 'name', 'tag', 'status']

    def buy(self):
        return '<a href="#">购买</a>'

    buy.verbose_name = '购买入口'

    def test(self, request, querySets):
        print("in test", )

    test.display_name = "测试动作"

    # 自定表单验证
    def default_form_validation_clean(self):
        if self.cleaned_data.get('name'):
            pass
        else:
            return ValidationError(
                _('%(value)s can not be null '),
                code='invalid',
                params={'value': 'name'},
            )

    # 自定字段验证clean_[字段名]
    def clean_qq(self):
        print('asdasdasd', self.cleaned_data.get('qq'))
        if len(self.cleaned_data.get('qq')) > 8:
            return self.cleaned_data.get('qq')
        else:
            self.add_error('qq', 'too short， need 8 words')


class ProductAdmin(BaseAdmin):
    list_display = ['id', 'name']
    readonly_table = True


class UserProfile(BaseAdmin):
    list_display = ['id', 'name']
    readonly_fields = ['last_login', 'password', 'email']
    filter_horizontal = ['user_permissions']


# todo 账号页定制
# class UserCreationForm(forms.ModelForm):
#     """A form for creating new users. Includes all the required
#     fields, plus a repeated password."""
#     password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
#     password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)
#
#     class Meta:
#         model = UserProfile
#         fields = ('email', 'name')
#
#     def clean_password2(self):
#         # Check that the two password entries match
#         password1 = self.cleaned_data.get("password1")
#         password2 = self.cleaned_data.get("password2")
#         if password1 and password2 and password1 != password2:
#             raise forms.ValidationError("Passwords don't match")
#         return password2
#
#     def save(self, commit=True):
#         # Save the provided password in hashed format
#         user = super().save(commit=False)
#         user.set_password(self.cleaned_data["password1"])
#         if commit:
#             user.save()
#         return user
#
#
# class UserChangeForm(forms.ModelForm):
#     """A form for updating users. Includes all the fields on
#     the user, but replaces the password field with admin's
#     password hash display field.
#     """
#     password = ReadOnlyPasswordHashField()
#
#     class Meta:
#         model = UserProfile
#         fields = ('email', 'password', 'name', 'is_active', 'is_superuser')
#
#     def clean_password(self):
#         # Regardless of what the user provides, return the initial value.
#         # This is done here, rather than on the field, because the
#         # field does not have access to the initial value
#         return self.initial["password"]
#
#
# class UserAdmin(BaseUserAdmin):
#     # The forms to add and change user instances
#     form = UserChangeForm
#     add_form = UserCreationForm
#
#     # The fields to be used in displaying the User model.
#     # These override the definitions on the base UserAdmin
#     # that reference specific fields on auth.User.
#     list_display = ('id', 'email', 'name', 'is_superuser')
#     list_filter = ('is_superuser',)
#     fieldsets = (
#         (None, {'fields': ('email', 'password')}),
#         ('Personal info', {'fields': ('name',)}),
#         ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'role', 'user_permissions', 'groups')}),
#     )
#     # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
#     # overrides get_fieldsets to use this attribute when creating a user.
#     add_fieldsets = (
#         (None, {
#             'classes': ('wide',),
#             'fields': ('email', 'name', 'password1', 'password2'),
#         }),
#     )
#     search_fields = ('email',)
#     ordering = ('id',)
#     filter_horizontal = ('role', 'user_permissions', 'groups')

class TemperatureAdmin(BaseAdmin):
    list_display = ['id', 'tempData', 'date']


def register(model_class, admin_class=None):
    if model_class._meta.app_label not in enabled_admins:
        enabled_admins[model_class._meta.app_label] = {}
    admin_class.model = model_class
    enabled_admins[model_class._meta.app_label][model_class._meta.model_name] = admin_class


register(models.Customer, CustomerAdmin)
register(models.Product, ProductAdmin)
register(models.UserProfile, UserProfile)
register(models.Temperature, TemperatureAdmin)
