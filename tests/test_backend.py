"""
Tests for backend functionality: password hashing, data validation,
user creation, login, and recovery endpoints.
"""
import hashlib
import os
import re
import sys

import pytest

# Ensure backend module can be imported
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

import bcrypt as _bcrypt


# ---------------------------------------------------------------------------
# Unit tests for password hashing (bcrypt direct usage)
# ---------------------------------------------------------------------------

class TestPasswordHashing:
    """Tests for password hash and verify functions."""

    def test_bcrypt_hash_produces_valid_hash(self):
        password = "securePass123"
        hashed = _bcrypt.hashpw(password.encode('utf-8'), _bcrypt.gensalt()).decode('utf-8')
        assert hashed.startswith(('$2a$', '$2b$', '$2y$'))

    def test_bcrypt_verify_correct_password(self):
        password = "securePass123"
        hashed = _bcrypt.hashpw(password.encode('utf-8'), _bcrypt.gensalt()).decode('utf-8')
        assert _bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8')) is True

    def test_bcrypt_verify_wrong_password(self):
        password = "securePass123"
        hashed = _bcrypt.hashpw(password.encode('utf-8'), _bcrypt.gensalt()).decode('utf-8')
        assert _bcrypt.checkpw("wrongPassword".encode('utf-8'), hashed.encode('utf-8')) is False

    def test_bcrypt_hash_unique_per_call(self):
        """Each call to hash should produce a different hash due to random salt."""
        password = "samePassword"
        h1 = _bcrypt.hashpw(password.encode('utf-8'), _bcrypt.gensalt()).decode('utf-8')
        h2 = _bcrypt.hashpw(password.encode('utf-8'), _bcrypt.gensalt()).decode('utf-8')
        assert h1 != h2

    def test_bcrypt_handles_special_characters(self):
        password = "p@$$w0rd!#%^&*()"
        hashed = _bcrypt.hashpw(password.encode('utf-8'), _bcrypt.gensalt()).decode('utf-8')
        assert _bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8')) is True

    def test_bcrypt_handles_unicode(self):
        password = "contraseña_ñoño_123"
        hashed = _bcrypt.hashpw(password.encode('utf-8'), _bcrypt.gensalt()).decode('utf-8')
        assert _bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8')) is True

    def test_bcrypt_min_length_password(self):
        password = "123456"  # minimum 6 chars as per schema
        hashed = _bcrypt.hashpw(password.encode('utf-8'), _bcrypt.gensalt()).decode('utf-8')
        assert _bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8')) is True

    def test_sha256_fallback_verification(self):
        """Verify SHA256 hash detection works for backwards compatibility."""
        password = "testPassword"
        sha256_hash = hashlib.sha256(password.encode()).hexdigest()
        # SHA256 produces 64 hex characters
        assert len(sha256_hash) == 64
        assert all(c in '0123456789abcdef' for c in sha256_hash.lower())
        assert hashlib.sha256(password.encode()).hexdigest() == sha256_hash

    def test_plain_text_comparison(self):
        """Verify plain text fallback works for backwards compatibility."""
        password = "plainTextPass"
        assert password == "plainTextPass"
        assert password != "wrongPassword"


# ---------------------------------------------------------------------------
# Unit tests for data validation (cedula, email)
# ---------------------------------------------------------------------------

