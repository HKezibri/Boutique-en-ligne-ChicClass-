
from flask import Flask, render_template,session, request, redirect, flash, url_for,current_app
from wtforms import Form, BooleanField, StringField, PasswordField, validators
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import Form, IntegerField, SelectField, BooleanField, TextAreaField, validators,DecimalField,SubmitField
from wtforms.validators import DataRequired
from datetime import datetime
from flask_uploads import IMAGES, UploadSet, configure_uploads, patch_request_class
import os
import sqlite3

from flask_login import LoginManager
from flask_login import login_required,current_user,logout_user,logout_user,login_user
from flask_login import UserMixin

from flask_msearch import Search 

from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage

import secrets


basedir = os.path.abspath(os.path.dirname(__file__))



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
app.config['SECRET_KEY']= "hkhkjhkj123598"
app.config['UPLOADED_PHOTOS_DEST'] = os.path.join(basedir,'static/assets')

photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)
patch_request_class(app)

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
search = Search()
search.init_app(app) 

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'customerLogin'
login_manager.needs_refresh_message_category = 'danger'
login_manager.login_message = u'SVP connecter vous '



class Addproduct(db.Model):
    __searchable__ = ['name','desc']
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Numeric(10,2),nullable=False)
    priced = db.Column (db.Integer, default=0)
    stock = db.Column (db.Integer, nullable=False)
    colors = db.Column (db.Text, nullable=False)
    desc = db.Column(db.Text, nullable=False)
    pub_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
   
    brand_id = db.Column(db.Integer, db.ForeignKey('brand.id'),nullable=False)
    brand = db.relationship('Brand',backref=db.backref('brands', lazy=True))

    category_id = db.Column(db.Integer, db.ForeignKey('category.id'),nullable=False)
    category = db.relationship('Category',backref=db.backref('posts', lazy=True))

    image = db.Column(db.String(150),nullable=False, default='image.jpg')

    def __repr__(self):
        return '<Addproduct %r>' % self.name



class Addproducts(Form):
    name = StringField('Nom', [validators.DataRequired()])
    price = DecimalField('Prix',[validators.DataRequired()])
    priced = IntegerField('Discount',default=0)
    stock = IntegerField('Stock',[validators.DataRequired()])
    description = TextAreaField('Description',[validators.DataRequired()])
    colors = TextAreaField ('Couleus',[validators.DataRequired()])
    image= FileField ('image', validators=[FileAllowed(['jpg','png','gif','jpeg'],'image seulement')])

class Addblog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    author = db.Column(db.String(80), nullable=False)
    content = db.Column(db.Text)
    text = db.Column(db.Text)
    pub_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    image = db.Column(db.String(150),nullable=False, default='image.jpg')



class Addblogs(Form):
    title = StringField('Titre', [validators.DataRequired()])
    author = StringField('Auteur', [validators.DataRequired()])
    content = TextAreaField('Contenu',[validators.DataRequired()])
    text = TextAreaField('Text',[validators.DataRequired()])
    
    image= FileField ('image', validators=[FileAllowed(['jpg','png','gif','jpeg'],'image seulement')])




class Brand(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(20),nullable=False,unique=True)

class Category(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(20),nullable=False,unique=True)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=False, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(180), unique=False, nullable=False)
    #profile = db.Column(db.String(180), unique=False, nullable=False)
    #default = 'profile.jpg'

    def __repr__(self):
        return '<User %r>' % self.username


