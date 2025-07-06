"""
JSON Serialization Support for CV Matching Models
"""

from dataclasses import asdict, fields
from typing import Dict, Any

class JSONSerializationMixin:
    """Mixin to add JSON serialization support to dataclasses"""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the dataclass instance to a dictionary"""
        return {
            k: v for k, v in asdict(self).items()
            if v is not None  # Skip None values
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'JSONSerializationMixin':
        """Create a dataclass instance from a dictionary"""
        field_types = {f.name: f.type for f in fields(cls)}
        
        # Convert nested dicts to appropriate dataclass instances
        processed_data = {}
        for key, value in data.items():
            if key in field_types:
                if hasattr(field_types[key], 'from_dict') and isinstance(value, dict):
                    processed_data[key] = field_types[key].from_dict(value)
                else:
                    processed_data[key] = value
                    
        return cls(**processed_data)