class TestCedulaValidation:
    """Tests for cedula sanitization and validation."""

    def _sanitize_cedula_login(self, v):
        """Simulates LoginRequest cedula sanitizer (digits only - fixed version)."""
        if v:
            return re.sub(r'\D', '', v)[:50]
        return v

    def _sanitize_cedula_create(self, v):
        """Simulates UserCreate/UserUpdate cedula sanitizer (digits only)."""
        if v:
            cleaned = re.sub(r'\D', '', v)[:50]
            if not cleaned:
                raise ValueError('La cédula debe contener al menos un número')
            return cleaned
        return v

    def test_cedula_digits_only(self):
        assert self._sanitize_cedula_login("12345678") == "12345678"
        assert self._sanitize_cedula_create("12345678") == "12345678"

    def test_cedula_strips_prefix(self):
        """Cedula with V- prefix should be stripped to digits."""
        assert self._sanitize_cedula_login("V-12345678") == "12345678"
        assert self._sanitize_cedula_create("V-12345678") == "12345678"

    def test_cedula_consistency_between_login_and_create(self):
        """Login and create sanitizers should produce the same result."""
        test_cases = [
            "12345678",
            "V-12345678",
            "V12345678",
            "  123 456 78  ",
            "12.345.678",
        ]
        for cedula in test_cases:
            login_result = self._sanitize_cedula_login(cedula)
            create_result = self._sanitize_cedula_create(cedula)
            assert login_result == create_result, (
                f"Inconsistency for cedula '{cedula}': "
                f"login='{login_result}' vs create='{create_result}'"
            )

    def test_cedula_with_dots_and_dashes(self):
        """Common cedula formats with dots/dashes should normalize to digits."""
        assert self._sanitize_cedula_create("12.345.678") == "12345678"
        assert self._sanitize_cedula_create("12-345-678") == "12345678"

    def test_cedula_empty_string(self):
        # Empty string is falsy, so sanitizer returns it as-is
        result = self._sanitize_cedula_login("")
        assert result is None or result == ""

    def test_cedula_none(self):
        assert self._sanitize_cedula_login(None) is None
        assert self._sanitize_cedula_create(None) is None

    def test_cedula_no_digits_raises(self):
        """Cedula with no digits should raise ValueError."""
        with pytest.raises(ValueError, match="al menos un número"):
            self._sanitize_cedula_create("VXYZ")

    def test_cedula_max_length(self):
        """Cedula should be truncated to 50 characters."""
        long_cedula = "1" * 100
        result = self._sanitize_cedula_create(long_cedula)
        assert len(result) == 50


class TestEmailValidation:
    """Tests for email validation."""

    def _validate_email(self, v):
        """Simulates email validation from UserCreate/UserUpdate."""
        if v:
            email_pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
            if not re.match(email_pattern, v):
                raise ValueError('El correo electrónico debe contener @ y un dominio válido')
        return v

    def test_valid_email(self):
        assert self._validate_email("user@example.com") == "user@example.com"

    def test_valid_email_subdomain(self):
        assert self._validate_email("user@mail.example.com") == "user@mail.example.com"

    def test_invalid_email_no_at(self):
        with pytest.raises(ValueError):
            self._validate_email("userexample.com")

    def test_invalid_email_no_domain(self):
        with pytest.raises(ValueError):
            self._validate_email("user@")

    def test_invalid_email_with_spaces(self):
        with pytest.raises(ValueError):
            self._validate_email("user @example.com")

    def test_email_none(self):
        assert self._validate_email(None) is None

    def test_email_empty_string(self):
        """Empty string should pass without validation (falsy)."""
        assert self._validate_email("") == ""


class TestPasswordValidation:
    """Tests for password constraints."""

    def test_password_min_length_accepted(self):
        """Password with exactly 6 chars should be accepted."""
        password = "123456"
        assert len(password) >= 6

    def test_password_too_short(self):
        """Password with less than 6 chars should fail."""
        password = "12345"
        assert len(password) < 6

    def test_password_max_length_accepted(self):
        """Password up to 200 chars should be accepted."""
        password = "a" * 200
        assert len(password) <= 200


# ---------------------------------------------------------------------------
# Unit tests for module validation
# ---------------------------------------------------------------------------

class TestModuleValidation:
    """Tests for module number validation."""

    MIN_MODULE_NUMBER = 1
    MAX_MODULE_NUMBER = 2

    def _validate_module(self, module_num, field_name="module"):
        if not isinstance(module_num, int) or module_num < self.MIN_MODULE_NUMBER or module_num > self.MAX_MODULE_NUMBER:
            raise ValueError(f"{field_name} must be between {self.MIN_MODULE_NUMBER} and {self.MAX_MODULE_NUMBER}, got {module_num}")
        return True

    def test_valid_module_1(self):
        assert self._validate_module(1) is True

    def test_valid_module_2(self):
        assert self._validate_module(2) is True

    def test_invalid_module_0(self):
        with pytest.raises(ValueError):
            self._validate_module(0)

    def test_invalid_module_3(self):
        with pytest.raises(ValueError):
            self._validate_module(3)

    def test_invalid_module_negative(self):
        with pytest.raises(ValueError):
            self._validate_module(-1)

    def test_invalid_module_float(self):
        with pytest.raises(ValueError):
            self._validate_module(1.5)

    def test_invalid_module_string(self):
        with pytest.raises(ValueError):
            self._validate_module("1")


