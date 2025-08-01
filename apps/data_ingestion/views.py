import os
import logging
from django.http import JsonResponse
from django.forms.models import model_to_dict
from django.views.decorators.http import require_GET
from data_ingestion.src.alpha_vantage_client import AlphaVantageClient
from data_ingestion.src.yahoo_finance_client import YahooFinanceClient
from data_ingestion.src.database_handler import DatabaseHandler
from data_ingestion.src.stock_price_service import StockPriceService
from data_ingestion.src.readers import PriceReader, CompanyInfoReader, ExchangeRateReader
from data_ingestion.models import HistoricalPrice, TickerInfo, BaseHistoricalExchangeRate

logger = logging.getLogger(__name__)

@require_GET
def fetch_and_save_data(request, ticker):
    """
    Fetches and saves daily stock price data for a given ticker symbol.
    This function uses the Alpha Vantage API to fetch daily stock price data
    for the specified ticker symbol and saves the data into the database
    using the Django ORM.
    Args:
        request (HttpRequest): The HTTP request object.
        ticker (str): The stock ticker symbol for which to fetch and save data.
    Returns:
        JsonResponse: A JSON response indicating the success or failure of the operation.
                      On success, the response contains a success message.
                      On failure, the response contains an error message and a 500 status code.
    Raises:
        Exception: If an error occurs during the data fetching or saving process, 
                   it is caught and returned in the JSON response.
    """
    try:
        client = AlphaVantageClient(api_key=os.getenv("ALPHA_VANTAGE_API_KEY"))
        repository = DatabaseHandler(model=HistoricalPrice)
        service = StockPriceService(client=client, repository=repository)

        try:
            service.save_daily_prices(ticker)
        except Exception as e:
            logger.warning(f"AlphaVantage failed: {e}. Falling back to YahooFinance.")
            client = YahooFinanceClient()
            repository = DatabaseHandler(model=HistoricalPrice)
            service = StockPriceService(client=client, repository=repository)
            service.save_daily_prices(ticker)

        return JsonResponse({
            "status": "success",
            "message": f"Data for {ticker} fetched and saved successfully."
        })
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=500)


@require_GET
def get_company_info(request, ticker):
    """
    Fetches stock information for a given ticker symbol using the Alpha Vantage API 
    and saves the data to the database.
    Args:
        request (HttpRequest): The HTTP request object.
        ticker (str): The stock ticker symbol for which information is to be fetched.
    Returns:
        JsonResponse: A JSON response indicating the success or failure of the operation.
                      On success, includes a message confirming the data was fetched and saved.
                      On failure, includes an error message and a 500 status code.
    Raises:
        Exception: If an error occurs during the API call or database operation.
    """
    
    try:
        try:
            client = AlphaVantageClient(api_key=os.getenv("ALPHA_VANTAGE_API_KEY"))
            repository = DatabaseHandler(model=TickerInfo)
            stock_info = client.get_overview(ticker)
            repository.save_company_information(ticker, stock_info)

            return JsonResponse({
                "status": "success",
                "data": f"Data for {ticker} fetched and saved successfully."
            })
        except Exception as e:
            logger.warning(f"AlphaVantage failed: {e}. Falling back to YahooFinance.")

            client = YahooFinanceClient()
            repository = DatabaseHandler(model=TickerInfo)
            stock_info = client.get_overview(ticker)
            print(stock_info)
            repository.save_company_information(ticker, stock_info)

            return JsonResponse({
                "status": "success",
                "data": f"Data for {ticker} fetched and saved successfully."
            })
    

    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=500)


@require_GET
def fetch_and_save_exchange_rates(request, from_currency):
    """
    Fetches and saves daily exchange rates for a given currency.
    This function uses the Alpha Vantage API to fetch daily exchange rate data
    for the specified `from_currency` and saves it to the database using the
    provided repository.
    Args:
        request (HttpRequest): The HTTP request object.
        from_currency (str): The currency code (e.g., "USD", "EUR") for which
            exchange rate data is to be fetched.
    Returns:
        JsonResponse: A JSON response indicating the success or failure of the operation.
            - On success: Returns a JSON response with a "success" status and a message.
            - On failure: Returns a JSON response with an "error" status, an error message,
              and a 500 HTTP status code.
    Raises:
        Exception: If an error occurs during the fetching or saving of exchange rate data,
        the exception is caught and its message is included in the error response.
    """
    client = AlphaVantageClient(api_key=os.getenv("ALPHA_VANTAGE_API_KEY"))
    repository = DatabaseHandler(model=BaseHistoricalExchangeRate)
    service = StockPriceService(client=client, repository=repository)

    try:
        service.save_daily_exchange_rates(from_currency)
        return JsonResponse({
            "status": "success",
            "message": f"Data for {from_currency} fetched and saved successfully."
        })
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=500)

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