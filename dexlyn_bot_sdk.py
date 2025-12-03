#!/usr/bin/env python3
"""
🎯 DEXLYN PERPETUALS BOT - SUPRA SDK VERSION (CORRECTED)

A completely customizable trading bot using the official Supra SDK.
All order parameters can be set via JSON configuration with complete flexibility.

📁 CONFIGURATION FILES:
- config.json          → Main trading configuration
- network.json         → Network and contract settings  
- wallets.json         → Wallet addresses and private keys
- strategies.json      → Trading strategies and cycles
- pairs.json           → Trading pairs and defaults

🎯 KEY FEATURES:
✅ Every order field customizable via JSON
✅ Uses official Supra SDK with private keys
✅ Support for all place_order_v3 parameters
✅ Flexible order definitions
✅ Validation and error handling
✅ Same structure as CLI version
"""

import os
import sys
import time
import json
import logging
import asyncio
from typing import List, Dict, Any, Optional
from pathlib import Path
import dotenv

# Correct Supra SDK imports based on documentation
from supra_sdk.account import Account
from supra_sdk.clients.rest import SupraClient
from supra_sdk.transactions import EntryFunction, TransactionArgument, TransactionPayload
from supra_sdk.type_tag import TypeTag, StructTag
from supra_sdk.bcs import Serializer
from supra_sdk.account_address import AccountAddress

dotenv.load_dotenv()

# ========== DEFAULT CONFIGURATION PATHS ==========

CONFIG_PATHS = {
    "main": "config.json",
    "network": "network.json", 
    "wallets": "wallets.json",
    "strategies": "strategies.json",
    "pairs": "pairs.json"
}

RPC_URLS = {
    "testnet": "https://rpc-testnet.supra.com",
    "mainnet": "https://rpc-mainnet.supra.com"
}

# ========== COMPLETE ORDER FIELD DEFINITIONS ==========

COMPLETE_ORDER_FIELDS = {
    # Required core fields
    "action": {
        "type": "string",
        "required": True,
        "description": "Order action type",
        "options": [
            "market_open_long", "market_open_short", "limit_open_long", "limit_open_short",
            "market_close_long", "market_close_short", "limit_close_long", "limit_close_short",
            "add_to_position", "add_collateral", "partial_close", "full_close",
            "custom"  # For fully custom parameter specification
        ]
    },
    
    # Identification fields
    "name": {
        "type": "string", 
        "required": True,
        "description": "Order name for logging"
    },
    "pair": {
        "type": "string",
        "required": True,
        "description": "Trading pair from pairs.json"
    },
    "wallet": {
        "type": "string",
        "required": True,
        "description": "Wallet from wallets.json"
    },
    
    # Core order parameters (can be specified in USD or units)
    "size_usd": {
        "type": "number",
        "required": False,
        "description": "Position size in USD (auto-converted to units)",
        "default": 300.0
    },
    "size_units": {
        "type": "integer", 
        "required": False,
        "description": "Position size in blockchain units (overrides size_usd)"
    },
    "collateral_usd": {
        "type": "number",
        "required": False,
        "description": "Collateral in USD (auto-converted to units)",
        "default": 3.0
    },
    "collateral_units": {
        "type": "integer",
        "required": False, 
        "description": "Collateral in blockchain units (overrides collateral_usd)"
    },
    "price": {
        "type": "number",
        "required": False,
        "description": "Price in USD (auto-converted to units)",
        "default": 3500.0
    },
    "price_units": {
        "type": "integer",
        "required": False,
        "description": "Price in blockchain units (overrides price)"
    },
    
    # Boolean flags (all optional with smart defaults)
    "is_long": {
        "type": "boolean",
        "required": False,
        "description": "True for LONG, False for SHORT (auto-determined from action)"
    },
    "is_increase": {
        "type": "boolean", 
        "required": False,
        "description": "True to open/add, False to close/reduce (auto-determined from action)"
    },
    "is_market": {
        "type": "boolean",
        "required": False,
        "description": "True for market order, False for limit order (auto-determined from action)"
    },
    "can_execute_above_price": {
        "type": "boolean",
        "required": False,
        "description": "Execution guard (auto-calculated for optimal execution)"
    },
    
    # Risk management fields
    "stop_loss": {
        "type": "number",
        "required": False,
        "description": "Stop loss price in USD",
        "default": 0.0
    },
    "stop_loss_units": {
        "type": "integer",
        "required": False,
        "description": "Stop loss in units (overrides stop_loss)"
    },
    "take_profit": {
        "type": "number", 
        "required": False,
        "description": "Take profit price in USD",
        "default": 0.0
    },
    "take_profit_units": {
        "type": "integer",
        "required": False,
        "description": "Take profit in units (overrides take_profit)"
    },
    
    # Advanced parameters
    "reduce_only": {
        "type": "boolean",
        "required": False,
        "description": "Reduce only flag",
        "default": False
    },
    "post_only": {
        "type": "boolean",
        "required": False, 
        "description": "Post only flag",
        "default": False
    },
    
    # Custom raw parameters (for advanced users)
    "custom_parameters": {
        "type": "object",
        "required": False,
        "description": "Raw parameters for complete control (overrides all other fields)"
    },
    
    # Order metadata
    "description": {
        "type": "string",
        "required": False,
        "description": "Order description for reference"
    },
    "wait_before": {
        "type": "number",
        "required": False,
        "description": "Seconds to wait before executing this order",
        "default": 0
    },
    "condition": {
        "type": "object",
        "required": False,
        "description": "Execution conditions (future feature)"
    }
}

