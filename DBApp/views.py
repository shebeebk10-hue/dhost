from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.template.loader import get_template

from xhtml2pdf import pisa

from .models import Invoice, Shop

from decimal import Decimal

from django.contrib.auth.models import User


# HOME

def home(request):
    return render(request, 'home.html')

def shops_auth(request):

    ERROR = ""

    # Your fixed password
    SECRET_PASSWORD = os.environ.get("SHOP_PASSWORD")

    if request.method == "POST":

        entered_password = request.POST.get('password')

        if entered_password == SECRET_PASSWORD:

            # Save session
            request.session['shops_access'] = True

            return redirect('shops')

        else:
            ERROR = "Wrong Password"

    return render(request, 'shops_auth.html', {'error': ERROR})
# SHOPS

def shops(request):

    # Check if password entered
    if not request.session.get('shops_access'):
        return redirect('shops_auth')

    shops = Shop.objects.all()

    return render(request, 'shops.html', {'shops': shops})


# VIEW DETAILS

def view_details(request, id):

    shop = get_object_or_404(Shop, id=id)

    invoices = Invoice.objects.filter(shop=shop).order_by('id')

    running_balance = Decimal('0.00')

    for inv in invoices:

        # total amount
        total = inv.weight * inv.rate

        # previous balance
        inv.previous_balance = running_balance

        # closing balance
        inv.closing_balance = (
            running_balance + total - inv.paid_amount
        )

        # update running balance
        running_balance = inv.closing_balance

    return render(request, 'view_details.html', {
        'invoices': invoices,
        'shop': shop
    })


# ADD INVOICE

def add_invoice(request, id):

    shop = get_object_or_404(Shop, id=id)

    invoices = Invoice.objects.filter(shop=shop).order_by('id')

    running_balance = Decimal('0.00')

    for inv in invoices:

        total = inv.weight * inv.rate

        net = total - inv.paid_amount

        running_balance += net

    previous_balance = running_balance

    if request.method == "POST":

        total = Decimal(
            request.POST.get('weight')
        ) * Decimal(
            request.POST.get('rate')
        )

        paid = Decimal(
            request.POST.get('paid_amount')
        )

        current_balance = total - paid
        
        closing = previous_balance + current_balance

        invoice = Invoice.objects.create(

    shop=shop,

    invoice_number=request.POST.get('invoice_number'),

    date=request.POST.get('date'),

    item_name=request.POST.get('item_name'),

    qty=int(request.POST.get('qty')),

    weight=Decimal(request.POST.get('weight')),

    rate=Decimal(request.POST.get('rate')),

    paid_amount=paid,

    total_amount=total,

    previous_balance=previous_balance,

    current_balance=current_balance,

    closing_balance=closing

)

        return redirect('invoice_success', id=invoice.id)

    return render(request, 'add_invoice.html', {

        'shop': shop,
        'previous_balance': previous_balance

    })


# DOWNLOAD PDF

