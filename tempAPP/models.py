from django.db import models
from django.utils.translation import ugettext as _
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser, PermissionsMixin
)
from django.utils.safestring import mark_safe


# Create your models here.
class Customer(models.Model):
    name = models.CharField(max_length=32, blank=True, null=True)
    qq = models.CharField(max_length=64, unique=True)
    phone = models.CharField(max_length=64, blank=True, null=True)
    email = models.EmailField(verbose_name='常用邮箱', blank=True, null=True)
    status_choices = ((0, '已购买'),
                      (1, '未购买'))
    status = models.SmallIntegerField(choices=status_choices, default=0)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    consultant = models.ForeignKey('UserProfile', on_delete=models.CASCADE)
    tag = models.ManyToManyField('Tag')
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{},{}'.format(self.qq, self.name)

    class Meta:
        verbose_name = '客户'
        verbose_name_plural = '客户'


class Product(models.Model):
    name = models.CharField(max_length=64, unique=True)
    rest = models.PositiveIntegerField()
    price = models.PositiveIntegerField()
    detail = models.TextField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '产品'
        verbose_name_plural = '产品'


class ContractTemplate(models.Model):
    name = models.CharField(verbose_name='合同名称', max_length=32, unique=True)
    template = models.TextField()

    def __str__(self):
        return self.name


class Payment(models.Model):
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE)
    product = models.ForeignKey('Product', verbose_name='购买的产品', on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(verbose_name='数量')
    consultant = models.ForeignKey('UserProfile', on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{},{},{}'.format(self.customer, self.product, self.amount)

    class Meta:
        verbose_name = '缴费记录'
        verbose_name_plural = '缴费记录'


class CustomerFollowUp(models.Model):
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE)
    content = models.TextField(verbose_name='跟进内容')
    consultant = models.ForeignKey('UserProfile', on_delete=models.CASCADE)
    intention_choices = ((0, '近期购买'),
                         (1, '近期无购买计划'),
                         (2, '已购买'),
                         (3, '已拉黑'),
                         (4, '已举报'))
    intention = models.SmallIntegerField(choices=intention_choices)
    date = models.DateTimeField(auto_now_add=True)
    tag = models.ManyToManyField('Tag')

    def __str__(self):
        return "<{} : {}>".format(self.customer.qq, self.intention)

    class Meta:
        verbose_name = '客户跟进表'
        verbose_name_plural = '客户跟进表'


class Menu(models.Model):
    name = models.CharField(max_length=32)
    url_name = models.CharField(max_length=32)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = '菜单'


class Tag(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '标签'
        verbose_name_plural = '标签'


class Role(models.Model):
    name = models.CharField(max_length=32, unique=True)
    menu = models.ManyToManyField('Menu', blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = '角色'


class UserProfileManager(BaseUserManager):
    def create_user(self, email, name, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            name=name,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email,
            password=password,
            name=name,
        )
        user.is_superuser = True
        user.save(using=self._db)
        return user


class UserProfile(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    password = models.CharField(_('password'), max_length=128, help_text=mark_safe('<a href="password/reset/">密码重置</a>'))
    name = models.CharField(max_length=32)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)
    # is_admin = models.BooleanField(default=False)
    role = models.ManyToManyField('Role')
    objects = UserProfileManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.email

    # def has_perm(self, perm, obj=None):
    #     "Does the user have a specific permission?"
    #     # Simplest possible answer: Yes, always
    #     return True
    #
    # def has_module_perms(self, app_label):
    #     "Does the user have permissions to view the app `app_label`?"
    #     # Simplest possible answer: Yes, always
    #     return True

    # @property
    # def is_staff(self):
    #     "Is the user a member of staff?"
    #     # Simplest possible answer: All admins are staff
    #     return self.is_superuser
    class Meta:
        permissions = (('tempAPP_查看所有项目', '11'), )
        verbose_name = '账号'


class Temperature(models.Model):
    tempData = models.CharField(max_length=32, verbose_name='温度')
    date = models.DateTimeField(auto_now_add=True)
    userId = models.ForeignKey(UserProfile, on_delete=models.CASCADE)

    def __str__(self):
        return self.tempData

    class Meta:
        verbose_name = '温度'

