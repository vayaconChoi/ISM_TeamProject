from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.template import loader
from .models import Warehouse,Inventory,Fruit,Shipping
from .forms import WarehouseForm
from datetime import datetime
from users import models as user_models
from collections import defaultdict
import json


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
    user_id = request.user.id
    user_warehouses = Warehouse.objects.filter(user_id=user_id)
    inventory_data = Inventory.objects.filter(warehouse__in=user_warehouses)
    aggregated_quantities = defaultdict(int)

    for inventory in inventory_data:
        aggregated_quantities[inventory.fruit_id] += inventory.inventory_quantity

    fruit_names = {fruit.id: fruit.fruit_name for fruit in Fruit.objects.all()}
    labels = [fruit_names[fruit_id] for fruit_id in aggregated_quantities.keys()]
    quantities = [quantity for quantity in aggregated_quantities.values()]

    # JSON 형식으로 변형... 이게 뭐노... 어렵다...
    labels_json = json.dumps(labels, ensure_ascii=False)
    quantities_json = json.dumps(quantities)

    # 현재 월 가져오기
    now = datetime.now()
    current_month = now.month

    context = {
        'warehouses': user_warehouses,
        'labels_json': labels_json,
        'quantities_json': quantities_json,
        'current_month': current_month,
    }

    return render(request, 'inventory/inventory_summary.html',context)

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
    user_id = request.user.id
    user_warehouses = Warehouse.objects.filter(user_id=user_id)
    inventory_data = Inventory.objects.filter(warehouse__in=user_warehouses)
    aggregated_quantities = defaultdict(int)

    for inventory in inventory_data:
        aggregated_quantities[inventory.fruit_id] += inventory.inventory_quantity

    fruit_names = {fruit.id: fruit.fruit_name for fruit in Fruit.objects.all()}
    labels = [fruit_names[fruit_id] for fruit_id in aggregated_quantities.keys()]
    quantities = [quantity for quantity in aggregated_quantities.values()]

    # JSON 형식으로 변형... 이게 뭐노... 어렵다...
    labels_json = json.dumps(labels, ensure_ascii=False)
    quantities_json = json.dumps(quantities)

    # 현재 월 가져오기
    now = datetime.now()
    current_month = now.month

    context = {
        'warehouses': user_warehouses,
        'labels_json': labels_json,
        'quantities_json': quantities_json,
        'current_month': current_month,
    }

    return render(request, 'shipping/shipping.html', context)



def shipping_edit(request):
    return render(request, "shipping/shipping_edit.html")


def warehouse(request):
    if request.method == 'POST':
        form = WarehouseForm(request.POST)
        if form.is_valid():
            warehouse_name = form.cleaned_data['warehouse_name']
            address = form.cleaned_data['address']
            warehouse_latitude = form.cleaned_data['warehouse_latitude']
            warehouse_longitude = form.cleaned_data['warehouse_longitude']

            # Save the data to the database
            Warehouse.objects.create(
                warehouse_name=warehouse_name,
                warehouse_longitude=warehouse_longitude,
                warehouse_latitude=warehouse_latitude,
                warehouse_address=address,
                user=request.user
            )
            return redirect('warehouse')  # Redirect to a success page
    else:
        form = WarehouseForm()
    return render(request, "warehouse/warehouse.html", {'form': form})


def warehouse_detail(request):
    return render(request, "warehouse/warehouse_detail.html")


def warehouse_edit(request):
    return render(request, "warehouse/warehouse_detail_edit.html")


def recommend(request):
    return render(request, "recommend/recommend_main.html")


def recommend_detail(request):
    return render(request, "recommend/recommend_detail.html")