# ========== DEFAULT CONFIGURATIONS ==========

DEFAULT_CONFIG = {
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
        "auto_calculate_execution_guard": True
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
        "console_output": True
    }
}

DEFAULT_NETWORK = {
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

DEFAULT_WALLETS = {
    "trader_1": {
        "address": "0xyourownaddresshere",
        "private_key": "your_private_key_hex_here",
        "description": "Primary trading wallet"
    },
    "trader_2": {
        "address": "yourownaddresshere", 
        "private_key": "your_private_key_hex_here",
        "description": "Secondary trading wallet"
    }
}

DEFAULT_PAIRS = {
    "ETH_USD": {
        "type_arg": "ETH_USD",
        "description": "Ethereum vs US Dollar",
        "available_testnet": True,
        "available_mainnet": True,
        "default_size_usd": 300.0,
        "default_collateral_usd": 3.0,
        "default_price": 3500.0,
        "min_size_usd": 300.0,
        "max_size_usd": 500000.0
    },
    "BTC_USD": {
        "type_arg": "BTC_USD",
        "description": "Bitcoin vs US Dollar",
        "available_testnet": True,
        "available_mainnet": True,
        "default_size_usd": 300.0,
        "default_collateral_usd": 3.0,
        "default_price": 50000.0,
        "min_size_usd": 300.0,
        "max_size_usd": 500000.0
    }
}

DEFAULT_STRATEGIES = {
    "basic_cycle": {
        "name": "Basic ETH Open/Close Cycle",
        "description": "Simple cycle opening and closing both LONG and SHORT positions",
        "network": "testnet",
        "cycles": -1,
        "orders": [
            {
                "name": "Open LONG ETH - Market",
                "action": "market_open_long",
                "pair": "ETH_USD",
                "wallet": "trader_1",
                "size_usd": 300.0,
                "collateral_usd": 3.0,
                "price": 3500.0,
                "stop_loss": 3150.0,
                "take_profit": 3850.0,
                "description": "Open long position with market order"
            },
            {
                "name": "Open SHORT ETH - Market", 
                "action": "market_open_short",
                "pair": "ETH_USD",
                "wallet": "trader_2",
                "size_usd": 300.0,
                "collateral_usd": 3.0,
                "price": 3500.0,
                "stop_loss": 3850.0,
                "take_profit": 3150.0,
                "description": "Open short position with market order"
            }
        ]
    },
    "fully_custom": {
        "name": "Fully Custom Orders Example",
        "description": "Demonstrates complete customization of all order fields",
        "network": "testnet", 
        "cycles": 1,
        "orders": [
            {
                "name": "Custom Limit Long",
                "action": "custom",
                "pair": "ETH_USD",
                "wallet": "trader_1",
                "custom_parameters": {
                    "size_units": 500000000,
                    "collateral_units": 10000000, 
                    "price_units": 3550000000000000,
                    "is_long": True,
                    "is_increase": True,
                    "is_market": False,
                    "stop_loss_units": 3195000000000000,
                    "take_profit_units": 3905000000000000,
                    "can_execute_above_price": False
                },
                "description": "Completely custom limit long order with all fields specified in units"
            }
        ]
    }
}

# ========== CONFIGURATION MANAGER ==========

class ConfigManager:
    """Manage all configuration loading and validation"""
    
    def __init__(self, config_dir: str = "."):
        self.config_dir = Path(config_dir)
        self.configs = {}
        
    def load_all_configs(self) -> Dict[str, Any]:
        """Load all configuration files (NOT strategies)"""
        self.configs = {
            "main": self.load_json_config(CONFIG_PATHS["main"], DEFAULT_CONFIG),
            "network": self.load_json_config(CONFIG_PATHS["network"], DEFAULT_NETWORK),
            "wallets": self.load_json_config(CONFIG_PATHS["wallets"], DEFAULT_WALLETS),
            "pairs": self.load_json_config(CONFIG_PATHS["pairs"], DEFAULT_PAIRS),
            "strategies": self.load_json_config(CONFIG_PATHS["strategies"], DEFAULT_STRATEGIES)
        }
        
        self.validate_configs()
        return self.configs
    
    def load_strategy_file(self, strategy_file_path: str) -> Dict[str, Any]:
        """Load a custom strategy file and return strategies dict"""
        path = Path(strategy_file_path)
        if not path.exists():
            raise FileNotFoundError(f"Strategy file not found: {strategy_file_path}")
        
        with open(path, 'r') as f:
            strategy_data = json.load(f)
        
        # Strategy files should contain one or more strategies
        if not isinstance(strategy_data, dict):
            raise ValueError("Strategy file must contain a JSON object")
        
        # Validate it contains at least one strategy-like structure
        valid_strategies = {}
        for key, value in strategy_data.items():
            if isinstance(value, dict) and 'orders' in value:
                valid_strategies[key] = value
            else:
                logging.warning(f"⚠️ Entry '{key}' in strategy file doesn't look like a valid strategy")
        
        if not valid_strategies:
            raise ValueError("No valid strategies found in strategy file")
        
        logging.info(f"✅ Loaded {len(valid_strategies)} strategies from: {strategy_file_path}")
        return valid_strategies
    
    def get_strategy(self, strategy_name: str = None) -> Dict:
        """Get strategy configuration"""
        if strategy_name is None:
            strategy_name = self.configs["main"]["default_strategy"]
        
        if strategy_name not in self.configs["strategies"]:
            available = list(self.configs["strategies"].keys())
            raise ValueError(f"Strategy '{strategy_name}' not found. Available: {available}")
        
        return self.configs["strategies"][strategy_name]

    def load_json_config(self, file_path: str, default_config: Dict = None) -> Dict:
        """Load JSON config file or return default if not exists"""
        path = self.config_dir / file_path
        
        if path.exists():
            try:
                with open(path, 'r') as f:
                    config = json.load(f)
                logging.info(f"✅ Loaded config: {file_path}")
                return config
            except Exception as e:
                logging.warning(f"⚠️ Failed to load {file_path}: {e}, using defaults")
        
        if default_config is not None:
            self.create_default_config(path, default_config)
            return default_config.copy()
        else:
            return {}

    def create_default_config(self, path: Path, default_config: Dict):
        """Create default config file for user to edit"""
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, 'w') as f:
                json.dump(default_config, f, indent=2)
            logging.info(f"📝 Created default config: {path}")
        except Exception as e:
            logging.error(f"❌ Failed to create default config {path}: {e}")
    
    def validate_configs(self):
        """Validate all loaded configurations"""
        network = self.configs["main"]["network"]
        if network not in self.configs["network"]:
            raise ValueError(f"Network '{network}' not found in network configuration")
        
        strategy = self.configs["main"]["default_strategy"]
        if strategy not in self.configs["strategies"]:
            raise ValueError(f"Strategy '{strategy}' not found in strategies configuration")
    
    def get_network_config(self, network: str = None) -> Dict:
        """Get network-specific configuration"""
        if network is None:
            network = self.configs["main"]["network"]
        return self.configs["network"][network]
    
    def get_strategy(self, strategy_name: str = None) -> Dict:
        """Get strategy configuration"""
        if strategy_name is None:
            strategy_name = self.configs["main"]["default_strategy"]
        return self.configs["strategies"][strategy_name]
    
    def get_wallet(self, wallet_name: str) -> Dict:
        """Get wallet configuration"""
        return self.configs["wallets"][wallet_name]
    
    def get_pair(self, pair_name: str) -> Dict:
        """Get trading pair configuration"""
        return self.configs["pairs"][pair_name]

