from flask import Blueprint, render_template

# Controller principal responsável pela rota inicial do sistema
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html') 