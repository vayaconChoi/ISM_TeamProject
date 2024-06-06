from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader


from .api import kamis, gonggong


def index(request):
    # 메인 페이지
    print('접속 중....')
    # 소매 데이터 가져오기...
    retail_price = kamis.data_for_graph()
    print("소매 데이터 가져오기 성공")
    print(retail_price)

    # 경매 데이터 가져오기...
    # real 당일 데이터 (From AT_도매시장종합)
    auction_data = gonggong.get_live_auction()
    print("경매 데이터 가져오기 성공")
    # print(auction_data) # 다량이라 평시 주석처리

    temp = loader.get_template('index.html')
    context = {
        "retail_price": retail_price[1],
        "retail_date": retail_price[0],
        "auction_data": auction_data
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