# ========== SUPRA SDK CLIENT MANAGER ==========

class SupraSDKClientManager:
    """Manage Supra SDK clients and accounts using correct SDK structure"""
    
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.network = config_manager.configs["main"]["network"]
        self.rpc_url = RPC_URLS[self.network]
        self.clients = {}
        self.accounts = {}
        
    async def get_client_and_account(self, wallet_name: str) -> tuple[SupraClient, Account]:
        """Get or create SupraClient and Account for a specific wallet"""
        if wallet_name in self.clients:
            return self.clients[wallet_name], self.accounts[wallet_name]
            
        wallet_config = self.config_manager.get_wallet(wallet_name)
        private_key_hex = wallet_config.get("private_key")
        
        if not private_key_hex or private_key_hex == "your_private_key_hex_here":
            raise ValueError(f"Private key not configured for wallet: {wallet_name}")
        
        try:
            # Initialize client
            client = SupraClient(self.rpc_url)
            
            # Load account from private key
            account = Account.load_key(private_key_hex)
            
            # Verify account address matches configuration
            expected_address = wallet_config['address']
            actual_address = account.address().__str__()
            
            if expected_address != actual_address:
                logging.warning(f"⚠️ Wallet {wallet_name} address mismatch: config={expected_address}, actual={actual_address}")
            
            # Fund account if needed (for testnet)
            if self.network == "testnet":
                try:
                    balance = await client.account_coin_balance(account.address(), "0x1::supra_coin::SupraCoin")
                    print("Balance:", balance)
                    if balance == 0:
                        logging.info(f"💰 Funding testnet account: {wallet_name}")
                        tx_hash = await client.faucet(account.address())
                        if tx_hash:
                            logging.info(f"✅ Faucet transaction: {tx_hash}")
                            # Wait for faucet to complete
                            await asyncio.sleep(5)
                except Exception as e:
                    logging.warning(f"⚠️ Could not check/fund account {wallet_name}: {e}")
            
            self.clients[wallet_name] = client
            self.accounts[wallet_name] = account
            
            logging.info(f"✅ SDK client and account initialized for wallet: {wallet_name}")
            return client, account
            
        except Exception as e:
            logging.error(f"❌ Failed to initialize SDK client for {wallet_name}: {e}")
            raise
    
    async def close_all(self):
        """Close all client connections"""
        for client in self.clients.values():
            await client.close()

