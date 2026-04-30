from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = "any_random_string_works_here" # Flask needs this for flash messages to work

# 1. Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///platform.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# 2. Database Model
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"Post('{self.author}', '{self.date_posted}')"

# 3. Create the database (Run this once)
with app.app_context():
    db.create_all()

# 4. Home Route (Handles Search and Display)
@app.route('/')
def home():
    search_query = request.args.get('search')
    
    if search_query:
        # Filter the posts
        all_posts = Post.query.filter(Post.content.contains(search_query)).order_by(Post.date_posted.desc()).all()
    else:
        # Newest First
        all_posts = Post.query.order_by(Post.date_posted.desc()).all()
    
    return render_template('index.html', user="Oluwatomisin", feed=all_posts)

# 5. Submit route (Saves new posts)
@app.route('/submit', methods=['POST'])
def submit():
    # Grab both pieces of data from the form
    author = request.form.get('author_name')
    content = request.form.get('user_input')
    
    if author and content:
        # Create the post using the name entered by the user
        new_post = Post(author=author, content=content) 
        db.session.add(new_post)
        db.session.commit()
        
    return redirect(url_for('home'))

# 6. About page
@app.route('/about')
def about():
    return render_template('about.html')

# 7. Delete route
@app.route('/delete/<int:id>')
def delete(id):
    post_to_delete = Post.query.get_or_404(id)
    db.session.delete(post_to_delete)
    db.session.commit()
    flash('Post has been deleted!', 'danger') # 'danger' is a category for red styling
    return redirect(url_for('home'))

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    post = Post.query.get_or_404(id)
    
    if request.method == 'POST':
        # Update the content with the new text from the form
        post.content = request.form.get('user_input')
        db.session.commit()
        flash('Post updated successfully!', 'success')
        return redirect(url_for('home'))
    
    # If it's a GET request, just show the edit page with the current post
    return render_template('edit.html', post=post)

@app.route('/profile/<string:author_name>')
def profile(author_name):
    # This finds only posts by the clicked author
    user_posts = Post.query.filter_by(author=author_name).order_by(Post.date_posted.desc()).all()
    # We pass 'Profile: Name' as the user so the header changes
    return render_template('index.html', user="Profile: " + author_name, feed=user_posts)

if __name__ == '__main__':
    app.run(debug=True)