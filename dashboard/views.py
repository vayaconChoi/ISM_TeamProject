from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse
from dashboard.models import Fruit,Origin,Inventory,Warehousing,Shipping,Warehouse, Barcode, MLModel
from .forms import FruitForm,OriginForm,InventoryForm,WarehousingForm,ShippingForm,WarehouseForm, BarcodeForm
from datetime import datetime,timedelta
from users import models as user_models
import json
from django.utils.dateparse import parse_datetime
import numpy as np
import pandas as pd
from django.shortcuts import render
import joblib
from sklearn.preprocessing import StandardScaler
from haversine import haversine

from .api import kamis, gonggong, naver, weather


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
    print(auction_data) # 다량이라 평시 주석처리

    user_id = request.user.id
    user_warehouses = Warehouse.objects.filter(user=user_id)

    warehouse_inventory = Inventory.objects.select_related('warehouse').filter(user=user_id)
    context = {
        "retail_price": retail_price[1],
        "retail_date": retail_price[0],
        "auction_data": auction_data,
        "user_warehouses": user_warehouses,
        "warehouse_inventory": warehouse_inventory
    }
    return render(request, 'index.html', context)

def inventory(request):
    user_id = request.user.id
    warehouses = Warehouse.objects.filter(user_id=user_id).select_related()
    user_warehouses = Warehouse.objects.filter(user_id=user_id)
    inventory_data = Inventory.objects.filter(warehouse__in=user_warehouses)
    aggregated_quantities = {
        '사과상품': 0,
        '사과중품': 0,
        '배상품': 0,
        '배중품': 0,

    }

    for inventory in inventory_data:
        # inventory에 있는 바코드로 해당 product 찾기
        print(inventory.barcode)
        prod_name = str(Barcode.objects.get(barcode_id=inventory.barcode).fruit)
        print(prod_name)
        aggregated_quantities[prod_name] += inventory.inventory_quantity

    quantity_list = [aggregated_quantities['사과상품'],aggregated_quantities['사과중품'], aggregated_quantities['배상품'],aggregated_quantities['배중품']]
    print(quantity_list)

    # JSON 형식으로 변형
    quantities_json = json.dumps(quantity_list)

    warehouse_inventory = Inventory.objects.select_related('warehouse').filter(user=user_id)
    print(warehouse_inventory)

    context = {
        'warehouses' : warehouses,
        'user_warehouses': user_warehouses,
        'inventory_data': inventory_data,
        'quantities_json': quantities_json,
        'warehouse_inventory': warehouse_inventory
    }

    return render(request, 'inventory/inventory_summary.html',context)

def inventory_details(request,inventory_id):
    user_id = request.user.id
    inventories = Inventory.objects.get(inventory_id=inventory_id, user=user_id)

    product_name = str(inventories.barcode.fruit)
    print(product_name)
    # 소매 데이터 가져오기...
    retail_price = kamis.data_for_graph(product_name)
    print("소매 데이터 가져오기 성공")
    print(retail_price)

    context = {
        "inventories":inventories,
        "retail_price": retail_price[1],
        "retail_date": retail_price[0],

    }
    return render(request, 'inventory/inventory_item_detail.html',context)

def product_setting(request):
    user_id = request.user.id
    form = BarcodeForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            barcode = form.save(commit=False)
            barcode.user_id = user_id
            barcode.save()
            return redirect('product_setting')

    fruits = Fruit.objects.all()
    barcodes = Barcode.objects.filter(user_id=user_id)
    origins = Origin.objects.all()
    context = {
        'form': form,
        'barcodes': barcodes,
        'fruits': fruits,
        'origins': origins
    }
    return render(request, 'product/product_setting.html', context)

def product_edit(request, barcode_id):
    user_id = request.user.id
    barcode = get_object_or_404(Barcode, barcode_id=barcode_id)
    barcodes = Barcode.objects.get(barcode_id=barcode_id, user_id=user_id)

    if request.method == 'POST':
        form = BarcodeForm(request.POST, instance=barcode)
        if form.is_valid():
            barcode = form.save(commit=False)
            barcode.user_id = user_id
            barcodes.delete()
            barcode.save()
            return redirect('product_setting')
    else:
        form = BarcodeForm(instance=barcode)

    fruits = Fruit.objects.all()
    origins = Origin.objects.all()

    context = {
        'form': form,
        'fruits': fruits,
        'origins': origins,
    }
    return render(request, 'product/product_edit.html', context)