# ========== ADVANCED TRADING ENGINE ==========

class AdvancedTradingEngine:
    """Trading engine with complete order field customization using correct SDK"""
    
    def __init__(self, config_manager: ConfigManager, sdk_manager: SupraSDKClientManager):
        self.config_manager = config_manager
        self.sdk_manager = sdk_manager
        self.network = config_manager.configs["main"]["network"]
        self.network_config = config_manager.get_network_config()
        
    def usd_to_units(self, usd_amount: float, decimal_type: str = "size") -> int:
        """Convert USD amount to blockchain units"""
        decimals = self.network_config[f"{decimal_type}_decimals"]
        return int(usd_amount * (10 ** decimals))
    
    def price_to_units(self, price: float) -> int:
        """Convert price to blockchain units"""
        return int(price * (10 ** self.network_config["price_decimals"]))
    
    def build_order_arguments(self, order_config: Dict) -> List[TransactionArgument]:
        """Build order arguments for SDK transaction"""
        
        # If custom_parameters is provided, use them directly
        if "custom_parameters" in order_config:
            return self.build_custom_order_arguments(order_config)
        
        # Otherwise, build arguments from individual fields
        return self.build_standard_order_arguments(order_config)
    
    def build_custom_order_arguments(self, order_config: Dict) -> List[TransactionArgument]:
        """Build arguments using completely custom parameters"""
        custom_params = order_config["custom_parameters"]
        wallet = self.config_manager.get_wallet(order_config["wallet"])
        
        # Validate required custom parameters
        required_fields = ["size_units", "collateral_units", "price_units", 
                          "is_long", "is_increase", "is_market", "can_execute_above_price"]
        
        for field in required_fields:
            if field not in custom_params:
                raise ValueError(f"Custom order missing required field: {field}")
        
        logging.info(f"🎯 Building CUSTOM order: {order_config['name']}")
        
        # Convert wallet address to AccountAddress
        wallet_address = AccountAddress.from_str(wallet['address'])
        
        return [
            TransactionArgument(wallet_address, Serializer.struct),  # address
            TransactionArgument(custom_params['size_units'], Serializer.u64),  # u64
            TransactionArgument(custom_params['collateral_units'], Serializer.u64),  # u64
            TransactionArgument(custom_params['price_units'], Serializer.u64),  # u64
            TransactionArgument(custom_params['is_long'], Serializer.bool),  # bool
            TransactionArgument(custom_params['is_increase'], Serializer.bool),  # bool
            TransactionArgument(custom_params['is_market'], Serializer.bool),  # bool
            TransactionArgument(custom_params.get('stop_loss_units', 0), Serializer.u64),  # u64
            TransactionArgument(custom_params.get('take_profit_units', 0), Serializer.u64),  # u64
            TransactionArgument(custom_params['can_execute_above_price'], Serializer.bool),  # bool
            TransactionArgument(AccountAddress.from_str("0x0"), Serializer.struct)  # address (0x0)
        ]
    
    def build_standard_order_arguments(self, order_config: Dict) -> List[TransactionArgument]:
        """Build arguments using standard field definitions"""
        
        # Get configuration
        pair_config = self.config_manager.get_pair(order_config["pair"])
        wallet = self.config_manager.get_wallet(order_config["wallet"])
        
        # Convert amounts to units (prefer explicit units over USD conversions)
        size_units = self.get_size_units(order_config, pair_config)
        collateral_units = self.get_collateral_units(order_config, pair_config)
        price_units = self.get_price_units(order_config, pair_config)
        stop_loss_units = self.get_stop_loss_units(order_config)
        take_profit_units = self.get_take_profit_units(order_config)
        
        # Determine order type parameters
        action = order_config["action"]
        is_long, is_increase, is_market = self.parse_action_flags(action, order_config)
        
        # Calculate execution guard (can be overridden)
        auto_calculate = self.config_manager.configs["main"]["orders"]["auto_calculate_execution_guard"]
        if "can_execute_above_price" in order_config:
            can_execute_above = order_config["can_execute_above_price"]
        elif auto_calculate:
            can_execute_above = self.calculate_execution_guard(is_long, is_increase, is_market)
        else:
            can_execute_above = True  # Default safe value
        
        # Convert wallet address to AccountAddress
        wallet_address = AccountAddress.from_str(wallet['address'])
        
        logging.info(f"📊 Building order: {order_config['name']}")
        logging.info(f"   Size: {size_units} units")
        logging.info(f"   Collateral: {collateral_units} units")
        logging.info(f"   Price: {price_units} units")
        logging.info(f"   Execution: Long={is_long}, Increase={is_increase}, Market={is_market}")
        logging.info(f"   Guard: can_execute_above_price={can_execute_above}")
        
        return [
            TransactionArgument(wallet_address, Serializer.struct),  # address
            TransactionArgument(size_units, Serializer.u64),  # u64
            TransactionArgument(collateral_units, Serializer.u64),  # u64
            TransactionArgument(price_units, Serializer.u64),  # u64
            TransactionArgument(is_long, Serializer.bool),  # bool
            TransactionArgument(is_increase, Serializer.bool),  # bool
            TransactionArgument(is_market, Serializer.bool),  # bool
            TransactionArgument(stop_loss_units, Serializer.u64),  # u64
            TransactionArgument(take_profit_units, Serializer.u64),  # u64
            TransactionArgument(can_execute_above, Serializer.bool),  # bool
            TransactionArgument(AccountAddress.from_str("0x0"), Serializer.struct)  # address (0x0)
        ]
    
    def get_size_units(self, order_config: Dict, pair_config: Dict) -> int:
        """Get size in units, preferring explicit units over USD conversion"""
        if "size_units" in order_config:
            return order_config["size_units"]
        elif "size_usd" in order_config:
            return self.usd_to_units(order_config["size_usd"], "size")
        else:
            return self.usd_to_units(pair_config["default_size_usd"], "size")
    
    def get_collateral_units(self, order_config: Dict, pair_config: Dict) -> int:
        """Get collateral in units"""
        if "collateral_units" in order_config:
            return order_config["collateral_units"]
        elif "collateral_usd" in order_config:
            return self.usd_to_units(order_config["collateral_usd"], "collateral")
        else:
            return self.usd_to_units(pair_config["default_collateral_usd"], "collateral")
    
    def get_price_units(self, order_config: Dict, pair_config: Dict) -> int:
        """Get price in units"""
        if "price_units" in order_config:
            return order_config["price_units"]
        elif "price" in order_config:
            return self.price_to_units(order_config["price"])
        else:
            return self.price_to_units(pair_config["default_price"])
    
    def get_stop_loss_units(self, order_config: Dict) -> int:
        """Get stop loss in units"""
        if "stop_loss_units" in order_config:
            return order_config["stop_loss_units"]
        elif "stop_loss" in order_config and order_config["stop_loss"] > 0:
            return self.price_to_units(order_config["stop_loss"])
        else:
            return 0
    
    def get_take_profit_units(self, order_config: Dict) -> int:
        """Get take profit in units"""
        if "take_profit_units" in order_config:
            return order_config["take_profit_units"]
        elif "take_profit" in order_config and order_config["take_profit"] > 0:
            return self.price_to_units(order_config["take_profit"])
        else:
            return 0
    
    def parse_action_flags(self, action: str, order_config: Dict) -> tuple:
        """Parse action and determine order flags with manual override support"""
        
        # Action type mappings
        action_map = {
            "market_open_long": (True, True, True),
            "market_open_short": (False, True, True),
            "limit_open_long": (True, True, False),
            "limit_open_short": (False, True, False),
            "market_close_long": (True, False, True),
            "market_close_short": (False, False, True),
            "limit_close_long": (True, False, False),
            "limit_close_short": (False, False, False),
            "add_to_position": (order_config.get("is_long", True), True, order_config.get("is_market", True)),
            "add_collateral": (order_config.get("is_long", True), True, True),
            "partial_close": (order_config.get("is_long", True), False, order_config.get("is_market", True)),
            "full_close": (order_config.get("is_long", True), False, order_config.get("is_market", True)),
            "custom": (order_config.get("is_long", True), order_config.get("is_increase", True), order_config.get("is_market", True))
        }
        
        if action not in action_map:
            raise ValueError(f"Unknown action: {action}")
        
        default_long, default_increase, default_market = action_map[action]
        
        # Allow manual override of any flag
        is_long = order_config.get("is_long", default_long)
        is_increase = order_config.get("is_increase", default_increase)
        is_market = order_config.get("is_market", default_market)
        
        return is_long, is_increase, is_market
    
    def calculate_execution_guard(self, is_long: bool, is_increase: bool, is_market: bool) -> bool:
        """Calculate optimal execution guard"""
        if is_increase and is_long:
            return False  # Buy at or below target
        elif is_increase and not is_long:
            return True   # Sell at or above target
        elif not is_increase and is_long:
            return True   # Sell at or above target
        else:  # not is_increase and not is_long
            return False  # Buy at or below target

    def build_type_arguments(self, order_config: Dict) -> List[TypeTag]:
        """Build type arguments for the transaction"""
        pair_config = self.config_manager.get_pair(order_config["pair"])
        network_config = self.network_config
        
        # Parse the struct tags from strings
        pair_type = StructTag.from_str(f"{network_config['contract_address']}::pair_types::{pair_config['type_arg']}")
        collateral_type = StructTag.from_str(network_config['collateral_token'])
        
        return [
            TypeTag(pair_type),
            TypeTag(collateral_type)
        ]

    def create_order_payload(self, order_config: Dict) -> TransactionPayload:
        """Create the complete transaction payload for placing an order"""
        function_args = self.build_order_arguments(order_config)
        type_args = self.build_type_arguments(order_config)
        network_config = self.network_config
        
        # Create entry function for place_order_v3
        entry_function = EntryFunction.natural(
            f"{network_config['contract_address']}::managed_trading",
            "place_order_v3",
            type_args,
            function_args
        )
        
        return TransactionPayload(entry_function)

