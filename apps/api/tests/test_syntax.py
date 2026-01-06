"""Tests for Python syntax validation to prevent runtime import errors"""
import pytest
import py_compile
import os
from pathlib import Path


class TestSyntaxValidation:
    """Test Python syntax validation"""
    
    def test_app_main_imports(self):
        """Test that app.main can be imported without syntax errors"""
        # This test ensures the main application can be imported
        # which is critical for Uvicorn to start the server
        import app.main
        assert hasattr(app.main, 'app'), "app.main should export 'app' instance"
    
    def test_all_python_files_compile(self):
        """Test that all Python files in app directory compile without syntax errors"""
        app_dir = Path(__file__).parent.parent / "app"
        python_files = list(app_dir.rglob("*.py"))
        
        assert len(python_files) > 0, "No Python files found in app directory"
        
        errors = []
        for py_file in python_files:
            try:
                py_compile.compile(str(py_file), doraise=True)
            except py_compile.PyCompileError as e:
                errors.append(f"{py_file.relative_to(app_dir)}: {e}")
        
        assert not errors, f"Syntax errors found in:\n" + "\n".join(errors)
