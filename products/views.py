from django.shortcuts import render
from django.http import  HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from products.models import Products
from products.serializers import ProductSerializer
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q  # To handle complex filters

from django.db import transaction

def greet(request):
    data = Products.objects.all()
    print(data)
    # if data.exists():
    product = data[0] #good practise to assign to a variable, rather access data[0] directly bcz query sets are lazy
    print("Before:", product.name)  # Output: ShivaShakti
    product.name = "SitaRam"
    product.save()  # Explicitly save the updated object
    product.refresh_from_db()  # Reload the object to confirm the change
    print("After:", product.name)  # Should now output: ShivaShakti
    # else:
    #     print("No products found.")
    return HttpResponse("Hey we found World")


@csrf_exempt
@api_view(['GET', 'POST'])
def create_r_get_products(request):
    if request.method == 'GET':
        # Fetch all products from the database
        data = Products.objects.all()
        # Serialize the data for JSON response
        serialized_products = ProductSerializer(data, many=True)
        return Response(serialized_products.data)  # Return the serialized data

    elif request.method == 'POST':
        # Deserialize and validate the incoming JSON data
        serialized_products = ProductSerializer(data=request.data)
        if serialized_products.is_valid():
            serialized_products.save()  # Save the valid data to the database
            return Response(serialized_products.data, status=status.HTTP_201_CREATED)  # Success response
        return Response(serialized_products.errors, status=status.HTTP_400_BAD_REQUEST)  # Error response


@api_view(['GET'])
def get_product(request, id):
    # Retrieves a single product based on the provided ID.
    data = Products.objects.get(id=id)
    # Serializes the specific product data into a format suitable for JSON responses.
    serialized_products = ProductSerializer(data)
    # Extracts the serialized product data (in JSON format).
    serialized_data = serialized_products.data
    # Sends the serialized product data as an API response.
    return Response(serialized_data)

@api_view(['GET'])
def filter_products(request):
    # Get filter parameters from the query string
    min_price = request.query_params.get('min_price', None)
    max_price = request.query_params.get('max_price', None)
    description = request.query_params.get('description', None)

    # Build dynamic filters using Q objects
    filter_query = Q()
    if min_price:
        filter_query &= Q(price__gte=min_price)  # Filter by minimum price
    if max_price:
        filter_query &= Q(price__lte=max_price)  # Filter by maximum price
    if description:
        filter_query &= Q(description__icontains=description)  # Filter by description keyword

    # Fetch filtered products from the database
    filtered_products = Products.objects.filter(filter_query)
    serialized_products = ProductSerializer(filtered_products, many=True)

    # Return the response with filtered data
    return Response(serialized_products.data, status=status.HTTP_200_OK)
