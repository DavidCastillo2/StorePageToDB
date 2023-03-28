import bs4 as bs
import urllib.request
from item import *
import db as db


def getShopItems():
    # bs4 setup
    source = urllib.request.urlopen('https://bluelotusbotanicalsfl.com/shop/page/1/').read()
    soup = bs.BeautifulSoup(source, 'lxml')

    # Find out how many pages there are
    navigationBar = soup.find("ul", {"class": "page-numbers nav-pagination links text-center"})
    items = navigationBar.find_all("li")
    totalPages = int(items[len(items)-2].text)

    print("Searching %d pages, please be patient\n" % totalPages)
    allItems = []
    # Iterate over all the webpages
    for i in range(1, 1+1):

        # Open the correct Webpage
        url = "https://bluelotusbotanicalsfl.com/shop/page/" + str(i) + "/"
        source = urllib.request.urlopen(url).read()
        soup = bs.BeautifulSoup(source, 'lxml')

        # Populate Item object with Webpage's data
        itemsList = soup.find_all("div", {"class": "product-small box"})
        for div in itemsList:
            # Product name
            result = div.find("p", {"class": "name product-title"})
            title = result.text

            # Category
            result = div.find("p", {"class": "category uppercase is-smaller no-text-overflow product-cat op-7"})
            category = result.text

            # Image
            result = div.find('img')
            imageURL = result['src']

            # Price
            result = (div.find_all("span", {"class": "woocommerce-Price-amount amount"}))

            priceList = []
            for item in result:
                itemPrice = float(item.text[1:])  # item price

                if len(priceList) != 0:
                    # Previous price higher than current itemPrice means its a markdown so we delete previous prices
                    if priceList[len(priceList)-1] > itemPrice:
                        priceList = [itemPrice]
                    else:
                        priceList.append(itemPrice)
                else:
                    priceList.append(itemPrice)

            # Changing page to specific item's page
            url = div.find("a")["href"]  # This is also the URL item
            source = urllib.request.urlopen(url).read()
            soup = bs.BeautifulSoup(source, 'lxml')
            div = soup.find("div", {"class": "product_meta"})  # main div we want

            # Tags
            tags = []
            tagDiv = div.find("span", {"class": "tagged_as"})
            if tagDiv is not None:
                allTags = tagDiv.find_all("a")
                for item in allTags:
                    tags.append(item.text)
            else:
                tags = None

            # SKU
            skuDiv = div.find("span", {"class": "sku_wrapper"})
            if skuDiv is not None:
                SKU = skuDiv.text[5:]
            else:
                SKU = None

            # Brand
            brandDiv = div.find_all("span", {"class": "posted_in"})
            brands = None
            if len(brandDiv) > 1:
                brandDiv = brandDiv[1]
                brands = []
                if brandDiv is not None:
                    allBrands = brandDiv.find_all("a")
                    for item in allBrands:
                        brands.append(item.text)
                else:
                    brands = None

            # Create Item object
            item = Item(name=title, price=priceList, image=imageURL, category=category, brand=brands, sku=SKU,
                        tags=tags, url=url)
            allItems.append(item)
            populateDataBase(title, priceList, imageURL, category, brands, SKU, tags, url)
        print("Page %d finished" % i)
    print("Completed searching all pages!\n")
    # return allItems


def populateDataBase(name, price, image, category, brand, sku, tag, url):
    # name
    if checkNull(name):
        name = "N/A"

    # prices
    if checkNull(price):
        prices = "N/A"
    else:
        prices = str(price).strip("[]").replace(",", ";")

    # image
    if checkNull(image):
        image = "N/A"

    # category
    if checkNull(category):
        category = "N/A"
    else:
        whiteList = set('abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
        category = ''.join(filter(whiteList.__contains__, category))

    # brands
    if checkNull(brand):
        brands = "N/A"
    else:
        brands = str(brand).strip("[]").replace(",", ";")

    # SKU
    if checkNull(sku):
        sku = "N/A"

    # tags
    if checkNull(tag):
        tags = "N/A"
    else:
        tags = str(tag).strip("[]").replace(",", ";")

    # url
    if checkNull(url):
        url = "N/A"

    arguments = ["name", "imageURL", "category", "SKU", "brands", "prices", "tags", "URL"]
    values = [name, image, category, sku, brands, prices, tags, url]
    insert("items", arguments, values)


def checkNull(item):
    if item is None:
        return True
    else:
        return False


def insert(tableName, arguments, values):
    # These arugments should be a list of strings
    # Basically this function runs this command with but with the custom values
    #       db.execute("INSERT INTO candidate (name, bio, img) VALUES (?, ?, ?)", (name, bio, image),)

    data = db.get_db()
    dbCommand = "INSERT INTO " + tableName + " "
    # fancy population of string
    dbCommand += ("(" + ', '.join(['%s']*len(arguments)) + ") ") % tuple(arguments)
    dbCommand += "VALUES" + " (" + ", ".join("?"*len(arguments)) + ")"
    data.execute(dbCommand, values, )
    data.commit()
