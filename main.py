from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'gizli_anahtar'

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
product_counter = 1000  # seller ürün ID'leri için başlangıç

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/product')
def product():
    kategori = request.args.get('category')
    all_products = products + seller_products
    if kategori:
        filtreli = [p for p in all_products if p['category'] == kategori]
    else:
        filtreli = all_products
    kategoriler = sorted(set([p['category'] for p in all_products]))
    return render_template('product.html', products=filtreli, categories=kategoriler, selected=kategori)

@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    if 'cart' not in session:
        session['cart'] = []
    session['cart'].append(product_id)
    return redirect(url_for('cart'))

@app.route('/cart')
def cart():
    all_products = products + seller_products
    cart_items = []
    if 'cart' in session:
        for product_id in session['cart']:
            for product in all_products:
                if product['id'] == product_id:
                    cart_items.append(product)
    return render_template('cart.html', cart=cart_items)

@app.route('/place_order', methods=['POST'])
def place_order():
    if 'user' not in session:
        return redirect(url_for('login'))
    if 'cart' not in session or not session['cart']:
        return redirect(url_for('cart'))

    all_products = products + seller_products
    cart_items = []
    for product_id in session['cart']:
        for product in all_products:
            if product['id'] == product_id:
                cart_items.append(product)

    orders.append({
        "username": session['user'],
        "items": cart_items
    })

    session['cart'] = []
    return redirect(url_for('orders_view'))

@app.route('/orders')
def orders_view():
    if 'user' not in session:
        return redirect(url_for('login'))

    user_orders = [order for order in orders if order['username'] == session['user']]
    return render_template('orders.html', orders=user_orders)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        for user in users:
            if user['username'] == username:
                return "Bu kullanıcı adı zaten alınmış."
        users.append({'username': username, 'password': password})
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        for user in users:
            if user['username'] == username and user['password'] == password:
                session['user'] = username
                return redirect(url_for('dashboard'))
        return 'Hatalı kullanıcı adı veya şifre'
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', user=session['user'])

@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('cart', None)
    session.pop('seller', None)
    return redirect(url_for('home'))

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/support', methods=['POST'])
def support():
    name = request.form.get('name')
    email = request.form.get('email')
    message = request.form.get('message')
    print(f"Destek Talebi Alındı:\nAd: {name}\nE-posta: {email}\nMesaj: {message}")
    return redirect(url_for('contact'))

# ---------- Satıcı Paneli ----------

@app.route('/seller/apply', methods=['GET', 'POST'])
def seller_apply():
    if request.method == 'POST':
        shop_name = request.form.get('shop_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        tax_no = request.form.get('tax_no')
        password = request.form.get('password')
        sellers.append({
            "shop_name": shop_name,
            "email": email,
            "phone": phone,
            "tax_no": tax_no,
            "password": password
        })
        return redirect(url_for('seller_login'))
    return render_template('seller_apply.html')

@app.route('/seller/login', methods=['GET', 'POST'])
def seller_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        for seller in sellers:
            if seller['email'] == email and seller['password'] == password:
                session['seller'] = email
                return redirect(url_for('seller_dashboard'))
        return "Hatalı e-posta veya şifre"
    return render_template('seller_login.html')

@app.route('/seller/dashboard')
def seller_dashboard():
    if 'seller' not in session:
        return redirect(url_for('seller_login'))
    seller_info = next((s for s in sellers if s['email'] == session['seller']), None)
    return render_template('seller_dashboard.html', seller=seller_info)

@app.route('/seller/products', methods=['GET', 'POST'])
def seller_products_view():
    if 'seller' not in session:
        return redirect(url_for('seller_login'))

    seller_items = [p for p in seller_products if p['seller_email'] == session['seller']]
    return render_template('seller_products.html', products=seller_items)

@app.route('/seller/add-product', methods=['GET', 'POST'])
def seller_add_product():
    global product_counter
    if 'seller' not in session:
        return redirect(url_for('seller_login'))

    if request.method == 'POST':
        name = request.form.get('name')
        price = float(request.form.get('price'))
        category = request.form.get('category')
        description = request.form.get('description')
        seller_email = session['seller']
        product_counter += 1
        seller_products.append({
            "id": product_counter,
            "name": name,
            "price": price,
            "category": category,
            "description": description,
            "seller_email": seller_email
        })
        return redirect(url_for('seller_products_view'))

    return render_template('seller_add_product.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=81)
