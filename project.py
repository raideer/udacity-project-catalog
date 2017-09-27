from flask import Flask, render_template, redirect, url_for
from flask import flash, request, jsonify
from flask_login import login_user, logout_user, current_user, login_required

from auth import OAuthSignIn, GoogleSignIn
from database import db, lm, User, Category, Item
from slugify import slugify

# Configuring Flask, SQLAlchemy and oAuth
app = Flask(__name__)
app.config.from_object('oauth_config')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
lm.init_app(app)
with app.app_context():
    db.create_all()


# This method will be called whenever a guest tries to access user restricted
# page
@lm.unauthorized_handler
def unauthorized():
    flash('Please log in to access that page', 'alert-danger')
    return redirect(url_for('login'))


@app.route("/")
def index():
    categories = Category.query.all()
    latest_items = Item.query.order_by(db.desc('created_at')).limit(3)
    return render_template('pages/index.html',
                           categories=categories, latest_items=latest_items)


@app.route("/catalog.json")
def json():
    categories = Category.query.all()
    return jsonify(Category=[i.serialize for i in categories])


@app.route("/catalog/<slug>")
def catalogItems(slug):
    categories = Category.query.all()
    catalog = Category.query.filter_by(slug=slugify(slug)).first()
    return render_template('pages/catalog.html', catalog=catalog,
                           categories=categories)


# Since this page should be accessed only by users, we can make use of the
# flask-login package and add the @login_required decorator to handle this
# functionality
@app.route("/catalog/create", methods=['GET', 'POST'])
@login_required
def createCatalog():
    errors = {}

    if request.method == 'POST':
        form_name = request.form['name']
        form_description = request.form['description']

        if not form_name:
            errors['name'] = "Category name is required!"

        if len(errors) == 0:
            user = User.query.filter_by(id=current_user.get_id()).one()
            category = Category(name=form_name, description=form_description,
                                user=user, slug=slugify(form_name))
            db.session.add(category)
            db.session.commit()
            return redirect(url_for('catalogItems', slug=category.slug))
    return render_template('pages/create_catalog.html', errors=errors)


@app.route("/catalog/<catalog_slug>/delete", methods=['GET', 'POST'])
@login_required
def deleteCatalog(catalog_slug):
    catalog_slug = slugify(catalog_slug)

    catalog = Category.query.filter_by(slug=catalog_slug).first()
    if not catalog:
        flash('Category not found', 'alert-danger')
        return redirect(url_for('index'))

    if len(catalog.items) > 0:
        flash('Cant delete %s because it is not empty!' % catalog.name,
              'alert-danger')
        return redirect(url_for('catalogItems', slug=catalog_slug))

    if request.method == 'POST':
        db.session.delete(catalog)
        db.session.commit()
        flash('Catalog successfuly deleted', 'alert-info')
        return redirect(url_for('index'))

    return render_template('pages/delete_catalog.html', catalog=catalog)


@app.route("/item/create", defaults={'catalog': None}, methods=['GET', 'POST'])
@app.route("/item/<catalog>/create", methods=['GET', 'POST'])
@login_required
def createCatalogItem(catalog):
    errors = {}
    categories = Category.query.all()

    if request.method == 'POST':
        form_name = request.form['name']
        form_category = request.form['category']
        form_description = request.form['description']

        if not form_name:
            errors['name'] = "Item name is required!"
        if not form_category:
            errors['category'] = "Category is required!"

        try:
            category = Category.query.filter_by(name=form_category).one()
        except Exception as e:
            errors['category'] = "That is not a valid category!"

        if not form_description:
            errors['description'] = "Description is required!"

        if len(errors) > 0:
            if form_category:
                catalog = form_category
            return render_template('pages/create_item.html',
                                   categories=categories, catalog=catalog,
                                   errors=errors, name=form_name,
                                   description=form_description)
        else:
            user = User.query.filter_by(id=current_user.get_id()).one()
            item = Item(name=form_name, description=form_description,
                        category=category, user=user)
            db.session.add(item)
            db.session.commit()
            flash('Item successfuly created', 'alert-info')
            return redirect(url_for('catalogItems', slug=category.slug))
    return render_template('pages/create_item.html', categories=categories,
                           catalog=catalog, errors=errors)


@app.route("/item/<item_id>/delete", methods=['GET', 'POST'])
@login_required
def deleteItem(item_id):
    item = Item.query.filter_by(id=item_id).first()

    if item.user != current_user:
        flash('You don\'t have the permissions to delete %s' % item.name,
              'alert-danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        db.session.delete(item)
        db.session.commit()
        flash('Item successfuly deleted', 'alert-info')
        return redirect(url_for('index'))
    return render_template('pages/delete_item.html', item=item)


@app.route("/item/<item_id>/edit", methods=['GET', 'POST'])
@login_required
def editItem(item_id):
    errors = {}
    categories = Category.query.all()
    item = Item.query.filter_by(id=item_id).first()

    if item.user != current_user:
        flash('You don\'t have the permissions to edit %s' % item.name,
              'alert-danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        form_name = request.form['name']
        form_category = request.form['category']
        form_description = request.form['description']

        if not form_name:
            errors['name'] = "Item name is required!"
        if not form_category:
            errors['category'] = "Category is required!"

        try:
            category = Category.query.filter_by(name=form_category).one()
        except Exception as e:
            errors['category'] = "That is not a valid category!"

        if not form_description:
            errors['description'] = "Description is required!"

        if len(errors) > 0:
            if form_category:
                catalog = form_category
            return render_template('pages/edit_item.html',
                                   categories=categories, errors=errors,
                                   item=item)
        else:
            item.name = form_name
            item.category = category
            item.description = form_description

            db.session.add(item)
            db.session.commit()
            return redirect(url_for('catalogItems', slug=category.slug))

    return render_template('pages/edit_item.html', categories=categories,
                           errors=errors, item=item)


@app.route("/catalog/<catalog>/<item>")
def catalogItem(catalog, item):
    return "'%s' description" % item


# Handles oAuth URL generation and redirecting
# Check out auth.py for more details
@app.route('/auth/<provider>')
def oauth_authorize(provider):
    # If the user is already logged in, redirect him/her to index
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()


# Handles callbacks from oAuth providers
@app.route('/callback/<provider>')
def oauth_callback(provider):
    # Again, making sure the user isn't logged in
    if not current_user.is_anonymous:
        return redirect(url_for('index'))

    oauth = OAuthSignIn.get_provider(provider)
    # oauth.callback() processes received request arguments, creates a new
    # oAuth session and returns the basic user credentials(id, username, email)
    social_id, username, email = oauth.callback()
    if social_id is None:
        flash('Authentication failed.')
        return redirect(url_for('index'))
    user = User.query.filter_by(social_id=social_id).first()
    if not user:
        user = User(social_id=social_id, nickname=username, email=email)
        db.session.add(user)
        db.session.commit()
    login_user(user, True)
    return redirect(url_for('index'))


@app.route('/login')
def login():
    if current_user is not None and current_user.is_authenticated:
        return redirect(url_for('index'))
    return render_template('pages/login.html')


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.secret_key = 'asecretkey'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
