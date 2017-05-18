# coding=utf-8
from flask_wtf import Form
from wtforms import StringField, SubmitField, TextAreaField, BooleanField, SelectField, IntegerField
from wtforms.validators import DataRequired, Length, Regexp, Email, ValidationError
from ..models import Role, User
from flask_pagedown.fields import PageDownField


class NameForm(Form):
    """
    StringField 构造函数中的可选参数 validators
    指定一个由验证函数组成的列表，
    在接受用户提交的数据之前验证数据
    """
    name = StringField(u'your name:', validators=[DataRequired()])
    submit = SubmitField('submit'.encode('utf-8'))


class EditProfileForm(Form):
    name = StringField(u'名字', validators=[Length(0, 64)])
    location = StringField(u'所在地', validators=[Length(0, 64)])
    about_me = TextAreaField(u'关于自己')
    submit = SubmitField(u'提交')


class EditProfileAdminForm(Form):
    email = StringField(u'邮箱', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    username = StringField(u'用户名', validators=[
        DataRequired(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                          'Usernames must have only letters, '
                                          'numbers, dots or underscores')])
    confirmed = BooleanField(u'验证')
    role = SelectField(u'角色', coerce=int)
    name = StringField(u'真实名字', validators=[Length(0, 64)])
    location = StringField(u'所在地', validators=[Length(0, 64)])
    about_me = TextAreaField(u'关于我')
    submit = SubmitField(u'提交')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data).first():
            raise ValidationError(u'邮箱已经被注册了.')

    def validate_username(self, field):
        if field.data != self.user.username and \
                User.query.filter_by(username=field.data).first():
            raise ValidationError(u'用户名已经被使用了.')


class PostForm(Form):
    body = PageDownField(u'写下你想说的话', validators=[DataRequired()])
    submit = SubmitField(u'提交')


class CommentForm(Form):
    body = StringField(u'', validators=[DataRequired()])
    submit = SubmitField(u'提交')


class ShowDataForm(Form):
    start_url = StringField(u'抓取微博链接', validators=[DataRequired(message=
                                                                u'请输入要抓取的微博链接（如http://weibo.cn/gzyhl)')])
    start_time = StringField(u'请输入抓取起始日期', validators=[DataRequired()])
    end_time = IntegerField(u'抓取天数', validators=[DataRequired()])
    submit = SubmitField(u'抓取微博数据')


class ShowClusterForm(Form):
    start_url = StringField(u'微博链接', validators=[DataRequired(message=u'请输入抓取的微博链接')])
    start_time = StringField(u'终止日期', validators=[DataRequired(message=u'请输入微博的终止日期')]) 
    days = IntegerField(u'分析天数', validators=[DataRequired()])
    #start_time = SelectField(u'选择分析日期', choices=[
    #    ('month', u'最近一个月'),
    #    ('days_15', u'最近15天'),
    #    ('weekend', u'最近一周'),
    #    ('three_month', u'最近3个月'),
    #    ('half_year', u'最近半年')
    #])
    #keywords = StringField(u'关键字', validators=[DataRequired(message=u'请输入若干关键字，用<,>逗号隔开')])
    # days = IntegerField(u'分析天数', validators=[DataRequired()])
    submit = SubmitField(u'生成热点话题')
