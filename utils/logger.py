import logging
import os
from datetime import datetime
from pathlib import Path


class Logger:
    """Centralized logging for JARVIS AI"""

    def __init__(self, name="jarvis", log_level=logging.INFO, log_file=None):
        """
        Initialize logger

        Args:
            name (str): Logger name
            log_level: Logging level
            log_file (str, optional): Log file path
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(log_level)

        # Clear existing handlers
        self.logger.handlers.clear()

        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # File handler (if log file specified)
        if log_file:
            self._setup_file_handler(log_file, formatter)
        else:
            # Default log file in logs directory
            logs_dir = Path("logs")
            logs_dir.mkdir(exist_ok=True)
            log_file = logs_dir / f"jarvis_{datetime.now().strftime('%Y%m%d')}.log"
            self._setup_file_handler(log_file, formatter)

    def _setup_file_handler(self, log_file, formatter):
        """Setup file handler for logging"""
        try:
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)  # More verbose file logging
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
        except Exception as e:
            print(f"⚠️ Could not setup file logging: {e}")

    def debug(self, message):
        """Log debug message"""
        self.logger.debug(message)

    def info(self, message):
        """Log info message"""
        self.logger.info(message)

    def warning(self, message):
        """Log warning message"""
        self.logger.warning(message)

    def error(self, message):
        """Log error message"""
        self.logger.error(message)

    def critical(self, message):
        """Log critical message"""
        self.logger.critical(message)

    def log_command(self, command, interpretation=None, result=None):
        """
        Log a command with its interpretation and result

        Args:
            command (str): Original command
            interpretation (dict, optional): Command interpretation
            result (dict, optional): Command result
        """
        self.info(f"COMMAND: {command}")
        if interpretation:
            self.debug(f"INTERPRETATION: {interpretation}")
        if result:
            self.info(f"RESULT: {result.get('success', False)} - {result.get('response', '')}")

    def log_api_call(self, endpoint, data=None, response=None):
        """
        Log API calls

        Args:
            endpoint (str): API endpoint
            data (dict, optional): Request data
            response (dict, optional): Response data
        """
        self.info(f"API_CALL: {endpoint}")
        if data:
            self.debug(f"REQUEST_DATA: {data}")
        if response:
            self.debug(f"RESPONSE_DATA: {response}")

    def log_error_with_traceback(self, message, exception=None):
        """
        Log error with full traceback

        Args:
            message (str): Error message
            exception (Exception, optional): Exception object
        """
        if exception:
            import traceback
            self.error(f"{message}: {str(exception)}\n{traceback.format_exc()}")
        else:
            self.error(message)

    def log_system_info(self, info):
        """
        Log system information

        Args:
            info (dict): System information
        """
        self.info("SYSTEM_INFO:")
        for key, value in info.items():
            self.info(f"  {key}: {value}")

    def create_module_logger(self, module_name):
        """
        Create a logger for a specific module

        Args:
            module_name (str): Module name

        Returns:
            Logger: Module-specific logger
        """
        return logging.getLogger(f"jarvis.{module_name}")

    @staticmethod
    def get_logger(name="jarvis"):
        """
        Get or create a logger instance

        Args:
            name (str): Logger name

        Returns:
            Logger: Logger instance
        """
        # Check if logger already exists and has handlers
        logger = logging.getLogger(name)
        if not logger.handlers:
            # Create new logger instance
            return Logger(name)
        return logger


# Global logger instance
logger = Logger.get_logger()