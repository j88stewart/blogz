from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:lc101@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = "Wt1X4r8AFZfuUt14"


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(600))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner
 

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return self.username


def is_len3(stringinput):
    ###is the string atleast 3 characters long##
    if len(stringinput) > 3:
        return True
    else:
        return False
def is_lenles20(stringinput):
    ###is the string less than 20 characters long##
    if len(stringinput) < 20:
        return True
    else:
        return False        

def is_blank(stringinput):
    if stringinput == "":
        return True
    else:
        return False    


@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'blog', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/', methods=['POST', 'GET'])
def index():
    users = User.query.all()
    blogs = Blog.query.all() 
    return render_template('index.html', users=users, blogs=blogs)        

@app.route('/login', methods=['POST', 'GET'])
def login():


    if request.method == 'GET':
        if 'username' not in session:
            return render_template("login.html")

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/newpost')
        else:
            error = 'No user or incorrect password'
            return render_template('login.html', error=error)
    else:

        return render_template('login.html')


@app.route('/signup', methods=['POST', 'GET'])
def signup():

    username_error=''
    password_error=''
    verify_error=''

    if request.method == 'GET':
        return render_template('signup.html')

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        if is_len3(username) == False:
            username_error = "username too short"
        if is_lenles20(username) == False:
            username_error = "username too long"   

        if is_len3(password) == False:
            password_error = "password too short"
        if is_lenles20(password) == False:
            password_error = "password too long" 

        if password != verify:
            verify_error = "password verify failed"    
        
        if username_error != '' or password_error != '' or verify_error != '':
            return render_template('signup.html', username=username, username_error=username_error,
            password_error=password_error, verify_error=verify_error)

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            username_error = "Username taken"
            return render_template('signup.html', username_error=username_error)
            
        else:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
    else:
        return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

 


@app.route('/blog', methods=['POST', 'GET'])
def blog():


    
    if request.args.get('user'):
        user_id = request.args.get("user")      
        user = User.query.get(user_id)
        blogs = Blog.query.filter_by(owner_id=user_id).all()
        #print('logged in as=', session['username'])
        return render_template('user.html', blogs=blogs, user=user)

    elif request.args.get('id'):
        blog_id = request.args.get('id')
        blog = Blog.query.get(blog_id)
        #print('logged in as=', session['username'])
        return render_template('singlepost.html', blog = blog)

    

    else:
        #print('logged in as=', session['username'])
        return render_template('blog.html', blogs=Blog.query.all(), users=User.query.all())
        
  


@app.route('/newpost', methods=['POST','GET'])
def newpost():

    title_error = ''
    body_error = ''
    title = ''
    body =  ''
    
    if request.method == 'POST':
        title = request.form['post_title']
        body = request.form['post_body']
        owner = User.query.filter_by(username=session['username']).first()
        

        if is_blank(title) == True:
            title_error = 'Title is Empty, please fill in'
            #flash here#
            
        if is_blank(body) == True:
            body_error = 'Body is Empty, please fill in'
            #flash here#

        if title_error == '' and body_error == '':
            new_post = Blog(title,body,owner)
            db.session.add(new_post)
            db.session.commit()
            return redirect ('/blog?id=' + str(new_post.id), )
        else:
            return render_template("newpost.html", title=title, body=body, title_error=title_error, body_error=body_error) 
    else:
        return render_template('newpost.html')

if __name__ == '__main__':
    app.run()