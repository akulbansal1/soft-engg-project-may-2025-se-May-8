"""
Configuration and environment tests
"""
import pytest
import os
from datetime import timedelta
from src.core.config import settings


class TestConfiguration:
    """Test application configuration"""
    
    def test_settings_load(self):
        """Test that settings load properly"""
        assert settings is not None
        assert hasattr(settings, 'DATABASE_URL')
        assert hasattr(settings, 'API_V1_STR')
        assert hasattr(settings, 'PROJECT_NAME')

    def test_api_version_prefix(self):
        """Test API version prefix is correctly set"""
        assert settings.API_V1_STR == "/api/v1"

    def test_project_name(self):
        """Test project name is set"""
        assert settings.PROJECT_NAME == "SE Project API"
        assert isinstance(settings.PROJECT_NAME, str)
        assert len(settings.PROJECT_NAME) > 0

    def test_database_url_format(self):
        """Test database URL is in correct format"""
        db_url = settings.DATABASE_URL
        assert isinstance(db_url, str)
        assert len(db_url) > 0
        
        # Should be either SQLite or PostgreSQL
        assert db_url.startswith(('sqlite://', 'postgresql://'))

    def test_redis_url_format(self):
        """Test Redis URL is in correct format"""
        redis_url = settings.REDIS_URL
        assert isinstance(redis_url, str)
        assert redis_url.startswith('redis://')

    def test_secret_key_exists(self):
        """Test that secret key is set"""
        assert hasattr(settings, 'SECRET_KEY')
        assert isinstance(settings.SECRET_KEY, str)
        assert len(settings.SECRET_KEY) > 0

    def test_debug_mode_type(self):
        """Test debug mode is boolean"""
        assert hasattr(settings, 'DEBUG')
        assert isinstance(settings.DEBUG, bool)

    def test_frontend_rp_id_format(self):
        """Test frontend rp_id is properly formatted"""
        assert hasattr(settings, 'FRONTEND_RP_ID')
        rp_id = settings.FRONTEND_RP_ID
        assert isinstance(rp_id, str)
        assert len(rp_id) > 0
        assert rp_id.count('.') <= 1 # Should not have subdomains, just domain or localhost


    def test_frontend_origin_format(self):
        """Test frontend origin is properly formatted"""
        assert hasattr(settings, 'FRONTEND_ORIGIN')
        origin = settings.FRONTEND_ORIGIN
        assert isinstance(origin, str)
        assert origin.startswith(('http://', 'https://'))


class TestDatabaseConfiguration:
    """Test database-specific configuration"""
    
    def test_database_type_detection(self):
        """Test database type detection methods"""
        # Test SQLite detection
        if settings.DATABASE_URL.startswith('sqlite://'):
            assert settings.is_sqlite == True
            assert settings.is_postgres == False
        
        # Test PostgreSQL detection
        if settings.DATABASE_URL.startswith('postgresql://'):
            assert settings.is_postgres == True
            assert settings.is_sqlite == False

    def test_postgres_url_generation(self):
        """Test PostgreSQL URL generation"""
        postgres_url = settings.postgres_url
        assert isinstance(postgres_url, str)
        assert postgres_url.startswith('postgresql://')
        
        # Should contain required components
        assert settings.POSTGRES_USER in postgres_url
        assert settings.POSTGRES_HOST in postgres_url
        assert settings.POSTGRES_PORT in postgres_url
        assert settings.POSTGRES_DB in postgres_url

    def test_postgres_settings(self):
        """Test PostgreSQL individual settings"""
        assert isinstance(settings.POSTGRES_HOST, str)
        assert isinstance(settings.POSTGRES_PORT, str)
        assert isinstance(settings.POSTGRES_DB, str)
        assert isinstance(settings.POSTGRES_USER, str)
        assert isinstance(settings.POSTGRES_PASSWORD, str)


