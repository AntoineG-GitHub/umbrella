from django.test import TestCase
from unittest.mock import Mock
from data_ingestion.src.stock_price_service import StockPriceService

class TestStockPriceService(TestCase):
    def setUp(self):
        self.mock_client = Mock()
        self.mock_repo = Mock()
        self.service = StockPriceService(self.mock_client, self.mock_repo)

    def test_save_daily_prices_eur(self):
        """
        Test saving daily stock prices for a ticker in EUR.
        """
        # Mock responses
        self.mock_client.get_daily_time_series.return_value = {
            "Time Series (Daily)": {
                "2023-01-01": {
                    "1. open": "100.00",
                    "2. high": "105.00", 
                    "3. low": "99.00",
                    "4. close": "102.00",
                    "5. volume": "1000000"
                }
            }
        }
        
        self.mock_client.get_overview.return_value = {
            "Currency": "EUR"
        }

        # Call service method
        self.service.save_daily_prices("MOCK")

        # Verify client calls
        self.mock_client.get_daily_time_series.assert_called_once_with("MOCK")
        self.mock_client.get_overview.assert_called_once_with("MOCK")
        self.mock_client.get_exchange_rates.assert_not_called()

        # Verify repo calls
        self.mock_repo.ensure_table_exists.assert_called_once()
        self.mock_repo.save_prices.assert_called_once()

    def test_save_daily_prices_usd(self):
        """
        Test saving daily stock prices for a ticker in USD.
        """
        # Mock responses
        self.mock_client.get_daily_time_series.return_value = {
            "Time Series (Daily)": {
                "2023-01-01": {
                    "1. open": "100.00",
                    "2. high": "105.00",
                    "3. low": "99.00", 
                    "4. close": "102.00",
                    "5. volume": "1000000"
                }
            }
        }

        self.mock_client.get_overview.return_value = {
            "Currency": "USD"
        }

        self.mock_client.get_exchange_rates.return_value = {
            "Time Series FX (Daily)": {
                "2023-01-01": {
                    "4. close": "0.85"
                }
            }
        }

        # Call service method
        self.service.save_daily_prices("MOCK")

        # Verify client calls
        self.mock_client.get_daily_time_series.assert_called_once_with("MOCK")
        self.mock_client.get_overview.assert_called_once_with("MOCK")
        self.mock_client.get_exchange_rates.assert_called_once()

        # Verify repo calls
        self.mock_repo.ensure_table_exists.assert_called_once()
        self.mock_repo.save_prices.assert_called_once()

    def test_save_daily_exchange_rates(self):
        # Mock response
        self.mock_client.get_exchange_rates.return_value = {
            "Time Series FX (Daily)": {
                "2023-01-01": {
                    "1. open": "0.84",
                    "2. high": "0.85",
                    "3. low": "0.83",
                    "4. close": "0.85"
                }
            }
        }

        # Call service method
        self.service.save_daily_exchange_rates("USD", "EUR")

        # Verify client calls
        self.mock_client.get_exchange_rates.assert_called_once_with("USD", "EUR")

        # Verify repo calls
        self.mock_repo.ensure_table_exists.assert_called_once()
        self.mock_repo.save_daily_exchange_rates.assert_called_once()
