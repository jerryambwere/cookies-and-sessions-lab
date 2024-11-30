from flask import Flask, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy_serializer import SerializerMixin

# Flask and Database Configuration
app = Flask(__name__)
app.secret_key = "your_secret_key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# SQLAlchemy Setup
metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})
db = SQLAlchemy(app, metadata=metadata)

# Models
class Article(db.Model, SerializerMixin):
    __tablename__ = 'articles'

    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(100))
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    preview = db.Column(db.String(255))
    minutes_to_read = db.Column(db.Integer)
    date = db.Column(db.DateTime, server_default=db.func.now())

    def __repr__(self):
        return f'Article {self.id} by {self.author}'

# Helper Function to Setup the Database
def setup_database():
    """Initialize the database with example articles."""
    db.create_all()
    # Add example articles (if the table is empty)
    if Article.query.count() == 0:
        db.session.add_all([
            Article(author="Author 1", title="First Article", content="Content of the first article.", preview="Preview 1", minutes_to_read=5),
            Article(author="Author 2", title="Second Article", content="Content of the second article.", preview="Preview 2", minutes_to_read=3),
            Article(author="Author 3", title="Third Article", content="Content of the third article.", preview="Preview 3", minutes_to_read=7),
        ])
        db.session.commit()

# Initialize the database when the app starts
with app.app_context():
    setup_database()

# Routes
@app.route('/articles/<int:id>', methods=['GET'])
def get_article(id):
    """Retrieve an article by ID with session-based view limits."""
    # Retrieve the article from the database
    article = Article.query.get(id)
    if not article:
        return jsonify({"message": "Article not found"}), 404

    # Initialize session page views using a ternary operator
    session['page_views'] = session.get('page_views', 0) + 1

    # Check if the user has exceeded the page view limit
    if session['page_views'] > 3:
        return jsonify({"message": "Maximum pageview limit reached"}), 401

    # Return the article data as JSON
    return jsonify(article.to_dict()), 200

@app.route('/clear', methods=['GET'])
def clear_session():
    """Clear the user's session."""
    session.clear()
    return jsonify({"message": "Session cleared"}), 200

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