class RegistrationForm(Form):
    name = StringField('Name', [validators.Length(min=4, max=25)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email Address', [validators.Length(min=6, max=35), validators.Email()])
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')


class LoginForm(Form):
    email = StringField('Email Address', [validators.Length(min=6, max=35), validators.Email()])
    password = PasswordField('New Password', [validators.DataRequired()])




class CustomerRegisterForm(Form):
    name = StringField('Name: ')
    username = StringField('Username: ',[validators.DataRequired()])
    email = StringField('Email: ', [validators.Email(), validators.DataRequired()])
    password = PasswordField('Password: ',[validators.DataRequired(),validators.EqualTo('confirm',message='Les mots de passe doivent etre identiques')])
    confirm = PasswordField('Repeat Password: ',[validators.DataRequired()])


    city = StringField('City: ',[validators.DataRequired()])
    contact = StringField('Contact: ',[validators.DataRequired()])
    address = StringField('Address: ',[validators.DataRequired()])
    profile = FileField ('Profile',validators=[FileAllowed(['jpg','png','jpeg','gif'],'Image only')])
    submit = SubmitField('Register')


class CustomerLoginForm(Form):
    email = StringField('Email: ', [validators.Email(), validators.DataRequired()])
    password = PasswordField('Password: ',[validators.DataRequired()])


@login_manager.user_loader
def user_loader(user_id):
    return Register.query.get(user_id)


class Register(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50), unique = False)
    username = db.Column(db.String(50), unique = True)
    email = db.Column(db.String(50), unique = True)
    password = db.Column(db.String(200), unique = False)
    city = db.Column(db.String(50), unique = False)
    contact = db.Column(db.String(50), unique = False)
    address = db.Column(db.String(50), unique = False)
    profile = db.Column(db.String(200), unique = False, default='profile.jpg')
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return '<Register %r>' % self.name



db.create_all()



'''********************************************************************************************************'''
'''********************************************************************************************************'''


@app.route("/")
def home():
    products= Addproduct.query.all()
    blogs = Addblog.query.all()
    categories = Category.query.all()
    return render_template("shop/home.html",products=products, blogs=blogs,categories=categories)


@app.route('/result')
def result():
    searchword = request.args.get('q')
    products = Addproduct.query.msearch(searchword, fields=['name','desc'], limit=3)
    categories = Category.query.all()
    return render_template('products/result.html',products=products, categories=categories)

@app.route("/shop")
def shop():
    titre='ChicClass-Boutique'
    brands = Brand.query.all() 
    categories = Category.query.all()
    page = request.args.get('page',1,type=int) 
    products= Addproduct.query.filter(Addproduct.stock>0).paginate(page=page,per_page=4)
    return render_template("shop/shop.html",titre=titre,brands=brands, products=products, categories=categories)

@app.route('/brand/<int:id>')
def get_brand(id):
    brand = Addproduct.query.filter_by(brand_id=id)
    brands = Brand.query.all() 
    page = request.args.get('page',1,type=int) 
    products= Addproduct.query.filter(Addproduct.stock>0).paginate(page=page,per_page=4)
    return render_template('shop/shop.html',brand=brand,products=products,brands=brands)

@app.route('/categories/<int:id>')
def get_category(id):
    get_c_prod = Addproduct.query.filter_by(category_id=id)
    categories = Category.query.all()
    page = request.args.get('page',1,type=int) 
    products= Addproduct.query.filter(Addproduct.stock>0).paginate(page=page,per_page=4)
    return render_template('shop/shop.html',get_c_prod=get_c_prod,categories=categories,products=products)


@app.route('/detailprod/<int:id>')
def detailprod(id):
    titre = 'ChicClass-produit'
    product = Addproduct.query.get_or_404(id)
    return render_template('products/detailprod.html',product=product,titre=titre)


'''==========================================================='''
'''=======================CART================================'''
'''==========================================================='''


@app.route("/cart")
def cart():
    titre='ChicClass-Panier'
    categories = Category.query.all()
    return render_template("shop/cart.html",titre=titre,categories=categories)


'''==========================================================='''
'''=======================END CART================================'''
'''==========================================================='''




'''==========================================================='''
'''=======================CUSTOMER================================'''
'''==========================================================='''
@app.route("/customer/register",methods=['GET','POST'])
def customer_register():
    titre ="ChicClass-S'inscrire"
    form = CustomerRegisterForm(request.form)
    if request.method == 'POST':
        has_password = bcrypt.generate_password_hash(form.password.data)
        register = Register(name=form.name.data, username=form.username.data, email=form.email.data, password=has_password,city=form.city.data,contact=form.contact.data, address=form.address.data)
        db.session.add(register)
        flash(f'Bienvenu {form.name.data}. Merci pour votre inscription')
        db.session.commit()
        return redirect(url_for('customerLogin'))
    return render_template('customer/register.html',form=form,titre=titre)



@app.route('/customer/login',methods=['GET','POST'])
def customerLogin():
    titre = 'ChicClass-Se connecter'
    form = CustomerLoginForm(request.form)
    if request.method == 'POST':
        user = Register.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password,form.password.data):
            login_user(user)
            flash('Vous etes connecte','success')
            next = request.args.get('next')
            return redirect(next or url_for('home'))
        flash('email et/ou mot de passe incorrecte','danger')
        return redirect(url_for('customerLogin'))
        
    return render_template('customer/login.html',form=form,titre = titre)
    