def download_invoice(request, id):

    invoice = get_object_or_404(Invoice, id=id)

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">

        <style>

            @page {{
                margin: 15mm;
            }}

            body {{
                font-family: Arial, sans-serif;
                color: #111827;
                font-size: 12px;
            }}

            .container {{
                width: 100%;
            }}

            /* HEADER */
            .header {{
                width: 100%;
                border-bottom: 1px solid #e5e7eb;
                padding-bottom: 10px;
                margin-bottom: 20px;
            }}

            .header-table {{
                width: 100%;
            }}

            .brand {{
                font-size: 22px;
                font-weight: bold;
            }}

            .sub {{
                font-size: 12px;
                color: #6b7280;
                margin-top: 3px;
            }}

            .invoice-title {{
                text-align: right;
                font-size: 20px;
                font-weight: bold;
            }}

            .meta {{
                width: 100%;
                margin-top: 20px;
                border-collapse: collapse;
            }}

            .meta td {{
                padding: 8px;
                border: 1px solid #e5e7eb;
            }}

            .label {{
                color: #6b7280;
                width: 120px;
            }}

            /* TABLE */
            .items {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }}

            .items th {{
                background: #111827;
                color: white;
                padding: 10px;
                font-size: 11px;
            }}

            .items td {{
                padding: 10px;
                border-bottom: 1px solid #e5e7eb;
                text-align: center;
            }}

            .right {{
                text-align: right;
            }}

            /* SUMMARY */
            .summary {{
                width: 300px;
                margin-left: auto;
                margin-top: 20px;
            }}

            .summary table {{
                width: 100%;
                border-collapse: collapse;
            }}

            .summary td {{
                padding: 6px;
            }}

            .total {{
                font-size: 14px;
                font-weight: bold;
            }}

            /* FOOTER */
            .footer {{
                margin-top: 50px;
                text-align: center;
                font-size: 11px;
                color: #6b7280;
            }}

            .signature {{
                margin-top: 40px;
                text-align: right;
            }}

            .line {{
                width: 180px;
                border-top: 1px solid #111827;
                margin-left: auto;
                margin-bottom: 5px;
            }}

        </style>
    </head>

    <body>

    <div class="container">

        <!-- HEADER -->
        <div class="header">
            <table class="header-table">
                <tr>
                    <td>
                        <div class="brand">DHOST CHICKEN</div>
                        <div class="sub">Fresh Chicken Supplier</div>
                        <div class="sub">Quality & Trusted Service</div>
                    </td>

                    <td class="invoice-title">
                        INVOICE <br><br>
                        #{invoice.invoice_number} <br>
                        {invoice.date}
                    </td>
                </tr>
            </table>
        </div>

        <!-- META -->
        <table class="meta">
            <tr>
                <td class="label">Shop Name</td>
                <td>{invoice.shop.name}</td>

                <td class="label">Status</td>
                <td>
                    {"Paid" if invoice.closing_balance == 0 else "Pending"}
                </td>
            </tr>
        </table>

        <!-- ITEMS -->
        <table class="items">
            <tr>
                <th>ITEM</th>
                <th>QTY</th>
                <th>WEIGHT</th>
                <th>RATE</th>
                <th>TOTAL</th>
            </tr>

            <tr>
                <td>{invoice.item_name}</td>
                <td>{invoice.qty}</td>
                <td>{invoice.weight} Kg</td>
                <td>{invoice.rate}</td>
                <td>{invoice.total_amount}</td>
            </tr>
        </table>

        <!-- SUMMARY -->
        <div class="summary">
            <table>
    <tr>
        <td>Previous Balance</td>
        <td class="right">{invoice.previous_balance}</td>
    </tr>

    <tr>
        <td>Paid Amount</td>
        <td class="right">{invoice.paid_amount}</td>
    </tr>

    

    <tr>
        <td class="total">Closing Balance</td>
        <td class="right total">{invoice.closing_balance}</td>
    </tr>
</table>
        </div>

        <!-- SIGNATURE -->
        <div class="signature">
            <div class="line"></div>
            Authorized Signature
        </div>

        <!-- FOOTER -->
        <div class="footer">
            Thank you for your business.<br>
            DHOST CHICKEN - Fresh Quality Chicken Supply
        </div>

    </div>

    </body>
    </html>
    """

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = (
        f'attachment; filename="invoice_{invoice.invoice_number}.pdf"'
        )
    pisa.CreatePDF(html, dest=response)
    return response


def invoice_success(request, id):

    invoice = get_object_or_404(Invoice, id=id)

    return render(request, 'invoice_success.html', {
        'invoice': invoice
    })


# EDIT INVOICE

def edit_invoice(request, id):

    invoice = get_object_or_404(Invoice, id=id)

    if request.method == 'POST':

        invoice.invoice_number = request.POST.get('invoice_number')

        invoice.date = request.POST.get('date')

        invoice.item_name = request.POST.get('item_name')

        invoice.qty = int(request.POST.get('qty'))

        invoice.weight = Decimal(request.POST.get('weight'))

        invoice.rate = Decimal(request.POST.get('rate'))

        invoice.paid_amount = Decimal(request.POST.get('paid_amount'))

        invoice.save()

        return redirect('view_details', id=invoice.shop.id)

    return render(request, 'edit_invoice.html', {
        'invoice': invoice
    })





# def create_admin(request):
#     User.objects.create_superuser(
#         username='admin',
#         password='abcd3232',
#         email='shebeebk10@gmail.com'
#     )
#     return HttpResponse("Admin created")




def delete_invoice(request, id):

    invoice = get_object_or_404(Invoice, id=id)

    shop_id = invoice.shop.id

    if request.method == 'POST':

        invoice.delete()

        return redirect(
            'view_details',
            id=shop_id
        )

    return render(
        request,
        'confirm_delete.html',
        {'invoice': invoice}
    )