def product_delete(request,barcode_id):
    user_id = request.user.id
    barcodes = Barcode.objects.get(barcode_id=barcode_id, user=user_id)
    if request.method == 'POST':
        barcodes.delete()
        return redirect('product_setting')
    return render(request, "product/product_delete_confirm.html", {'barcodes': barcodes, 'user': user_id})

def warehousing(request):
    user_id = request.user.id

    warehouses = Warehouse.objects.filter(user_id=user_id).select_related()
    warehousings = Warehousing.objects.filter(user=user_id)

    # 초반 form에서 받아오는 바코드임
    barcode = request.POST.get('barcode')
    # 이 바코드 가지고, 원산지와 상품명을 받아와야 함
    barcode_info = {}
    if barcode:
        barcode_info = Barcode.objects.get(barcode_id=barcode)

    # 파이차트를 위한 데이터 끌어 모으기
    aggregated_quantities = {
        '사과상품': 0,
        '사과중품': 0,
        '배상품': 0,
        '배중품': 0,

    }
    for 입고 in warehousings:
        print(입고.barcode)
        print(입고.warehousing_quantity)
        # inventory에 해당하는 product 찾기
        prod_name = str(Barcode.objects.get(barcode_id=입고.barcode).fruit)
        print(prod_name)
        aggregated_quantities[prod_name] = aggregated_quantities[prod_name] + 입고.warehousing_quantity


    quantity_list = [aggregated_quantities['사과상품'],aggregated_quantities['사과중품'], aggregated_quantities['배상품'],aggregated_quantities['배중품']]
    print(quantity_list)

    # form 진행
    form = WarehousingForm(user_id, request.POST or  None)

    if request.method == 'POST':
        if form.is_valid():
            warehousing = form.save(commit=False)
            warehousing.user_id = user_id
            warehousing.save()
            plus_inventory(warehousing)
            put_warehousing_until(warehousing)
            return redirect('warehousing')
    else:
        form = WarehousingForm(user_id)

    context = {
        'warehouses': warehouses,
        'quantity_list': quantity_list,
        'warehousings': warehousings,
        'form': form,
        'barcode': barcode,
        'barcode_info': barcode_info,
    }
    return render(request, "warehousing/warehousing.html",context)

def plus_inventory(instance, **kwargs):
    try:
        inventory = Inventory.objects.get(
            warehouse=instance.warehouse,
            barcode=instance.barcode,
            user=instance.user
        )
        inventory.inventory_quantity += instance.warehousing_quantity
        inventory.save()
    except Inventory.DoesNotExist:
        Inventory.objects.create(
            warehouse=instance.warehouse,
            barcode=instance.barcode,
            user=instance.user,
            inventory_quantity=instance.warehousing_quantity
        )

def minus_inventory(instance, **kwargs):
    try:
        inventory = Inventory.objects.get(
            warehouse=instance.warehouse,
            barcode=instance.barcode,
            user=instance.user
        )
        if inventory.inventory_quantity >= instance.Shipping_quantity:
            inventory.inventory_quantity -= instance.Shipping_quantity
            inventory.save()
        else:
            raise ValueError(f"재고가 부족합니다. 현재 재고: {inventory.inventory_quantity}, 출고 수량: {instance.shipping_quantity}")
    except Inventory.DoesNotExist:
        raise ValueError("재고 정보가 존재하지 않습니다.")

def put_warehousing_until(instance,**kwargs):
    instance.warehousing_until = instance.warehousing_time + timedelta(days = instance.barcode.fruit.fruit_day_plus)
    instance.save()