@app.route('/customer/logout')
def customer_logout():
    logout_user()
    return redirect(url_for('home'))


'''============================================================================================='''
'''=====================================END CUSTOMER============================================'''
'''============================================================================================='''

'''============================================================================================='''
'''============================================ADMIN============================================'''
'''============================================================================================='''

@app.route("/admin")
def admin():
    if 'email' not in session:
        flash("SVP connectez vous d'abbord",'danger')
        return redirect(url_for('login'))
    products = Addproduct.query.all()
    blogs = Addblog.query.all()
    return render_template('admin/indexadm.html',titre='Admin page', products=products,blogs=blogs)




@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        hash_password = bcrypt.generate_password_hash(form.password.data)
        user = User(name=form.name.data,username=form.username.data, email=form.email.data, password=hash_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Bienvenu {form.name.data}. Merci pour votre inscription')
        return redirect(url_for('login'))
    return render_template('admin/register.html', form=form, titre ='inscripition page')

    
    
@app.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm(request.form)
    if request.method == "POST" and form.validate():
        user = User.query.filter_by(email = form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            session['email'] = form.email.data
            flash(f'Bienvenu {form.email.data} Vous etes connecte')
            return redirect(request.args.get('next') or url_for('admin'))
        else:
            flash('Mot de Passe incorrecte', 'danger')
    return render_template("admin/login.html", form=form, titre="login page")

@app.route('/admin/logout')
def admin_logout():
    logout_user()
    return redirect(url_for('login'))

'''============================================================================================='''
'''========================================END ADMIN============================================'''
'''============================================================================================='''


'''============================================================================================='''
'''=========================================== BRAND============================================'''
'''============================================================================================='''

@app.route('/addbrand',methods=["GET","POST"])
def addbrand():
    if 'email' not in session:
        flash("SVP connectez vous d'abbord",'danger')
        return redirect(url_for('login'))

    if request.method =="POST":
        getbrand = request.form.get('brand')
        brand = Brand(name=getbrand)
        db.session.add(brand)
        flash(f'La marque {getbrand} est ajoute')
        db.session.commit()
        return redirect(url_for('admin'))
    return render_template('products/addbrand.html',brands='brands')

@app.route('/brands')
def brands():
    if 'email' not in session:
        flash("SVP connectez vous d'abbord",'danger')
        return redirect(url_for('login'))
    brands = Brand.query.order_by(Brand.id.desc()).all()
    return render_template('admin/brand.html', titre='marques page',brands=brands)

@app.route('/updatebrand/<int:id>',methods=['GET','POST'])
def updatebrand(id):
    if 'email' not in session:
        flash("SVP connectez vous d'abbord",'danger')
        return redirect(url_for('login'))
    updatebrand = Brand.query.get_or_404(id)
    brand = request.form.get('brand')
    if request.method == 'POST':
        updatebrand.name = brand
        flash(f'la marque est modifie')
        db.session.commit()
        return redirect(url_for('brands'))
    return render_template('products/updatebrand.html',titre='Mise a jour marque', updatebrand=updatebrand)


@app.route('/deletebrand/<int:id>', methods=['POST'])
def deletebrand(id):
    brand = Brand.query.get_or_404(id)
    if request.method == 'POST':
        db.session.delete(brand)
        db.session.commit()
        flash(f'La marque {brand.name} est supprime')
        return redirect(url_for('admin'))
    flash(f'La marque {brand.name} ne peux pas etre supprime')
    return redirect(url_for('admin'))

'''============================================================================================='''
'''=========================================END BRND============================================'''
'''============================================================================================='''

'''============================================================================================='''
'''=========================================CATEGORY============================================'''
'''============================================================================================='''

@app.route('/addcat',methods=["GET","POST"])
def addcat():
    if 'email' not in session:
        flash("SVP connectez vous d'abbord",'danger')
        return redirect(url_for('login'))
    if request.method =="POST":
        getbrand = request.form.get('category')
        cat = Category(name=getbrand)
        db.session.add(cat)
        flash(f'La categorie {getbrand} est ajoute')
        db.session.commit()
        return redirect(url_for('admin'))
    return render_template('products/addbrand.html')

@app.route('/category')
def category():
    if 'email' not in session:
        flash("SVP connectez vous d'abbord",'danger')
        return redirect(url_for('login'))
    categories = Category.query.order_by(Category.id.desc()).all()
    return render_template('admin/brand.html', titre='categories page',categories=categories)


@app.route('/updatecat/<int:id>',methods=['GET','POST'])
def updatecat(id):
    if 'email' not in session:
        flash("SVP connectez vous d'abbord",'danger')
        return redirect(url_for('login'))
    updatecat = Category.query.get_or_404(id)
    category = request.form.get('category')
    if request.method == 'POST':
        updatecat.name =  category
        flash(f'la categorie est modifie')
        db.session.commit()
        return redirect(url_for('category'))
    return render_template('products/updatebrand.html',titre='Mise a jour categorie', updatecat=updatecat)



@app.route('/deletecategory/<int:id>', methods=['POST'])
def deletecategory(id):
    category = Category.query.get_or_404(id)
    if request.method == 'POST':
        db.session.delete(category)
        db.session.commit()
        flash(f'La categorie {category.name} est supprime')
        return redirect(url_for('admin'))
    flash(f'La categorie {category.name} ne peux pas etre supprime')
    return redirect(url_for('admin'))




'''============================================================================================='''
'''========================================END CATEGORY========================================='''
'''============================================================================================='''


'''============================================================================================='''
'''=============================================BLOG============================================'''
'''============================================================================================='''

'''@app.route("/blog")
def blog():
    titre='ChicClass-Panier'
    blog = Addblog.query.all()
    categories = Category.query.all()
    return render_template("blog.html",titre=titre,blog=blog,categories=categories)'''

@app.route('/readmoreblog/<int:id>')
def readmoreblog(id):
    titre='ChicClass-Blog'
    categories = Category.query.all()
    blog = Addblog.query.get_or_404(id)
    return render_template('shop/blog.html',blog=blog,categories=categories,titre=titre)

@app.route('/addblog', methods=['GET','POST'])
def addblog():
    if 'email' not in session:
        flash("SVP connectez vous d'abbord",'danger')
        return redirect(url_for('login'))
    
    
    form = Addblogs(request.form)
    if request.method == "POST":
        title = form.title.data
        author = form.author.data
        content = form.content.data
        text = form.content.data
    
        image = photos.save(request.files.get('image'), name=secrets.token_hex(10)+".")

        addblg = Addblog(title=title,author=author, content=content, image=image,text=text)

        db.session.add(addblg)
        flash(f'Le blog {title} est ajoute au data base')
        db.session.commit()

        return redirect(url_for("admin"))
    return render_template('products/addblog.html', titre='Ajouter les blogs', form=form)



@app.route('/updateblog/<int:id>',methods=['GET','POST'])
def updateblog(id):
    blog = Addblog.query.get_or_404(id)
    form = Addblogs(request.form)
    if request.method == 'POST':
        blog.title = form.title.data
        blog.author = form.author.data
        blog.content = form.content.data
        blog.text = form.text.data
        if request.files.get('image'):
            try:
                os.unlink(os.path.join(current_app.root_path, "static/assets/"+blog.image))
                blog.image = photos.save(request.files.get('image'), name=secrets.token_hex(10)+".")
            except:
                blog.image = photos.save(request.files.get('image'), name=secrets.token_hex(10)+".")
        
        db.session.commit()
        flash(f'le blog est mise a jour')
        return redirect(url_for('admin'))

    form.title.data = blog.title
    form.author.data = blog.author
    form.content.data = blog.content
    form.text.data = blog.text
    
    return  render_template('products/updateblog.html',form=form,blog=blog)



@app.route('/deleteblog/<int:id>',methods=["POST"])
def deleteblog(id):
    blog = Addblog.query.get_or_404(id)
    if request.method == 'POST':
        if request.files.get('image'):
            try:
                os.unlink(os.path.join(current_app.root_path, "static/assets/"+blog.image)) 
            except Exception as e:
                print(e)
        
        db.session.delete(blog)
        db.session.commit()
        flash(f'Le blog {blog.title} a ete supprimer')
        return redirect(url_for('admin'))
    flash(f'Le blog ne peut pas etre supprimer')
    return redirect(url_for('admin'))



'''============================================================================================='''
'''=========================================END BLOG============================================'''
'''============================================================================================='''


'''============================================================================================='''
'''==========================================PRODUCT============================================'''
'''============================================================================================='''




@app.route('/addproduct', methods=['GET','POST'])
def addproduct():
    if 'email' not in session:
        flash("SVP connectez vous d'abbord",'danger')
        return redirect(url_for('login'))
    
    brands = Brand.query.all()
    categories = Category.query.all()
    form = Addproducts(request.form)
    if request.method == "POST":
        name = form.name.data
        price = form.price.data
        priced = form.priced.data
        stock = form.stock.data
        colors = form.colors.data
        desc = form.description.data
        brand = request.form.get('brand')
        category = request.form.get('category')
        image = photos.save(request.files.get('image'), name=secrets.token_hex(10)+".")

        addpro = Addproduct(name=name,price=price, priced=priced,stock=stock,colors=colors,
        desc=desc,brand_id=brand, category_id=category, image=image)

        db.session.add(addpro)
        flash(f'Le produit {name} est ajoute au data base')
        db.session.commit()

        return redirect(url_for("admin"))
    return render_template('products/addproduct.html', titre='Ajouter les produits', form=form, brands=brands, categories= categories)




@app.route('/updateproduct/<int:id>',methods=['GET','POST'])
def updateproduct(id):
    brands = Brand.query.all()
    categories = Category.query.all()
    product = Addproduct.query.get_or_404(id)
    brand = request.form.get('brand')
    category = request.form.get('category')
    form = Addproducts(request.form)
    if request.method == 'POST':
        product.name = form.name.data
        product.price = form.price.data
        product.priced = form.priced.data
        product.brand_id = brand
        product.category_id = category
        product.colors = form.colors.data
        product.desc = form.description.data
        if request.files.get('image'):
            try:
                os.unlink(os.path.join(current_app.root_path, "static/assets/"+product.image))
                product.image = photos.save(request.files.get('image'), name=secrets.token_hex(10)+".")
            except:
                product.image = photos.save(request.files.get('image'), name=secrets.token_hex(10)+".")
        db.session.commit()
        flash(f'le produit est mise a jour')
        return redirect(url_for('admin'))

    form.name.data = product.name
    form.price.data = product.price
    form.priced.data = product.priced
    form.stock.data = product.stock
    form.colors.data = product.colors
    form.description.data = product.desc
    return  render_template('products/updateproduct.html',form=form,brands=brands,categories=categories,product=product)


@app.route('/deleteproduct/<int:id>',methods=["POST"])
def deleteproduct(id):
    product = Addproduct.query.get_or_404(id)
    if request.method == 'POST':
        if request.files.get('image'):
            try:
                os.unlink(os.path.join(current_app.root_path, "static/assets/"+product.image)) 
            except Exception as e:
                print(e)
        
        db.session.delete(product)
        db.session.commit()
        flash(f'Le produit {product.name} a ete supprimer')
        return redirect(url_for('admin'))
    flash(f'Le produit ne peut pas etre supprimer')
    return redirect(url_for('admin'))




'''============================================================================================='''
'''===========================================END PRODUCT======================================='''
'''============================================================================================='''





if __name__=="__main__":
    app.run(debug=True)