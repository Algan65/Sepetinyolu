from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'gizli_anahtar'

# Örnek ürünler
products = [
    {"id": 1, "name": "Güneş Kremi", "price": 149},
    {"id": 2, "name": "Nemlendirici", "price": 99},
    {"id": 3, "name": "Makyaj Seti", "price": 259}
]

# Geçici kullanıcı listesi
users = []

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/product')
def product():
    return render_template('product.html', products=products)

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

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # Aynı kullanıcı varsa kayıt etme
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=81)
