# coding=utf-8
from flask import render_template, redirect, \
    url_for, current_app, abort, flash, request, make_response
from . import main
from .forms import EditProfileForm, EditProfileAdminForm, PostForm, CommentForm, ShowDataForm, ShowClusterForm
from .. import db
from ..models import User, Role, Post, Permission, Comment
from flask_login import login_required, current_user
from ..decorators import admin_required, permission_required
from ..analyse.k_means_to_weibo import main1
from ..python_analyse.classify_every_type_topic import k_means_every_type_topic
from ..python_analyse.classify_main import classify_main, \
        threads_crawl
from ..python_analyse.classify_topic import topic
from ..analyse.handle_redis import r, show_redis_data
from ..analyse.weibo_text_from_database import use_mysql
from ..python_analyse.weibo_crawl01.main import only_one_thread
from ..python_analyse.main import cluster
from ..python_analyse.config import get_keywords, get_keywords_content
from ..python_analyse.classify_every_type_topic import k_means_every_type_topic
# from ..python_analyse.tasks import classify_main as classify
from ..python_analyse.product_picture import show_keyword
from collections import defaultdict
import operator
import os
import time
import datetime
from multiprocessing import Pool
# from ..python_analyse.weibo_crawl01 import main as main_index
from celery import Celery
from redis import Redis

r2 = Redis(host='localhost', port=6379, db=2)
abs_path = os.path.dirname(os.path.abspath(__file__))


@main.route('/show_cluster', methods=['GET', 'POST'])
@login_required
def show_cluster():
    form = ShowClusterForm()
     
    word_tag = ['买卖交易', '求助', '校园生活', '学校新闻', '网络', '情感', '毕业话题']
    word_tag = [name for name in word_tag]
    type_name = '学校新闻'
    category = request.values.get("category")
    if category:
        new_word_tag = []
        type_name = category
        new_word_tag.append(category)
        for word in word_tag:
            if word != category:
                new_word_tag.append(word)
    else:
        new_word_tag = word_tag
    hot_word = new_word_tag[0]
    hot = {}
    for i in range(1, 5):
        if r2.lrange(hot_word + ':cluster:' + str(i), 0, -1):
            value = r2.lrange(hot_word + ':cluster:' + str(i), 0, -1)[0]
            hot[hot_word + ':cluster:' + str(i)] = float(value)
    print(hot)
    hot = sorted(hot.items(), key=lambda x: x[1], reverse=True)
    print(hot)
    max_value = {}
    if hot:
        max_name = hot[0][0]
        max_value = hot[0][1]
    else:
        max_name = '默认'
        max_value = 0.0
    size_list = {}
    for index in range(10):
        size = len(r.lrange(type_name + ':cluster:' + str(index + 1), 0, -1))
        if size > 0:
            size_list[type_name + ':cluster:' + str(index+1)] = size

    # max_size_name = max(size_list.items(), key=operator.itemgetter(1))[0]
    category_list = sorted(size_list.keys())

    cate = request.values.get("name")
    if cate:
        new_category_list = []
        contents = show_redis_data(cate)
        new_category_list.append(cate)
        for i in category_list:
            if i != cate:
                new_category_list.append(i)
    else:
        contents = show_redis_data(type_name + ":cluster:1")
        new_category_list = category_list

    if form.validate_on_submit():
        start_url = form.start_url.data
        end_time = form.start_time.data
        days = form.days.data
        d = datetime.datetime.now()
        # days = 0
        #if start_time == 'month':
        #    date = (datetime.datetime.now() - 
        #            datetime.timedelta(days=30)).strftime('%Y-%m-%d')
        #    start_time = date
        #    days = 30
        #elif start_time == 'weekend':
        #    date = (datetime.datetime.now() - datetime.timedelta(days=7)).strftime('%Y-%m-%d')
        #    start_time = date
        #    days = 7
        #elif start_time == u'days_15':
        #    date = (datetime.datetime.now() - datetime.timedelta(days=15)).strftime('%Y-%m-%d')
        #    start_time = date
        #    days = 15
        #elif start_time == u'three_month':
        #    date = (datetime.datetime.now() - datetime.timedelta(days=90)).strftime('%Y-%m-%d')
        #    start_time = date
        #    days = 90
        #else:
        #    days = 150
        # end_time = form.end_time.data
        # main1(start_time, end_time)
        # end_time = d.strftime("%Y-%m-%d")
        from urllib.parse import urlparse
        urls = urlparse(start_url)
        database_name = urls.path.strip('/')
        print(database_name)
        # start_url = start_url.split()[-1]
        print(end_time, days)
        topic(end_time, days)
        k_means_every_type_topic() 
        # cluster(end_time, days, database_name) 
        # threads_crawl(start_url, end_time, end_time)
        # only_one_thread(start_url, start_time, end_time)
    
        return redirect(url_for('.show_cluster'))

    sub_content = []
    for index, content in enumerate(contents):
        text, zans, comments, pub_time = content.split('\t')
        sub_content.append([index, text, zans, comments, pub_time])
    contents = sub_content
    # category_list = []
    return render_template('show_cluster.html', form=form, contents=contents,
                           category_list=new_category_list, word_tag=new_word_tag,
                           max_value=max_value, max_name=max_name)