# ========== TRADE EXECUTOR ==========

class AdvancedTradeExecutor:
    """Execute trades with complete field customization using correct SDK"""
    
    def __init__(self, config_manager: ConfigManager, engine: AdvancedTradingEngine, sdk_manager: SupraSDKClientManager):
        self.config_manager = config_manager
        self.engine = engine
        self.sdk_manager = sdk_manager
        
    async def execute_order(self, order_config: Dict) -> bool:
        """Execute a single order with complete customization using SDK"""
        try:
            # Handle wait_before if specified
            wait_before = order_config.get("wait_before", 0)
            if wait_before > 0:
                logging.info(f"⏳ Waiting {wait_before} seconds before order...")
                await asyncio.sleep(wait_before)
            
            # Get SDK client and account for the wallet
            client, account = await self.sdk_manager.get_client_and_account(order_config["wallet"])
            
            # Create order payload
            payload = self.engine.create_order_payload(order_config)
            
            logging.info(f"🤖 Executing: {order_config['name']}")
            if order_config.get("description"):
                logging.info(f"📝 Description: {order_config['description']}")
            
            # Create and submit signed transaction
            signed_txn = await client.create_signed_transaction(account, payload)
            result = await client.submit_transaction(signed_txn)
            
            if result:
                logging.info(f"✅ {order_config['name']} - SUCCESS")
                logging.info(f"📄 Transaction Hash: {result}")
                return True
            else:
                logging.error(f"❌ {order_config['name']} - FAILED: No transaction hash returned")
                return False
                
        except Exception as e:
            logging.error(f"❌ {order_config['name']} - FAILED: {e}")
            return False
    
    async def execute_strategy(self, strategy_name: str = None) -> bool:
        """Execute a complete trading strategy"""
        strategy = self.config_manager.get_strategy(strategy_name)
        orders = strategy.get("orders", [])
        
        logging.info(f"🔄 Executing strategy: {strategy['name']}")
        logging.info(f"📝 Description: {strategy['description']}")
        
        success_count = 0
        for i, order in enumerate(orders, 1):
            logging.info(f"📊 [{i}/{len(orders)}] Processing: {order['name']}")
            
            success = await self.execute_order(order)
            if success:
                success_count += 1
            
            # Sleep between orders (except last one)
            if i < len(orders):
                sleep_time = self.config_manager.configs["main"]["timing"]["sleep_between_orders"]
                logging.info(f"⏳ Waiting {sleep_time} seconds...")
                await asyncio.sleep(sleep_time)
        
        logging.info(f"🎯 Strategy completed: {success_count}/{len(orders)} orders successful")
        return success_count == len(orders)

