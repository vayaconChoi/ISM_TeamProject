from django.shortcuts import render


def index(request):
    return render(request, 'index.html')


def inventory(request):
    return render(request, 'inventory/inventory_summary.html')


def inventory_details(request):
    return render(request, 'inventory/inventory_item_detail.html')


def product_setting(request):
    return render(request, 'product/product_setting.html')


def product_edit(request):
    return render(request, "product/product_edit.html")


def warehousing(request):
    return render(request, "warehousing/warehousing.html")


def warehousing_edit(request):
    return render(request, "warehousing/warehousing_edit.html")


def shipping(request):
    return render(request, "shipping/shipping.html")


def shipping_edit(request):
    return render(request, "shipping/shipping_edit.html")


def warehouse(request):
    return render(request, "warehouse/warehouse.html")


def warehouse_detail(request):
    return render(request, "warehouse/warehouse_detail.html")


def warehouse_edit(request):
    return render(request, "warehouse/warehouse_detail_edit.html")


def recommend(request):
    return render(request, "recommend/recommend_main.html")


def recommend_detail(request):
    return render(request, "recommend/recommend_detail.html")
