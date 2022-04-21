from flask import Blueprint
from flask import render_template, request, flash
from wtforms import Form, StringField
from domain import Domain
from app.utils.config_loader import ConfigLoader


class SearchForm(Form):
    query = StringField('Введите ключевые слова')


# domain = Domain(config=ConfigLoader())
index_bp = Blueprint('index', __name__)
about_bp = Blueprint('about', __name__)
search_bp = Blueprint('search', __name__)


def route(app):
    global domain
    domain = Domain(config=ConfigLoader())
    app.register_blueprint(index_bp)
    app.register_blueprint(about_bp)
    app.register_blueprint(search_bp)


@index_bp.route('/')
def index():
    return render_template('home.html', graph=domain.plot_map_data())


@about_bp.route('/about')
def about():
    return render_template('about.html')


@search_bp.route('/search', methods=['GET', 'POST'])
def search():
    form = SearchForm(request.form)
    if request.method == 'POST':
        query = form.query.data
        response = domain.predict(query)
        flash(f'Выполнен поиск по запросу "{query}"')
        return render_template('search.html', vacancies=response, form=form)
    return render_template('search.html', form=form)