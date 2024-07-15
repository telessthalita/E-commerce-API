from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'

db = SQLAlchemy(app)
CORS(app)

#Usuários 
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=True)

#Produtos 
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True)

app.route('/login', method=["POST"])
def login():
    data = request.json

    user = User.query.filter_by(username=data.get("username")).first()    
    print(user)
    return jsonify({"message": "Logged in successfully"})
@app.route('/api/products/add', methods=["POST"])
def add_product():
    data = request.json
    if 'name' in data and 'price' in data:
        product = Product(name=data["name"], price=data["price"], description=data.get("description", ""))
        db.session.add(product)
        db.session.commit()
        return jsonify({"message": "Product added successfully."})
    return jsonify({"message": "Invalid product data."}), 400

@app.route('/api/products/delete/<int:product_id>', methods=["DELETE"])
def delete_product(product_id):
    product = Product.query.get(product_id)
    if product:
        db.session.delete(product)
        db.session.commit()
        return jsonify({"message": "Product deleted successfully."})
    return jsonify({"message": "Product not found."}), 400

@app.route('/api/products/<int:product_id>', methods=["GET"])
def get_product_details(product_id):
    product = Product.query.get(product_id)
    if product:
        return jsonify({
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "description": product.description,
        })
    return jsonify({"message": "Product not found"}), 404

@app.route('/api/products/<int:product_id>', methods=["PUT"])
def update_product(product_id):
    product = product.query.get(product_id)
    if not product:
        return jsonify ({"message": "Product not found"}), 404
    data = request.json
    if 'name' in data:
        product.name = data['name']
        
    if 'price' in data:
        product.name = data['price']

    if 'description' in data:
        product.name = data['description']

    return jsonify ({"message:" "Product update successfully"})

@app.route('/api/products', methods=['GET'])
def get_products( ):
    products = Product.query.all()
    product_list = []
    print (products)
    for product in products:
        produc_data = {
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "description": product.description,
        }
        product_list.append(produc_data)
    return jsonify (product_list)
        
   
# Definir uma rota raiz  e a função que será executada ao requisitar
@app.route('/')
def hello_world():
    return 'Hello World'

if __name__ == "__main__":
    app.run(debug=True)
