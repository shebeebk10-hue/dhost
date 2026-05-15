from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.template.loader import get_template

from xhtml2pdf import pisa

from .models import Invoice, Shop

from decimal import Decimal


# HOME

def home(request):
    return render(request, 'home.html')

def shops_auth(request):

    ERROR = ""

    # Your fixed password
    SECRET_PASSWORD = "1234"

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

        closing = previous_balance + total - paid

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

            closing_balance=closing

        )

        return redirect('download_invoice', id=invoice.id)

    return render(request, 'add_invoice.html', {

        'shop': shop,
        'previous_balance': previous_balance

    })


# DOWNLOAD PDF

def download_invoice(request, id):

    invoice = get_object_or_404(Invoice, id=id)

    template = get_template('invoice_pdf.html')

    html = template.render({

        'invoice': invoice

    })

    response = HttpResponse(content_type='application/pdf')

    response['Content-Disposition'] = (
        f'attachment; filename="invoice_{invoice.invoice_number}.pdf"'
    )

    pisa_status = pisa.CreatePDF(

        html,

        dest=response

    )

    if pisa_status.err:

        return HttpResponse('Error generating PDF')

    return response


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


# DELETE INVOICE

def delete_invoice(request, id):

    invoice = get_object_or_404(Invoice, id=id)

    shop_id = invoice.shop.id

    if request.method == 'POST':

        invoice.delete()

    return redirect('view_details', id=shop_id)