# ========== CONFIGURATION GENERATORS ==========

def generate_complete_config_files():
    """Generate all configuration files with complete examples"""
    
    # Enhanced strategies with complete field examples
    enhanced_strategies = {
        **DEFAULT_STRATEGIES,
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
                    "take_profit": 3905.0,
                    "description": "Using USD amounts (auto-converted to units)"
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
                    "take_profit_units": 3240000000000000,
                    "description": "Using exact blockchain units"
                },
                {
                    "name": "Manual Flags Override",
                    "action": "add_to_position",
                    "pair": "ETH_USD", 
                    "wallet": "trader_1",
                    "size_usd": 300.0,
                    "is_long": False,  # Override default
                    "is_market": True, # Override default  
                    "can_execute_above_price": True,  # Manual execution guard
                    "description": "Manually overriding auto-calculated flags"
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
                        "is_long": True,
                        "is_increase": True, 
                        "is_market": False,
                        "stop_loss_units": 3285000000000000,
                        "take_profit_units": 4015000000000000,
                        "can_execute_above_price": False
                    },
                    "description": "Complete control with raw parameters"
                },
                {
                    "name": "Delayed Order Execution",
                    "action": "market_close_long", 
                    "pair": "ETH_USD",
                    "wallet": "trader_1",
                    "size_usd": 300.0,
                    "wait_before": 10,
                    "description": "Waits 10 seconds before executing"
                }
            ]
        }
    }
    
    configs = {
        "config.json": DEFAULT_CONFIG,
        "network.json": DEFAULT_NETWORK,
        "wallets.json": DEFAULT_WALLETS,
        "pairs.json": DEFAULT_PAIRS,
        "strategies.json": enhanced_strategies
    }
    
    for filename, config in configs.items():
        with open(filename, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"✅ Generated {filename}")
    
    # Generate field reference
    generate_field_reference()

