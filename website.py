from flask import Flask, render_template

app = Flask(__name__)

# Example product data
products = [
    {'id': 1, 'name': 'MacBook Pro', 'description': 'High-performance laptop from Apple', 'price': 'RM10,999', 'image': 'macbook_pro.jpg', 'details': 'The MacBook Pro is a powerful laptop designed for professionals.'},
    {'id': 2, 'name': 'ROG Laptop', 'description': 'Gaming laptop from ASUS', 'price': 'RM11,499', 'image': 'rog_laptop.jpg', 'details': 'The ROG laptop is built for gaming with a high refresh rate screen and powerful GPU.'},
    {'id': 3, 'name': 'Acer Predator', 'description': 'High-end gaming laptop from Acer', 'price': 'RM11,400', 'image': 'acer_predator.jpg', 'details': 'Acer Predator provides excellent gaming performance at an affordable price.'},
    {'id': 4, 'name': 'Macbook Air', 'description': 'Lean. Mean. M3 Machine', 'price': 'RM5,569', 'image': 'macb_air.jpg', 'details': 'With up to 18 hours of battery life, you can blaze through whatever you’re into all day long.'},
    {'id': 5, 'name': 'HP ZBook Firefly', 'description': '16 inch G11 Mobile Workstation PC', 'price': 'RM8,466', 'image': 'hp.jpg', 'details': 'Pro-level performance combines with true mobility in this sleek and powerful laptop.'}
]

@app.route('/')
def home():
    return render_template('index.html', products=products)

@app.route('/product/<int:id>')
def product_detail(id):
    # Find the product by id
    product = next((item for item in products if item["id"] == id), None)
    if product:
        return render_template('product_detail.html', product=product)
    else:
        return "Product not found", 404

if __name__ == '__main__':
    app.run(debug=True)


