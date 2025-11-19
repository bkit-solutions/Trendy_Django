# products/recommendations.py

from django.utils import timezone
from products.models import Product, Category # Make sure Category is imported if used
from orders.models import OrderItem # Assuming OrderItem tracks what's bought
from django.db.models import Sum
import random

class RecommendationEngine:
    def __init__(self):
        # You can initialize any models or pre-load data here if needed
        pass

    def get_trending_products(self, limit=4):
        """
        Returns globally popular/trending products based on recent sales.
        If not enough recent sales, fills with random products.
        """
        # Get product IDs with most sales in the last 30 days
        popular_product_ids = OrderItem.objects.filter(
            order__created_at__gte=timezone.now() - timezone.timedelta(days=30)
        ).values('product').annotate(total_quantity=Sum('quantity')).order_by('-total_quantity')[:limit].values_list('product_id', flat=True)

        products = list(Product.objects.filter(id__in=popular_product_ids))

        # Fill up with random products if not enough from sales
        if len(products) < limit:
            remaining_limit = limit - len(products)
            random_products = Product.objects.exclude(id__in=[p.id for p in products]).order_by('?')[:remaining_limit]
            products.extend(list(random_products))

        return products


    def get_personalized_recommendations(self, user, limit=4):
        """
        Generates recommendations for a specific user based on their purchased categories.
        Falls back to trending if user has no purchase history or if not enough recommendations.
        """
        if not user.is_authenticated:
            return self.get_trending_products(limit) # Fallback for anonymous

        # Get categories of products the user has purchased
        # Ensure 'category' field exists on your Product model and is a ForeignKey to Category model
        user_purchased_categories = OrderItem.objects.filter(order__user=user).values_list('product__category', flat=True).distinct()

        recommended_products = []
        purchased_product_ids = OrderItem.objects.filter(order__user=user).values_list('product__id', flat=True)

        # Recommend products from the user's most purchased categories
        for category_id in user_purchased_categories:
            products_in_category = Product.objects.filter(category__id=category_id).exclude(id__in=purchased_product_ids).order_by('?')[:limit - len(recommended_products)]
            recommended_products.extend(list(products_in_category))
            if len(recommended_products) >= limit:
                break

        # If not enough, fill with trending products, ensuring no duplicates
        if len(recommended_products) < limit:
            trending = self.get_trending_products(limit - len(recommended_products))
            for p in trending:
                if p not in recommended_products:
                    recommended_products.append(p)

        return recommended_products[:limit]


    def get_similar_to_products(self, product_ids, limit=4, exclude_ids=None):
        """
        Returns products similar to a given list of product IDs (e.g., from a wishlist).
        Similarity is based on category. Fills with trending if not enough similar.
        """
        if not product_ids:
            return self.get_trending_products(limit)

        if exclude_ids is None:
            exclude_ids = []

        # Ensure all IDs are integers for filtering
        all_excluded_ids = list(map(int, list(product_ids) + list(exclude_ids)))

        # Get categories of the specified products
        target_products_categories = Product.objects.filter(id__in=product_ids).values_list('category', flat=True).distinct()

        # Find other products in those categories, excluding the original products and any other excluded IDs
        similar_products = list(Product.objects.filter(
            category__in=target_products_categories
        ).exclude(
            id__in=all_excluded_ids
        ).order_by('?')[:limit]) # order_by('?') for random selection, but could be based on popularity in category

        # If not enough similar products, fill with trending
        if len(similar_products) < limit:
            trending = self.get_trending_products(limit - len(similar_products))
            for p in trending:
                if p not in similar_products and p.id not in all_excluded_ids:
                    similar_products.append(p)

        return similar_products[:limit]