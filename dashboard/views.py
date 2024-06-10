from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse
from django.template import loader
from .models import Fruit,Origin,Inventory,Warehousing,Shipping,Warehouse, Barcode
from .forms import FruitForm,OriginForm,InventoryForm,WarehousingForm,ShippingForm,WarehouseForm, BarcodeForm
from datetime import datetime
from django.contrib import messages
from users import models as user_models
from collections import defaultdict
import json
from django.utils.dateparse import parse_datetime

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
    # auction_data = gonggong.get_live_auction()
    print("경매 데이터 가져오기 성공")
    # print(auction_data) # 다량이라 평시 주석처리

    user_id = request.user.id
    user_warehouses = Warehouse.objects.filter(user=user_id)

    temp = loader.get_template('index.html')
    context = {
        "retail_price": retail_price[1],
        "retail_date": retail_price[0],
        # "auction_data": auction_data,
        "warehouses" : user_warehouses
    }
    return HttpResponse(temp.render(context, request))

def inventory(request):
    user_id = request.user.id
    warehouses = Warehouse.objects.filter(user_id=user_id).select_related()
    user_warehouses = Warehouse.objects.filter(user_id=user_id)
    inventory_data = Inventory.objects.filter(warehouse__in=user_warehouses)
    # inventories = Inventory.objects.all()
    aggregated_quantities = defaultdict(int)

    for inventory in inventory_data:
        aggregated_quantities[inventory.fruit_id] += inventory.inventory_quantity

    fruit_names = {fruit.fruit_id: fruit.fruit_name for fruit in Fruit.objects.all()}
    labels = [fruit_names[fruit_id] for fruit_id in aggregated_quantities.keys()]
    quantities = [quantity for quantity in aggregated_quantities.values()]

    # JSON 형식으로 변형... 이게 뭐노... 어렵다...
    labels_json = json.dumps(labels, ensure_ascii=False)
    quantities_json = json.dumps(quantities)

    # 현재 월 가져오기
    now = datetime.now()
    current_month = now.month

    context = {
        'warehouses' : warehouses,
        'user_warehouses': user_warehouses,
        'labels_json': labels_json,
        'quantities_json': quantities_json,
        'current_month': current_month,
        # 'inventories': inventories,
    }

    return render(request, 'inventory/inventory_summary.html',context)

def inventory_details(request):
    user_id = request.user.id
    inventories = Inventory.objects.get(id=user_id)
    context = {
        "inventories":inventories,
    }
    return render(request, 'inventory/inventory_item_detail.html',context)

def product_setting(request):


    return render(request, 'product/product_setting.html')

def product_edit(request):
    return render(request, "product/product_edit.html")

