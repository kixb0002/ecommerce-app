"""API de catalogue et devis : stateless, sans paiement ni données personnelles."""
from flask import Flask, jsonify, request

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024
PRODUCTS = {
    'keyboard': {'id': 'keyboard', 'name': 'Clavier', 'unit_price_cents': 4900},
    'mouse': {'id': 'mouse', 'name': 'Souris', 'unit_price_cents': 2500},
    'headset': {'id': 'headset', 'name': 'Casque', 'unit_price_cents': 7900},
}


@app.after_request
def headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Cache-Control'] = 'no-store'
    return response


@app.get('/healthz')
@app.get('/readyz')
def health():
    return jsonify(status='ok')


@app.get('/api/products')
def products():
    return jsonify(currency='EUR', products=list(PRODUCTS.values()))


@app.post('/api/quotes')
def quote():
    payload = request.get_json(silent=True)
    items = payload.get('items') if isinstance(payload, dict) else None
    if not isinstance(items, list) or not 1 <= len(items) <= 50:
        return jsonify(error='items doit contenir entre 1 et 50 lignes'), 400
    lines = []
    for item in items:
        if not isinstance(item, dict):
            return jsonify(error='Ligne de panier invalide'), 400
        product_id, quantity = item.get('product_id'), item.get('quantity')
        if not isinstance(product_id, str) or product_id not in PRODUCTS:
            return jsonify(error='Produit inconnu'), 400
        if type(quantity) is not int or not 1 <= quantity <= 99:
            return jsonify(error='quantity doit être un entier entre 1 et 99'), 400
        product = PRODUCTS[product_id]
        # Les prix viennent exclusivement du catalogue serveur, jamais du client.
        lines.append(dict(product_id=product_id, quantity=quantity,
                          unit_price_cents=product['unit_price_cents'],
                          subtotal_cents=product['unit_price_cents'] * quantity))
    return jsonify(currency='EUR', lines=lines,
                   total_cents=sum(line['subtotal_cents'] for line in lines))
