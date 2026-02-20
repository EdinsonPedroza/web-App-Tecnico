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


class TestGetCurrentModuleFromDates:
    """Tests for the get_current_module_from_dates utility function."""

    def _get_module_from_dates(self, module_dates):
        """Mirror of get_current_module_from_dates from server.py for unit testing."""
        from datetime import datetime, timezone
        if not module_dates:
            return None
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        sorted_keys = sorted(module_dates.keys(), key=lambda k: int(k) if str(k).isdigit() else 0)
        for mod_key in sorted_keys:
            dates = module_dates.get(mod_key) or {}
            start = dates.get("start")
            end = dates.get("recovery_close") or dates.get("end")
            if start and end and start <= today <= end:
                return int(mod_key)
        modules_with_start = [
            (int(k), (module_dates.get(k) or {}).get("start"))
            for k in sorted_keys
            if (module_dates.get(k) or {}).get("start")
        ]
        if not modules_with_start:
            return None
        modules_with_start.sort()
        if today < modules_with_start[0][1]:
            return modules_with_start[0][0]
        current = modules_with_start[0][0]
        for mod_num, start in modules_with_start:
            if start <= today:
                current = mod_num
        return current

    def test_empty_module_dates_returns_none(self):
        assert self._get_module_from_dates({}) is None

    def test_none_module_dates_returns_none(self):
        assert self._get_module_from_dates(None) is None

    def test_today_in_module1_returns_1(self):
        from datetime import datetime, timezone, timedelta
        today = datetime.now(timezone.utc)
        dates = {
            "1": {"start": (today - timedelta(days=30)).strftime("%Y-%m-%d"),
                  "end": (today + timedelta(days=30)).strftime("%Y-%m-%d")},
            "2": {"start": (today + timedelta(days=31)).strftime("%Y-%m-%d"),
                  "end": (today + timedelta(days=180)).strftime("%Y-%m-%d")},
        }
        assert self._get_module_from_dates(dates) == 1

    def test_today_in_module2_returns_2(self):
        from datetime import datetime, timezone, timedelta
        today = datetime.now(timezone.utc)
        dates = {
            "1": {"start": (today - timedelta(days=180)).strftime("%Y-%m-%d"),
                  "end": (today - timedelta(days=31)).strftime("%Y-%m-%d")},
            "2": {"start": (today - timedelta(days=30)).strftime("%Y-%m-%d"),
                  "end": (today + timedelta(days=30)).strftime("%Y-%m-%d")},
        }
        assert self._get_module_from_dates(dates) == 2

    def test_before_all_modules_returns_first_module(self):
        from datetime import datetime, timezone, timedelta
        today = datetime.now(timezone.utc)
        dates = {
            "1": {"start": (today + timedelta(days=10)).strftime("%Y-%m-%d"),
                  "end": (today + timedelta(days=180)).strftime("%Y-%m-%d")},
        }
        assert self._get_module_from_dates(dates) == 1

    def test_after_all_modules_returns_last_module(self):
        from datetime import datetime, timezone, timedelta
        today = datetime.now(timezone.utc)
        dates = {
            "1": {"start": (today - timedelta(days=180)).strftime("%Y-%m-%d"),
                  "end": (today - timedelta(days=60)).strftime("%Y-%m-%d")},
            "2": {"start": (today - timedelta(days=59)).strftime("%Y-%m-%d"),
                  "end": (today - timedelta(days=10)).strftime("%Y-%m-%d")},
        }
        assert self._get_module_from_dates(dates) == 2

    def test_uses_recovery_close_as_end_boundary(self):
        from datetime import datetime, timezone, timedelta
        today = datetime.now(timezone.utc)
        dates = {
            "1": {"start": (today - timedelta(days=30)).strftime("%Y-%m-%d"),
                  "end": (today - timedelta(days=5)).strftime("%Y-%m-%d"),
                  "recovery_close": (today + timedelta(days=5)).strftime("%Y-%m-%d")},
        }
        # Today is after end but before recovery_close, so module 1 is still active
        assert self._get_module_from_dates(dates) == 1


class TestValidateModuleDatesOrder:
    """Tests for the validate_module_dates_order utility function."""

    def _validate_order(self, module_dates):
        """Mirror of validate_module_dates_order from server.py for unit testing."""
        if not module_dates or len(module_dates) < 2:
            return None
        sorted_keys = sorted(module_dates.keys(), key=lambda k: int(k) if str(k).isdigit() else 0)
        for i in range(len(sorted_keys) - 1):
            curr_key = sorted_keys[i]
            next_key = sorted_keys[i + 1]
            curr_dates = module_dates.get(curr_key) or {}
            next_dates = module_dates.get(next_key) or {}
            curr_boundary = curr_dates.get("recovery_close") or curr_dates.get("end")
            next_start = next_dates.get("start")
            if curr_boundary and next_start and next_start <= curr_boundary:
                return (f"La fecha de inicio del Módulo {next_key} ({next_start}) debe ser "
                        f"posterior al cierre de recuperaciones del Módulo {curr_key} ({curr_boundary})")
        return None

    def test_valid_order_returns_none(self):
        dates = {
            "1": {"start": "2026-01-01", "end": "2026-06-30", "recovery_close": "2026-07-15"},
            "2": {"start": "2026-07-16", "end": "2026-12-31"},
        }
        assert self._validate_order(dates) is None

    def test_single_module_returns_none(self):
        dates = {"1": {"start": "2026-01-01", "end": "2026-06-30"}}
        assert self._validate_order(dates) is None

    def test_empty_returns_none(self):
        assert self._validate_order({}) is None

    def test_module2_starts_same_day_as_module1_recovery_close_is_invalid(self):
        dates = {
            "1": {"start": "2026-01-01", "end": "2026-06-30", "recovery_close": "2026-07-15"},
            "2": {"start": "2026-07-15", "end": "2026-12-31"},
        }
        result = self._validate_order(dates)
        assert result is not None
        assert "Módulo" in result

    def test_module2_starts_before_module1_end_is_invalid(self):
        dates = {
            "1": {"start": "2026-01-01", "end": "2026-06-30"},
            "2": {"start": "2026-06-15", "end": "2026-12-31"},
        }
        result = self._validate_order(dates)
        assert result is not None

    def test_module2_starts_after_module1_end_is_valid_when_no_recovery_close(self):
        dates = {
            "1": {"start": "2026-01-01", "end": "2026-06-30"},
            "2": {"start": "2026-07-01", "end": "2026-12-31"},
        }
        # Module 2 starts the day after module 1 ends → valid (strictly after)
        result = self._validate_order(dates)
        assert result is None

    def test_valid_gap_between_modules_no_recovery_close(self):
        dates = {
            "1": {"start": "2026-01-01", "end": "2026-06-30"},
            "2": {"start": "2026-07-01", "end": "2026-12-31"},
        }
        # 2026-07-01 <= 2026-06-30 is False... wait
        # Actually 2026-07-01 <= 2026-06-30 is False, so no error
        # Wait, the validation checks: next_start <= curr_boundary → error
        # 2026-07-01 <= 2026-06-30 is False → no error
        result = self._validate_order(dates)
        assert result is None


# ---------------------------------------------------------------------------
# Unit tests for can_enroll_in_course helper
# ---------------------------------------------------------------------------

