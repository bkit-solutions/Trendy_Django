# ecommerce/urls.py (Your Main Project URLS)

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from products import views as product_views
from products.views import (
    products_list, product_detail, categories_list,
    add_to_cart, remove_from_cart, update_cart, cart,
    add_to_wishlist, remove_from_wishlist, wishlist,
    checkout, place_order, order_history, order_detail,
    track_order, add_review, product_reviews, buy_now,
    apply_coupon
)
# Corrected import for accounts views - only those *directly* used in this urls.py
from accounts.views import (
    register, # profile, add_address, delete_address, # These are included via accounts.ui_urls now
    customer_support, login_view, logout_view
)

# Customize admin site
admin.site.login_template = 'admin/login.html'
admin.site.logout_template = 'accounts/logout.html'

urlpatterns = [
    # Main pages
    path('', product_views.home, name='home'), # Your general homepage
    path('admin/', admin.site.urls),

    # Product related URLs
    path('products/', product_views.products_list, name='products_list'),
    path('products/<slug:slug>/', product_views.product_detail, name='product_detail'),
    path('categories/', product_views.categories_list, name='categories_list'),
    path('search/', product_views.search_products, name='search_products'),
    path('product-search/', product_views.search_products, name='search_products'), 

    # Cart & Wishlist (from products app views)
    path('cart/', cart, name='cart'),
    path('cart/add/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:item_id>/', update_cart, name='update_cart'),
    path('cart/apply-coupon/', apply_coupon, name='apply_coupon'),
    # NOTE: Your main wishlist path is here from product_views, which is fine
    path('wishlist/', wishlist, name='wishlist'), 
    path('api/products/wishlist/toggle/<int:product_id>/', product_views.toggle_wishlist, name='toggle_wishlist'),
    path('wishlist/add/<int:product_id>/', add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:product_id>/', remove_from_wishlist, name='remove_from_wishlist'),

    # Checkout & Orders
    path('checkout/', checkout, name='checkout'),
    path('place-order/', place_order, name='place_order'),
    path('buy-now/<int:product_id>/', buy_now, name='buy_now'),
    path('orders/', include('orders.urls')), # Orders app URLs

    # --- CRITICAL CHANGE FOR ACCOUNTS URLS ---
    # 1. Regular UI accounts URLs (dashboard, profile, etc.)
    #    These will now be accessible via the /accounts/ prefix
    path('accounts/', include('accounts.ui_urls')), 

    # 2. Your API accounts URLs
    #    These will be accessible via the /api/accounts/ prefix
    path('api/accounts/', include('accounts.api_urls')), 
    # --- END CRITICAL CHANGE ---

    # Authentication URLs (directly from accounts.views if not handled by accounts.ui_urls)
    # Note: If these paths like 'login/' are also in accounts.ui_urls.py,
    # then calling them directly here might create conflicts or be redundant.
    # It's better to let accounts.ui_urls handle all accounts UI paths.
    # So, if accounts.ui_urls has path('login/', login_view), then REMOVE this line below:
    path('login/', login_view, name='login'), # Keep this here if you want login at root
    path('logout/', logout_view, name='logout'), # Keep this here if you want logout at root
    path('register/', register, name='register'), # Keep this here if you want register at root

    # If 'profile' is handled by accounts.ui_urls, REMOVE this directly mapped one
    # path('account/', profile, name='profile'), 

    # Password Reset/Change (standard Django auth views)
    path('account/password/change/', 
          auth_views.PasswordChangeView.as_view(template_name='accounts/password_change.html'),
          name='change_password'),
    path('account/password/change/done/',
          auth_views.PasswordChangeDoneView.as_view(template_name='accounts/password_change_done.html'),
          name='password_change_done'),
    path('account/password/reset/',
          auth_views.PasswordResetView.as_view(template_name='accounts/password_reset.html'),
          name='password_reset'),
    path('account/password/reset/done/',
          auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'),
          name='password_reset_done'),
    path('account/password/reset/confirm/<uidb64>/<token>/',
          auth_views.PasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html'),
          name='password_reset_confirm'),

    # User Profile & Support
    # If these are handled by accounts.ui_urls, REMOVE these directly mapped ones
    # path('account/address/add/', add_address, name='add_address'),
    # path('account/address/delete/<int:address_id>/', delete_address, name='delete_address'),
    path('support/', customer_support, name='customer_support'), # Keep if this is global support
    path('reviews/', product_reviews, name='product_reviews'), # Keep if this is global product reviews list
    path('products/<slug:slug>/review/', add_review, name='add_review'), # Keep if global add review

    # API URLs for JWT and other apps
    path('api/products/', include('products.urls')), # Assuming products.urls has its DRF router
    path('api/orders/', include('orders.urls')),     # Assuming orders.urls has its DRF router
    # path('api/recommendations/', include('recommendations.urls')), # This app's urls need to be defined if uncommented
    path('api/payments/', include('payments.urls')), # Assuming payments.urls has its DRF router
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

# Serve media and static files
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)