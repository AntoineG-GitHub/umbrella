import os
import logging
from django.http import JsonResponse
from django.forms.models import model_to_dict
from django.views.decorators.http import require_GET
from django.views.decorators.cache import cache_page
from data_ingestion.src.readers import PriceReader, CompanyInfoReader, ExchangeRateReader

logger = logging.getLogger(__name__)

@cache_page(60 * 60)  # Cache for 1 hour
@require_GET
def get_company_info(request, ticker):
    """
    Retrieve and return information about a company based on its ticker symbol.
    Args:
        request (HttpRequest): The HTTP request object.
        ticker (str): The ticker symbol of the company to retrieve information for.
    Returns:
        JsonResponse: A JSON response containing:
            - "status": "success" if the company information is found, otherwise "error".
            - "data": A dictionary representation of the company information if found.
            - "message": An error message if no information is found.
            - HTTP status code 200 on success, 404 on error.
    Raises:
        None
    """
    reader = CompanyInfoReader()
    company = reader.get_info(ticker)

    if not company:
        return JsonResponse({"status": "error", "message": f"No info found for {ticker}"}, status=404)

    return JsonResponse({
        "status": "success",
        "data": model_to_dict(company)
    })

@require_GET
def get_prices(request, ticker):
    """
    Retrieve historical price data for a given ticker within a specified date range.
    Args:
        request (HttpRequest): The HTTP request object containing query parameters.
            - start_date (str): The start date for the price data in "YYYY-MM-DD" format (optional).
            - end_date (str): The end date for the price data in "YYYY-MM-DD" format (optional).
        ticker (str): The stock ticker symbol for which to retrieve price data.
    Returns:
        JsonResponse: A JSON response containing:
            - status (str): The status of the request ("success").
            - ticker (str): The stock ticker symbol.
            - data (list): A list of dictionaries representing the price data.
    """
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    reader = PriceReader()
    prices = reader.get_prices(ticker, start_date, end_date)

    data = [model_to_dict(price) for price in prices]
    
    return JsonResponse({
        "status": "success",
        "ticker": ticker,
        "data": data
    })

@require_GET
def get_exchange_rates(request, from_currency):
    """
    Handles a request to retrieve exchange rates for a given currency pair 
    and date range.
    Args:
        request (HttpRequest): The HTTP request object containing query parameters.
            - to_currency (str, optional): The target currency code. Defaults to 'EUR' if not provided.
            - start_date (str, optional): The start date for the exchange rate query in 'YYYY-MM-DD' format.
            - end_date (str, optional): The end date for the exchange rate query in 'YYYY-MM-DD' format.
        from_currency (str): The source currency code.
    Returns:
        JsonResponse: A JSON response containing:
            - status (str): The status of the request ('success').
            - from_currency (str): The source currency code.
            - to_currency (str): The target currency code.
            - data (list): A list of dictionaries representing the exchange rate data.
    """
    to_currency = request.GET.get("to_currency")
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    if to_currency is None:
        to_currency = 'EUR'

    reader = ExchangeRateReader()
    exchange_rates = reader.get_exchange_rates(from_currency, to_currency, start_date, end_date)

    data = [model_to_dict(rate) for rate in exchange_rates]

    return JsonResponse({
        "status": "success",
        "from_currency": from_currency,
        "to_currency": to_currency,
        "data": data
    })