def generate_field_reference():
    """Generate a reference file showing all available order fields"""
    reference = {
        "order_field_reference": COMPLETE_ORDER_FIELDS,
        "examples": {
            "simple_usd_based_order": {
                "name": "Simple USD-Based Order",
                "action": "market_open_long", 
                "pair": "ETH_USD",
                "wallet": "trader_1",
                "size_usd": 100.0,
                "collateral_usd": 50.0,
                "price": 3500.0
            },
            "advanced_units_based_order": {
                "name": "Advanced Units-Based Order",
                "action": "limit_open_short",
                "pair": "ETH_USD",
                "wallet": "trader_2", 
                "size_units": 50000000,
                "collateral_units": 25000000,
                "price_units": 3600000000000000,
                "stop_loss_units": 3960000000000000,
                "take_profit_units": 3240000000000000,
                "is_long": False,
                "is_increase": True,
                "is_market": False,
                "can_execute_above_price": True
            },
            "completely_custom_order": {
                "name": "Completely Custom Order",
                "action": "custom",
                "pair": "ETH_USD",
                "wallet": "trader_1",
                "custom_parameters": {
                    "size_units": 100000000,
                    "collateral_units": 50000000,
                    "price_units": 3500000000000000,
                    "is_long": True,
                    "is_increase": True,
                    "is_market": True,
                    "stop_loss_units": 3150000000000000,
                    "take_profit_units": 3850000000000000,
                    "can_execute_above_price": False
                }
            }
        }
    }
    
    with open("field_reference.json", 'w') as f:
        json.dump(reference, f, indent=2)
    print("✅ Generated field_reference.json")

# ========== MAIN BOT CONTROLLER ==========

class AdvancedDexlynTradingBot:
    """Main trading bot controller with complete customization using correct SDK"""
    
    def __init__(self, config_dir: str = "."):
        self.config_manager = ConfigManager(config_dir)
        self.configs = self.config_manager.load_all_configs()
        self.sdk_manager = SupraSDKClientManager(self.config_manager)
        self.engine = AdvancedTradingEngine(self.config_manager, self.sdk_manager)
        self.executor = AdvancedTradeExecutor(self.config_manager, self.engine, self.sdk_manager)
    
    def load_custom_strategies(self, strategy_file_path: str):
        """Load custom strategies from a file"""
        custom_strategies = self.config_manager.load_strategy_file(strategy_file_path)
        # Merge with existing strategies (custom strategies override existing ones with same name)
        self.configs["strategies"].update(custom_strategies)
        self.config_manager.configs["strategies"].update(custom_strategies)
        
        strategy_names = list(custom_strategies.keys())
        logging.info(f"📈 Loaded custom strategies: {', '.join(strategy_names)}")
        return strategy_names
    
    async def run(self, strategy_name: str = None, cycles: int = None):
        """Run the trading bot"""
        if strategy_name is None:
            strategy_name = self.configs["main"]["default_strategy"]
        
        strategy = self.config_manager.get_strategy(strategy_name)
        if cycles is None:
            cycles = strategy.get("cycles", -1)
        
        logging.info("🚀 DEXLYN ADVANCED TRADING BOT STARTING (SDK VERSION)")
        logging.info(f"🌐 Network: {self.configs['main']['network']}")
        logging.info(f"📈 Strategy: {strategy['name']}")
        logging.info(f"🔁 Cycles: {'Infinite' if cycles == -1 else cycles}")
        logging.info(f"📊 Orders in strategy: {len(strategy.get('orders', []))}")
        
        cycle_count = 0
        try:
            while cycles == -1 or cycle_count < cycles:
                cycle_count += 1
                logging.info(f"\n🎯 CYCLE #{cycle_count}")
                
                success = await self.executor.execute_strategy(strategy_name)
                
                if cycles == -1 or cycle_count < cycles:
                    sleep_time = self.configs["main"]["timing"]["sleep_between_cycles"]
                    logging.info(f"😴 Sleeping {sleep_time} seconds...")
                    await asyncio.sleep(sleep_time)
                    
        except KeyboardInterrupt:
            logging.info("\n🛑 Trading bot stopped by user")
        except Exception as e:
            logging.error(f"💥 Unexpected error: {e}")
        finally:
            # Clean up SDK connections
            await self.sdk_manager.close_all()