def warehousing_edit(request, warehousing_id):
    user_id = request.user.id
    try:
        warehousing = Warehousing.objects.get(warehousing_id=warehousing_id, user=user_id)
    except Warehousing.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'POST':
        form = WarehousingForm(user_id, request.POST, instance=warehousing)
        if form.is_valid():
            form.save()
            barcode = warehousing.barcode.barcode_id
            warehouse_id = warehousing.warehouse.warehouse_id
            inventory = Inventory.objects.get(user_id=user_id, barcode=barcode, warehouse_id=warehouse_id)
            shipping_delta = Shipping.objects.filter(user_id=user_id, barcode=barcode, warehouse_id=warehouse_id)
            warehousing_delta = Warehousing.objects.filter(user_id=user_id, barcode=barcode, warehouse_id=warehouse_id)

            quantity = 0
            for i in warehousing_delta:
                quantity += i.warehousing_quantity
            for i in shipping_delta:
                quantity -= i.Shipping_quantity
            inventory.inventory_quantity = quantity
            inventory.save()
            return redirect('warehousing')
    else:
        form = WarehousingForm(user_id, instance=warehousing, initial={'warehousing_id': warehousing.warehousing_id})

    warehousings = Warehousing.objects.filter(user=user_id)
    warehouses = Warehouse.objects.filter(user=user_id)
    context = {
        'form': form,
        'warehousing': warehousing,
        'warehousings': warehousings,
        'warehouses': warehouses
    }
    return render(request, 'warehousing/warehousing_edit.html', context)

def warehouseing_delete(request,warehousing_id):
    user = request.user
    warehousings = Warehousing.objects.get(warehousing_id=warehousing_id, user=user)
    if request.method == 'POST':
        warehousings.delete()
        barcode = warehousings.barcode.barcode_id
        warehouse_id = warehousings.warehouse.warehouse_id
        inventory = Inventory.objects.get(user_id=user, barcode=barcode, warehouse_id=warehouse_id)
        shipping_delta = Shipping.objects.filter(user_id=user, barcode=barcode, warehouse_id=warehouse_id)
        warehousing_delta = Warehousing.objects.filter(user_id=user, barcode=barcode, warehouse_id=warehouse_id)

        quantity = 0
        for i in warehousing_delta:
            quantity += i.warehousing_quantity
        for i in shipping_delta:
            quantity -= i.Shipping_quantity
        inventory.inventory_quantity = quantity
        inventory.save()
        return redirect('warehousing')
    return render(request,"warehousing/warehousing_delete_confirm.html",{'warehousings':warehousings,'user':user})

