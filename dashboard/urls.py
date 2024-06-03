from django.urls import path
from dashboard import views

urlpatterns = [
    path("", views.index, name="index"),
    path("inventory", views.inventory, name="inventory"),
    path("inventory/1", views.inventory_details, name='inventory-item'),
    path("product", views.product_setting, name='product-setting'),
    path("product/edit/1", views.product_edit, name='product-edit'),
    path("warehousing", views.warehousing, name='warehousing'),
    path("warehousing/edit/1", views.warehousing_edit, name="warehousing_edit"),

    path("shipping", views.shipping, name="shipping"),
    path("shipping/edit/1", views.shipping_edit, name="shipping_edit"),
    
    path("warehouse", views.warehouse, name="warehouse"),
    path("warehouse/1", views.warehouse_detail, name="warehouse_detail"),
    path("warehouse/1/edit", views.warehouse_edit, name="warehouse_edit"),
    
    path("recommend", views.recommend, name="recommend"),
    path("recommend/detail/1", views.recommend_detail, name="recommend_detail")
]