@main.route('/show_data', methods=['GET', 'POST'])
@login_required
def show_data():
    form = ShowDataForm()
    conn, cur = use_mysql()
    sql = 'SELECT * FROM content;'
    cur.execute(sql)
    contents = cur.fetchall() 
    if form.validate_on_submit():
        start_url = form.start_url.data
        start_time = form.start_time.data
        #d = datetime.datetime.now()
        #if start_time == u'最近一个月':
        #    date = (datetime.datetime.now() - 
        #            datetime.timedelta(days=30)).strftime('%Y-%m-%d')
        #    start_time = date
        #elif start_time == u'最近一周':
        #    date = (datetime.datetime.now() - datetime.timedelta(days=7)).strftime('%Y-%m-%d')
        #    start_time = date
        #else:
        #    date = (datetime.datetime.now() - datetime.timedelta(days=15)).strftime('%Y-%m-%d')
        #    start_time = date
        end_time = form.end_time.data
        # main1(start_time, end_time)
        classify_main(start_url, start_time, end_time) 
        # threads_crawl(start_url, end_time, end_time)
        # only_one_thread(start_url, start_time, end_time)
        return redirect(url_for('.show_data'))

    sub_content = []
    for index, content in enumerate(contents[:30]):
        text, zans, comments, pub_time = content[1], content[5], content[4], content[2]
        sub_content.append([index, text, zans, comments, pub_time])
    contents = sub_content
    # category_list = []
    return render_template('show_data.html', form=form, contents=contents)


@main.route('/show_data/<int:id>', methods=['GET', 'POST'])
def show_every_data(id):
    form = ShowDataForm()
    type_name = u'学校新闻二次聚类结果'
    file_name = type_name + str(id)

    contents = show_redis_data(file_name)
    if form.validate_on_submit():
        start_time = form.start_time.data
        end_time = form.end_time.data
        main1(start_time, end_time)
        return redirect(url_for('.show_every_data', id=id))

    sub_content = []
    for index, content in enumerate(contents):
        text, zans, comments, pub_time = content.split('\t')
        sub_content.append([index, text, zans, comments, pub_time])
    contents = sub_content
    return render_template('show_data.html', form=form, contents=contents)


@main.route('/show_picture')
def show_picture():
    basedir_name = os.path.dirname(os.path.abspath(__file__))
    print(basedir_name)
    basedir_name = '/home/guoweikuang/weibo_showing/app/static/images'
    images_list = os.listdir(basedir_name)
    word_tag = ['买卖交易', '求助', '校园生活', '学校新闻', '网络', '情感']
    category = request.values.get("category")
    if category:

        new_category_list = []
        index = word_tag.index(category)
        new_category_list.append(category)
        for word in word_tag:
            if word != category:
                new_category_list.append(word)
    else:
        new_category_list = word_tag
        index = 3

    return render_template('show_picture.html', images=images_list, categorys=new_category_list, categorys_flag=index)