def shipping(request):
    user_id = request.user.id

    warehouses = Warehouse.objects.filter(user_id=user_id)
    inventory_data = Inventory.objects.filter(warehouse__in=warehouses)

    shippings = Shipping.objects.filter(user_id=user_id)

    # 초반 form에서 받아오는 바코드임
    barcode = request.POST.get('barcode')
    # 이 바코드 가지고, 원산지와 상품명을 받아와야 함
    barcode_info ={}
    if barcode:
        barcode_info = Barcode.objects.get(barcode_id=barcode)

    # 파이차트를 위한 데이터 끌어 모으기
    aggregated_quantities = {
        '사과상품': 0,
        '사과중품': 0,
        '배상품': 0,
        '배중품': 0,

    }

    for 출고 in shippings:
        print(출고.barcode)
        print(출고.Shipping_quantity)
        # inventory에 해당하는 product 찾기
        prod_name = str(Barcode.objects.get(barcode_id=출고.barcode).fruit)
        print(prod_name)
        aggregated_quantities[prod_name] = aggregated_quantities[prod_name] + 출고.Shipping_quantity

    quantity_list = [aggregated_quantities['사과상품'],aggregated_quantities['사과중품'], aggregated_quantities['배상품'],aggregated_quantities['배중품']]
    print(quantity_list)

    #form 진행
    form = ShippingForm(user_id, request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            shipping = form.save(commit=False)
            shipping.user_id = user_id
            shipping.save()
            minus_inventory(shipping)
            return redirect('shipping')
    else:
        form = ShippingForm(user_id)


    context = {
        'warehouses': warehouses,
        'quantity_list': quantity_list,
        'shippings': shippings,
        'form': form,
        'barcode': barcode,
        'barcode_info': barcode_info,
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
            barcode = shipping.barcode.barcode_id
            warehouse_id = shipping.warehouse.warehouse_id
            inventory = Inventory.objects.get(user_id=user_id, barcode=barcode, warehouse_id=warehouse_id)
            shipping_delta = Shipping.objects.filter(user_id=user_id, barcode=barcode, warehouse_id=warehouse_id)
            warehousing_delta = Warehousing.objects.filter(user_id=user_id, barcode=barcode, warehouse_id=warehouse_id)

            quantity = 0
            for i in warehousing_delta:
                quantity += i.warehousing_quantity
            for i in shipping_delta:
                quantity -= i.Shipping_quantity
            inventory.inventory_quantity = quantity
            inventory.save()
            return redirect('shipping')
    else:
        form = ShippingForm(user_id, instance=shipping, initial={'shipping_id': shipping.shipping_id})

    shippings = Shipping.objects.filter(user_id=user_id)
    warehouses = Warehouse.objects.filter(user_id=user_id)
    context = {
        'form': form,
        'shippings': shippings,
        'warehouses': warehouses,
        'shipping':shipping
    }
    return render(request, 'shipping/shipping_edit.html', context)

def shipping_delete(request,shipping_id):
    user_id = request.user.id
    shippings = Shipping.objects.get(shipping_id=shipping_id, user_id=user_id)
    if request.method == 'POST':
        shippings.delete()
        barcode = shippings.barcode.barcode_id
        warehouse_id = shippings.warehouse.warehouse_id
        inventory = Inventory.objects.get(user_id=user_id, barcode=barcode, warehouse_id=warehouse_id)
        shipping_delta = Shipping.objects.filter(user_id=user_id, barcode=barcode, warehouse_id=warehouse_id)
        warehousing_delta = Warehousing.objects.filter(user_id=user_id, barcode=barcode, warehouse_id=warehouse_id)

        quantity = 0
        for i in warehousing_delta:
            quantity += i.warehousing_quantity
        for i in shipping_delta:
            quantity -= i.Shipping_quantity
        inventory.inventory_quantity = quantity
        inventory.save()
        return redirect('shipping')
    return render(request,"shipping/shipping_delete_confirm.html",{'shippings':shippings,'user':user_id})


def warehouse(request):
    user_id = request.user.id
    user_warehouses = Warehouse.objects.filter(user_id=user_id)

    if request.method == 'POST':
        form = WarehouseForm(user_id, request.POST)
        if form.is_valid():
            warehouse = form.save(commit=False)
            warehouse.warehouse_latitude = request.POST.get('warehouse_latitude')
            warehouse.warehouse_longitude = request.POST.get('warehouse_longitude')
            warehouse.user_id = user_id
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
    warehouses = Warehouse.objects.get(warehouse_id=warehouse_id)
    warehousings = Warehousing.objects.filter(user_id = request.user.id,warehouse_id = warehouse_id)
    inventories = Inventory.objects.select_related('barcode').filter(warehouse_id=warehouse_id)

    # 재고량 PieChart 데이터
    quantity_list = [0, 0, 0,0]
    for i in inventories:
        print(i.inventory_quantity)
        if str(i.barcode.fruit.fruit_name) == "사과상품":
            quantity_list[0] += i.inventory_quantity
        elif str(i.barcode.fruit_id) == "사과중품":
            quantity_list[1] += i.inventory_quantity
        elif str(i.barcode.fruit_id) == "배상품":
            quantity_list[2] += i.inventory_quantity
        else:
            quantity_list[3] += i.inventory_quantity


    context = {
        'warehouse': warehouses,
        'warehousings' : warehousings,
        'quantity_list' : quantity_list
    }
    return render(request, "warehouse/warehouse_detail.html", context)


def warehouse_edit(request,warehouse_id):
    user_id = request.user.id
    try:
        warehouse = Warehouse.objects.get(warehouse_id=warehouse_id, user_id=user_id)
    except Warehouse.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'POST':
        form = WarehouseForm(user_id, request.POST, instance=warehouse)
        if form.is_valid():
            warehouse = form.save(commit=False)
            warehouse.warehouse_latitude = request.POST.get('warehouse_latitude')
            warehouse.warehouse_longitude = request.POST.get('warehouse_longitude')
            warehouse.user_id = user_id
            warehouse.save()
            return redirect("warehouse")
    else:
        form = WarehouseForm(user_id, instance=warehouse, initial={'warehouse_id': warehouse_id})
    warehouses = Warehouse.objects.filter(user_id=user_id)
    context = {
        'form': form,
        'warehouses': warehouses,
    }
    return render(request, 'warehouse/warehouse_detail_edit.html', context)

def warehouse_delete(request,warehouse_id):
    user_id = request.user.id
    Warehouses = Warehouse.objects.get(warehouse_id=warehouse_id, user_id=user_id)
    if request.method == 'POST':
        Warehouses.delete()
        return redirect('warehouse')
    context = {
        'Warehouses': Warehouses,
        'user': user_id,
    }
    return render(request, "warehouse/warehouse_delete_confirm.html", context)



def origin_setting(request):
    form = OriginForm(request.POST or None)
    origins = Origin.objects.all()
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('origin_setting')
    return render(request, 'origin/origin_setting.html', {'form':form,'origins':origins})

def origin_delete(request,origin_id):
    origins = Origin.objects.get(origin_id=origin_id)
    if request.method == 'POST':
        origins.delete()
        return redirect('origin_setting')
    return render(request, "origin/origin_delete_confirm.html", {'origins': origins})

# dashboard/views.py

def origin_edit(request, origin_id):
    try:
        origin = Origin.objects.get(origin_id=origin_id)
    except Origin.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'POST':
        form = OriginForm(request.POST, instance=origin)
        if form.is_valid():
            origins = form.save(commit=False)
            origins.origin_latitude = request.POST.get('origin_latitude')
            origins.origin_longitude = request.POST.get('origin_longitude')
            origins.save()
            return redirect("origin_setting")
    else:
        form = OriginForm(instance=origin)
    origins = Origin.objects.get(origin_id = origin_id)
    context = {
        'form': form,
        'origins': origins,
    }
    return render(request, 'origin/origin_edit.html', context)


def recommend(request):
    try:
        # 디버깅 시작
        print("Starting recommend view")

        # 데이터 로드
        naver_df = naver.get_naver_api()
        weather_df = weather.weather_for_ML(90)
        print("Data loaded successfully")

        # 버튼 클릭 후에 결과가 보이도록
        button_clicked = False

        if request.method == "POST":
            button_clicked = True

        # 스케일러 로드
        scaler_instance = MLModel.objects.get(name="SScaler")
        scaler = joblib.load(scaler_instance.model_file.path)
        print("Scaler loaded successfully")

        # 데이터 프레임 병합 및 스케일링
        combined_df = pd.concat([weather_df, naver_df], axis=1).fillna(0)
        combined_df.reset_index(drop=True, inplace=True)
        scaled_data = scaler.transform(combined_df)
        scaled_df = pd.DataFrame(scaled_data, columns=combined_df.columns)
        print("Data merged and scaled successfully")

        # 최근 데이터 추출
        recent_30_days = scaled_df.head(30).reset_index(drop=True)
        recent_60_days = scaled_df.head(60).reset_index(drop=True)
        recent_90_days = scaled_df.head(90).reset_index(drop=True)

        # 모델 로드
        pear_high = MLModel.objects.get(name="pear_high")
        pear_mid = MLModel.objects.get(name="pear_mid")
        apple_high = MLModel.objects.get(name="apple_high")
        apple_mid = MLModel.objects.get(name="apple_mid")

        pear_high_model = joblib.load(pear_high.model_file.path)
        pear_mid_model = joblib.load(pear_mid.model_file.path)
        apple_high_model = joblib.load(apple_high.model_file.path)
        apple_mid_model = joblib.load(apple_mid.model_file.path)
        print("Models loaded successfully")

        # 예측
        prediction_pear_high_10 = int(pear_high_model.predict(recent_30_days)[-1])
        prediction_pear_high_20 = int(pear_high_model.predict(recent_60_days)[-1])
        prediction_pear_high_30 = int(pear_high_model.predict(recent_90_days)[-1])
        prediction_pear_mid_10 = int(pear_mid_model.predict(recent_30_days)[-1])
        prediction_pear_mid_20 = int(pear_mid_model.predict(recent_60_days)[-1])
        prediction_pear_mid_30 = int(pear_mid_model.predict(recent_90_days)[-1])
        prediction_apple_high_10 = int(apple_high_model.predict(recent_30_days)[-1])
        prediction_apple_high_20 = int(apple_high_model.predict(recent_60_days)[-1])
        prediction_apple_high_30 = int(apple_high_model.predict(recent_90_days)[-1])
        prediction_apple_mid_10 = int(apple_mid_model.predict(recent_30_days)[-1])
        prediction_apple_mid_20 = int(apple_mid_model.predict(recent_60_days)[-1])
        prediction_apple_mid_30 = int(apple_mid_model.predict(recent_90_days)[-1])
        print("Predictions made successfully")

        # 거리 계산
        user_id = request.user.id
        dist = {}
        barcodes = Barcode.objects.all()
        warehouses = Warehouse.objects.all()

        for barcode in barcodes:
            for warehouse in warehouses:
                try:
                    origin_latitude = float(barcode.origin.origin_latitude)
                    origin_longitude = float(barcode.origin.origin_longitude)
                    warehouse_latitude = float(warehouse.warehouse_latitude)
                    warehouse_longitude = float(warehouse.warehouse_longitude)

                    distance = calculate_distance(
                        origin_latitude,
                        origin_longitude,
                        warehouse_latitude,
                        warehouse_longitude
                    )

                    if barcode.fruit.fruit_name in ['사과상품', '사과중품']:
                        coordinate_apple = (
                            barcode.fruit.fruit_name,
                            barcode.origin.origin_location,
                            warehouse.warehouse_name
                        )
                        dist[coordinate_apple] = distance
                    else:
                        coordinate_pear = (
                            barcode.fruit.fruit_name,
                            barcode.origin.origin_location,
                            warehouse.warehouse_name
                        )
                        dist[coordinate_pear] = distance
                except ValueError:
                    continue

        nearest_apple, nearest_apple_distance, nearest_apple_origin, nearest_pear, nearest_pear_distance, nearest_pear_origin = find_nearest_warehouses(dist)
        print("Distance calculations done successfully")

        # 컨텍스트 생성
        context = {
            'button_clicked': button_clicked,
            'pear_high_10': prediction_pear_high_10,
            'pear_high_20': prediction_pear_high_20,
            'pear_high_30': prediction_pear_high_30,
            'pear_mid_10': prediction_pear_mid_10,
            'pear_mid_20': prediction_pear_mid_20,
            'pear_mid_30': prediction_pear_mid_30,
            'apple_high_10': prediction_apple_high_10,
            'apple_high_20': prediction_apple_high_20,
            'apple_high_30': prediction_apple_high_30,
            'apple_mid_10': prediction_apple_mid_10,
            'apple_mid_20': prediction_apple_mid_20,
            'apple_mid_30': prediction_apple_mid_30,
            'nearest_apple': nearest_apple,
            'nearest_apple_distance': nearest_apple_distance,
            'nearest_apple_origin': nearest_apple_origin,
            'nearest_pear_distance': nearest_pear_distance,
            'nearest_pear_origin': nearest_pear_origin,
            'nearest_pear': nearest_pear,
        }
        print("Context prepared successfully")

        return render(request, "recommend/recommend_main.html", context)
    except Exception as e:
        print(f"Error: {e}")
        return render(request, "recommend/recommend_main.html", {'error': str(e)})

def calculate_distance(origin_latitude, origin_longitude, warehouse_latitude, warehouse_longitude):
    origin_coordinate = (origin_latitude, origin_longitude)
    warehouse_coordinate = (warehouse_latitude, warehouse_longitude)
    distance = haversine(origin_coordinate, warehouse_coordinate, unit='km')
    return distance


def find_nearest_warehouses(dist):
    nearest_apple = None
    nearest_apple_distance = float('inf')
    nearest_apple_origin = None
    nearest_pear = None
    nearest_pear_distance = float('inf')
    nearest_pear_origin = None

    for coordinate, distance in dist.items():
        if coordinate[0] in ['사과상품', '사과중품']:
            if distance < nearest_apple_distance:
                nearest_apple = coordinate[0]
                nearest_apple_distance = distance
                nearest_apple_origin = coordinate[1]
        else:
            if distance < nearest_pear_distance:
                nearest_pear = coordinate[0]
                nearest_pear_distance = distance
                nearest_pear_origin = coordinate[1]

    return nearest_apple, nearest_apple_distance, nearest_apple_origin, nearest_pear, nearest_pear_distance, nearest_pear_origin

def recommend_detail(request):
    return render(request, "recommend/recommend_detail.html")

