"""
Database connectivity and basic operations tests
"""
import pytest
from sqlalchemy import text, inspect
from src.db.database import Base
from src.models.user import User
from src.models.passkey import PasskeyCredential

# Import test engine from conftest
from tests.conftest import engine


class TestDatabaseConnectivity:
    """Test database connection and basic operations"""
    
    def test_database_connection(self, client):
        """Test that database connection is working"""
        # Test basic connection
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            assert result.fetchone()[0] == 1

    def test_database_tables_exist(self, client):
        """Test that required tables exist in database"""
        # Get table names using proper SQLAlchemy inspector
        inspector = inspect(engine)
        table_names = inspector.get_table_names()
        
        # Check that our tables exist
        expected_tables = ['users', 'passkey_credentials']
        for table in expected_tables:
            assert table in table_names, f"Table {table} should exist"

    def test_user_table_structure(self, client):
        """Test User table structure"""
        # Check User table columns
        from sqlalchemy import inspect
        inspector = inspect(engine)
        columns = [col['name'] for col in inspector.get_columns('users')]
        
        expected_columns = ['id', 'name', 'phone', 'is_active', 'created_at']
        for column in expected_columns:
            assert column in columns, f"Column {column} should exist in users table"

    def test_passkey_table_structure(self, client):
        """Test PasskeyCredential table structure"""
        from sqlalchemy import inspect
        inspector = inspect(engine)
        columns = [col['name'] for col in inspector.get_columns('passkey_credentials')]
        
        expected_columns = ['id', 'user_id', 'credential_id', 'public_key', 'sign_count', 'created_at']
        for column in expected_columns:
            assert column in columns, f"Column {column} should exist in passkey_credentials table"

    def test_foreign_key_relationships(self, client):
        """Test that foreign key relationships are properly set up"""
        from sqlalchemy import inspect
        inspector = inspect(engine)
        
        # Check foreign keys in passkey_credentials table
        foreign_keys = inspector.get_foreign_keys('passkey_credentials')
        
        # Should have a foreign key to users table
        user_fk_found = False
        for fk in foreign_keys:
            if fk['referred_table'] == 'users':
                user_fk_found = True
                assert 'user_id' in fk['constrained_columns']
                
        assert user_fk_found, "passkey_credentials should have foreign key to users table"


class TestDatabaseOperations:
    """Test basic database CRUD operations"""
    
    def test_can_create_tables(self, client):
        """Test that tables can be created without errors"""
        # This is already done in conftest.py, but we test it explicitly
        try:
            Base.metadata.create_all(bind=engine)
            success = True
        except Exception:
            success = False
        
        assert success, "Should be able to create database tables"

    def test_can_drop_tables(self, client):
        """Test that tables can be dropped without errors"""
        try:
            # Create and then drop tables
            Base.metadata.create_all(bind=engine)
            Base.metadata.drop_all(bind=engine)
            # Recreate for other tests
            Base.metadata.create_all(bind=engine)
            success = True
        except Exception:
            success = False
        
        assert success, "Should be able to drop database tables"

    def test_database_isolation(self, client):
        """Test that test database is isolated"""
        # Check that we're using in-memory database for tests
        assert str(engine.url) == "sqlite:///:memory:", "Tests should use in-memory database"


class TestModelDefinitions:
    """Test that SQLAlchemy models are properly defined"""
    
    def test_user_model_attributes(self, client):
        """Test User model has required attributes"""
        user = User()
        
        # Check that model has expected attributes
        assert hasattr(user, 'id')
        assert hasattr(user, 'name')
        assert hasattr(user, 'phone')
        assert hasattr(user, 'is_active')
        assert hasattr(user, 'created_at')
        
        # Check that relationships exist
        assert hasattr(user, 'passkey_credentials')

    def test_passkey_model_attributes(self, client):
        """Test PasskeyCredential model has required attributes"""
        passkey = PasskeyCredential()
        
        # Check that model has expected attributes
        assert hasattr(passkey, 'id')
        assert hasattr(passkey, 'user_id')
        assert hasattr(passkey, 'credential_id')
        assert hasattr(passkey, 'public_key')
        assert hasattr(passkey, 'sign_count')
        assert hasattr(passkey, 'created_at')
        
        # Check that relationships exist
        assert hasattr(passkey, 'user')

    def test_model_string_representations(self, client):
        """Test that models have proper string representations"""
        user = User(name="Test User", phone="+1234567890")
        user_str = str(user)
        assert "Test User" in user_str
        
        passkey = PasskeyCredential(credential_id="test_credential")
        passkey_str = str(passkey)
        assert "test_cre..." in passkey_str