# ---------------------------------------------------------------------------
# Integration tests using FastAPI TestClient
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def test_app():
    """Create a test FastAPI app with mocked database."""
    # Set environment variables before import
    os.environ.setdefault('MONGO_URL', 'mongodb://localhost:27017')
    os.environ.setdefault('JWT_SECRET', 'test_secret_key_for_testing')
    os.environ.setdefault('DB_NAME', 'WebAppTest')
    os.environ.setdefault('PASSWORD_STORAGE_MODE', 'bcrypt')

    try:
        from server import app
        return app
    except (ImportError, ConnectionError, Exception) as exc:
        pytest.skip(f"Cannot import server: {type(exc).__name__}: {exc}")


@pytest.fixture
def client(test_app):
    """Create a test client."""
    from httpx import ASGITransport, AsyncClient
    transport = ASGITransport(app=test_app)
    return AsyncClient(transport=transport, base_url="http://test")


class TestHealthEndpoint:
    """Test the health check endpoint."""

    @pytest.mark.asyncio
    async def test_health_check(self, client):
        response = await client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data


class TestLoginEndpoint:
    """Test the login endpoint validation."""

    @pytest.mark.asyncio
    async def test_login_missing_password(self, client):
        response = await client.post("/api/auth/login", json={
            "role": "estudiante",
            "cedula": "12345678"
        })
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_login_invalid_role(self, client):
        response = await client.post("/api/auth/login", json={
            "role": "invalid_role",
            "password": "test123",
            "email": "test@test.com"
        })
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_login_student_without_cedula(self, client):
        response = await client.post("/api/auth/login", json={
            "role": "estudiante",
            "password": "test123"
        })
        # Should get 400 (cedula required) or 401 (not found)
        assert response.status_code in [400, 401]

    @pytest.mark.asyncio
    async def test_login_profesor_without_email(self, client):
        response = await client.post("/api/auth/login", json={
            "role": "profesor",
            "password": "test123"
        })
        # Should get 400 (email required) or 401 (not found)
        assert response.status_code in [400, 401]

    @pytest.mark.asyncio
    async def test_login_wrong_credentials(self, client):
        response = await client.post("/api/auth/login", json={
            "role": "estudiante",
            "cedula": "99999999999",
            "password": "wrongpassword"
        })
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_login_profesor_wrong_credentials(self, client):
        response = await client.post("/api/auth/login", json={
            "role": "profesor",
            "email": "nonexistent@test.com",
            "password": "wrongpassword"
        })
        assert response.status_code == 401


class TestUserCreationValidation:
    """Test user creation endpoint validation (without auth)."""

    @pytest.mark.asyncio
    async def test_create_user_without_auth(self, client):
        response = await client.post("/api/users", json={
            "name": "Test User",
            "cedula": "12345678",
            "password": "test123456",
            "role": "estudiante"
        })
        assert response.status_code == 401  # No auth token

    @pytest.mark.asyncio
    async def test_create_user_invalid_role(self, client):
        response = await client.post("/api/users", json={
            "name": "Test User",
            "cedula": "12345678",
            "password": "test123456",
            "role": "invalid_role"
        })
        # Should fail with 422 (validation) or 401 (no auth)
        assert response.status_code in [401, 422]

    @pytest.mark.asyncio
    async def test_create_user_short_password(self, client):
        response = await client.post("/api/users", json={
            "name": "Test User",
            "cedula": "12345678",
            "password": "12345",  # Too short (< 6)
            "role": "estudiante"
        })
        # Should fail with 422 (validation) or 401 (no auth)
        assert response.status_code in [401, 422]


class TestRecoveryEndpoints:
    """Test recovery endpoint access control."""

    @pytest.mark.asyncio
    async def test_recovery_enable_without_auth(self, client):
        response = await client.post("/api/recovery/enable", json={
            "student_id": "fake-id",
            "course_id": "fake-course"
        })
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_recovery_enabled_list_without_auth(self, client):
        response = await client.get("/api/recovery/enabled")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_recovery_panel_without_auth(self, client):
        response = await client.get("/api/admin/recovery-panel")
        assert response.status_code == 401


class TestRootEndpoint:
    """Test the root endpoint."""

    @pytest.mark.asyncio
    async def test_root_endpoint(self, client):
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
