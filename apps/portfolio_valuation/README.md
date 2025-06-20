# Portfolio Valuation App

## Overview
The `portfolio_valuation` app is responsible for calculating and managing portfolio valuations, including Net Asset Value (NAV) per unit, user share snapshots, and daily portfolio snapshots. It integrates with transaction data and historical price data to compute portfolio metrics and track gains or losses over time.

## Features
- **Portfolio Valuation**: Calculate the total portfolio value based on historical asset prices and transaction data.
- **NAV Computation**: Compute the Net Asset Value (NAV) per unit for the portfolio.

📈 NAV – Net Asset Value

The Net Asset Value (NAV) represents the value of one share/unit of the portfolio at a given date. It is used to measure the value of a user's investment in the fund over time.

🧮 Formula

$$ NAV = \frac{\text{Total Portfolio Value(cash + assets)}}{\text{Units Outstanding}} $$

📦 Components:

**Portfolio value**: Value of held assets (stocks, ETFs, etc.) + Available cash (from deposits, dividends, sales, etc. minus purchases, fees, and withdrawals)
**Units Outstanding**:The total number of units issued to users since the fund's inception, adjusted daily based on deposits and withdrawals.

Note that a deposit or a widthdrawal is not impacting the NAV. By depositing or withdrawing, the total value of the portfolio changes by the same amount as the total units issued. 

- **Total gain or loss**: Track the total gain or loss of the portfolio over time.
Total gain or loss is calculated as the total deposits, dividends and sells minus the total purchases, fees and withdrawals. It is recomputed every 

- **User Share Snapshots**: Track individual user holdings and their corresponding value.
The amount of units held by each user was defined at the start. And once the deposit or withdraw money, the basically buy or sell units of the fund. 

- **Daily Portfolio Snapshots**: Store daily metrics such as total portfolio value, NAV per unit, cash position, and gains/losses.

- **Batch Valuation**: Perform valuations for a range of dates.

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
### Portfolio Valuation
- **Compute Valuation**: `/portfolio_valuation/compute/?date=YYYY-MM-DD`
  - Triggers the valuation logic for the specified date.
- **Batch Valuation**: `/portfolio_valuation/batch`
  - Computes valuations for a range of dates.

### User Share Snapshots
- **Get User Snapshots**: `/portfolio_valuation/user_snapshots/<int:user_id>/`
  - Retrieves user share snapshots for a specific user.

### Daily Portfolio Snapshots
- **Get Daily Portfolio Snapshots**: `/portfolio_valuation/get_daily_portfolio_snapshot/`
  - Retrieves daily portfolio snapshots for a specified date range.

## Admin Panel
The app provides an admin interface for managing data:
- **DailyPortfolioSnapshotAdmin**: View and filter daily portfolio snapshots.
- **UserShareSnapshotAdmin**: Manage user share snapshots.

## Testing
The app includes unit tests for key functionalities:
- **ValuationServiceTest**: Validates portfolio valuation logic and NAV computation.
- **FeeHandlingTest**: Ensures fees are correctly applied to portfolio metrics.
- **NAVComputationTest**: Tests the computation of NAV per unit across different scenarios.

## Dependencies
- Django
- pandas_market_calendars (for market schedule validation)
- Decimal (for precise financial calculations)

## Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt