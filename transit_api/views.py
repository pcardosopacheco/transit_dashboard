from django.shortcuts import render
from .utils import fetch_transit_data


def index(request):
    transit_data = fetch_transit_data()
    context = {
        'transit_data': transit_data,
    }
    return render(request, 'transit_data.html', context)
