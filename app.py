from flask import Flask, render_template, redirect, url_for, request, make_response, flash
from models import db, Client, Invoice, InvoiceItems
from datetime import datetime
from weasyprint import HTML
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'abcd'

db.init_app(app)

with app.app_context():
    db.create_all()

def get_company_info():
    with open('company_info.json', 'r') as f:
        return json.load(f)

@app.route('/')
def home():
    return redirect(url_for('clients'))

@app.route('/clients', methods = ['GET','POST'])
def clients():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        company = request.form['company']
        notes = request.form['notes']

        new_client = Client(name=name, email=email, phone=phone, company=company, notes=notes)
        db.session.add(new_client)
        db.session.commit()
        return redirect(url_for('clients'))
    
    clients = Client.query.all()
    return render_template('clients.html', clients=clients)

@app.route('/invoices/new', methods = ['GET','POST'])
def new_invoice():
    clients = Client.query.all()

    if request.method == 'POST':
        client_id = request.form['client']
        date = datetime.now().strftime("%Y-%m-%d")
        status = request.form['status']
        items = []

        total_amount = 0
        description = request.form.getlist('description')
        quantities = request.form.getlist('quantity')
        rates = request.form.getlist('rate')
    
        for desc, qty, rate in zip(description,quantities, rates):
            qty = int(qty)
            rate = float(rate)
            amount = qty * rate
            total_amount += amount
            items.append({'description': desc, 'quantity': qty, 'rate': rate, 'amount': amount})

        invoice = Invoice(client_id=client_id, date=date, total_amount=total_amount, payment_status=status)
        print(invoice.payment_status)
        db.session.add(invoice)
        db.session.commit()

        for item in items:
            line = InvoiceItems(invoice_id=invoice.id, **item)
            db.session.add(line)

        db.session.commit()
        return redirect(url_for('clients'))
    
    return render_template('new_invoice.html',clients=clients)

@app.route('/invoices')
def invoices():
    all_invoices = Invoice.query.all()
    return render_template('invoices.html', invoices = all_invoices)

@app.route('/invoices/<int:invoice_id>')
def view_invoice(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    company_info = get_company_info()
    return render_template('invoice_details.html', invoice=invoice, company=company_info)

@app.route('/invoices/<int:invoice_id>/edit', methods=['GET', 'POST'])
def edit_invoice(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    clients = Client.query.all()

    if request.method == 'POST':
        invoice.client_id = request.form['client']

        # Track total manually
        total = 0

        # Update existing items
        for item in invoice.items:
            item_id = str(item.id)
            item.description = request.form.get(f'description_{item_id}', '')
            item.quantity = int(request.form.get(f'quantity_{item_id}', 0))
            item.rate = float(request.form.get(f'rate_{item_id}', 0.0))
            item.amount = item.quantity * item.rate
            total += item.amount  # Add to total

        # Add new items dynamically
        i = 0
        while True:
            desc = request.form.get(f'new_description_{i}')
            qty = request.form.get(f'new_quantity_{i}')
            rate = request.form.get(f'new_rate_{i}')
            if not (desc and qty and rate):
                break
            try:
                qty = int(qty)
                rate = float(rate)
                amount = qty * rate
                total += amount  # Add to total here as well

                new_item = InvoiceItems(
                    invoice_id=invoice.id,
                    description=desc,
                    quantity=qty,
                    rate=rate,
                    amount=amount
                )
                db.session.add(new_item)
            except ValueError:
                pass
            i += 1

        # Set total_amount after all items (existing + new)
        invoice.total_amount = total

        db.session.commit()
        return redirect(url_for('invoices'))

    return render_template('edit_invoice.html', invoice=invoice, clients=clients)


@app.route('/invoices/<int:invoice_id>/delete')
def delete_invoice(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    
    # Delete invoice items first
    for item in invoice.items:
        db.session.delete(item)

    db.session.delete(invoice)
    db.session.commit()
    return redirect(url_for('invoices'))


@app.route('/invoices/<int:invoice_id>/download')
def download_invoice_pdf(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    rendered = render_template('invoice_details.html', invoice=invoice, company = get_company_info())
    pdf = HTML(string=rendered).write_pdf()

    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=invoice_{invoice_id}.pdf'

    return response

@app.route('/invoices/<int:invoice_id>/status', methods=['POST'])
def update_invoice_status(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    new_status = request.form['status']
    invoice.payment_status = new_status
    db.session.commit()
    return redirect(url_for('invoices'))

@app.route('/company/edit', methods=['GET', 'POST'])
def edit_company():
    if request.method == 'POST':
        # Get form data
        company_data = {
            "name": request.form['name'],
            "logo": request.form['logo'],
            "address": request.form['address'],
            "email": request.form['email'],
            "phone": request.form['phone'],
            "gst": request.form['gst']
        }

        # Save to JSON
        with open('company_info.json', 'w') as f:
            json.dump(company_data, f, indent=4)

        flash("Company info updated successfully!", "success")
        return redirect(url_for('edit_company'))
    
    try:
        company_info = get_company_info()
    except FileNotFoundError:
        company_info = {
            "name": "", "logo": "", "address": "",
            "email": "", "phone": "", "gst": ""
        }

    return render_template('edit_company.html', company=company_info)
if __name__ == "__main__":
    app.run(debug = True)