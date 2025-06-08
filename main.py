from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'gizli_anahtar'

# Ürün listesi (kategori dahil)
products = [
    {"id": 1, "name": "Güneş Kremi", "price": 149, "category": "Cilt Bakımı"},
    {"id": 2, "name": "Nemlendirici", "price": 99, "category": "Cilt Bakımı"},
    {"id": 3, "name": "Makyaj Seti", "price": 259, "category": "Makyaj"},
    {"id": 4, "name": "Ruj", "price": 89, "category": "Makyaj"},
    {"id": 5, "name": "Parfüm", "price": 199, "category": "Parfüm"}
]

# Geçici kullanıcı ve sipariş listesi
users = []
orders = []

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/product')
def product():
    kategori = request.args.get('category')
    if kategori:
        filtreli = [p for p in products if p['category'] == kategori]
    else:
        filtreli = products
    kategoriler = sorted(set([p['category'] for p in products]))
    return render_template('product.html', products=filtreli, categories=kategoriler, selected=kategori)

@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    if 'cart' not in session:
        session['cart'] = []
    session['cart'].append(product_id)
    return redirect(url_for('cart'))

@app.route('/cart')
def cart():
    cart_items = []
    if 'cart' in session:
        for product_id in session['cart']:
            for product in products:
                if product['id'] == product_id:
                    cart_items.append(product)
    return render_template('cart.html', cart=cart_items)

@app.route('/place_order', methods=['POST'])
def place_order():
    if 'user' not in session:
        return redirect(url_for('login'))
    if 'cart' not in session or not session['cart']:
        return redirect(url_for('cart'))

    cart_items = []
    for product_id in session['cart']:
        for product in products:
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=81)
