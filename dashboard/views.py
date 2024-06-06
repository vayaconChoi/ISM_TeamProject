from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader


from .api import kamis

def index(request):
    # 메인 페이지
    print('접속 중....')
    # 데이터 가져오기...
    retail_price = kamis.data_for_graph()
    print("소매 데이터 가져오기 성공")
    print(retail_price)

    temp = loader.get_template('index.html')
    context = {
        "retail_price": retail_price[1],
        "retail_date": retail_price[0]
    }
    return HttpResponse(temp.render(context, request))


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