def warehousing(request):
    user_id = request.user.id
    warehouses = Warehouse.objects.filter(user_id=user_id).select_related()
    user_warehouses = Warehouse.objects.filter(user_id=user_id)
    inventory_data = Inventory.objects.filter(warehouse__in=user_warehouses)
    warehousings = Warehouse.objects.filter(user_id=user_id)
    aggregated_quantities = defaultdict(int)



    for inventory in inventory_data:
        aggregated_quantities[inventory.fruit_id] += inventory.inventory_quantity

    fruit_names = {fruit.fruit_id: fruit.fruit_name for fruit in Fruit.objects.all()}
    labels = [fruit_names[fruit_id] for fruit_id in aggregated_quantities.keys()]
    quantities = [quantity for quantity in aggregated_quantities.values()]

    # JSON 형식으로 변형... 이게 뭐노... 어렵다...
    labels_json = json.dumps(labels, ensure_ascii=False)
    quantities_json = json.dumps(quantities)

    # 현재 월 가져오기
    now = datetime.now()
    current_month = now.month

    # form 진행
    form = WarehousingForm(user_id, request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            warehousing = form.save(commit=False)
            warehousing.user_id = user_id
            warehousing.save()
            return redirect('warehousing')
    else:
        form = WarehousingForm(user_id)

    context = {
        'warehouses': warehouses,
        'user_warehouses': user_warehouses,
        'labels_json': labels_json,
        'quantities_json': quantities_json,
        'current_month': current_month,
        'warehousings':warehousings,
        'form':form,
    }
    return render(request, "warehousing/warehousing.html",context)

def warehousing_edit(request):
    user_id = request.user.id
    try:
        warehousing = Warehousing.objects.get(warehousing_id=warehousing_id, user_id=user_id)
    except Warehousing.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'POST':
        form = WarehousingForm(user_id, request.POST, instance=warehousing)
        if form.is_valid():
            form.save()
            return redirect('warehousing')
    else:
        form = WarehousingForm(user_id, instance=warehousing, initial={'warehousing_id': warehousing.warehousing_id})

    warehousings = Warehousing.objects.filter(user_id=user_id)
    warehouses = Warehouse.objects.filter(user_id=user_id)
    context = {
        'form': form,
        'warehousings': warehousings,
        'warehouses': warehouses
    }
    return render(request, 'warehousing/warehousing_edit.html', context)

def shipping(request):
    user_id = request.user.id
    user_warehouses = Warehouse.objects.filter(user_id=user_id)
    inventory_data = Inventory.objects.filter(warehouse__in=user_warehouses)
    aggregated_quantities = defaultdict(int)
    shippingments = Shipping.objects.filter(warehouse__in=user_warehouses).select_related('barcode__fruit')
    # barcode_id = Shipping.objects.filter()
    for inventory in inventory_data:
        aggregated_quantities[inventory.fruit_id] += inventory.inventory_quantity

    fruit_names = {fruit.fruit_id: fruit.fruit_name for fruit in Fruit.objects.all()}
    labels = [fruit_names[fruit_id] for fruit_id in aggregated_quantities.keys()]
    quantities = [quantity for quantity in aggregated_quantities.values()]

    # JSON 형식으로 변형... 이게 뭐노... 어렵다...
    labels_json = json.dumps(labels, ensure_ascii=False)
    quantities_json = json.dumps(quantities)

    # 현재 월 가져오기
    now = datetime.now()
    current_month = now.month

    #form 진행
    form = ShippingForm(user_id, request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            shipping = form.save(commit=False)
            shipping.user_id = user_id
            shipping.save()
            return redirect('shipping')
    else:
        form = ShippingForm(user_id)

    shippings = Shipping.objects.filter(user_id=user_id)
    warehouses = Warehouse.objects.filter(user_id=user_id)


    context = {
        'form': form,
        'warehouses': user_warehouses,
        'labels_json': labels_json,
        'quantities_json': quantities_json,
        'current_month': current_month,
        'shippings': shippings,
        'shippingments': shippingments,
    }

    return render(request, 'shipping/shipping.html', context)



def shipping_edit(request,shipping_id):
    user_id = request.user.id
    try:
        shipping = Shipping.objects.get(shipping_id = shipping_id, user_id=user_id)
    except Shipping.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'POST':
        form = ShippingForm(user_id, request.POST, instance=shipping)
        if form.is_valid():
            form.save()
            return redirect('shipping')
    else:
        form = ShippingForm(user_id, instance=shipping, initial={'shipping_id': shipping.shipping_id})

    shippings = Shipping.objects.filter(user_id=user_id)
    warehouses = Warehouse.objects.filter(user_id=user_id)
    context = {
        'form': form,
        'shippings': shippings,
        'warehouses': warehouses
    }
    return render(request, 'shipping/shipping_edit.html', context)

def shipping_delete(request,shipping_id):
    user_id = request.user.id
    shippings = Shipping.objects.get(shipping_id=shipping_id, user_id=user_id)
    if request.method == 'POST':
        shippings.delete()
        return redirect('shipping')
    return render(request,"shipping/shipping_delete_confirm.html",{'shippings':shippings,'user':user_id})

def warehouse(request):
    user_id = request.user.id
    user_warehouses = Warehouse.objects.filter(user_id=user_id)

    if request.method == 'POST':
        form = WarehouseForm(user_id, request.POST)
        if form.is_valid():
            warehouse = form.save(commit=False)
            warehouse.user_id = user.id
            warehouse.save()
            return redirect('warehouse')
    else:
        form = WarehouseForm(user_id)
        context = {
            'form': form,
            'warehouses': user_warehouses
        }
        return render(request, "warehouse/warehouse.html", context)


def warehouse_detail(request,warehouse_id):
    warehouses = Warehouse.objects.get(id=id)
    form = WarehouseForm(request.POST or None, instance=warehouses)
    return render(request, "warehouse/warehouse_detail.html", {'form': form,'warehouse': warehouses})


def warehouse_edit(request):
    warehouses = Warehouse.objects.get(id=id)
    form = WarehouseForm(request.POST or None, instance = warehouses)
    if form.is_valid():
        form.save()
        return redirect('warehouse')
    return render(request, "warehouse/warehouse_detail_edit.html")

def warehouse_delete(request,warehouse_id):
    user_id = request.user.id
    Warehouses = Warehouse.objects.get(warehouse_id=warehouse_id, user_id=user_id)
    if request.method == 'POST':
        Warehouses.delete()
        return redirect('warehousing')
    context = {
        'Warehouses': Warehouses,
        'user': user_id,
    }
    return render(request, "warehousing/warehousing_delete_confirm.html", context)

def recommend(request):
    return render(request, "recommend/recommend_main.html")


def recommend_detail(request):
    return render(request, "recommend/recommend_detail.html")