# coding: utf-8
from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from config import config
from flask_login import LoginManager
from flask_pagedown import PageDown
# from .analyse import k_means_to_weibo
from .celery_worker import make_celery


bootstrap = Bootstrap()
# 时间日期渲染
moment = Moment()
db = SQLAlchemy()
mail = Mail()
pagedown = PageDown()

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    app.config.update(
    CELERY_BROKER_URL='redis://localhost:6379',
    CELERY_RESULT_BACKEND='redis://localhost:6379'
)
    celery = make_celery(app)

    bootstrap.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    pagedown.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    """
    注册蓝本时使用的 url_prefix 是可选参数。如果使用了这个参数，
    注册后蓝本中定义的所有路由都会加上指定的前缀，即这个例子中的/auth
    """
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .api_1_0 import api as api_1_0_blueprint
    app.register_blueprint(api_1_0_blueprint, url_prefix='/api/v1.0')

    return app

