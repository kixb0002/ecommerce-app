import unittest
from app import app


class QuoteTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_total_uses_catalogue_not_client_price(self):
        result = self.client.post('/api/quotes', json={'items': [
            {'product_id': 'keyboard', 'quantity': 2, 'unit_price_cents': 1},
            {'product_id': 'mouse', 'quantity': 1}]})
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.json['total_cents'], 12300)

    def test_bad_quantities_and_unknown_product(self):
        for quantity in (0, -1, 100, True, 1.5, '2', None):
            with self.subTest(quantity=quantity):
                result = self.client.post('/api/quotes', json={'items': [
                    {'product_id': 'mouse', 'quantity': quantity}]})
                self.assertEqual(result.status_code, 400)
        self.assertEqual(self.client.post('/api/quotes', json={'items': [
            {'product_id': 'unknown', 'quantity': 1}]}).status_code, 400)

    def test_malformed_and_oversized_input(self):
        for payload in (None, [], {}, {'items': []}, {'items': ['invalid']},
                        {'items': [{}] * 51}):
            self.assertEqual(self.client.post('/api/quotes', json=payload).status_code, 400)
        self.assertEqual(self.client.post('/api/quotes', data='x' * 17000,
                                         content_type='application/json').status_code, 413)

    def test_health_and_catalogue(self):
        self.assertEqual(self.client.get('/healthz').status_code, 200)
        self.assertEqual(self.client.get('/readyz').status_code, 200)
        self.assertEqual(len(self.client.get('/api/products').json['products']), 3)


if __name__ == '__main__':
    unittest.main()
