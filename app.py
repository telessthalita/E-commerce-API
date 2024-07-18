from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = "minha_chave_123"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'

login_manager = LoginManager()
db = SQLAlchemy(app)
login_manager.init_app(app)
login_manager.login_view = 'login'
CORS(app)

# Usuários
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=True)
    cart = db.relationship('CartItem', backref='user', lazy=True)

# Produtos
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True)

# Carrinho
class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)

# Autenticação
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login', methods=["POST"])
def login():
    try:
        data = request.json
        user = User.query.filter_by(username=data.get("username")).first()

        if user and data.get("password") == user.password:
            login_user(user)
            return jsonify({"message": "Logged in successfully"})
        
        return jsonify({"message": "Unauthorized. Invalid credentials"}), 401
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@app.route('/logout', methods=["POST"])
@login_required
def logout():
    try:
        logout_user()
        return jsonify({"message": "Logout successfully"})
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@app.route('/api/products/add', methods=["POST"])
@login_required
def add_product():
    try:
        data = request.json
        if 'name' in data and 'price' in data:
            product = Product(name=data["name"], price=data["price"], description=data.get("description", ""))
            db.session.add(product)
            db.session.commit()
            return jsonify({"message": "Product added successfully."})
        return jsonify({"message": "Invalid product data."}), 400
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@app.route('/api/products/delete/<int:product_id>', methods=["DELETE"])
@login_required
def delete_product(product_id):
    try:
        product = Product.query.get(product_id)
        if product:
            db.session.delete(product)
            db.session.commit()
            return jsonify({"message": "Product deleted successfully."})
        return jsonify({"message": "Product not found."}), 400
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@app.route('/api/products/<int:product_id>', methods=["GET"])
@login_required
def get_product_details(product_id):
    try:
        product = Product.query.get(product_id)
        if product:
            return jsonify({
                "id": product.id,
                "name": product.name,
                "price": product.price,
                "description": product.description,
            })
        return jsonify({"message": "Product not found"}), 404
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@app.route('/api/products/<int:product_id>', methods=["PUT"])
@login_required
def update_product(product_id):
    try:
        product = Product.query.get(product_id)
        if not product:
            return jsonify({"message": "Product not found"}), 404
        data = request.json
        if 'name' in data:
            product.name = data['name']
        
        if 'price' in data:
            product.price = data['price']

        if 'description' in data:
            product.description = data['description']

        db.session.commit()
        return jsonify({"message": "Product updated successfully"})
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@app.route('/api/products', methods=['GET'])
@login_required
def get_products():
    try:
        products = Product.query.all()
        product_list = []
        for product in products:
            product_data = {
                "id": product.id,
                "name": product.name,
                "price": product.price,
                "description": product.description,
            }
            product_list.append(product_data)
        return jsonify(product_list)
    except Exception as e:
        return jsonify({"message": str(e)}), 500

# Checkout
@app.route('/api/cart/add/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    try:
        user = User.query.get(current_user.id)
        product = Product.query.get(product_id)

        if user and product:
            cart_item = CartItem(user_id=user.id, product_id=product.id)
            db.session.add(cart_item)
            db.session.commit()
            return jsonify({'message': 'Item added to the cart successfully'}), 200
        return jsonify({'message': 'Failed to add item to the cart'}), 400
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/api/cart/remove/<int:product_id>', methods=['DELETE'])
@login_required
def remove_from_cart(product_id):
    try:
        cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
        if cart_item:
            db.session.delete(cart_item)
            db.session.commit()
            return jsonify({'message': 'Item removed from the cart successfully'}), 200
        return jsonify({'message': 'Failed to remove item from the cart'}), 400
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/api/cart', methods=['GET'])
@login_required
def view_cart():
     user = User.query.get(int(current_user.id))
     cart_items = user.cart
     for cart_item in cart_items:
         print()
     #TODO: terminar a rota de itens no carrinho 
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
