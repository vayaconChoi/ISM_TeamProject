from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse
from .models import Fruit,Origin,Inventory,Warehousing,Shipping,Warehouse, Barcode, MLModel
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


from .api import kamis, gonggong,naver,weather


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

    context = {
        "retail_price": retail_price[1],
        "retail_date": retail_price[0],
        # "auction_data": auction_data,
        "warehouses": user_warehouses,
    }
    return render(request, 'index.html', context)

def inventory(request):
    user_id = request.user.id
    warehouses = Warehouse.objects.filter(user_id=user_id).select_related()
    user_warehouses = Warehouse.objects.filter(user_id=user_id)
    inventory_data = Inventory.objects.filter(warehouse__in=user_warehouses)
    aggregated_quantities = {
        '사과':0,
        '배':0
    }


    for inventory in inventory_data:
        # inventory에 있는 바코드로 해당 product 찾기
        print(inventory.barcode)
        prod_name = str(Barcode.objects.get(barcode_id=inventory.barcode).fruit)
        print(prod_name)
        aggregated_quantities[prod_name] += inventory.inventory_quantity

    quantities = [aggregated_quantities["사과"], aggregated_quantities["배"]]
    print(quantities)

    # JSON 형식으로 변형
    quantities_json = json.dumps(quantities)

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
    context = {
        "inventories":inventories,
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
    barcode_info ={}
    if barcode:
        barcode_info = Barcode.objects.get(barcode_id=barcode)

    # 파이차트를 위한 데이터 끌어 모으기
    aggregated_quantities = {
        '사과': 0,
        '배': 0
    }
    for 입고 in warehousings:
        print(입고.barcode)
        print(입고.warehousing_quantity)
        # inventory에 해당하는 product 찾기
        prod_name = str(Barcode.objects.get(barcode_id=입고.barcode).fruit)
        print(prod_name)
        aggregated_quantities[prod_name] = aggregated_quantities[prod_name] + 입고.warehousing_quantity


    quantity_list = [aggregated_quantities['사과'], aggregated_quantities['배']]
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
            return redirect('warehousing')
    else:
        form = WarehousingForm(user_id, instance=warehousing, initial={'warehousing_id': warehousing.warehousing_id})

    warehousings = Warehousing.objects.filter(user=user_id)
    warehouses = Warehouse.objects.filter(user=user_id)
    context = {
        'form': form,
        'warehousings': warehousings,
        'warehouses': warehouses
    }
    return render(request, 'warehousing/warehousing_edit.html', context)

def warehouseing_delete(request,warehousing_id):
    user = request.user
    warehousings = Warehousing.objects.get(warehousing_id=warehousing_id, user=user)
    if request.method == 'POST':
        warehousings.delete()
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
        '사과': 0,
        '배': 0
    }

    for 출고 in shippings:
        print(출고.barcode)
        print(출고.Shipping_quantity)
        # inventory에 해당하는 product 찾기
        prod_name = str(Barcode.objects.get(barcode_id=출고.barcode).fruit)
        print(prod_name)
        aggregated_quantities[prod_name] = aggregated_quantities[prod_name] + 출고.Shipping_quantity

    quantity_list = [aggregated_quantities['사과'], aggregated_quantities['배']]
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
    context = {
        'warehouse': warehouses,
        'warehousings' : warehousings
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

def load_model(model_path):
    return joblib.load(model_path)

def make_prediction(X,y):
    return model.predict(X,y)

def recommend(request):
    naver_df = naver.get_naver_api()
    weather_df = weather.weather_for_ML(90)

    # scaler_instance = MLModel.objects.get(name="SScaler")
    # scaler = load_model(scaler_instance.model_file.path)

    # 두 데이터프레임을 합침
    combined_df = pd.concat([weather_df,naver_df], axis=1)
    combined_df.reset_index(drop=True,inplace=True)
    combined_df.rename(columns={'평균기온':'평균기온',"평균풍속":"평균풍속","배 검색량":"배 검색량","사과 검색량":"사과 검색량"}, inplace=True)

    def create_dataset(X, time_steps=30, future_step=10):
        Xs = []
        for i in range(len(X) - time_steps - future_step + 1):
            Xs.append(X[i:(i + time_steps)].values.flatten())

        return np.array(Xs)

    X_train = create_dataset(combined_df)

    # scaled_df = scaler.transform(combined_df)
    # scaled_df.drop('index', axis=1, inplace=True)

    # 최근 30일, 최근 60일, 최근 90일 데이터프레임 생성
    recent_30_days = create_dataset(combined_df,30,10)
    recent_60_days = create_dataset(combined_df,60,20)
    recent_90_days = create_dataset(combined_df,90,30)

    # Load Random Forest model
    pear_high_10_instance = MLModel.objects.get(name="pear_high_10")
    pear_high_10 = load_model(pear_high_10_instance.model_file.path)

    pear_high_20_instance = MLModel.objects.get(name="pear_high_20")
    pear_high_20 = load_model(pear_high_20_instance.model_file.path)

    pear_high_30_instance = MLModel.objects.get(name="pear_high_30")
    pear_high_30 = load_model(pear_high_30_instance.model_file.path)

    pear_mid_10_instance = MLModel.objects.get(name="pear_mid_10")
    pear_mid_10 = load_model(pear_mid_10_instance.model_file.path)

    pear_mid_20_instance = MLModel.objects.get(name="pear_mid_20")
    pear_mid_20 = load_model(pear_mid_20_instance.model_file.path)

    pear_mid_30_instance = MLModel.objects.get(name="pear_mid_30")
    pear_mid_30 = load_model(pear_mid_30_instance.model_file.path)

    apple_high_10_instance = MLModel.objects.get(name="apple_high_10")
    apple_high_10 = load_model(apple_high_10_instance.model_file.path)

    apple_high_20_instance = MLModel.objects.get(name="apple_high_20")
    apple_high_20 = load_model(apple_high_20_instance.model_file.path)

    apple_high_30_instance = MLModel.objects.get(name="apple_high_30")
    apple_high_30 = load_model(apple_high_30_instance.model_file.path)

    apple_mid_10_instance = MLModel.objects.get(name="apple_mid_10")
    apple_mid_10 = load_model(apple_mid_10_instance.model_file.path)

    apple_mid_20_instance = MLModel.objects.get(name="apple_mid_20")
    apple_mid_20 = load_model(apple_mid_20_instance.model_file.path)

    apple_mid_30_instance = MLModel.objects.get(name="apple_mid_30")
    apple_mid_30 = load_model(apple_mid_30_instance.model_file.path)

    # Make predictions
    # prediction_pear_high_30 = pear_high_10.predict(recent_30_days)
    # prediction_pear_high_60 = pear_high_20.predict(recent_60_days)
    # prediction_pear_high_90 = pear_high_30.predict(recent_90_days)
    #
    # prediction_pear_mid_30 = pear_mid_10.predict(recent_30_days)
    # prediction_pear_mid_60 = pear_mid_20.predict(recent_60_days)
    # prediction_pear_mid_90 = pear_mid_30.predict(recent_90_days)

    prediction_apple_high_30 = apple_high_10.predict(recent_30_days)
    # prediction_apple_high_60 = apple_high_20.predict(recent_60_days)
    # prediction_apple_high_90 = apple_high_30.predict(recent_90_days)
    #
    # prediction_apple_mid_30 = apple_mid_10.predict(recent_30_days)
    # prediction_apple_mid_60 = apple_mid_20.predict(recent_60_days)
    # prediction_apple_mid_90 = apple_mid_30.predict(recent_90_days)


    context = {
        # 'prediction_pear_high_30': prediction_pear_high_30,
        # 'prediction_pear_high_60': prediction_pear_high_60,
        # 'prediction_pear_high_90': prediction_pear_high_90,
        # 'prediction_pear_mid_30': prediction_pear_mid_30,
        # 'prediction_pear_mid_60': prediction_pear_mid_60,
        # 'prediction_pear_mid_90': prediction_pear_mid_90,
        'prediction_apple_high_30': prediction_apple_high_30,
        # 'prediction_apple_high_60': prediction_apple_high_60,
        # 'prediction_apple_high_90': prediction_apple_high_90,
        # 'prediction_apple_mid_30': prediction_apple_mid_30,
        # 'prediction_apple_mid_60': prediction_apple_mid_60,
        # 'prediction_apple_mid_90': prediction_apple_mid_90,
    }
    return render(request, 'recommend/recommend.html', context)


def recommend_detail(request):
    return render(request, "recommend/recommend_detail.html")