# ========== MAIN ENTRY ==========

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Dexlyn Perpetuals Trading Bot - Corrected SDK Version with Complete Field Customization",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
🎯 CORRECTED SUPRA SDK VERSION - COMPLETE FIELD CUSTOMIZATION:

USES OFFICIAL SUPRA SDK STRUCTURE:
✅ Uses SupraClient from supra_sdk.clients.rest
✅ Uses Account from supra_sdk.account  
✅ Uses TransactionPayload, EntryFunction, TransactionArgument
✅ Uses proper TypeTag and StructTag for type arguments
✅ Uses correct BCS Serializer for arguments

KEY FEATURES:
✅ No CLI dependencies - pure Python SDK
✅ Private key authentication
✅ Automatic testnet faucet funding
✅ Proper transaction building and submission
✅ Same field customization as CLI version

SETUP REQUIREMENTS:
1. Install supra-sdk: pip install supra-sdk
2. Set private keys in wallets.json as hex strings
3. No environment variables needed

ORDER FIELDS - YOU CAN CUSTOMIZE EVERYTHING:

Basic Fields (Auto-converted):
  size_usd: 100.0           → Position size in USD
  collateral_usd: 50.0       → Collateral in USD  
  price: 3500.0              → Price in USD

Advanced Fields (Exact units):
  size_units: 50000000       → Exact size in blockchain units
  collateral_units: 25000000 → Exact collateral in units
  price_units: 3500000000000000 → Exact price in units

Complete Control:
  custom_parameters:         → Raw parameters for full control

QUICK START:
1. Generate configs: python {sys.argv[0]} --generate-configs
2. Edit wallets.json with your private keys (hex format)
3. Run: python {sys.argv[0]} --strategy complete_examples

EXAMPLES:
  python {sys.argv[0]} --strategy basic_cycle
  python {sys.argv[0]} --strategy-file my_strategy.json
        """
    )
    
    parser.add_argument("--generate-configs", action="store_true", help="Generate all configuration files with examples")
    parser.add_argument("--generate-reference", action="store_true", help="Generate field reference file")
    parser.add_argument("--strategy", help="Strategy name to execute")
    parser.add_argument("--cycles", type=int, help="Number of cycles to run")
    parser.add_argument("--config-dir", default=".", help="Configuration directory")
    parser.add_argument("--strategy-file", help="Custom strategy JSON file to load")    
    args = parser.parse_args()
    
    # Setup logging
    log_config = DEFAULT_CONFIG.get("logging", {})
    log_config = ConfigManager(args.config_dir).load_json_config(CONFIG_PATHS["main"], DEFAULT_CONFIG).get("logging", log_config)
    env_level = log_config["level"] if log_config["level"] else "INFO"
    log_file = log_config.get("log_file", "dexlyn_trading_sdk.log")
    console_output = log_config.get("console_output", True)
    
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, env_level.upper()))
    
    # Update file handler if different file
    if console_output:
        if not any(isinstance(handler, logging.StreamHandler) for handler in logger.handlers):
            logger.addHandler(logging.StreamHandler())
    for handler in logger.handlers:
        if isinstance(handler, logging.FileHandler):
            logger.removeHandler(handler)
    new_handler = logging.FileHandler(log_file, encoding='utf-8')
    logger.addHandler(new_handler)
    
    print("\n=== DEXLYN PERPETUALS TRADING BOT - CORRECTED SUPRA SDK VERSION ===\n")
    
    if args.generate_configs:
        generate_complete_config_files()
        print("🎉 All configuration files generated with complete examples!")
        print("📚 See field_reference.json for all available fields")
        return
    
    if args.generate_reference:
        generate_field_reference()
        print("✅ Field reference generated!")
        return
    
    print("🔐 Using private keys from wallets.json configuration")
    print("💡 Make sure you have set your private keys in wallets.json")

    try:
        # Initialize bot with configurations
        bot = AdvancedDexlynTradingBot(args.config_dir)
        
        # Load custom strategy file if provided
        if args.strategy_file:
            loaded_strategies = bot.load_custom_strategies(args.strategy_file)
            print(f"📈 Loaded strategies: {', '.join(loaded_strategies)}")
            
            # If no specific strategy specified, use the first loaded one
            if not args.strategy and loaded_strategies:
                args.strategy = loaded_strategies[0]
                print(f"🎯 Using strategy: {args.strategy}")
        
        print("🚀 Starting trading bot (Corrected SDK version)...")
        
        # Run the async bot
        asyncio.run(bot.run(args.strategy, args.cycles))
        
    except Exception as e:
        logging.error(f"❌ Failed to start bot: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()