

class APIFetcher:
    def get_daily_time_series(self, ticker: str) -> dict:
        """
        Fetch daily stock price series for a given ticker.
        
        Args:
            ticker (str): The stock ticker symbol
            
        Returns:
            dict: A dictionary containing the daily time series data
        """
        raise NotImplementedError("This method should be implemented by subclasses.")
    
    def get_exchange_rate_history(self) -> dict:
        """
        Fetch historical exchange rate data.
        
        Returns:
            dict: A dictionary containing the exchange rate history
        """
        raise NotImplementedError("This method should be implemented by subclasses.")
    
    def get_overview(self, ticker: str) -> dict:
        """
        Fetch an overview of the stock for a given ticker.
        
        Args:
            ticker (str): The stock ticker symbol
            
        Returns:
            dict: A dictionary containing the stock overview data
        """
        raise NotImplementedError("This method should be implemented by subclasses.")