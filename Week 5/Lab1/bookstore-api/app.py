from flask import Flask
from models import db
from routes.books import bp as books_bp

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bookstore.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
app.register_blueprint(books_bp, url_prefix='/api/v1/books')

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(port=5000, debug=True)