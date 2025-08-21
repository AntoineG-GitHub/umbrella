# Portfolio Valuation App

## Overview
The `portfolio_valuation` app is responsible for calculating and managing portfolio valuations, including Net Asset Value (NAV) per unit, user share snapshots, and daily portfolio snapshots. It integrates with transaction data and historical price data to compute portfolio metrics and track gains or losses over time.

## Features
- **Portfolio Valuation**: Calculate the total portfolio value based on historical asset prices and transaction data, with cash value and investment values.
- **NAV Computation**: Compute the Net Asset Value (NAV) per unit for the portfolio.
- **User Share Snapshots**: Track individual user holdings and their corresponding value.

## Models
### DailyPortfolioSnapshot
Tracks daily portfolio metrics, including:
- `date`: The date of the snapshot.
- `total_value`: Total portfolio value in EUR.
- `total_units`: Total fund units in circulation.
- `nav_per_unit`: Net Asset Value per unit.
- `gain_or_loss`: Total portfolio gain or loss.
- `cash`: Available cash position.
- `portfolio_total_value`: Combined value of assets and cash.
- `net_inflows`: Net deposits minus withdrawals.

### UserShareSnapshot
Tracks individual user holdings, including:
- `date`: The date of the snapshot.
- `user_id`: The ID of the user.
- `units_held`: Total units held by the user.
- `value_held`: Total value of the user's holdings.

## API Endpoints
### Daily Portfolio Snapshots
- **Get Daily Portfolio Snapshots**: `/portfolio_valuation/get_daily_portfolio_snapshot/`
  - Retrieves daily portfolio snapshots for a specified date range.

- **Get Daily User Snapshots**: `/portfolio_valuation/user_snapshots/id:int`
  - Retrieves daily user snapshots for a specified date range.


## Testing
The app includes unit tests for key functionalities:
- **ValuationServiceTest**: Validates portfolio valuation logic and NAV computation.
- **FeeHandlingTest**: Ensures fees are correctly applied to portfolio metrics.
- **NAVComputationTest**: Tests the computation of NAV per unit across different scenarios.

## Commands
The following management commands are available for interacting with the portfolio valuation app:

- **compute_valuation_batch**: Compute the valuation for a batch of dates. Practically, loops over the date and call the adily computation.
    ```bash
    python manage.py compute_valuation_batch --date=YYYY-MM-DD
    ```
- **compute_valuation**: Compute the valuation for a specific date.
    ```bash
    python manage.py compute_valuation --start-date=YYYY-MM-DD --end-date=YYYY-MM-DD
    ``` 