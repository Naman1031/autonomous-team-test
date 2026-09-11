import unittest
from app import app
from models import User, Subscription
from services import apply_discount

app.config['TESTING'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'

with app.app_context():
    User.query.delete()
    Subscription.query.delete()

    user = User(id=1, name='John Doe', email='john@example.com')
    subscription = Subscription(user_id=1, amount=100.0)
    user.subscriptions.append(subscription)
    db.session.add(user)
    db.session.commit()

    class TestApplyDiscount(unittest.TestCase):
        def test_apply_discount(self):
            response = app.post('/apply-discount', json={'user_id': 1, 'discount': 10.0})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json['message'], 'Discount applied successfully')

            subscription = Subscription.query.filter_by(user_id=1).first()
            self.assertEqual(subscription.amount, 90.0)

        def test_user_not_found(self):
            response = app.post('/apply-discount', json={'user_id': 2, 'discount': 10.0})
            self.assertEqual(response.status_code, 404)

        def test_subscription_not_found(self):
            user = User(id=1, name='John Doe', email='john@example.com')
            db.session.add(user)
            db.session.commit()

            response = app.post('/apply-discount', json={'user_id': 1, 'discount': 10.0})
            self.assertEqual(response.status_code, 404)

    if __name__ == '__main__':
        unittest.main()