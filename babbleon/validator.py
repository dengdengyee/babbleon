from pathlib import Path
import re
from typing import Dict, Any, List, Set, Tuple
import yaml
import click

class ReferenceValidator:
    """Validates references against the reference.yaml file"""
    
    def __init__(self, reference_data: Dict[str, Any], docs_content: str):
        """
        Initialize validator with reference data and docs content
        
        Args:
            reference_data: Parsed reference.yaml content
            docs_content: Content of docs.md
        """
        self.reference_data = reference_data
        self.docs_content = docs_content
    
    def extract_references_from_docs(self) -> Set[str]:
        """
        Extract all references in dot notation format from docs
        Returns a set of unique reference paths
        """
        # Match `something.something` patterns, allowing multiple dots
        reference_pattern = r'`([a-zA-Z][a-zA-Z0-9_]*(?:\.[a-zA-Z][a-zA-Z0-9_]*)*)`'
        matches = re.findall(reference_pattern, self.docs_content)
        return set(matches)
    
    def validate_path(self, path: str) -> Tuple[bool, Any]:
        """
        Validate if a dot notation path exists in the reference data
        
        Args:
            path: Dot notation path (e.g., 'tabs.index.button')
            
        Returns:
            Tuple of (is_valid, value_if_valid)
        """
        current = self.reference_data
        try:
            for part in path.split('.'):
                if not isinstance(current, dict):
                    return False, None
                if part not in current:
                    return False, None
                current = current[part]
            return True, current
        except Exception:
            return False, None
    
    def validate_reference(self, path: str) -> Dict[str, Any]:
        """
        Validate a single reference path and return detailed result
        
        Args:
            path: Reference path to validate
            
        Returns:
            Dictionary with validation details
        """
        is_valid, value = self.validate_path(path)
        
        return {
            'path': path,
            'valid': is_valid,
            'value': value if is_valid else None,
            'value_type': type(value).__name__ if is_valid else None
        }
    
    def validate_docs(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Validate all references in docs
        
        Returns:
            Dictionary containing valid and invalid references with details
        """
        docs_references = self.extract_references_from_docs()
        results = {
            'valid': [],
            'invalid': []
        }
        
        for ref in docs_references:
            validation = self.validate_reference(ref)
            if validation['valid']:
                results['valid'].append(validation)
            else:
                results['invalid'].append(validation)
        
        # Sort results by path for consistent output
        results['valid'].sort(key=lambda x: x['path'])
        results['invalid'].sort(key=lambda x: x['path'])
        
        return results

def format_validation_result(result: Dict[str, Any]) -> str:
    """Format a single validation result for display"""
    path = result['path']
    if result['valid']:
        value = result['value']
        if isinstance(value, (str, int, float, bool)):
            return f"✅ {path}: {value}"
        else:
            return f"✅ {path}: (complex type) {result['value_type']}"
    else:
        return f"❌ {path}: not found"