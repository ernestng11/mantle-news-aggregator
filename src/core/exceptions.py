"""
Custom exceptions for the application
"""

class PGOnchainError(Exception):
    """Base exception for PG Onchain application"""
    pass

class ConfigurationError(PGOnchainError):
    """Raised when configuration is invalid"""
    pass

class TelegramError(PGOnchainError):
    """Raised when Telegram operations fail"""
    pass

class TradingError(PGOnchainError):
    """Raised when trading operations fail"""
    pass

class OrderError(TradingError):
    """Raised when order operations fail"""
    pass

class WalletError(TradingError):
    """Raised when wallet operations fail"""
    pass

class ValidationError(PGOnchainError):
    """Raised when input validation fails"""
    pass 