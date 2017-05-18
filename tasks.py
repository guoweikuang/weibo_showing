from app.python_analyse.weibo_crawl01.main import main
from celery import Celery


app = Celery('tasks', backend='redis://localhost/5', broker='redis://localhost/0')


@app.task
def classify_main(start_url, end_time, days):
    for i in range(1, int(days)):
        main(i, start_url)


