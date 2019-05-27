from flask import Blueprint, g, render_template, redirect, url_for, g, flash
from flask_security import current_user, login_required, current_user
from app import db

bp = Blueprint('deals', __name__)

#@bp.before_app_request
#def before_request():
#    g.search_form = SearchForm()

@bp.route('/index', methods=['GET', 'POST'])
@bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    deals = current_user.get_deals()
    return render_template('deals/index.html',
                title='Deals',
                deals=deals)