@main.route('/show_opinion')
def show_opinion():
    all_opinion = [u'反动言论', u'心理健康', u'社会突发事件', u'校园安全']
    conn, cur = use_mysql()
    sql = 'select * from opinion;'
    cur.execute(sql)
    rows = cur.fetchall()
    contents = defaultdict(list)
    for row in rows:
        for key in all_opinion:
            if row[1] == key:
                contents[key].append(row)

    title_type = request.values.get('category')
    if title_type:
        new_category_list = []
        index = all_opinion.index(title_type)
        new_category_list.append(title_type)
        for word in all_opinion:
            if word != title_type:
                new_category_list.append(word)
        rows = contents[title_type]
    else:
        new_category_list = all_opinion
        rows = contents[u'心理健康']
        # title = all_opinion[0]
    # print new_category_list
    return render_template('show_mysql_data.html', categorys=new_category_list, rows=rows)


@main.route('/show_topic')
def show_topic():
    file_name = ''
    contents = get_keywords_content() 

    total = []
    for content in contents:
        total.append(content.decode('utf-8').strip().replace('\n', '').split('\t'))

    keywords = get_keywords()
    keywords = [key.decode('utf-8') for key in keywords]
    return render_template('show_hot_topic.html', rows=total, keywords=keywords)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash(u'你的个人主页被更新了.')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        flash(u'个人主页已经更新！')
        return redirect(url_for('.user', username=current_user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)


@main.route('/', methods=['GET', 'POST'])
def index():
    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and \
            form.validate_on_submit():
        post = Post(body=form.body.data,
                    author=current_user._get_current_object())
        db.session.add(post)
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    show_followed = False
    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get('show_followed', ''))
    if show_followed:
        query = current_user.followed_posts
    else:
        query = Post.query
    pagination = query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    return render_template('index.html', form=form, posts=posts,
                           show_followed=show_followed, pagination=pagination)


@main.route('/user/<username>', methods=['GET', 'POST'])
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    return render_template('user.html', user=user, posts=posts,
                           pagination=pagination)


@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    post = Post.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data,
                          post=post,
                          author=current_user._get_current_object())
        db.session.add(comment)
        flash(u'你的评论已经被发布！')
        return redirect(url_for('.post', id=post.id, page=-1))
    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (post.comments.count() - 1) / \
               current_app.config['FLASKY_COMMENTS_PER_PAGE'] + 1
    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False
    )
    comments = pagination.items
    return render_template('post.html', posts=[post], form=form,
                           comments=comments, pagination=pagination)


@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and \
            not current_user.can(Permission.ADMINISTER):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.body = form.body.data
        db.session.add(post)
        flash(u'你的文章已经更新！')
        return redirect(url_for('.post', id=post.id))
    form.body.data = post.body
    return render_template('edit_post.html', form=form, post=post)


@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(u'无效的用户！')
        return redirect(url_for('.index'))
    if current_user.is_following(user):
        flash(u'你已经关注了该用户！')
        return redirect(url_for('.user', username=username))
    current_user.follow(user)
    flash(u'你现在关注了%s' % username)
    return redirect(url_for('.user', username=username))


@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(u'无效的用户！')
        return redirect(url_for('.index'))
    if not current_user.is_following(user):
        flash(u'你已经取消关注了该用户！')
        return redirect(url_for('.user', username=username))
    current_user.unfollow(user)
    flash(u'你现在取消关注了 %s.' % username)
    return redirect(url_for('.user', username=username))


@main.route('/followers/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(u'无效的用户！')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(
        page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.follower, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title="Followers of",
                           endpoint='.followers', pagination=pagination,
                           follows=follows)


@main.route('/followed_by/<username>')
def followed_by(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(u'无效的用户！')
        redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(
        page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.followed, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title='Followed by',
                           endpoint='.followed_by', pagination=pagination,
                           follows=follows)


@main.route('/all')
@login_required
def show_all():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '', max_age=24 * 60 * 60 * 30)
    return resp


@main.route('/followed')
@login_required
def show_followed():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '1', max_age=24 * 60 * 60 * 30)
    return resp


@main.route('/moderate')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate():
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    return render_template('moderate.html', comments=comments,
                           pagination=pagination, page=page)


@main.route('/moderate/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_enable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = False
    db.session.add(comment)
    return redirect(url_for('.moderate',
                            page=request.args.get('page', 1, type=int)))


@main.route('/moderate/disable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_disable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = True
    db.session.add(comment)
    return redirect(url_for('.moderate',
                            page=request.args.get('page', 1, type=int)))





