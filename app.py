###########################################################################################################################################
#                                                                                                                                         #
#                                                           App Setup                                                                     #
#                                                                                                                                         #
###########################################################################################################################################
from celery.result import AsyncResult
from flask import Flask, redirect, request, g, render_template, url_for, session
import jinja2 as ninja
import os
from db import init_app, init_db
from item import Item

useCelery = True

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

# Celery
app.config.update(
    CELERY_BROKER_URL=os.environ.get('REDIS_URL', 'redis://localhost:6379/0'),
    CELERY_RESULT_BACKEND=os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
)

# Make flask App
init_app(app)

###########################################################################################################################################
#                                                                                                                                         #
#                                                           Flask Routing                                                                 #
#                                                                                                                                         #
###########################################################################################################################################
from sort import *
from tasks import make_celery
import db as db


override = None
insert = None


@app.route('/')
def home():
    items = getCurrentItems()
    pageObject = render_template('home.html', items=items)
    return pageObject


@app.route('/test')
def test():
    getShopItems()
    return "Die"


def getCurrentItems():
    dataBase = db.get_db()
    cursor = dataBase.cursor()

    allItems = []
    for row in cursor.execute('SELECT * FROM items'):
        title = row["name"]
        prices = row["prices"]
        imageURL = row["imageURL"]
        category = row["category"]
        brands = row["brands"]
        SKU = row["SKU"]
        tags = row["tags"]
        URL = row["URL"]

        # turn List items into Lists
        prices = prices.split(";")
        prices = map(float, prices)
        prices = list(prices)

        brands = brands.split(";")
        for i in range(0, len(brands)):
            brands[i] = brands[i].replace("'", "")

        tags = tags.split(";")
        for i in range(0, len(tags)):
            tags[i] = tags[i].replace("'", "")

        item = Item(name=title, price=prices, image=imageURL, category=category, brand=brands, sku=SKU,
                    tags=tags, url=URL)
        allItems.append(item)

    print("RETURNED " + str(len(allItems)) + " ITEMS\n\n\n")
    return allItems


@app.route("/scrape")
def scrape():
    with app.app_context():
        update.delay()
    return "Hello"


@app.route('/overview', methods=("GET", "POST"))
def overview():
    global insert
    global override
    if request.method == "POST":
        if "findName" in request.form:
            override = findName(insert, request.form['name'])
            return redirect(url_for('home'))
        elif "findBrand" in request.form:
            override = findBrand(insert, request.form['brand'])
            return redirect(url_for('home'))

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


@app.route("/die")
def die():
    # db.insert("test", ["name"], ["test"])
    dataBase = db.get_db()
    cursor = dataBase.cursor()

    for row in cursor.execute('SELECT * FROM test'):
        if row["name"] == 'test':
            # db.remove('test', 'name', 'test')
            return "Test FOUND"
    return "TEST NOT FOUND"


@app.route("/die2")
def die2():
    with app.app_context():
        celeryItem = test.delay()
        print(type(celeryItem))
    return "Test() Task queued"

###########################################################################################################################################
#                                                                                                                                         #
#                                                           Create Flask Host                                                             #
#                                                                                                                                         #
###########################################################################################################################################
app.app_context().push()


from celery import Celery
from getShopItems import getShopItems
from celery.signals import task_postrun

celery = make_celery(app)
# celery.config_from_object("celerysettings")


@celery.task
def update():
    # Flask.current_app.logger.info("I have the application context")
    with app.app_context():
        getShopItems()
    return "No app context"


@celery.task
def test():
    dataBase = db.get_db()
    db.insert("test", ["name"], ["test"])
    cursor = dataBase.cursor()

    for row in cursor.execute('SELECT * FROM test'):
        if row["name"] == 'test':
            # db.remove('test', 'name', 'test')
            return "die Completed"
        else:
            return "CRITICAL FAILURE, WE DID NOT DO AS INSTRUCTED"


@task_postrun.connect
def close_session(*args, **kwargs):
    db.close_db()


if __name__ == '__main__':
    # app.run(debug=True)
    if useCelery:
        with app.app_context():
            celery.start()
        import os

    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT)



