###########################################################################################################################################
#                                                                                                                                         #
#                                                           App Setup                                                                     #
#                                                                                                                                         #
###########################################################################################################################################
from celery.result import AsyncResult
from flask import Flask, redirect, request, g, render_template, url_for, session
import jinja2 as ninja
import os
from db import init_app
from getShopItems import getShopItems

app = Flask(__name__)

# Make the WSGI interface available at the top level so wfastcgi can get it.
wsgi_app = app.wsgi_app

# jinja2 setup
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja2_env = ninja.Environment(loader=ninja.FileSystemLoader(template_dir))

# SQLite database setup
app.config.from_mapping(
    SECRET_KEY="dev",
    DATABASE=os.path.join(app.instance_path, "myData.sqlite"),
)

# Make flask App
init_app(app)

###########################################################################################################################################
#                                                                                                                                         #
#                                                           Flask Routing                                                                 #
#                                                                                                                                         #
###########################################################################################################################################
from sort import *
from tasks import update
'''from celery import Celery


def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


app.config.update(BROKER_URL=os.environ['REDIS_URL'],
                  CELERY_RESULT_BACKEND=os.environ['REDIS_URL'])
celery = make_celery(app)


@celery.task()
def update():
    global items
    items = getShopItems()


x = update.delay()
print(x.task_id)'''
override = None
fetch = None
insert = None


def checkFetch():
    global fetchID
    result = AsyncResult(request.POST[fetchID])
    status = result.status
    traceback = result.traceback
    result = result.result
    print(result)


@app.route('/')
def home():
    global override
    global insert
    global fetch

    print("\n\n\n", end="")
    if insert is None:
        print("insert is NONE")
    else:
        print("insetr: " + insert)
    if fetch is None:
        print("fetch is NONE")
    else:
        print("fetch EXISTS")
    if override is None:
        print("override is NONE")
    else:
        print("override EXISTS")

    if fetch is None:
        # Queue up our data
        fetch = update.delay()
        print("\n\n%s\n\n" % str(type(fetch)))
        return render_template('home.html')
    elif insert is None:
        # check if it's done fetching
        if fetch.state == "SUCCESS":
            insert = fetch.get()
            return render_template('home.html', items=insert)
    else:
        # We have our data
        insert = sort(items, "name")
        if override is not None:
            insert = override
            override = None
        pageObject = render_template('home.html', items=insert)
        return pageObject


@app.route('/overview', methods=("GET", "POST"))
def overview():
    global items
    global override
    if request.method == "POST":
        if "findName" in request.form:
            insert = findName(items, request.form['name'])
            override = insert
            return redirect(url_for('home', items=insert))
        elif "findBrand" in request.form:
            insert = findBrand(items, request.form['brand'])
            override = insert
            return redirect(url_for('home', items=insert))

    pageObject = render_template('find.html')
    return pageObject


@app.route('/settings')
def settings():
    pageObject = render_template('home.html')

    return pageObject


@app.route('/compare')
def compare():
    pageObject = render_template('home.html')

    return pageObject


###########################################################################################################################################
#                                                                                                                                         #
#                                                           Create Flask Host                                                             #
#                                                                                                                                         #
###########################################################################################################################################


if __name__ == '__main__':
    # app.run(debug=True)

    import os

    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT)
