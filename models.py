from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Client(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    company = db.Column(db.String(100))
    notes = db.Column(db.Text)

class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    date = db.Column(db.String(20))
    total_amount = db.Column(db.Float)
    payment_status = db.Column(db.String(20))

    client = db.relationship('Client', backref=db.backref('invoices', lazy=True))

class InvoiceItems(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoice.id'), nullable=False)
    description = db.Column(db.String(200))
    quantity = db.Column(db.Integer)
    rate = db.Column(db.Float)
    amount = db.Column(db.Float)

    invoice = db.relationship('Invoice', backref=db.backref('items', lazy=True))
