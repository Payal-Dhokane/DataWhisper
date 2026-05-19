"""Validation utilities for request validation and error handling."""

import pandas as pd
import streamlit as st
from dataclasses import dataclass
from typing import Optional, Any, Dict, List
import json


@dataclass
class ValidationResult:
    """Structured validation result."""
    is_valid: bool
    error_message: Optional[str] = None
    error_code: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "error_message": self.error_message,
            "error_code": self.error_code
        }
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict())
    
    def show_error(self) -> bool:
        if not self.is_valid and self.error_message:
            st.error(self.error_message)
            return True
        return False


class RequestValidator:
    """Validates incoming requests and data payloads."""
    
    @staticmethod
    def validate_csv_file(uploaded_file) -> ValidationResult:
        """Validate uploaded CSV file."""
        if uploaded_file is None:
            return ValidationResult(
                is_valid=False,
                error_message="No file uploaded. Please upload a CSV file.",
                error_code="NO_FILE"
            )
        
        if hasattr(uploaded_file, 'name') and not uploaded_file.name.endswith('.csv'):
            return ValidationResult(
                is_valid=False,
                error_message="Invalid file type. Only CSV files are supported.",
                error_code="INVALID_FILE_TYPE"
            )
        
        if hasattr(uploaded_file, 'size'):
            if uploaded_file.size == 0:
                return ValidationResult(
                    is_valid=False,
                    error_message="The uploaded file is empty.",
                    error_code="EMPTY_FILE"
                )
            if uploaded_file.size > 50 * 1024 * 1024:  # 50MB
                return ValidationResult(
                    is_valid=False,
                    error_message="File too large. Maximum size is 50MB.",
                    error_code="FILE_TOO_LARGE"
                )
        
        return ValidationResult(is_valid=True)
    
    @staticmethod
    def validate_dataframe(df: Optional[pd.DataFrame]) -> ValidationResult:
        """Validate pandas DataFrame."""
        if df is None:
            return ValidationResult(
                is_valid=False,
                error_message="No data available. Please upload a dataset first.",
                error_code="NO_DATA"
            )
        
        if df.empty:
            return ValidationResult(
                is_valid=False,
                error_message="The dataset is empty.",
                error_code="EMPTY_DATASET"
            )
        
        if df.shape[0] < 2:
            return ValidationResult(
                is_valid=False,
                error_message="Dataset must have at least 2 rows for analysis.",
                error_code="INSUFFICIENT_ROWS"
            )
        
        if df.shape[1] < 1:
            return ValidationResult(
                is_valid=False,
                error_message="Dataset must have at least 1 column.",
                error_code="NO_COLUMNS"
            )
        
        return ValidationResult(is_valid=True)
    
    @staticmethod
    def validate_chat_message(message: str) -> ValidationResult:
        """Validate chat input message."""
        if not message:
            return ValidationResult(
                is_valid=False,
                error_message="Please enter a message.",
                error_code="EMPTY_MESSAGE"
            )
        
        if not message.strip():
            return ValidationResult(
                is_valid=False,
                error_message="Message cannot be empty or whitespace only.",
                error_code="WHITESPACE_MESSAGE"
            )
        
        if len(message) > 2000:
            return ValidationResult(
                is_valid=False,
                error_message="Message too long. Maximum is 2000 characters.",
                error_code="MESSAGE_TOO_LONG"
            )
        
        return ValidationResult(is_valid=True)
    
    @staticmethod
    def validate_llm_inputs(**kwargs) -> ValidationResult:
        """Validate inputs before sending to LLM API."""
        for key, value in kwargs.items():
            if value is None or (isinstance(value, str) and not value.strip()):
                return ValidationResult(
                    is_valid=False,
                    error_message=f"Missing required input: {key}",
                    error_code="MISSING_INPUT"
                )
        
        return ValidationResult(is_valid=True)
    
    @staticmethod
    def validate_plot_data(data: pd.DataFrame, required_cols: int = 1) -> ValidationResult:
        """Validate data before generating plots."""
        result = RequestValidator.validate_dataframe(data)
        if not result.is_valid:
            return result
        
        numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
        if len(numeric_cols) < required_cols:
            return ValidationResult(
                is_valid=False,
                error_message=f"Insufficient numeric columns for visualization. Found {len(numeric_cols)}, need {required_cols}.",
                error_code="INSUFFICIENT_NUMERIC_COLS"
            )
        
        return ValidationResult(is_valid=True)


def safe_api_call(validator_fn, *args, **kwargs):
    """Decorator/wrapper for safe API calls with validation."""
    def wrapper(*args, **kwargs):
        result = validator_fn(*args, **kwargs)
        if not result.is_valid:
            return result
        return None  # Validation passed
    return wrapper


def validate_and_execute(validator_fn, execute_fn, *args, on_error_return=None, **kwargs):
    """Validate inputs and execute function only if valid."""
    result = validator_fn(*args, **kwargs)
    if not result.is_valid:
        return result, on_error_return
    try:
        output = execute_fn(*args, **kwargs)
        return ValidationResult(is_valid=True), output
    except Exception as e:
        return ValidationResult(
            is_valid=False,
            error_message=f"Execution error: {str(e)}",
            error_code="EXECUTION_ERROR"
        ), on_error_return