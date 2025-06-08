from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'gizli_anahtar'

# Jinja2 context'e yıl bilgisini doğrudan ver
@app.context_processor
def inject_year():
    return {'now': datetime.utcnow()}

# Ürün listesi (kategori dahil)
products = [
    {"id": 1, "name": "Güneş Kremi", "price": 149, "category": "Cilt Bakımı", "description": ""},
    {"id": 2, "name": "Nemlendirici", "price": 99, "category": "Cilt Bakımı", "description": ""},
    {"id": 3, "name": "Makyaj Seti", "price": 259, "category": "Makyaj", "description": ""},
    {"id": 4, "name": "Ruj", "price": 89, "category": "Makyaj", "description": ""},
    {"id": 5, "name": "Parfüm", "price": 199, "category": "Parfüm", "description": ""}
]

users = []
orders = []
sellers = []
seller_products = []
user_favorites = {}
user_accounts = {}
product_counter = 1000

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/product')
def product():
    kategori = request.args.get('category')
    all_products = products + seller_products
    filtreli = [p for p in all_products if p['category'] == kategori] if kategori else all_products
    kategoriler = sorted(set([p['category'] for p in all_products]))
    return render_template('product.html', products=filtreli, categories=kategoriler, selected=kategori)

@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    session.setdefault('cart', []).append(product_id)
    return redirect(url_for('cart'))

@app.route('/cart')
def cart():
    all_products = products + seller_products
    cart_items = [p for pid in session.get('cart', []) for p in all_products if p['id'] == pid]
    return render_template('cart.html', cart=cart_items)

@app.route('/place_order', methods=['POST'])
def place_order():
    if 'user' not in session or not session.get('cart'):
        return redirect(url_for('cart'))
    all_products = products + seller_products
    cart_items = [p for pid in session['cart'] for p in all_products if p['id'] == pid]
    orders.append({"username": session['user'], "items": cart_items})
    session['cart'] = []
    return redirect(url_for('orders_view'))

@app.route('/orders')
def orders_view():
    if 'user' not in session:
        return redirect(url_for('login'))
    user_orders = [o for o in orders if o['username'] == session['user']]
    return render_template('orders.html', orders=user_orders)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        if any(u['username'] == username for u in users):
            return "Bu kullanıcı adı zaten alınmış."
        users.append({'username': username, 'password': request.form.get('password')})
        user_accounts[username] = {
            'email': request.form.get('email'),
            'registration_date': datetime.now().strftime("%Y-%m-%d")
        }
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        for u in users:
            if u['username'] == request.form.get('username') and u['password'] == request.form.get('password'):
                session['user'] = u['username']
                return redirect(url_for('dashboard'))
        return 'Hatalı kullanıcı adı veya şifre'
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', user=session['user'])

@app.route('/account')
def account():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('account.html', account_data=user_accounts.get(session['user']))

@app.route('/change_password', methods=['POST'])
def change_password():
    if 'user' not in session:
        return redirect(url_for('login'))
    for u in users:
        if u['username'] == session['user']:
            u['password'] = request.form.get('new_password')
            break
    return redirect(url_for('account'))

@app.route('/favorites')
def favorites():
    if 'user' not in session:
        return redirect(url_for('login'))
    fav_ids = user_favorites.get(session['user'], [])
    all_products = products + seller_products
    fav_products = [p for p in all_products if p['id'] in fav_ids]
    return render_template('favorites.html', favorites=fav_products)

@app.route('/add_to_favorites/<int:product_id>')
def add_to_favorites(product_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    favs = user_favorites.setdefault(session['user'], [])
    if product_id not in favs:
        favs.append(product_id)
    return redirect(url_for('favorites'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/support', methods=['POST'])
def support():
    print(f"Destek Talebi: {request.form.get('name')} | {request.form.get('email')} | {request.form.get('message')}")
    return redirect(url_for('contact'))

# ---------- Satıcı Paneli ----------
@app.route('/seller/apply', methods=['GET', 'POST'])
def seller_apply():
    if request.method == 'POST':
        sellers.append({
            "shop_name": request.form.get('shop_name'),
            "email": request.form.get('email'),
            "phone": request.form.get('phone'),
            "tax_no": request.form.get('tax_no'),
            "password": request.form.get('password')
        })
        return redirect(url_for('seller_login'))
    return render_template('seller_apply.html')

@app.route('/seller/login', methods=['GET', 'POST'])
def seller_login():
    if request.method == 'POST':
        for s in sellers:
            if s['email'] == request.form.get('email') and s['password'] == request.form.get('password'):
                session['seller'] = s['email']
                return redirect(url_for('seller_dashboard'))
        return "Hatalı e-posta veya şifre"
    return render_template('seller_login.html')

@app.route('/seller/dashboard')
def seller_dashboard():
    if 'seller' not in session:
        return redirect(url_for('seller_login'))
    seller_info = next((s for s in sellers if s['email'] == session['seller']), None)
    return render_template('seller_dashboard.html', seller=seller_info)

@app.route('/seller/products')
def seller_products_view():
    if 'seller' not in session:
        return redirect(url_for('seller_login'))
    items = [p for p in seller_products if p['seller_email'] == session['seller']]
    return render_template('seller_products.html', products=items)

@app.route('/seller/add-product', methods=['GET', 'POST'])
def seller_add_product():
    global product_counter
    if 'seller' not in session:
        return redirect(url_for('seller_login'))
    if request.method == 'POST':
        product_counter += 1
        seller_products.append({
            "id": product_counter,
            "name": request.form.get('name'),
            "price": float(request.form.get('price')),
            "category": request.form.get('category'),
            "description": request.form.get('description'),
            "seller_email": session['seller']
        })
        return redirect(url_for('seller_products_view'))
    return render_template('seller_add_product.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=81)
