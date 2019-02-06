# application.py
# main application for "Item Catalog" Project
# written by J K Thomson, 24 January 2019
import random
import string
import httplib2
import requests
import json
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    jsonify,
    make_response)
from flask import session as login_session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from database_setup import Base, Category, Instrument, User
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog"

engine = create_engine(
    'sqlite:///orchestra.db',
    connect_args={'check_same_thread': False})
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# --------------- AUTHENITCATION ----------------

# LOGIN SCREEN - Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template(
        'showlogin.html', STATE=state)

# GOOGLE CONNECT - user logs in with Google+ credentials
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # if state token from server doesn't match ours, return an error
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # otherise get one-time authorization code from server
    code = request.data

    try:
        # exchange the one-time authorization code for a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        # oops, the exchange failed, return error
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # see if there's a valid access token inside the credentials object
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    # if google didn't verify the access token, return an error
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # verify that the access token is used for the intended user
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # verify that the access token is valid for this app
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    # see if user is already logged in
    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # login was successful, store access token in the session for later use
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # use google+ api to get some user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = answer.json()

    # grab the desired user info from the returned data oebject
    if 'name' in data:
        login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # see if user exists in DB, create new user if not
    user_id = getUserID(login_session["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += 'Login successful: '
    output += login_session['email']
    output += ' is now logged in!'
    return output

# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['email']
        del login_session['picture']
        if 'username' in login_session:
            del login_session['username']

        response = make_response(
            json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return redirect(url_for('showOrchestra'))
    else:
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# ---------------- USER INTERFACE SCREENS ------------------

# HOME SCREEN - Orchestra page with no category selected
@app.route('/')
@app.route('/orchestra/')
def showOrchestra():
    categories = session.query(Category).all()
    umail = getUserEmail()
    return render_template(
        'showorchestra.html', user_email=umail, categories=categories)

# CATEGORY SCREEN - Orchestra page with a category selected
@app.route('/category/<int:category_id>/')
def showCategory(category_id):
    categories = session.query(Category).all()
    category = session.query(Category).filter_by(id=category_id).one_or_none()
    if not category:
        return "404 error: category not found", 404
    instruments = session.query(Instrument).filter_by(category_id=category_id)
    umail = getUserEmail()
    return render_template(
        'showcategory.html', user_email=umail,
        categories=categories, category=category, instruments=instruments,
        category_id=category_id)

# INSTRUMENT DETAILS SCREEN
@app.route('/category/<int:category_id>/instrument/<int:instrument_id>/')
def showInstrument(category_id, instrument_id):
    instrument = session.query(
        Instrument).filter_by(id=instrument_id).one_or_none()
    if not instrument:
        return("404 error: instrument not found", 404)
    category = session.query(
        Category).filter_by(id=instrument.category_id).one()
    umail = getUserEmail()
    creator = getUserInfo(instrument.user_id)
    if 'email' not in login_session or creator.id != login_session['user_id']:
        is_owner = False
    else:
        is_owner = True
    return render_template(
        'showinstrument.html', user_email=umail, user_is_owner=is_owner,
        instrument=instrument, category=category)

# NEW INSTRUMENT SCREEN
@app.route('/category/<int:category_id>/instrument/new',
           methods=['GET', 'POST'])
def newInstrument(category_id):
    if 'email' not in login_session:
        return redirect(url_for('showLogin'))
    categories = session.query(Category).all()
    umail = getUserEmail()
    message = ""
    if request.method == 'POST':
        # create an Instrument object from posted data
        newItem = createInstrument(request, login_session['user_id'])
        # if any field is blank, reject the post
        if (not newItem.name or not newItem.description
                or not newItem.picture_url or not newItem.picture_attr
                or not newItem.category_id):
            message = "All fields are required"
            return render_template(
                'newinstrument.html', user_email=umail,
                item=newItem, categories=categories,
                message=message), 400
        session.add(newItem)
        session.commit()
        return redirect(url_for(
            'showCategory', category_id=newItem.category_id))
    else:
        newItem = Instrument(
            name="",
            description="",
            picture_url="",
            picture_attr="",
            category_id=category_id)
        return render_template(
            'newinstrument.html', user_email=umail,
            item=newItem, categories=categories,
            message=message)


# EDIT INSTRUMENT SCREEN
@app.route(
    '/category/<int:category_id>/instrument/<int:instrument_id>/edit',
    methods=['GET', 'POST'])
def editInstrument(category_id, instrument_id):
    # if no user is logged in, no editing is allowed
    if 'email' not in login_session:
        return redirect(url_for('showLogin'))
    # make sure edited item exists
    editedItem = session.query(
        Instrument).filter_by(id=instrument_id).one_or_none()
    if not editedItem:
        return("404 error: instrument not found", 404)
    # in order to edit an instrument, logged-in user
    # must be the one who created it
    if editedItem.user_id != login_session['user_id']:
        return redirect(
            url_for('showInstrument',
                    category_id=category_id,
                    instrument_id=instrument_id))
    # gather up some info
    categories = session.query(Category).all()
    umail = getUserEmail()
    message = ""
    if request.method == 'POST':
        # create an Instrument object from posted data
        formItem = createInstrument(request, login_session['user_id'])
        # replace edited item's parmeters with form's values
        editedItem.name = formItem.name
        editedItem.description = formItem.description
        editedItem.category_id = formItem.category_id
        editedItem.picture_url = formItem.picture_url
        editedItem.picture_attr = formItem.picture_attr
        # if any field is blank, reject the post
        if (not editedItem.name or not editedItem.description
                or not editedItem.picture_url or not editedItem.picture_attr
                or not editedItem.category_id):
            message = "All fields are required"
            return render_template(
                'editinstrument.html', user_email=umail,
                category_id=category_id, item=editedItem,
                categories=categories, message=message), 400
        session.add(editedItem)
        session.commit()
        return redirect(
            url_for('showInstrument',
                    category_id=editedItem.category_id,
                    instrument_id=instrument_id))
    else:
        return render_template(
            'editinstrument.html', user_email=umail, category_id=category_id,
            item=editedItem, categories=categories, message=message), 400


# DELETE INSTRUMENT SCREEN
@app.route('/category/<int:category_id>/instrument/<int:instrument_id>/delete',
           methods=['GET', 'POST'])
def deleteInstrument(category_id, instrument_id):
    if 'email' not in login_session:
        return redirect(url_for('showLogin'))
    itemToDelete = session.query(
        Instrument).filter_by(id=instrument_id).one_or_none()
    if not itemToDelete:
        return("404 error: instrument not found", 404)
    umail = getUserEmail()
    # in order to delete an instrument, logged-in user
    # must be the one who created it
    if itemToDelete.user_id != login_session['user_id']:
        return redirect(
            url_for('showInstrument',
                    category_id=category_id,
                    instrument_id=instrument_id))
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        return redirect(url_for('showCategory', category_id=category_id))
    else:
        return render_template(
            'deleteInstrument.html', user_email=umail, item=itemToDelete)


# HELPER FUNCTIONS
# create a new instrument from POST request
def createInstrument(request, creator_id):
    # strip away leading and trailing spaces
    form_name = ""
    form_description = ""
    form_picture_url = ""
    form_picture_attr = ""
    form_category = ""
    if request.form['name']:
        form_name = request.form['name'].strip()
    if request.form['description']:
        form_description = request.form['description'].strip()
    if request.form['picture_url']:
        form_picture_url = request.form['picture_url'].strip()
    if request.form['picture_attr']:
        form_picture_attr = request.form['picture_attr'].strip()
    if request.form['category']:
        form_category_id = getCategoryId(request.form['category'])
    # create a new Instrument from entered data
    inst = Instrument(
        name=form_name,
        description=form_description,
        picture_url=form_picture_url,
        picture_attr=form_picture_attr,
        category_id=form_category_id,
        user_id=creator_id)
    return inst


# create a new user in the database
def createUser(login_session):
    uname = ""
    if 'username' in login_session:
        uname = login_session['username']
    newUser = User(name=uname,
                   email=login_session['email'],
                   picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


# given a category name, return its ID
def getCategoryId(catName):
    categories = session.query(Category).all()
    for c in categories:
        if c.name == catName:
            return c.id
    return None


# given a user_id, return the corresponding User object
def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


# given an email address, return the corresonding user_id
def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except NoResultFound:
        return None


# get logged in user's email address
def getUserEmail():
    if 'email' in login_session:
        return login_session['email']
    return None

# ------------- HANDLE API REQUESTS -----------------

# API - Return all categories
@app.route('/categories/JSON')
def categoriesJSON():
    categories = session.query(Category).all()
    return jsonify(Categories=[c.serialize for c in categories])

# API - Return a single category
@app.route('/category/<int:category_id>/JSON')
def categoryJSON(category_id):
    category = session.query(Category).filter_by(
        id=category_id).one_or_none()
    if not category:
        return "404 error: category not found", 404
    return jsonify(Category=category.serialize)

# API - Return all instruments
@app.route('/instruments/JSON')
def instrumentsJSON():
    instruments = session.query(Instrument).all()
    return jsonify(Instruments=[i.serialize for i in instruments])

# API - Return a single instrument
@app.route('/instrument/<int:instrument_id>/JSON')
def instrumentJSON(instrument_id):
    instrument = session.query(Instrument).filter_by(
        id=instrument_id).one_or_none()
    if not instrument:
        return "404 error: instrument not found", 404
    return jsonify(Instrument=instrument.serialize)

# API - Return all users
@app.route('/users/JSON')
def usersJSON():
    users = session.query(User).all()
    return jsonify(Users=[u.serialize for u in users])

# API - Return a single user
@app.route('/user/<int:user_id>/JSON')
def userJSON(user_id):
    user = session.query(User).filter_by(id=user_id).one_or_none()
    if not user:
        return "404 error: user not found", 404
    return jsonify(User=user_id.serialize)


if __name__ == '__main__':
    app.secret_key = 'a_really_really_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