class TestSecurityConfiguration:
    """Test security-related configuration"""

    def test_cors_origins(self):
        """Test CORS origins configuration"""
        assert hasattr(settings, 'ALLOWED_ORIGINS')
        origins = settings.ALLOWED_ORIGINS
        assert isinstance(origins, list)
        
        # Should include frontend domain
        assert settings.FRONTEND_ORIGIN in origins

    def test_session_configuration(self):
        """Test session-related configuration"""
        assert hasattr(settings, 'SESSION_TOKEN_EXPIRY')
        assert hasattr(settings, 'CHALLENGE_TIMEOUT')
        assert hasattr(settings, 'CHALLENGE_CACHE_EXPIRY')
        
        # Should be reasonable timeouts
        assert settings.SESSION_TOKEN_EXPIRY.total_seconds() > 0
        assert settings.CHALLENGE_TIMEOUT > 0
        assert settings.CHALLENGE_CACHE_EXPIRY > 0


class TestEnvironmentVariables:
    """Test environment variable handling"""
    
    def test_env_file_loading(self):
        """Test that .env file loading works"""
        # This test verifies that dotenv loading doesn't break
        from dotenv import load_dotenv
        
        try:
            load_dotenv()
            success = True
        except Exception:
            success = False
        
        assert success, "Should be able to load .env file"

    def test_default_values(self):
        """Test that default values are used when env vars are not set"""
        # Test with a temporarily unset environment variable
        original_value = os.environ.get('NONEXISTENT_VAR')
        
        if 'NONEXISTENT_VAR' in os.environ:
            del os.environ['NONEXISTENT_VAR']
        
        # Should use default value
        test_value = os.getenv('NONEXISTENT_VAR', 'default_test_value')
        assert test_value == 'default_test_value'
        
        # Restore original value if it existed
        if original_value is not None:
            os.environ['NONEXISTENT_VAR'] = original_value

    def test_boolean_env_parsing(self):
        """Test that boolean environment variables are parsed correctly"""
        # Test debug flag parsing
        debug_value = os.getenv("DEBUG", "True").lower() == "true"
        assert isinstance(debug_value, bool)


class TestConfigurationValidation:
    """Test configuration validation and consistency"""
    
    def test_urls_are_valid(self):
        """Test that configured URLs are valid"""
        # Database URL should not be empty
        assert len(settings.DATABASE_URL) > 0
        
        # Redis URL should not be empty
        assert len(settings.REDIS_URL) > 0
        
        # Frontend RP ID should not be empty
        assert len(settings.FRONTEND_RP_ID) > 0

        # Frontend origin should be a valid URL
        assert len(settings.FRONTEND_ORIGIN) > 0
        assert settings.FRONTEND_ORIGIN.startswith(('http://', 'https://'))

    def test_timeouts_are_reasonable(self):
        """Test that configured timeouts are reasonable"""
        # Challenge timeout should be between 1 minute and 1 hour (in milliseconds)
        min_timeout = int(timedelta(minutes=1).total_seconds() * 1000)  # 1 min in milliseconds
        max_timeout = int(timedelta(hours=1).total_seconds() * 1000)   # 1 hour in milliseconds
        assert min_timeout <= settings.CHALLENGE_TIMEOUT <= max_timeout
        
        # Cache expiry should be reasonable (in seconds)
        assert 60 <= settings.CHALLENGE_CACHE_EXPIRY <= 7200  # 1 min to 2 hours in seconds
        
        # Session expiry should be at least 1 hour
        assert settings.SESSION_TOKEN_EXPIRY.total_seconds() >= 3600  # At least 1 hour

    def test_required_settings_present(self):
        """Test that all required settings are present"""
        required_settings = [
            'DATABASE_URL', 'REDIS_URL', 'SECRET_KEY', 'API_V1_STR',
            'PROJECT_NAME', 'FRONTEND_RP_ID', 'DEBUG'
        ]
        
        for setting in required_settings:
            assert hasattr(settings, setting), f"Setting {setting} should be present"
            value = getattr(settings, setting)
            assert value is not None, f"Setting {setting} should not be None"
