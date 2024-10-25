import pytest
from babbleon.validator import ReferenceValidator

@pytest.fixture
def sample_reference_data():
    return {
        "tabs": {
            "index": "Correction",
            "favorites": "History",
            "settings": {
                "title": "Settings",
                "description": "Configure your preferences"
            }
        },
        "buttons": {
            "save": "Save",
            "cancel": "Cancel"
        }
    }

@pytest.fixture
def sample_docs_content():
    return """# Navigation

The main navigation contains several tabs:
- `tabs.index`: Main correction tab
- `tabs.favorites`: History view
- `tabs.settings.title`: Settings page
- `tabs.unknown`: This is an invalid reference
- `buttons.save`: Save button

## Other Elements
- `buttons.cancel`: Cancel button
- `buttons.unknown`: Another invalid reference
- `unknown.path`: Invalid path
"""

class TestReferenceValidator:
    def test_extract_references_from_docs(self, sample_reference_data, sample_docs_content):
        validator = ReferenceValidator(sample_reference_data, sample_docs_content)
        references = validator.extract_references_from_docs()
        
        expected_references = {
            'tabs.index',
            'tabs.favorites',
            'tabs.settings.title',
            'tabs.unknown',
            'buttons.save',
            'buttons.cancel',
            'buttons.unknown',
            'unknown.path'
        }
        
        assert references == expected_references

    def test_validate_path_valid_simple(self, sample_reference_data, sample_docs_content):
        validator = ReferenceValidator(sample_reference_data, sample_docs_content)
        is_valid, value = validator.validate_path('tabs.index')
        
        assert is_valid is True
        assert value == "Correction"

    def test_validate_path_valid_nested(self, sample_reference_data, sample_docs_content):
        validator = ReferenceValidator(sample_reference_data, sample_docs_content)
        is_valid, value = validator.validate_path('tabs.settings.title')
        
        assert is_valid is True
        assert value == "Settings"

    def test_validate_path_invalid_top_level(self, sample_reference_data, sample_docs_content):
        validator = ReferenceValidator(sample_reference_data, sample_docs_content)
        is_valid, value = validator.validate_path('unknown.path')
        
        assert is_valid is False
        assert value is None

    def test_validate_path_invalid_nested(self, sample_reference_data, sample_docs_content):
        validator = ReferenceValidator(sample_reference_data, sample_docs_content)
        is_valid, value = validator.validate_path('tabs.unknown')
        
        assert is_valid is False
        assert value is None

    def test_validate_reference_valid_string(self, sample_reference_data, sample_docs_content):
        validator = ReferenceValidator(sample_reference_data, sample_docs_content)
        result = validator.validate_reference('buttons.save')
        
        assert result == {
            'path': 'buttons.save',
            'valid': True,
            'value': 'Save',
            'value_type': 'str'
        }

    def test_validate_reference_valid_dict(self, sample_reference_data, sample_docs_content):
        validator = ReferenceValidator(sample_reference_data, sample_docs_content)
        result = validator.validate_reference('tabs.settings')
        
        assert result == {
            'path': 'tabs.settings',
            'valid': True,
            'value': {
                'title': 'Settings',
                'description': 'Configure your preferences'
            },
            'value_type': 'dict'
        }

    def test_validate_reference_invalid(self, sample_reference_data, sample_docs_content):
        validator = ReferenceValidator(sample_reference_data, sample_docs_content)
        result = validator.validate_reference('buttons.unknown')
        
        assert result == {
            'path': 'buttons.unknown',
            'valid': False,
            'value': None,
            'value_type': None
        }

    def test_validate_docs(self, sample_reference_data, sample_docs_content):
        validator = ReferenceValidator(sample_reference_data, sample_docs_content)
        results = validator.validate_docs()
        
        # Check valid references
        valid_paths = {result['path'] for result in results['valid']}
        expected_valid = {
            'tabs.index',
            'tabs.favorites',
            'tabs.settings.title',
            'buttons.save',
            'buttons.cancel'
        }
        assert valid_paths == expected_valid
        
        # Check invalid references
        invalid_paths = {result['path'] for result in results['invalid']}
        expected_invalid = {
            'tabs.unknown',
            'buttons.unknown',
            'unknown.path'
        }
        assert invalid_paths == expected_invalid
        
        # Verify some specific values
        valid_dict = {result['path']: result['value'] for result in results['valid']}
        assert valid_dict['tabs.index'] == 'Correction'
        assert valid_dict['buttons.save'] == 'Save'

    def test_regex_pattern_edge_cases(self, sample_reference_data):
        # Test various edge cases for reference pattern matching
        edge_case_docs = """
        - `valid`: Valid single segment
        - `valid.path`: Valid
        - `a.b.c.d`: Many segments
        - `123.invalid`: Invalid start
        - `invalid.123`: Invalid with numbers
        - `valid_path.with_underscore`: Valid with underscore
        - Not a reference: a.b.c
        - ``: Empty
        - ` space.path `: With spaces
        """
        
        validator = ReferenceValidator(sample_reference_data, edge_case_docs)
        references = validator.extract_references_from_docs()

        print(references)
        
        # These should be matched
        assert 'valid' in references
        assert 'valid.path' in references
        assert 'a.b.c.d' in references
        assert 'valid_path.with_underscore' in references
        
        # These should not be matched
        assert 'invalid.123' not in references
        assert '123.invalid' not in references
        assert '' not in references
        assert 'space.path' not in references

    def test_empty_docs(self, sample_reference_data):
        validator = ReferenceValidator(sample_reference_data, "")
        results = validator.validate_docs()
        
        assert results['valid'] == []
        assert results['invalid'] == []

    def test_empty_reference_data(self, sample_docs_content):
        validator = ReferenceValidator({}, sample_docs_content)
        results = validator.validate_docs()
        
        # All references should be invalid when reference data is empty
        assert results['valid'] == []
        assert len(results['invalid']) == len(validator.extract_references_from_docs())





@pytest.fixture
def temp_babbleon_dir(tmp_path):
    """Create a temporary .babbleon directory with test files"""
    babbleon_dir = tmp_path / ".babbleon"
    babbleon_dir.mkdir()
    return babbleon_dir

@pytest.fixture
def sample_reference_yaml(temp_babbleon_dir):
    """Create a sample reference.yaml file"""
    content = """
tabs:
  index: Correction
  favorites: History
  settings:
    title: Settings
    description: Configure your preferences
buttons:
  save: Save
  cancel: Cancel
"""
    reference_file = temp_babbleon_dir / "reference.yaml"
    reference_file.write_text(content)
    return reference_file

@pytest.fixture
def sample_docs_md(temp_babbleon_dir):
    """Create a sample docs.md file"""
    content = """# Navigation

The main navigation contains several tabs:
- `tabs.index`: Main correction tab
- `tabs.favorites`: History view
- `tabs.settings.title`: Settings page
- `tabs.unknown`: This is an invalid reference
- `buttons.save`: Save button

## Other Elements
- `buttons.cancel`: Cancel button
- `buttons.unknown`: Another invalid reference
- `unknown.path`: Invalid path
"""
    docs_file = temp_babbleon_dir / "docs.md"
    docs_file.write_text(content)
    return docs_file
