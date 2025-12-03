# 🚀 Dexlyn Perpetuals Trading Bot - SDK Version Complete Documentation

## 📖 Table of Contents
1. [Overview](#-overview)
2. [Quick Start](#-quick-start)
3. [Installation](#-installation)
4. [Configuration Files](#-configuration-files)
5. [Order Field Reference](#-order-field-reference)
6. [Trading Strategies](#-trading-strategies)
7. [Advanced SDK Features](#-advanced-sdk-features)
8. [Command Line Usage](#-command-line-usage)
9. [Test Execution Commands](#-test-execution-commands)
10. [Troubleshooting](#-troubleshooting)

## 🎯 Overview

The Dexlyn Perpetuals Trading Bot (SDK Version) is a fully customizable automated trading system that uses the official Supra SDK to interact with Dexlyn perpetual contracts. This version provides a pure Python interface with private key authentication, eliminating the need for CLI dependencies.

### Key Features
- ✅ **Pure Python SDK** - No CLI dependencies, uses official Supra SDK
- ✅ **Private Key Authentication** - Secure wallet management
- ✅ **Complete Field Control** - Every order parameter customizable via JSON
- ✅ **Multi-Network Support** - Testnet and Mainnet ready
- ✅ **Automatic Testnet Funding** - Built-in faucet integration
- ✅ **Flexible Strategies** - Pre-built and custom strategies
- ✅ **Cross-Platform** - Windows, macOS, Linux support

## 🚀 Quick Start

### Step 1: Installation
```bash
# Install Supra SDK
pip install supra-sdk

# Install bot dependencies
pip install python-dotenv
```

### Step 2: Generate Configuration Files
```bash
python dexlyn_bot_sdk.py --generate-configs
```
This creates:
- `config.json` - Main settings
- `network.json` - Network configurations
- `wallets.json` - Your wallet private keys
- `pairs.json` - Trading pairs
- `strategies.json` - Trading strategies
- `field_reference.json` - Complete field documentation

### Step 3: Configure Your Wallets

**Edit `wallets.json`:**
```json
{
  "trader_1": {
    "address": "0xYOUR_WALLET_ADDRESS_HERE",
    "private_key": "YOUR_PRIVATE_KEY_HEX_HERE",
    "description": "My trading wallet"
  }
}
```

**Important:** Private keys must be in hex format (64 characters). Never share your private keys!

### Step 4: Run the Bot
```bash
# Basic test run
python dexlyn_bot_sdk.py --strategy basic_cycle --cycles 1

# Continuous trading
python dexlyn_bot_sdk.py --strategy basic_cycle

# Custom strategy
python dexlyn_bot_sdk.py --custom-config my_strategy.json
```

## 📦 Installation

### Prerequisites
- Python 3.12+
- Supra SDK
- Valid Supra wallet with private key

### Installation Commands
```bash
# Install from requirements (if available)
pip install -r requirements.txt

# Or install individually
pip install supra-sdk python-dotenv

# Verify installation
python -c "from supra_sdk.account import Account; print('✅ Supra SDK installed')"
```

## 📁 Configuration Files

### 1. config.json - Main Configuration
```json
{
  "network": "testnet",
  "default_strategy": "basic_cycle",
  "trading": {
    "default_size_usd": 300.0,
    "default_collateral_usd": 3.0,
    "default_leverage": 50.0,
    "max_position_size_usd": 500000.0,
    "min_position_size_usd": 300.0
  },
  "orders": {
    "default_slippage_tolerance": 0.01,
    "default_timeout_seconds": 240,
    "confirmation_attempts": 3,
    "auto_calculate_execution_guard": true
  },
  "timing": {
    "sleep_between_orders": 6,
    "sleep_between_cycles": 10,
    "retry_delay": 5
  },
  "risk_management": {
    "partial_close_ratio": 0.5,
    "add_position_ratio": 0.3,
    "add_collateral_ratio": 0.2,
    "stop_loss_percent": 0.10,
    "take_profit_percent": 0.15
  },
  "logging": {
    "level": "INFO",
    "log_file": "dexlyn_trading_sdk.log",
    "console_output": true
  }
}
```

### 2. network.json - Network Settings
```json
{
  "testnet": {
    "contract_address": "0xae38541466939b577823389765d966ba206b19be954fc87011fa10dc91e2fe0f",
    "collateral_token": "0x4f316ce2960250e7ac1206a07d07b2cbef3897d3cb8c12369d30c08ecd39c61c::tusdc_coin::TUSDC",
    "size_decimals": 6,
    "collateral_decimals": 6,
    "price_decimals": 10
  },
  "mainnet": {
    "contract_address": "0x215f242bec12c3d66b469668bc48b71e87fc1c7fd8e1764ac773423f0e2ba18b",
    "collateral_token": "0x9176f70f125199a3e3d5549ce795a8e906eed75901d535ded623802f15ae3637::cdp_multi::CASH",
    "size_decimals": 8,
    "collateral_decimals": 8,
    "price_decimals": 10
  }
}
```

### 3. wallets.json - Wallet Configuration (CRITICAL: KEEP SECURE!)
```json
{
  "trader_1": {
    "address": "0xYOUR_WALLET_ADDRESS",
    "private_key": "0xPRIVATE_KEY_HEX_64_CHARACTERS",
    "description": "Primary trading wallet"
  },
  "trader_2": {
    "address": "0xANOTHER_WALLET_ADDRESS",
    "private_key": "0xANOTHER_PRIVATE_KEY_HEX",
    "description": "Secondary wallet for hedging"
  }
}
```

**Security Note:** 
- Store `wallets.json` in a secure location
- Never commit private keys to version control
- Use environment variables or secret managers in production
- Consider using hardware wallets for large funds

### 4. pairs.json - Trading Pairs
```json
{
  "ETH_USD": {
    "type_arg": "ETH_USD",
    "description": "Ethereum vs US Dollar",
    "available_testnet": true,
    "available_mainnet": true,
    "default_size_usd": 300.0,
    "default_collateral_usd": 3.0,
    "default_price": 3500.0,
    "min_size_usd": 300.0,
    "max_size_usd": 500000.0
  },
  "BTC_USD": {
    "type_arg": "BTC_USD",
    "description": "Bitcoin vs US Dollar",
    "available_testnet": true,
    "available_mainnet": true,
    "default_size_usd": 300.0,
    "default_collateral_usd": 3.0,
    "default_price": 50000.0,
    "min_size_usd": 300.0,
    "max_size_usd": 500000.0
  },
  "SOL_USD": {
    "type_arg": "SOL_USDT",
    "description": "Solana vs US Dollar",
    "available_testnet": true,
    "available_mainnet": true,
    "default_size_usd": 300.0,
    "default_collateral_usd": 3.0,
    "default_price": 150.0,
    "min_size_usd": 300.0,
    "max_size_usd": 500000.0
  },
  "ADA_USD": {
    "type_arg": "ADA_USDT",
    "description": "Cardano vs US Dollar",
    "available_testnet": true,
    "available_mainnet": false,
    "default_size_usd": 300.0,
    "default_collateral_usd": 3.0,
    "default_price": 1.2,
    "min_size_usd": 300.0,
    "max_size_usd": 500000.0
  },
  "SUPRA_USD": {
    "type_arg": "SUPRA_USDT",
    "description": "Supra vs US Dollar",
    "available_testnet": true,
    "available_mainnet": true,
    "default_size_usd": 300.0,
    "default_collateral_usd": 3.0,
    "default_price": 0.5,
    "min_size_usd": 300.0,
    "max_size_usd": 500000.0
  },
  "DOGE_USD": {
    "type_arg": "DOGE_USDT",
    "description": "Dogecoin vs US Dollar",
    "available_testnet": true,
    "available_mainnet": false,
    "default_size_usd": 300.0,
    "default_collateral_usd": 3.0,
    "default_price": 0.25,
    "min_size_usd": 300.0,
    "max_size_usd": 500000.0
  },
  "XLM_USD": {
    "type_arg": "XLM_USDT",
    "description": "Stellar vs US Dollar",
    "available_testnet": true,
    "available_mainnet": false,
    "default_size_usd": 300.0,
    "default_collateral_usd": 3.0,
    "default_price": 0.3,
    "min_size_usd": 300.0,
    "max_size_usd": 500000.0
  },
  "LINK_USD": {
    "type_arg": "LINK_USDT",
    "description": "Chainlink vs US Dollar",
    "available_testnet": true,
    "available_mainnet": false,
    "default_size_usd": 300.0,
    "default_collateral_usd": 3.0,
    "default_price": 25.0,
    "min_size_usd": 300.0,
    "max_size_usd": 500000.0
  },
  "ARB_USD": {
    "type_arg": "ARB_USDT",
    "description": "Arb vs US Dollar",
    "available_testnet": true,
    "available_mainnet": false,
    "default_size_usd": 300.0,
    "default_collateral_usd": 3.0,
    "default_price": 1.0,
    "min_size_usd": 300.0,
    "max_size_usd": 500000.0
  },
  "HYPE_USD": {
    "type_arg": "HYPE_USDT",
    "description": "Hype vs US Dollar",
    "available_testnet": true,
    "available_mainnet": false,
    "default_size_usd": 300.0,
    "default_collateral_usd": 3.0,
    "default_price": 0.1,
    "min_size_usd": 300.0,
    "max_size_usd": 500000.0
  },
  "AVAX_USD": {
    "type_arg": "AVAX_USDC",
    "description": "Avalanche vs US Dollar",
    "available_testnet": true,
    "available_mainnet": false,
    "default_size_usd": 300.0,
    "default_collateral_usd": 3.0,
    "default_price": 40.0,
    "min_size_usd": 300.0,
    "max_size_usd": 500000.0
  },
  "BNB_USD": {
    "type_arg": "BNB_USDC",
    "description": "Binance Coin vs US Dollar",
    "available_testnet": true,
    "available_mainnet": false,
    "default_size_usd": 300.0,
    "default_collateral_usd": 3.0,
    "default_price": 400.0,
    "min_size_usd": 300.0,
    "max_size_usd": 500000.0
  },
  "OP_USD": {
    "type_arg": "OP_USDT",
    "description": "Optimism vs US Dollar",
    "available_testnet": true,
    "available_mainnet": false,
    "default_size_usd": 300.0,
    "default_collateral_usd": 3.0,
    "default_price": 2.0,
    "min_size_usd": 300.0,
    "max_size_usd": 500000.0
  },
  "XRP_USD": {
    "type_arg": "XRP_USDT",
    "description": "Ripple vs US Dollar",
    "available_testnet": true,
    "available_mainnet": false,
    "default_size_usd": 300.0,
    "default_collateral_usd": 3.0,
    "default_price": 0.7,
    "min_size_usd": 300.0,
    "max_size_usd": 500000.0
  }
}
```

## 📊 Order Field Reference

### Core Required Fields
| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `name` | string | ✅ | Order name for logging | `"Open ETH Long"` |
| `action` | string | ✅ | Order action type | `"market_open_long"` |
| `pair` | string | ✅ | Trading pair | `"ETH_USD"` |
| `wallet` | string | ✅ | Wallet to use | `"trader_1"` |

### Size and Collateral Fields
| Field | Type | Description | Testnet Example | Mainnet Example |
|-------|------|-------------|-----------------|-----------------|
| `size_usd` | number | Position size in USD | `300.0` ($300) | `300.0` ($300) |
| `size_units` | integer | Exact size in units | `300000000` | `30000000000` |
| `collateral_usd` | number | Collateral in USD | `3.0` ($3) | `3.0` ($3) |
| `collateral_units` | integer | Exact collateral in units | `3000000` | `300000000` |

### Price Fields
| Field | Type | Description | Example Value |
|-------|------|-------------|---------------|
| `price` | number | Price in USD | `3500.0` |
| `price_units` | integer | Exact price in units | `3500000000000000` |
| `stop_loss` | number | Stop loss in USD | `3150.0` |
| `stop_loss_units` | integer | Exact stop loss in units | `3150000000000000` |
| `take_profit` | number | Take profit in USD | `3850.0` |
| `take_profit_units` | integer | Exact take profit in units | `3850000000000000` |

### Boolean Flags
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `is_long` | boolean | auto | `true` for LONG, `false` for SHORT |
| `is_increase` | boolean | auto | `true` to open/add, `false` to close |
| `is_market` | boolean | auto | `true` for market, `false` for limit |
| `can_execute_above_price` | boolean | auto | Execution guard for slippage |

### Advanced Fields
| Field | Type | Description |
|-------|------|-------------|
| `custom_parameters` | object | Raw parameters for complete control |
| `wait_before` | number | Seconds to wait before execution |
| `description` | string | Order description for reference |

## 🎯 Trading Strategies

### Pre-built Strategies

#### 1. Basic Cycle
```json
{
  "basic_cycle": {
    "name": "Basic ETH Open/Close Cycle",
    "description": "Simple cycle opening and closing both LONG and SHORT positions",
    "network": "testnet",
    "cycles": -1,
    "orders": [
      {
        "name": "Open LONG ETH",
        "action": "market_open_long",
        "pair": "ETH_USD",
        "wallet": "trader_1",
        "size_usd": 300.0,
        "collateral_usd": 3.0,
        "price": 3500.0,
        "stop_loss": 3150.0,
        "take_profit": 3850.0
      },
      {
        "name": "Open SHORT ETH",
        "action": "market_open_short",
        "pair": "ETH_USD",
        "wallet": "trader_2", 
        "size_usd": 300.0,
        "collateral_usd": 3.0,
        "price": 3500.0,
        "stop_loss": 3850.0,
        "take_profit": 3150.0
      }
    ]
  }
}
```

#### 2. Complete Examples Strategy
```json
{
  "complete_examples": {
    "name": "Complete Field Examples",
    "description": "Shows all possible field customizations",
    "network": "testnet",
    "cycles": 1,
    "orders": [
      {
        "name": "USD-Based Market Long",
        "action": "market_open_long",
        "pair": "ETH_USD",
        "wallet": "trader_1",
        "size_usd": 300.0,
        "collateral_usd": 3.0,
        "price": 3550.0,
        "stop_loss": 3195.0,
        "take_profit": 3905.0
      },
      {
        "name": "Units-Based Limit Short", 
        "action": "limit_open_short",
        "pair": "ETH_USD",
        "wallet": "trader_2",
        "size_units": 300000000,
        "collateral_units": 3000000,
        "price_units": 3600000000000000,
        "stop_loss_units": 3960000000000000,
        "take_profit_units": 3240000000000000
      },
      {
        "name": "Fully Custom Raw Order",
        "action": "custom",
        "pair": "ETH_USD",
        "wallet": "trader_1", 
        "custom_parameters": {
          "size_units": 300000000,
          "collateral_units": 3000000,
          "price_units": 3650000000000000,
          "is_long": true,
          "is_increase": true, 
          "is_market": false,
          "stop_loss_units": 3285000000000000,
          "take_profit_units": 4015000000000000,
          "can_execute_above_price": false
        }
      }
    ]
  }
}
```

### Creating Custom Strategies

#### Simple Strategy File (my_strategy.json)
```json
{
  "my_strategy": {
    "name": "My Custom Strategy",
    "description": "A custom trading strategy",
    "network": "testnet",
    "cycles": 3,
    "orders": [
      {
        "name": "Open Long Position",
        "action": "market_open_long",
        "pair": "ETH_USD",
        "wallet": "trader_1",
        "size_usd": 150.0,
        "collateral_usd": 1.5,
        "price": 3525.0,
        "stop_loss": 3172.5,
        "take_profit": 3877.5,
        "description": "Open small long position"
      },
      {
        "name": "Add to Position",
        "action": "add_to_position",
        "pair": "ETH_USD",
        "wallet": "trader_1",
        "size_usd": 75.0,
        "additional_collateral_usd": 0.75,
        "wait_before": 30,
        "description": "Add to position after 30 seconds"
      }
    ]
  }
}
```

## ⚙️ Advanced SDK Features

### SDK Architecture
```python
# Core SDK Components Used:
from supra_sdk.account import Account                # Wallet management
from supra_sdk.clients.rest import SupraClient      # Network communication
from supra_sdk.transactions import (                # Transaction building
    EntryFunction, 
    TransactionArgument, 
    TransactionPayload
)
from supra_sdk.type_tag import TypeTag, StructTag   # Type definitions
from supra_sdk.bcs import Serializer                # Binary encoding
from supra_sdk.account_address import AccountAddress # Address handling
```

### Automatic Testnet Funding
The SDK version automatically detects and funds testnet accounts:
```python
# Built-in faucet integration
if network == "testnet":
    balance = await client.account_coin_balance(account.address())
    if balance == 0:
        tx_hash = await client.faucet(account.address())
        # Waits for faucet completion
```

### Transaction Building Process
1. **Account Loading**: Private key → Account object
2. **Argument Creation**: Convert JSON fields → TransactionArguments
3. **Type Tag Creation**: Parse contract types → TypeTags
4. **Payload Creation**: Build EntryFunction → TransactionPayload
5. **Transaction Signing**: Account signs the payload
6. **Submission**: Send to network via REST client

### Units Conversion Guide

**Testnet:**
- Size: 1 USD = 1,000,000 units
- Collateral: 1 USD = 1,000,000 units  
- Price: 1 USD = 10,000,000,000 units

**Mainnet:**
- Size: 1 USD = 100,000,000 units
- Collateral: 1 USD = 100,000,000 units
- Price: 1 USD = 10,000,000,000 units

**Examples:**
```json
// Testnet - $300 position
"size_usd": 300.0        // Auto-converted to 300000000 units
"size_units": 300000000  // Explicit units

// Mainnet - $300 position  
"size_usd": 300.0        // Auto-converted to 30000000000 units
"size_units": 30000000000 // Explicit units

// Price - $3500
"price": 3500.0          // Auto-converted to 3500000000000000 units
"price_units": 3500000000000000 // Explicit units
```

### Order Actions Reference

| Action | Description | Auto Parameters |
|--------|-------------|-----------------|
| `market_open_long` | Open LONG with market order | `is_long=true, is_increase=true, is_market=true` |
| `market_open_short` | Open SHORT with market order | `is_long=false, is_increase=true, is_market=true` |
| `limit_open_long` | Open LONG with limit order | `is_long=true, is_increase=true, is_market=false` |
| `limit_open_short` | Open SHORT with limit order | `is_long=false, is_increase=true, is_market=false` |
| `market_close_long` | Close LONG with market order | `is_long=true, is_increase=false, is_market=true` |
| `market_close_short` | Close SHORT with market order | `is_long=false, is_increase=false, is_market=true` |
| `limit_close_long` | Close LONG with limit order | `is_long=true, is_increase=false, is_market=false` |
| `limit_close_short` | Close SHORT with limit order | `is_long=false, is_increase=false, is_market=false` |
| `add_to_position` | Add to existing position | `is_increase=true` |
| `add_collateral` | Add collateral only | `size=0, is_increase=true` |
| `partial_close` | Partial close position | `is_increase=false` |
| `full_close` | Full close position | `is_increase=false` |
| `custom` | Complete custom control | No auto parameters |

## 🛠️ Command Line Usage

### Basic Commands
```bash
# Generate all configuration files
python dexlyn_bot_sdk.py --generate-configs

# Generate field reference
python dexlyn_bot_sdk.py --generate-reference

# Run basic strategy
python dexlyn_bot_sdk.py --strategy basic_cycle

# Run with limited cycles
python dexlyn_bot_sdk.py --strategy basic_cycle --cycles 3

# Use custom config directory
python dexlyn_bot_sdk.py --config-dir ./my_configs
```

### Advanced Usage Examples

```bash
# Load custom strategy file
python dexlyn_bot_sdk.py --strategy-file my_strategy.json

# Multiple wallets strategy
python dexlyn_bot_sdk.py --strategy complete_examples --cycles 5

# Quick test with single order file
python dexlyn_bot_sdk.py --strategy-file quick_test.json --cycles 1
```

### Help Command
```bash
python dexlyn_bot_sdk.py --help
```


## 📋 Test Execution Commands

### Individual Test Categories
```bash
# Use the main bot with custom strategy file
python dexlyn_bot_sdk.py --strategy-file test_cases/basic_orders/basic_market_orders.json

# Run test suite
python run_all_tests.py --suite basic_market_orders

# List all available tests
python run_all_tests.py --list
```

## 🎯 Test Coverage Summary

### Order Types Covered:
- ✅ Market Open Long/Short
- ✅ Limit Open Long/Short  
- ✅ Market Close Long/Short
- ✅ Limit Close Long/Short
- ✅ Add to Position
- ✅ Add Collateral
- ✅ Partial Close
- ✅ Full Close
- ✅ Custom Orders

### Position Flows Covered:
- ✅ Complete Long Lifecycle
- ✅ Complete Short Lifecycle  
- ✅ Hedging Strategies
- ✅ Multi-Pair Trading
- ✅ Portfolio Distribution
- ✅ Scalping Strategies
- ✅ Recovery Strategies

### Risk Management Covered:
- ✅ Stop Loss Configurations
- ✅ Take Profit Configurations
- ✅ Position Sizing Variations
- ✅ Leverage Management
- ✅ Multi-Wallet Risk Distribution

### Advanced Scenarios:
- ✅ Units-Based Precision Trading
- ✅ High Frequency Ordering
- ✅ Large Position Testing
- ✅ Multi-Cycle Strategies
- ✅ Custom Parameter Control


## 🔧 Troubleshooting

### Common Issues

**1. SDK Installation Issues**
```
ModuleNotFoundError: No module named 'supra_sdk'
```
Solution: Install the Supra SDK:
```bash
pip install supra-sdk
```

**2. Private Key Format Error**
```
ValueError: Invalid private key format
```
Solution: Ensure private keys are 64-character hex strings:
```json
"private_key": "0x0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
```

**3. Testnet Funding Issues**
```
Warning: Could not check/fund account
```
Solution: 
- Check network connectivity
- Verify wallet address is correct
- Manually fund via testnet faucet if needed

**4. Transaction Failures**
```
Error: Transaction failed to submit
```
Solution:
- Check account balance
- Verify network status
- Increase gas fees in configuration
- Check contract address is correct

### Log Files

- `dexlyn_trading_sdk.log` - Main trading log with SDK details
- Check for detailed error messages and transaction hashes

### Debug Mode
For detailed debugging, modify `config.json`:
```json
"logging": {
  "level": "DEBUG",
  "log_file": "debug.log",
  "console_output": true
}
```

## 📋 Best Practices

### Security Best Practices
1. **Secure Private Keys**: Never store private keys in plain text in production
2. **Environment Variables**: Use environment variables for sensitive data
3. **Limited Permissions**: Use separate trading wallets with limited funds
4. **Regular Audits**: Review wallet permissions regularly
5. **Backup Configs**: Keep secure backups of wallet configurations

### Configuration Management
1. **Version Control**: Use git for strategy files (excluding private keys)
2. **Configuration Testing**: Test new strategies on testnet first
3. **Incremental Changes**: Make small changes and test thoroughly
4. **Documentation**: Document strategy logic and parameters
5. **Backup Strategies**: Keep working strategy backups

### Performance Optimization
1. **Network Selection**: Use appropriate RPC endpoints
2. **Batch Operations**: Group related orders in strategies
3. **Optimal Timing**: Adjust sleep intervals based on network conditions
4. **Error Handling**: Implement robust error recovery
5. **Monitoring**: Set up alerts for failed transactions

### Risk Management
1. **Position Sizing**: Never risk more than 2-5% per trade
2. **Stop Losses**: Always use stop losses for protection
3. **Leverage Management**: Use conservative leverage (10-20x recommended)
4. **Diversification**: Trade multiple pairs and strategies
5. **Capital Allocation**: Distribute funds across multiple wallets

## 🆘 Support

### Getting Help
1. Check the log file for detailed error messages
2. Verify all configuration files are properly formatted
3. Ensure your Supra SDK is properly installed
4. Test with the basic cycle strategy first

### Emergency Stop
To immediately stop the bot:
- Press `Ctrl+C` in the terminal
- The bot will complete the current order and stop gracefully

### Recovery Procedures
If the bot stops unexpectedly:
1. Check the last completed transaction in logs
2. Verify wallet balances via blockchain explorer
3. Check open positions on Dexlyn
4. Resume with adjusted strategy if needed

### Testing Procedures
```bash
# Step 1: Test network connection
python -c "from supra_sdk.clients.rest import SupraClient; print('✅ SDK imports work')"

# Step 2: Test configuration loading
python dexlyn_bot_sdk.py --generate-configs

# Step 3: Test basic strategy (small size)
# Edit strategy to use minimal amounts, then run:
python dexlyn_bot_sdk.py --strategy basic_cycle --cycles 1

# Step 4: Gradually increase complexity
```

## 🔄 Migration from CLI Version

If migrating from the CLI version:

1. **Install SDK**: `pip install supra-sdk`
2. **Convert Wallets**: Replace `profile` with `private_key` in `wallets.json`
3. **Remove Password**: No need for `SUPRA_CLI_PASSWORD` environment variable
4. **Update Commands**: Change script name from `dexlyn_bot.py` to `dexlyn_bot_sdk.py`
5. **Test Thoroughly**: Start with testnet and small amounts

## 📞 Need More Help?

If you encounter issues not covered in this documentation:

1. Check the `field_reference.json` for complete field documentation
2. Review the example strategies in `strategies.json`
3. Test with the basic cycle strategy to verify setup
4. Consult Supra SDK documentation for API details
5. Check network status and RPC endpoints

---

## 🎉 Ready to Trade!

You're now ready to use the Dexlyn Perpetuals Trading Bot SDK version. Remember:

✅ **Start Small**: Begin with testnet and small position sizes  
✅ **Secure First**: Keep private keys secure and backed up  
✅ **Test Thoroughly**: Validate strategies before committing capital  
✅ **Monitor Regularly**: Keep an eye on bot performance and logs  

Happy trading with the power of Supra SDK! 🚀