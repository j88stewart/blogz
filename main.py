from flask import Flask, request, redirect, render_template, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:lc101@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(600))
    

    def __init__(self, title, body):
        self.title = title
        self.body = body

def allposts():
    return Blog.query.all()

def is_blank(stringinput):
    if stringinput == "":
        return True
    else:
        return False    

@app.route('/', methods=['POST', 'GET'])
def index():
    return redirect ('/blog')


@app.route('/blog', methods=['POST', 'GET'])
def posts():

    blog_id = request.args.get('id')

    

    if blog_id:

        
        blog = Blog.query.get(blog_id)
        return render_template('singlepost.html', blog = blog)
    else:
        return render_template('blog.html', blogs=Blog.query.all())    




@app.route('/newpost', methods=['POST','GET'])
def newpost():

    title_error = ''
    body_error = ''
    title = ''
    body =  ''

    if request.method == 'POST':
        title = request.form['post_title']
        body = request.form['post_body']
        

        if is_blank(title) == True:
            title_error = 'Title is Empty, please fill in'
            #flash here#
            
        if is_blank(body) == True:
            body_error = 'Body is Empty, please fill in'
            #flash here#

        if title_error == '' and body_error == '':
            new_post = Blog(title,body)
            db.session.add(new_post)
            db.session.commit()
            return redirect ('/blog?id=' + str(new_post.id))
        else:
            return render_template("newpost.html", title=title, body=body, title_error=title_error, body_error=body_error) 
    else:
        return render_template('newpost.html')

if __name__ == '__main__':
    app.run()