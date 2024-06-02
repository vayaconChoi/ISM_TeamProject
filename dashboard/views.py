from django.shortcuts import render


def index(request):
    return render(request, 'index.html')


def inventory(request):
    return render(request, 'inventory/inventory_summary.html')

def inventory_details(request):
    return render(request, 'inventory/inventory_item_detail.html')