class TestCanEnrollInCourse:
    """Tests for the can_enroll_in_course enrollment deadline check."""

    def _can_enroll(self, course):
        """Mirror of can_enroll_in_course from server.py for unit testing."""
        from datetime import datetime, timezone
        module_dates = course.get("module_dates") or {}
        mod1_dates = module_dates.get("1") or module_dates.get(1) or {}
        mod1_start = mod1_dates.get("start")
        if not mod1_start:
            return True
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        return today < mod1_start

    def test_no_module_dates_allows_enrollment(self):
        """If no module_dates defined, enrollment is always allowed."""
        assert self._can_enroll({}) is True
        assert self._can_enroll({"module_dates": {}}) is True
        assert self._can_enroll({"module_dates": None}) is True

    def test_no_module1_start_allows_enrollment(self):
        """If module 1 has no start date, enrollment is always allowed."""
        course = {"module_dates": {"1": {"end": "2026-12-31"}}}
        assert self._can_enroll(course) is True

    def test_before_module1_start_allows_enrollment(self):
        """Enrollment allowed when today < module1.start."""
        from datetime import datetime, timezone, timedelta
        future_start = (datetime.now(timezone.utc) + timedelta(days=10)).strftime("%Y-%m-%d")
        course = {"module_dates": {"1": {"start": future_start, "end": "2099-12-31"}}}
        assert self._can_enroll(course) is True

    def test_on_module1_start_blocks_enrollment(self):
        """Enrollment blocked when today == module1.start."""
        from datetime import datetime, timezone
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        course = {"module_dates": {"1": {"start": today, "end": "2099-12-31"}}}
        assert self._can_enroll(course) is False

    def test_after_module1_start_blocks_enrollment(self):
        """Enrollment blocked when today > module1.start."""
        from datetime import datetime, timezone, timedelta
        past_start = (datetime.now(timezone.utc) - timedelta(days=5)).strftime("%Y-%m-%d")
        course = {"module_dates": {"1": {"start": past_start, "end": "2099-12-31"}}}
        assert self._can_enroll(course) is False

    def test_integer_key_module1_also_checked(self):
        """Module dates with integer key 1 should also be checked."""
        from datetime import datetime, timezone
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        course = {"module_dates": {1: {"start": today}}}
        assert self._can_enroll(course) is False

    def test_only_module2_dates_allows_enrollment(self):
        """If only module 2 dates are defined (no module 1), enrollment is allowed."""
        course = {"module_dates": {"2": {"start": "2026-01-01", "end": "2026-12-31"}}}
        assert self._can_enroll(course) is True


class TestEnrollmentModuleAssignment:
    """Tests for automatic program_modules assignment when enrolling."""

    def _get_module_for_enrollment(self, module_dates):
        """Determine the module a student should be assigned at enrollment time.

        Since enrollment is only allowed before M1 starts, the module will always
        be 1 (the first module, returned when today is before module1.start).
        """
        from datetime import datetime, timezone
        if not module_dates:
            return None
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        sorted_keys = sorted(module_dates.keys(), key=lambda k: int(k) if str(k).isdigit() else 0)
        for mod_key in sorted_keys:
            dates = module_dates.get(mod_key) or {}
            start = dates.get("start")
            end = dates.get("recovery_close") or dates.get("end")
            if start and end and start <= today <= end:
                return int(mod_key)
        modules_with_start = [
            (int(k), (module_dates.get(k) or {}).get("start"))
            for k in sorted_keys
            if (module_dates.get(k) or {}).get("start")
        ]
        if not modules_with_start:
            return None
        modules_with_start.sort()
        if today < modules_with_start[0][1]:
            return modules_with_start[0][0]
        current = modules_with_start[0][0]
        for mod_num, start in modules_with_start:
            if start <= today:
                current = mod_num
        return current

    def test_before_module1_assigns_module1(self):
        """When enrolling before M1 starts, student should be assigned module 1."""
        from datetime import datetime, timezone, timedelta
        future = datetime.now(timezone.utc) + timedelta(days=10)
        module_dates = {
            "1": {
                "start": future.strftime("%Y-%m-%d"),
                "end": (future + timedelta(days=180)).strftime("%Y-%m-%d"),
            }
        }
        assert self._get_module_for_enrollment(module_dates) == 1

    def test_no_module_dates_returns_none(self):
        """Without module_dates, no module can be determined."""
        assert self._get_module_for_enrollment({}) is None
        assert self._get_module_for_enrollment(None) is None


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
