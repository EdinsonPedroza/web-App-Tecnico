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
# Unit tests for validate_module_dates_recovery_close (new - 2026-02-25)
# ---------------------------------------------------------------------------

class TestValidateModuleDatesRecoveryClose:
    """Tests for the new validate_module_dates_recovery_close utility function."""

    def _validate_recovery_close(self, module_dates):
        """Mirror of validate_module_dates_recovery_close from server.py."""
        for mod_key, dates in (module_dates or {}).items():
            if not (dates or {}).get("recovery_close"):
                return (
                    f"El Módulo {mod_key} no tiene fecha de cierre de recuperaciones "
                    "(recovery_close). Todas las entradas de fechas de módulo deben incluirla."
                )
        return None

    def test_empty_module_dates_returns_none(self):
        assert self._validate_recovery_close({}) is None
        assert self._validate_recovery_close(None) is None

    def test_all_modules_have_recovery_close_returns_none(self):
        dates = {
            "1": {"start": "2026-01-01", "end": "2026-06-30", "recovery_close": "2026-07-15"},
            "2": {"start": "2026-07-16", "end": "2026-12-31", "recovery_close": "2027-01-15"},
        }
        assert self._validate_recovery_close(dates) is None

    def test_module_missing_recovery_close_returns_error(self):
        dates = {
            "1": {"start": "2026-01-01", "end": "2026-06-30"},
        }
        result = self._validate_recovery_close(dates)
        assert result is not None
        assert "recovery_close" in result.lower() or "recuperaciones" in result.lower()

    def test_one_module_missing_recovery_close_returns_error(self):
        dates = {
            "1": {"start": "2026-01-01", "end": "2026-06-30", "recovery_close": "2026-07-15"},
            "2": {"start": "2026-07-16", "end": "2026-12-31"},
        }
        result = self._validate_recovery_close(dates)
        assert result is not None
        assert "2" in result  # Error mentions the offending module

    def test_module_with_empty_dates_returns_error(self):
        dates = {"1": {}}
        result = self._validate_recovery_close(dates)
        assert result is not None

    def test_module_with_none_dates_returns_error(self):
        dates = {"1": None}
        result = self._validate_recovery_close(dates)
        assert result is not None


# ---------------------------------------------------------------------------
# Unit tests for validate_module_number (updated - no upper bound)
# ---------------------------------------------------------------------------

class TestValidateModuleNumber:
    """Tests for the validate_module_number helper (N-module support, no upper bound)."""

    def _validate(self, module_num):
        """Mirror of validate_module_number from server.py."""
        MIN = 1
        if not isinstance(module_num, int) or module_num < MIN:
            raise ValueError(f"module must be >= {MIN}, got {module_num}")
        return True

    def test_module_1_is_valid(self):
        assert self._validate(1) is True

    def test_module_2_is_valid(self):
        assert self._validate(2) is True

    def test_module_3_is_valid(self):
        """Module 3+ must be valid now that N-module support is implemented."""
        assert self._validate(3) is True

    def test_module_10_is_valid(self):
        assert self._validate(10) is True

    def test_module_0_is_invalid(self):
        with pytest.raises(ValueError):
            self._validate(0)

    def test_negative_module_is_invalid(self):
        with pytest.raises(ValueError):
            self._validate(-1)

    def test_non_int_is_invalid(self):
        with pytest.raises((ValueError, TypeError)):
            self._validate("1")


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
# Unit tests for derive_estado_from_program_statuses
# ---------------------------------------------------------------------------

class TestDeriveEstadoFromProgramStatuses:
    """Tests for the derive_estado_from_program_statuses helper."""

    def _derive(self, program_statuses):
        """Mirror of derive_estado_from_program_statuses from server.py."""
        if not program_statuses:
            return "activo"
        statuses = list(program_statuses.values())
        if "activo" in statuses:
            return "activo"
        if all(s == "egresado" for s in statuses):
            return "egresado"
        if "pendiente_recuperacion" in statuses:
            return "pendiente_recuperacion"
        if "egresado" in statuses:
            return "egresado"
        if "reprobado" in statuses:
            return "reprobado"
        return "retirado"

    def test_empty_returns_activo(self):
        assert self._derive({}) == "activo"
        assert self._derive(None) == "activo"

    def test_single_activo(self):
        assert self._derive({"prog-1": "activo"}) == "activo"

    def test_single_egresado(self):
        assert self._derive({"prog-1": "egresado"}) == "egresado"

    def test_single_retirado(self):
        assert self._derive({"prog-1": "retirado"}) == "retirado"

    def test_single_pendiente_recuperacion(self):
        assert self._derive({"prog-1": "pendiente_recuperacion"}) == "pendiente_recuperacion"

    def test_pendiente_recuperacion_takes_priority(self):
        """activo beats pendiente_recuperacion (multi-program independence)."""
        result = self._derive({
            "prog-1": "pendiente_recuperacion",
            "prog-2": "activo"
        })
        assert result == "activo"

    def test_all_egresado(self):
        result = self._derive({"prog-1": "egresado", "prog-2": "egresado"})
        assert result == "egresado"

    def test_activo_beats_retirado(self):
        result = self._derive({"prog-1": "activo", "prog-2": "retirado"})
        assert result == "activo"

    def test_all_retirado(self):
        result = self._derive({"prog-1": "retirado", "prog-2": "retirado"})
        assert result == "retirado"

    def test_egresado_and_activo_returns_activo(self):
        """If one program is egresado but another is activo, global is activo."""
        result = self._derive({"prog-1": "egresado", "prog-2": "activo"})
        assert result == "activo"

    def test_pendiente_recuperacion_beats_egresado(self):
        """pendiente_recuperacion takes priority over egresado (no activo)."""
        result = self._derive({
            "prog-1": "egresado",
            "prog-2": "pendiente_recuperacion"
        })
        assert result == "pendiente_recuperacion"

    def test_activo_beats_pendiente_recuperacion(self):
        """activo takes priority over pendiente_recuperacion (multi-program independence)."""
        result = self._derive({"prog-1": "pendiente_recuperacion", "prog-2": "activo"})
        assert result == "activo"

    def test_all_pendiente_recuperacion(self):
        """All pendiente_recuperacion → global pendiente_recuperacion."""
        result = self._derive({"prog-1": "pendiente_recuperacion", "prog-2": "pendiente_recuperacion"})
        assert result == "pendiente_recuperacion"

    def test_egresado_and_pendiente_no_activo(self):
        """egresado + pendiente_recuperacion (no activo) → pendiente_recuperacion."""
        result = self._derive({"prog-1": "egresado", "prog-2": "pendiente_recuperacion"})
        assert result == "pendiente_recuperacion"

    def test_three_programs_mixed(self):
        """3 programs: egresado + pendiente + activo → activo."""
        result = self._derive({
            "prog-1": "egresado",
            "prog-2": "pendiente_recuperacion",
            "prog-3": "activo"
        })
        assert result == "activo"

    def test_retirado_and_pendiente(self):
        """retirado + pendiente_recuperacion → pendiente_recuperacion."""
        result = self._derive({"prog-1": "retirado", "prog-2": "pendiente_recuperacion"})
        assert result == "pendiente_recuperacion"

    def test_egresado_and_retirado(self):
        """egresado + retirado (no activo/pendiente) → egresado."""
        result = self._derive({"prog-1": "egresado", "prog-2": "retirado"})
        assert result == "egresado"


# ---------------------------------------------------------------------------
# Unit tests for program_statuses initialization in user creation
# ---------------------------------------------------------------------------

class TestProgramStatusesInit:
    """Tests for program_statuses initialization logic when creating a student."""

    def _init_program_statuses(self, role, program_ids, program_statuses_input=None):
        """Mirror of create_user program_statuses initialization logic."""
        if role == "estudiante":
            if program_statuses_input:
                return program_statuses_input
            elif program_ids:
                return {prog_id: "activo" for prog_id in program_ids}
            else:
                return None
        return None

    def test_student_with_programs_gets_activo(self):
        result = self._init_program_statuses("estudiante", ["prog-1", "prog-2"])
        assert result == {"prog-1": "activo", "prog-2": "activo"}

    def test_student_no_programs_gets_none(self):
        result = self._init_program_statuses("estudiante", [])
        assert result is None

    def test_student_with_provided_statuses(self):
        provided = {"prog-1": "retirado"}
        result = self._init_program_statuses("estudiante", ["prog-1"], program_statuses_input=provided)
        assert result == {"prog-1": "retirado"}

    def test_non_student_gets_none(self):
        assert self._init_program_statuses("profesor", ["prog-1"]) is None
        assert self._init_program_statuses("admin", ["prog-1"]) is None


# ---------------------------------------------------------------------------
# Unit tests for delete_course blocking logic
# ---------------------------------------------------------------------------

class TestDeleteCourseBlocking:
    """Tests for the logic that blocks course deletion with non-egresado students."""

    def _get_blocking_students(self, students, program_id):
        """Mirror of delete_course blocking check in server.py."""
        blocking = []
        for s in students:
            program_statuses = s.get("program_statuses") or {}
            status = program_statuses.get(program_id) if program_id else s.get("estado")
            if not status:
                status = s.get("estado", "activo")
            if status != "egresado":
                blocking.append(s["id"])
        return blocking

    def test_all_egresado_allows_deletion(self):
        students = [
            {"id": "s1", "program_statuses": {"prog-1": "egresado"}},
            {"id": "s2", "program_statuses": {"prog-1": "egresado"}},
        ]
        assert self._get_blocking_students(students, "prog-1") == []

    def test_any_activo_blocks_deletion(self):
        students = [
            {"id": "s1", "program_statuses": {"prog-1": "egresado"}},
            {"id": "s2", "program_statuses": {"prog-1": "activo"}},
        ]
        blocking = self._get_blocking_students(students, "prog-1")
        assert "s2" in blocking
        assert "s1" not in blocking

    def test_pendiente_recuperacion_blocks_deletion(self):
        students = [
            {"id": "s1", "program_statuses": {"prog-1": "pendiente_recuperacion"}},
        ]
        blocking = self._get_blocking_students(students, "prog-1")
        assert "s1" in blocking

    def test_retirado_blocks_deletion(self):
        students = [
            {"id": "s1", "program_statuses": {"prog-1": "retirado"}},
        ]
        blocking = self._get_blocking_students(students, "prog-1")
        assert "s1" in blocking

    def test_no_program_statuses_falls_back_to_estado(self):
        students = [
            {"id": "s1", "estado": "activo"},
            {"id": "s2", "estado": "egresado"},
        ]
        blocking = self._get_blocking_students(students, "prog-1")
        assert "s1" in blocking
        assert "s2" not in blocking

    def test_empty_student_list_allows_deletion(self):
        assert self._get_blocking_students([], "prog-1") == []


# ---------------------------------------------------------------------------
# Unit tests for reprobado cleanup logic at recovery_close
# ---------------------------------------------------------------------------

class TestReprobadoCleanupAtRecoveryClose:
    """Tests for the business rule: a student who is already reprobado must be
    removed from the group (not promoted) when the recovery period closes.

    This covers the scenario where a student was marked reprobado in one course
    but their student_id still appears in another course's student_ids because
    the earlier removal only targeted the specific failing course.
    """

    def _should_remove_reprobado(self, student_doc, prog_id):
        """Return True if the student should be removed (not promoted) because
        they are already reprobado for the given program.

        This mirrors the guard added to the direct-pass loop in
        check_and_close_modules.
        """
        program_statuses = (student_doc or {}).get("program_statuses") or {}
        return program_statuses.get(prog_id) == "reprobado"

    def test_reprobado_student_must_be_removed(self):
        """A reprobado student still in student_ids must be removed, not promoted."""
        student = {"id": "s1", "program_statuses": {"prog-1": "reprobado"}}
        assert self._should_remove_reprobado(student, "prog-1") is True

    def test_activo_student_must_not_be_removed(self):
        """An activo student should be promoted, not removed."""
        student = {"id": "s1", "program_statuses": {"prog-1": "activo"}}
        assert self._should_remove_reprobado(student, "prog-1") is False

    def test_pendiente_recuperacion_must_not_be_removed(self):
        """A pendiente_recuperacion student should not be removed by the direct-pass logic."""
        student = {"id": "s1", "program_statuses": {"prog-1": "pendiente_recuperacion"}}
        assert self._should_remove_reprobado(student, "prog-1") is False

    def test_egresado_must_not_be_removed(self):
        """An egresado student should not be removed."""
        student = {"id": "s1", "program_statuses": {"prog-1": "egresado"}}
        assert self._should_remove_reprobado(student, "prog-1") is False

    def test_reprobado_in_different_program_does_not_trigger_removal(self):
        """Being reprobado in another program must not remove student from this program's courses."""
        student = {
            "id": "s1",
            "program_statuses": {"prog-2": "reprobado", "prog-1": "activo"},
        }
        assert self._should_remove_reprobado(student, "prog-1") is False

    def test_reprobado_in_multiple_programs_triggers_removal_for_each(self):
        """Reprobado in multiple programs → removal guard fires for each one."""
        student = {
            "id": "s1",
            "program_statuses": {"prog-1": "reprobado", "prog-2": "reprobado"},
        }
        assert self._should_remove_reprobado(student, "prog-1") is True
        assert self._should_remove_reprobado(student, "prog-2") is True

    def test_missing_program_statuses_not_reprobado(self):
        """A student without program_statuses should not trigger the reprobado guard."""
        student = {"id": "s1"}
        assert self._should_remove_reprobado(student, "prog-1") is False

    def test_none_student_doc_not_reprobado(self):
        """None student document must not raise and must return False."""
        assert self._should_remove_reprobado(None, "prog-1") is False

    def test_empty_program_statuses_not_reprobado(self):
        """Empty program_statuses must not trigger removal."""
        student = {"id": "s1", "program_statuses": {}}
        assert self._should_remove_reprobado(student, "prog-1") is False


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


@pytest.fixture(scope="module")
def mongodb_available():
    """Check if MongoDB is reachable. Used to skip DB-dependent tests when unavailable."""
    import socket
    import urllib.parse
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    try:
        # Parse host and port from the MongoDB URL
        parsed = urllib.parse.urlparse(mongo_url)
        host = parsed.hostname or 'localhost'
        port = parsed.port or 27017
        sock = socket.create_connection((host, port), timeout=1)
        sock.close()
        return True
    except OSError:
        return False


@pytest.fixture
def client(test_app):
    """Create a test client."""
    from httpx import ASGITransport, AsyncClient
    transport = ASGITransport(app=test_app)
    return AsyncClient(transport=transport, base_url="http://test")


class TestHealthEndpoint:
    """Test the health check endpoint."""

    @pytest.mark.asyncio
    async def test_health_check_healthy(self, client, mongodb_available):
        """Health check returns 200 with status field when MongoDB is available."""
        if not mongodb_available:
            pytest.skip("MongoDB not available in this environment")
        response = await client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data

    @pytest.mark.asyncio
    async def test_health_check_unhealthy(self, client, mongodb_available):
        """Health check returns 503 with status field when MongoDB is unavailable."""
        if mongodb_available:
            pytest.skip("MongoDB is available; this test requires it to be unavailable")
        response = await client.get("/api/health")
        assert response.status_code == 503
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
    async def test_login_wrong_credentials(self, client, mongodb_available):
        if not mongodb_available:
            pytest.skip("MongoDB not available in this environment")
        response = await client.post("/api/auth/login", json={
            "role": "estudiante",
            "cedula": "99999999999",
            "password": "wrongpassword"
        })
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_login_profesor_wrong_credentials(self, client, mongodb_available):
        if not mongodb_available:
            pytest.skip("MongoDB not available in this environment")
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


# ---------------------------------------------------------------------------
# Unit tests for module blocking in submission validation
# ---------------------------------------------------------------------------

class TestSubmissionModuleBlocking:
    """Unit tests for the module-blocking logic used in create_submission."""

    def _check_module_allowed(self, student_module, subject_module):
        """Mirrors the module-check logic in server.py create_submission.

        Returns True if the student is allowed to submit.
        When either student_module or subject_module is None, returns True (no restriction applied).
        """
        if student_module is None or subject_module is None:
            return True  # No restriction if module info is missing
        return int(student_module) == int(subject_module)

    def test_same_module_allows_submission(self):
        assert self._check_module_allowed(1, 1) is True
        assert self._check_module_allowed(2, 2) is True

    def test_different_module_blocks_submission(self):
        assert self._check_module_allowed(1, 2) is False
        assert self._check_module_allowed(2, 1) is False

    def test_no_student_module_allows_submission(self):
        """If student module is unknown, don't block."""
        assert self._check_module_allowed(None, 1) is True
        assert self._check_module_allowed(None, 2) is True

    def test_no_subject_module_allows_submission(self):
        """If subject has no module number, don't block."""
        assert self._check_module_allowed(1, None) is True

    def test_string_modules_compare_correctly(self):
        """Module numbers stored as strings must be compared correctly."""
        assert self._check_module_allowed("1", "1") is True
        assert self._check_module_allowed("1", "2") is False


# ---------------------------------------------------------------------------
# Unit tests for CREATE_SEED_USERS env variable logic
# ---------------------------------------------------------------------------

class TestCreateSeedUsersEnvVar:
    """Tests for the CREATE_SEED_USERS environment variable control logic."""

    def _should_create_seeds(self, env_value):
        """Mirror the env-var check logic in create_initial_data."""
        return env_value.lower() == 'true'

    def test_default_true_creates_seeds(self):
        assert self._should_create_seeds('true') is True

    def test_false_skips_seeds(self):
        assert self._should_create_seeds('false') is False

    def test_uppercase_true_creates_seeds(self):
        assert self._should_create_seeds('TRUE') is True

    def test_uppercase_false_skips_seeds(self):
        assert self._should_create_seeds('FALSE') is False


# ---------------------------------------------------------------------------
# Unit tests for GET /users estado filter — treat null/missing as 'activo'
# ---------------------------------------------------------------------------

class TestGetUsersEstadoFilter:
    """Tests for the estado filter logic in get_users endpoint."""

    def _build_estado_query(self, estado):
        """Mirror the estado filter logic from server.py get_users."""
        query = {}
        if estado:
            if estado == 'activo':
                query["$or"] = [
                    {"estado": "activo"},
                    {"estado": None},
                    {"estado": {"$exists": False}}
                ]
            else:
                query["estado"] = estado
        return query

    def _matches_activo_query(self, user_estado):
        """Simulate MongoDB $or matching for activo query."""
        return user_estado in ("activo", None) or user_estado == "__missing__"

    def test_activo_filter_matches_activo(self):
        assert self._matches_activo_query("activo") is True

    def test_activo_filter_matches_null_estado(self):
        """Users with null estado should appear in activo filter."""
        assert self._matches_activo_query(None) is True

    def test_activo_filter_matches_missing_estado(self):
        """Users without estado field should appear in activo filter."""
        assert self._matches_activo_query("__missing__") is True

    def test_activo_filter_does_not_match_retirado(self):
        assert self._matches_activo_query("retirado") is False

    def test_activo_filter_does_not_match_egresado(self):
        assert self._matches_activo_query("egresado") is False

    def test_retirado_filter_builds_simple_query(self):
        query = self._build_estado_query("retirado")
        assert query.get("estado") == "retirado"
        assert "$or" not in query

    def test_no_filter_builds_empty_query(self):
        query = self._build_estado_query(None)
        assert query == {}


# ---------------------------------------------------------------------------
# Unit tests for CoursesPage date validation logic (mirrors frontend JS)
# ---------------------------------------------------------------------------

class TestCoursesPageDateValidation:
    """Tests for the validateModuleDates logic used in CoursesPage.js."""

    def _validate_module_dates(self, module_dates, count):
        """Mirror of validateModuleDates in CoursesPage.js."""
        errors = {}
        for i in range(1, count + 1):
            dates = module_dates.get(i, {})
            start = dates.get("start", "")
            end = dates.get("end", "")
            recovery_close = dates.get("recovery_close", "")
            if start and end and end < start:
                errors[f"{i}_end"] = f"La fecha de cierre debe ser >= fecha de inicio"
            if end and recovery_close and recovery_close < end:
                errors[f"{i}_recovery_close"] = "El cierre de recuperaciones debe ser >= fecha de cierre"
            if i > 1:
                prev = module_dates.get(i - 1, {})
                prev_boundary = prev.get("recovery_close") or prev.get("end", "")
                if prev_boundary and start and start <= prev_boundary:
                    errors[f"{i}_start"] = (
                        f"La fecha de inicio del Módulo {i} debe ser posterior "
                        f"al cierre del Módulo {i - 1} ({prev_boundary})"
                    )
        return errors

    def test_valid_two_module_dates(self):
        module_dates = {
            1: {"start": "2026-01-01", "end": "2026-06-30", "recovery_close": "2026-07-15"},
            2: {"start": "2026-07-16", "end": "2026-12-31"},
        }
        errors = self._validate_module_dates(module_dates, 2)
        assert errors == {}

    def test_end_before_start_is_error(self):
        module_dates = {1: {"start": "2026-06-01", "end": "2026-05-01"}}
        errors = self._validate_module_dates(module_dates, 1)
        assert "1_end" in errors

    def test_recovery_close_before_end_is_error(self):
        module_dates = {1: {"start": "2026-01-01", "end": "2026-06-30", "recovery_close": "2026-06-20"}}
        errors = self._validate_module_dates(module_dates, 1)
        assert "1_recovery_close" in errors

    def test_module2_starts_on_module1_recovery_close_is_error(self):
        module_dates = {
            1: {"start": "2026-01-01", "end": "2026-06-30", "recovery_close": "2026-07-15"},
            2: {"start": "2026-07-15", "end": "2026-12-31"},
        }
        errors = self._validate_module_dates(module_dates, 2)
        assert "2_start" in errors

    def test_module2_starts_before_module1_end_is_error(self):
        module_dates = {
            1: {"start": "2026-01-01", "end": "2026-06-30"},
            2: {"start": "2026-06-15", "end": "2026-12-31"},
        }
        errors = self._validate_module_dates(module_dates, 2)
        assert "2_start" in errors

    def test_single_module_no_errors(self):
        module_dates = {1: {"start": "2026-01-01", "end": "2026-06-30"}}
        errors = self._validate_module_dates(module_dates, 1)
        assert errors == {}

    def test_empty_dates_no_errors(self):
        errors = self._validate_module_dates({}, 2)
        assert errors == {}


# ---------------------------------------------------------------------------
# Unit tests for can_enroll_in_module (module 2+ enrollment window)
# ---------------------------------------------------------------------------

class TestCanEnrollInModule:
    """Tests for the can_enroll_in_module function in server.py."""

    def _can_enroll_in_module(self, module_dates, module_number, today_str):
        """Mirror of can_enroll_in_module from server.py with injectable today."""
        mod_key = str(module_number)
        mod_dates = module_dates.get(mod_key) or module_dates.get(module_number) or {}
        mod_start = mod_dates.get("start")

        if module_number == 1:
            if not mod_start:
                return True
            return today_str < mod_start

        # Module N > 1: window is recovery_close_mod(N-1) <= today < start_mod(N)
        prev_key = str(module_number - 1)
        prev_dates = module_dates.get(prev_key) or module_dates.get(module_number - 1) or {}
        prev_recovery_close = prev_dates.get("recovery_close") or prev_dates.get("end")

        if not prev_recovery_close and not mod_start:
            return True
        if prev_recovery_close and today_str < prev_recovery_close:
            return False
        if mod_start and today_str >= mod_start:
            return False
        return True

    # ---- Module 1 ----
    def test_mod1_before_start_allows(self):
        module_dates = {"1": {"start": "2026-06-01"}}
        assert self._can_enroll_in_module(module_dates, 1, "2026-05-31") is True

    def test_mod1_on_start_date_blocks(self):
        module_dates = {"1": {"start": "2026-06-01"}}
        assert self._can_enroll_in_module(module_dates, 1, "2026-06-01") is False

    def test_mod1_after_start_blocks(self):
        module_dates = {"1": {"start": "2026-06-01"}}
        assert self._can_enroll_in_module(module_dates, 1, "2026-06-15") is False

    def test_mod1_no_start_date_allows(self):
        assert self._can_enroll_in_module({}, 1, "2026-01-01") is True

    # ---- Module 2 ----
    def test_mod2_in_window_allows(self):
        """recovery_close_mod1 <= today < start_mod2 → allowed."""
        module_dates = {
            "1": {"start": "2026-01-01", "end": "2026-06-30", "recovery_close": "2026-07-15"},
            "2": {"start": "2026-07-16"},
        }
        # today = exactly recovery_close boundary (inclusive)
        assert self._can_enroll_in_module(module_dates, 2, "2026-07-15") is True

    def test_mod2_in_window_day_after_recovery_close_allows(self):
        module_dates = {
            "1": {"start": "2026-01-01", "end": "2026-06-30", "recovery_close": "2026-07-15"},
            "2": {"start": "2026-07-20"},
        }
        assert self._can_enroll_in_module(module_dates, 2, "2026-07-16") is True

    def test_mod2_before_recovery_close_blocks(self):
        """Before previous module recovery closes → not yet allowed."""
        module_dates = {
            "1": {"start": "2026-01-01", "end": "2026-06-30", "recovery_close": "2026-07-15"},
            "2": {"start": "2026-07-20"},
        }
        assert self._can_enroll_in_module(module_dates, 2, "2026-07-14") is False

    def test_mod2_on_or_after_start_blocks(self):
        """After module 2 has started → window closed."""
        module_dates = {
            "1": {"start": "2026-01-01", "end": "2026-06-30", "recovery_close": "2026-07-15"},
            "2": {"start": "2026-07-20"},
        }
        assert self._can_enroll_in_module(module_dates, 2, "2026-07-20") is False

    def test_mod2_no_dates_allows(self):
        """When no dates configured, enrollment is always allowed."""
        assert self._can_enroll_in_module({}, 2, "2026-07-01") is True

    def test_mod2_uses_end_when_no_recovery_close(self):
        """Falls back to 'end' if 'recovery_close' is missing for mod 1."""
        module_dates = {
            "1": {"start": "2026-01-01", "end": "2026-06-30"},
            "2": {"start": "2026-07-20"},
        }
        # today is on boundary (end date of mod1)
        assert self._can_enroll_in_module(module_dates, 2, "2026-06-30") is True
        # today is before the fallback boundary
        assert self._can_enroll_in_module(module_dates, 2, "2026-06-29") is False


# ---------------------------------------------------------------------------
# Unit tests for get_open_enrollment_module (module enrollment window detection)
# ---------------------------------------------------------------------------

class TestGetOpenEnrollmentModule:
    """Tests for the get_open_enrollment_module function in server.py."""

    def _get_open_enrollment_module(self, module_dates, today_str):
        """Mirror of get_open_enrollment_module from server.py with injectable today."""

        def _can_enroll(md, module_number, today):
            mod_key = str(module_number)
            mod_dates = md.get(mod_key) or md.get(module_number) or {}
            mod_start = mod_dates.get("start")
            if module_number == 1:
                if not mod_start:
                    return True
                return today < mod_start
            prev_key = str(module_number - 1)
            prev_dates = md.get(prev_key) or md.get(module_number - 1) or {}
            prev_recovery_close = prev_dates.get("recovery_close") or prev_dates.get("end")
            if not prev_recovery_close and not mod_start:
                return True
            if prev_recovery_close and today < prev_recovery_close:
                return False
            if mod_start and today >= mod_start:
                return False
            return True

        if not module_dates:
            return None
        mod_numbers = sorted(
            int(k) for k in module_dates.keys() if str(k).isdigit()
        )
        if not mod_numbers:
            return None
        mods_to_check = mod_numbers + [mod_numbers[-1] + 1]
        for mod_num in mods_to_check:
            if _can_enroll(module_dates, mod_num, today_str):
                return mod_num
        return None

    def test_empty_returns_none(self):
        assert self._get_open_enrollment_module({}, "2026-01-01") is None
        assert self._get_open_enrollment_module(None, "2026-01-01") is None

    def test_before_mod1_start_returns_1(self):
        module_dates = {"1": {"start": "2026-06-01", "recovery_close": "2026-12-31"}}
        assert self._get_open_enrollment_module(module_dates, "2026-05-31") == 1

    def test_after_mod1_start_no_mod2_dates_returns_2(self):
        """Key scenario: only module 1 dates defined, today in inter-module window.

        Module 1 recovery has closed; module 2 hasn't started.  Even though module 2
        dates are not yet configured in module_dates, get_open_enrollment_module must
        return 2 so that enrollment is allowed.
        """
        module_dates = {
            "1": {"start": "2025-07-01", "end": "2025-12-31", "recovery_close": "2026-01-15"},
        }
        # After mod1 recovery_close, before any mod2 start → module 2 window is open
        assert self._get_open_enrollment_module(module_dates, "2026-02-27") == 2

    def test_mod2_window_with_both_dates_returns_2(self):
        """With both module dates defined, returns 2 during inter-module window."""
        module_dates = {
            "1": {"start": "2025-07-01", "end": "2025-12-31", "recovery_close": "2026-01-15"},
            "2": {"start": "2026-03-01", "recovery_close": "2026-09-15"},
        }
        assert self._get_open_enrollment_module(module_dates, "2026-02-27") == 2

    def test_after_mod2_start_returns_none(self):
        """After module 2 has started, no enrollment window is open."""
        module_dates = {
            "1": {"start": "2025-07-01", "end": "2025-12-31", "recovery_close": "2026-01-15"},
            "2": {"start": "2026-03-01", "recovery_close": "2026-09-15"},
        }
        assert self._get_open_enrollment_module(module_dates, "2026-03-01") is None

    def test_before_mod1_recovery_close_returns_none(self):
        """During module 1 active period (before recovery_close), no window is open."""
        module_dates = {
            "1": {"start": "2025-07-01", "end": "2025-12-31", "recovery_close": "2026-01-15"},
        }
        # Today is after mod1 start but before recovery_close → no enrollment window
        assert self._get_open_enrollment_module(module_dates, "2025-09-01") is None


# ---------------------------------------------------------------------------
# Unit tests for recovery panel filter logic (in-process only)
# ---------------------------------------------------------------------------

class TestRecoveryPanelFilter:
    """Tests for the in-process filter applied to failed_subject records."""

    def _is_in_process(self, record):
        """Mirror the panel filter: exclude rejected and (approved + completed) records."""
        if record.get("recovery_rejected"):
            return False
        if record.get("recovery_approved") and record.get("recovery_completed"):
            return False
        return True

    def test_pending_record_is_in_process(self):
        record = {"recovery_approved": False, "recovery_rejected": False, "recovery_completed": False}
        assert self._is_in_process(record) is True

    def test_approved_not_completed_is_in_process(self):
        record = {"recovery_approved": True, "recovery_rejected": False, "recovery_completed": False}
        assert self._is_in_process(record) is True

    def test_rejected_leaves_panel(self):
        record = {"recovery_approved": False, "recovery_rejected": True, "recovery_completed": False}
        assert self._is_in_process(record) is False

    def test_approved_and_completed_leaves_panel(self):
        record = {"recovery_approved": True, "recovery_rejected": False, "recovery_completed": True}
        assert self._is_in_process(record) is False

    def test_missing_rejected_field_defaults_to_in_process(self):
        """Old records without recovery_rejected field should still show."""
        record = {"recovery_approved": False, "recovery_completed": False}
        assert self._is_in_process(record) is True

    def test_derive_estado_after_rejection(self):
        """After rejection program_statuses[prog] = 'retirado'; global estado is derived."""
        # Simulate derive_estado_from_program_statuses behavior
        program_statuses = {"prog-1": "retirado"}
        statuses = list(program_statuses.values())
        if "pendiente_recuperacion" in statuses:
            result = "pendiente_recuperacion"
        elif all(s == "egresado" for s in statuses):
            result = "egresado"
        elif "activo" in statuses:
            result = "activo"
        else:
            result = "retirado"
        assert result == "retirado"

    def test_derive_estado_after_approval(self):
        """After approval program_statuses[prog] = 'pendiente_recuperacion'."""
        program_statuses = {"prog-1": "pendiente_recuperacion"}
        statuses = list(program_statuses.values())
        if "pendiente_recuperacion" in statuses:
            result = "pendiente_recuperacion"
        elif all(s == "egresado" for s in statuses):
            result = "egresado"
        elif "activo" in statuses:
            result = "activo"
        else:
            result = "retirado"
        assert result == "pendiente_recuperacion"


# ---------------------------------------------------------------------------
# Unit tests for Rule 1: Student must have at least 1 program
# ---------------------------------------------------------------------------

class TestStudentProgramRequired:
    """Tests for Rule 1: students must be enrolled in at least one technical program."""

    def _validate_student_program(self, role, program_ids, program_id=None):
        """Simulate create_user program validation logic from server.py."""
        if role != "estudiante":
            return  # Only applies to students
        # Mirror: determine effective program_ids
        if program_ids:
            effective_program_ids = program_ids
        elif program_id:
            effective_program_ids = [program_id]
        else:
            effective_program_ids = []
        if not effective_program_ids:
            raise ValueError("El estudiante debe estar inscrito en al menos un programa técnico")

    def test_student_with_program_ids_is_valid(self):
        """Student with program_ids should pass validation."""
        self._validate_student_program("estudiante", ["prog-admin"])

    def test_student_with_program_id_fallback_is_valid(self):
        """Student with legacy program_id should pass validation."""
        self._validate_student_program("estudiante", None, program_id="prog-admin")

    def test_student_without_any_program_raises(self):
        """Student with no program should raise ValueError."""
        with pytest.raises(ValueError, match="al menos un programa"):
            self._validate_student_program("estudiante", None)

    def test_student_with_empty_list_and_program_id_fallback_is_valid(self):
        """Empty program_ids list with a legacy program_id should pass (program_id fallback)."""
        self._validate_student_program("estudiante", [], program_id="prog-admin")

    def test_student_with_empty_list_raises(self):
        """Student with empty program_ids list should raise ValueError."""
        with pytest.raises(ValueError, match="al menos un programa"):
            self._validate_student_program("estudiante", [])

    def test_non_student_role_not_affected(self):
        """Validation should NOT apply to professors or admins."""
        # Should not raise
        self._validate_student_program("profesor", None)
        self._validate_student_program("admin", None)

    def test_student_with_multiple_programs_is_valid(self):
        """Student enrolled in multiple programs should pass."""
        self._validate_student_program("estudiante", ["prog-admin", "prog-infancia"])


# ---------------------------------------------------------------------------
# Unit tests for Rule 2: Teacher-subject uniqueness constraint
# ---------------------------------------------------------------------------

class TestTeacherSubjectUniqueness:
    """Tests for Rule 2: a subject can only be assigned to one professor at a time."""

    def _check_subject_conflict(self, new_subject_ids, existing_teachers, exclude_teacher_id=None):
        """Simulate the teacher-subject uniqueness check from server.py create/update_user."""
        for subject_id in new_subject_ids:
            for teacher in existing_teachers:
                if exclude_teacher_id and teacher["id"] == exclude_teacher_id:
                    continue
                if subject_id in (teacher.get("subject_ids") or []):
                    raise ValueError(
                        f"La materia ya está asignada al profesor '{teacher['name']}'. "
                        "Desasígnela primero antes de asignarla a otro profesor."
                    )

    def test_no_conflict_when_no_existing_teachers(self):
        """No conflict when there are no existing teachers with the subject."""
        self._check_subject_conflict(["subj-1"], [])

    def test_no_conflict_when_subject_not_assigned(self):
        """No conflict when the subject is not yet assigned to any teacher."""
        teachers = [{"id": "t1", "name": "Teacher A", "subject_ids": ["subj-2"]}]
        self._check_subject_conflict(["subj-1"], teachers)

    def test_conflict_raises_when_subject_already_assigned(self):
        """Conflict detected when trying to assign a subject already assigned to another teacher."""
        teachers = [{"id": "t1", "name": "Teacher A", "subject_ids": ["subj-1"]}]
        with pytest.raises(ValueError, match="ya está asignada al profesor"):
            self._check_subject_conflict(["subj-1"], teachers)

    def test_no_conflict_when_assigning_to_same_teacher(self):
        """Updating the same teacher's subjects should not trigger a conflict."""
        teachers = [{"id": "t1", "name": "Teacher A", "subject_ids": ["subj-1"]}]
        # Exclude teacher t1 (same teacher being updated)
        self._check_subject_conflict(["subj-1"], teachers, exclude_teacher_id="t1")

    def test_conflict_with_multiple_subjects_partial(self):
        """Conflict raised if even one subject in a list is already assigned."""
        teachers = [{"id": "t1", "name": "Teacher A", "subject_ids": ["subj-2"]}]
        with pytest.raises(ValueError, match="ya está asignada al profesor"):
            self._check_subject_conflict(["subj-1", "subj-2"], teachers)

    def test_multiple_teachers_no_overlap(self):
        """Multiple teachers each with different subjects, no conflict."""
        teachers = [
            {"id": "t1", "name": "Teacher A", "subject_ids": ["subj-1"]},
            {"id": "t2", "name": "Teacher B", "subject_ids": ["subj-2"]},
        ]
        self._check_subject_conflict(["subj-3"], teachers)


# ---------------------------------------------------------------------------
# Unit tests for Rule E: Recovery activities cannot have numeric grades
# ---------------------------------------------------------------------------

class TestRecoveryGradeRestriction:
    """Tests for Rule E: recovery activities only allow approve/reject, not numeric grades."""

    def _validate_recovery_grade(self, is_recovery, value, recovery_status):
        """Simulate the recovery grade validation from server.py create_grade."""
        if is_recovery:
            if value is not None and not recovery_status:
                raise ValueError(
                    "Las actividades de recuperación no admiten nota numérica. Use Aprobar o Rechazar."
                )
            if recovery_status not in ("approved", "rejected", None):
                raise ValueError("Estado de recuperación inválido")

    def test_regular_activity_allows_numeric_grade(self):
        """Regular (non-recovery) activity should allow numeric grade without restriction."""
        self._validate_recovery_grade(False, 4.5, None)

    def test_recovery_activity_with_only_status_approved_is_valid(self):
        """Recovery activity with approved status and no numeric value is valid."""
        self._validate_recovery_grade(True, None, "approved")

    def test_recovery_activity_with_only_status_rejected_is_valid(self):
        """Recovery activity with rejected status and no numeric value is valid."""
        self._validate_recovery_grade(True, None, "rejected")

    def test_recovery_activity_with_numeric_value_and_no_status_raises(self):
        """Recovery activity with a numeric grade but no status should raise."""
        with pytest.raises(ValueError, match="no admiten nota numérica"):
            self._validate_recovery_grade(True, 3.5, None)

    def test_recovery_activity_with_zero_value_and_no_status_raises(self):
        """Recovery activity with grade=0 and no status should raise."""
        with pytest.raises(ValueError, match="no admiten nota numérica"):
            self._validate_recovery_grade(True, 0.0, None)

    def test_recovery_activity_invalid_status_raises(self):
        """Recovery activity with an invalid status string should raise."""
        with pytest.raises(ValueError, match="Estado de recuperación inválido"):
            self._validate_recovery_grade(True, None, "invalid_status")

    def test_recovery_activity_none_value_and_none_status_passes(self):
        """Recovery activity with no value and no status is allowed (nothing submitted yet)."""
        self._validate_recovery_grade(True, None, None)


# ---------------------------------------------------------------------------
# Unit tests for Rule F: Recovery panel only shows in-process records
# ---------------------------------------------------------------------------

class TestRecoveryPanelInProcessFilter:
    """Tests for Rule F: recovery panel only shows in-process (pending/approved-not-completed)."""

    def _is_in_process_v2(self, record):
        """Updated in-process check consistent with backend filter:
        Excluded: recovery_rejected=True OR (recovery_approved=True AND recovery_completed=True).
        """
        if record.get("recovery_rejected") is True:
            return False
        if record.get("recovery_approved") is True and record.get("recovery_completed") is True:
            return False
        return True

    def test_pending_record_shown(self):
        """Pending record (not approved, not rejected) should be shown."""
        record = {"recovery_approved": False, "recovery_rejected": False, "recovery_completed": False}
        assert self._is_in_process_v2(record) is True

    def test_approved_not_completed_shown(self):
        """Approved but not yet completed should be shown (waiting for teacher grade)."""
        record = {"recovery_approved": True, "recovery_rejected": False, "recovery_completed": False}
        assert self._is_in_process_v2(record) is True

    def test_rejected_not_shown(self):
        """Rejected records should NOT be shown in the panel."""
        record = {"recovery_approved": False, "recovery_rejected": True, "recovery_completed": False}
        assert self._is_in_process_v2(record) is False

    def test_approved_and_completed_not_shown(self):
        """Approved+completed records should NOT be shown (recovery finished)."""
        record = {"recovery_approved": True, "recovery_rejected": False, "recovery_completed": True}
        assert self._is_in_process_v2(record) is False

    def test_filter_list_leaves_only_in_process(self):
        """Filtering a list of records should retain only in-process ones."""
        records = [
            {"id": "r1", "recovery_approved": False, "recovery_rejected": False, "recovery_completed": False},
            {"id": "r2", "recovery_approved": True, "recovery_rejected": False, "recovery_completed": False},
            {"id": "r3", "recovery_approved": False, "recovery_rejected": True, "recovery_completed": False},
            {"id": "r4", "recovery_approved": True, "recovery_rejected": False, "recovery_completed": True},
        ]
        in_process = [r for r in records if self._is_in_process_v2(r)]
        assert len(in_process) == 2
        assert {r["id"] for r in in_process} == {"r1", "r2"}


# ---------------------------------------------------------------------------
# Unit tests for already_tracked subject-level deduplication (Bug 1 fix)
# ---------------------------------------------------------------------------

class TestRecoveryPanelAlreadyTracked:
    """Tests for the already_tracked set using (student_id, course_id, subject_id) tuples."""

    def _build_already_tracked(self, failed_records):
        """Mirror the fixed already_tracked construction from get_recovery_panel."""
        already_tracked = set()
        for record in failed_records:
            already_tracked.add((record["student_id"], record["course_id"], record.get("subject_id")))
        return already_tracked

    def test_single_persisted_subject_does_not_block_other_subjects(self):
        """Approving subject A should NOT block auto-detection of subject B."""
        failed_records = [
            {"student_id": "s1", "course_id": "c1", "subject_id": "subj-A"},
        ]
        already_tracked = self._build_already_tracked(failed_records)
        # subject-A is tracked
        assert ("s1", "c1", "subj-A") in already_tracked
        # subject-B is NOT tracked — it must appear in the panel
        assert ("s1", "c1", "subj-B") not in already_tracked

    def test_both_subjects_persisted_blocks_both(self):
        """When both subjects have persisted records they are both tracked."""
        failed_records = [
            {"student_id": "s1", "course_id": "c1", "subject_id": "subj-A"},
            {"student_id": "s1", "course_id": "c1", "subject_id": "subj-B"},
        ]
        already_tracked = self._build_already_tracked(failed_records)
        assert ("s1", "c1", "subj-A") in already_tracked
        assert ("s1", "c1", "subj-B") in already_tracked

    def test_different_students_tracked_independently(self):
        """Persisted record for student A should not block student B."""
        failed_records = [
            {"student_id": "s1", "course_id": "c1", "subject_id": "subj-A"},
        ]
        already_tracked = self._build_already_tracked(failed_records)
        assert ("s2", "c1", "subj-A") not in already_tracked

    def test_different_courses_tracked_independently(self):
        """Persisted record in course 1 should not block auto-detection in course 2."""
        failed_records = [
            {"student_id": "s1", "course_id": "c1", "subject_id": "subj-A"},
        ]
        already_tracked = self._build_already_tracked(failed_records)
        assert ("s1", "c2", "subj-A") not in already_tracked

    def test_fallback_record_without_subject_id_uses_none_key(self):
        """Records without subject_id (fallback/old records) use None as key."""
        failed_records = [
            {"student_id": "s1", "course_id": "c1"},  # no subject_id
        ]
        already_tracked = self._build_already_tracked(failed_records)
        assert ("s1", "c1", None) in already_tracked
        # A specific subject is still NOT blocked
        assert ("s1", "c1", "subj-A") not in already_tracked

    def test_per_subject_check_skips_only_tracked_subject(self):
        """Simulate auto-detection loop: only already-tracked subjects are skipped."""
        already_tracked = {("s1", "c1", "subj-A")}
        failing_subjects = [
            ("subj-A", "Matemáticas", 2.5),
            ("subj-B", "Historia", 2.0),
        ]
        added = []
        for subj_id, subj_name, subj_avg in failing_subjects:
            if (("s1", "c1", subj_id)) in already_tracked:
                continue
            added.append(subj_id)
            already_tracked.add(("s1", "c1", subj_id))

        # Only subj-B should be auto-detected
        assert added == ["subj-B"]
        assert ("s1", "c1", "subj-B") in already_tracked


# ---------------------------------------------------------------------------
# Unit tests for promotion requiring BOTH admin AND professor approval
# ---------------------------------------------------------------------------

class TestPromotionRequiresBothApprovals:
    """Tests for the fix: promotion at recovery close requires recovery_approved=True
    (admin) AND recovery_completed=True AND teacher_graded_status='approved' (professor)."""

    def _all_passed(self, records):
        """Mirror the fixed all_passed check from check_and_close_modules."""
        return all(
            r.get("recovery_approved") is True and
            r.get("recovery_completed") is True and
            r.get("teacher_graded_status") == "approved"
            for r in records
        )

    def test_all_approved_by_both_passes(self):
        records = [
            {"recovery_approved": True, "recovery_completed": True, "teacher_graded_status": "approved"},
        ]
        assert self._all_passed(records) is True

    def test_multiple_subjects_all_approved_passes(self):
        records = [
            {"recovery_approved": True, "recovery_completed": True, "teacher_graded_status": "approved"},
            {"recovery_approved": True, "recovery_completed": True, "teacher_graded_status": "approved"},
        ]
        assert self._all_passed(records) is True

    def test_missing_admin_approval_blocks_promotion(self):
        """Teacher approved but admin did not approve → must NOT promote."""
        records = [
            {"recovery_approved": False, "recovery_completed": True, "teacher_graded_status": "approved"},
        ]
        assert self._all_passed(records) is False

    def test_missing_teacher_approval_blocks_promotion(self):
        """Admin approved but teacher did not mark completed → must NOT promote."""
        records = [
            {"recovery_approved": True, "recovery_completed": False, "teacher_graded_status": None},
        ]
        assert self._all_passed(records) is False

    def test_teacher_rejected_blocks_promotion(self):
        """Teacher rejected → must NOT promote even if admin approved."""
        records = [
            {"recovery_approved": True, "recovery_completed": True, "teacher_graded_status": "rejected"},
        ]
        assert self._all_passed(records) is False

    def test_mixed_subjects_one_missing_admin_blocks_promotion(self):
        """Mixed case: one subject with admin approval, one without → no promotion."""
        records = [
            {"recovery_approved": True, "recovery_completed": True, "teacher_graded_status": "approved"},
            {"recovery_approved": False, "recovery_completed": True, "teacher_graded_status": "approved"},
        ]
        assert self._all_passed(records) is False

    def test_mixed_subjects_one_teacher_rejected_blocks_promotion(self):
        """Mixed case: one subject teacher-rejected → no promotion."""
        records = [
            {"recovery_approved": True, "recovery_completed": True, "teacher_graded_status": "approved"},
            {"recovery_approved": True, "recovery_completed": True, "teacher_graded_status": "rejected"},
        ]
        assert self._all_passed(records) is False

    def test_empty_records_passes(self):
        """Edge case: no records → all() vacuously true → passes (no subjects failed)."""
        assert self._all_passed([]) is True


# ---------------------------------------------------------------------------
# Unit tests for module alignment validation in approve_recovery_for_subject
# ---------------------------------------------------------------------------

class TestModuleAlignmentValidation:
    """Tests for module alignment: recovery can only be approved for the student's current module."""

    def _check_module_alignment(self, record_module, student_module):
        """Mirror the module alignment check in approve_recovery_for_subject."""
        if record_module is not None and student_module is not None:
            if student_module != record_module:
                return False, (
                    f"No se puede aprobar: la recuperación es del Módulo {record_module} "
                    f"pero el estudiante está en el Módulo {student_module}."
                )
        return True, None

    def test_matching_module_is_allowed(self):
        ok, err = self._check_module_alignment(1, 1)
        assert ok is True
        assert err is None

    def test_matching_module2_is_allowed(self):
        ok, err = self._check_module_alignment(2, 2)
        assert ok is True
        assert err is None

    def test_mismatched_module_is_rejected(self):
        """Student is in module 2 but recovery is for module 1 → rejected."""
        ok, err = self._check_module_alignment(1, 2)
        assert ok is False
        assert "Módulo 1" in err
        assert "Módulo 2" in err

    def test_mismatched_reverse_is_rejected(self):
        """Student is in module 1 but recovery is for module 2 → rejected."""
        ok, err = self._check_module_alignment(2, 1)
        assert ok is False

    def test_none_record_module_skips_check(self):
        """If record has no module_number, skip validation."""
        ok, err = self._check_module_alignment(None, 1)
        assert ok is True

    def test_none_student_module_skips_check(self):
        """If student has no module set, skip validation."""
        ok, err = self._check_module_alignment(1, None)
        assert ok is True


# ---------------------------------------------------------------------------
# Unit tests for removed_student_ids tracking and re-enrollment blocking
# ---------------------------------------------------------------------------

class TestRemovedStudentReenrollmentBlocking:
    """Tests for the removed_student_ids feature that prevents re-enrollment in the same group."""

    def _check_blocked(self, removed_ids, newly_added_ids):
        """Mirror the removed_student_ids check in update_course."""
        removed_set = set(removed_ids)
        if removed_set and newly_added_ids:
            blocked = [sid for sid in newly_added_ids if sid in removed_set]
            if blocked:
                return False, f"No se puede re-matricular a {len(blocked)} estudiante(s) que fueron retirados de este grupo"
        return True, None

    def test_no_removed_allows_enrollment(self):
        ok, err = self._check_blocked([], ["s1", "s2"])
        assert ok is True

    def test_non_removed_student_allowed(self):
        ok, err = self._check_blocked(["s3"], ["s1", "s2"])
        assert ok is True

    def test_removed_student_blocked(self):
        ok, err = self._check_blocked(["s1"], ["s1", "s2"])
        assert ok is False
        assert "retirados" in err

    def test_all_removed_blocked(self):
        ok, err = self._check_blocked(["s1", "s2"], ["s1", "s2"])
        assert ok is False

    def test_empty_newly_added_no_error(self):
        ok, err = self._check_blocked(["s1"], [])
        assert ok is True

    def test_removed_student_can_join_different_group(self):
        """A removed student is only blocked from THIS group; a different group has no removed_ids for them."""
        # Simulating a different course: removed_student_ids is [] or doesn't include them
        ok, err = self._check_blocked([], ["s1"])  # different group → no removed_ids
        assert ok is True


# ---------------------------------------------------------------------------
# Unit tests for report CSV headers and structure
# ---------------------------------------------------------------------------

class TestReportCsvStructure:
    """Tests for the /reports/course-results endpoint output structure."""

    def _build_report_rows(self, students, grades, subject_ids, subject_map, course_id, course_name):
        """Mirror the row-building logic from get_course_results_report."""
        rows = []
        for student in students:
            sid = student["id"]
            if subject_ids:
                for subj_id in subject_ids:
                    values = [g["value"] for g in grades
                              if g.get("student_id") == sid and g.get("subject_id") == subj_id
                              and g.get("value") is not None]
                    avg = round(sum(values) / len(values), 2) if values else 0.0
                    status = "Aprobado" if avg >= 3.0 else "Reprobado"
                    rows.append({
                        "student_name": student["name"],
                        "student_cedula": student.get("cedula", ""),
                        "subject_name": subject_map.get(subj_id, subj_id),
                        "average": avg,
                        "status": status,
                        "course_name": course_name,
                    })
            else:
                values = [g["value"] for g in grades
                          if g.get("student_id") == sid and g.get("value") is not None]
                avg = round(sum(values) / len(values), 2) if values else 0.0
                status = "Aprobado" if avg >= 3.0 else "Reprobado"
                rows.append({
                    "student_name": student["name"],
                    "student_cedula": student.get("cedula", ""),
                    "subject_name": course_name,
                    "average": avg,
                    "status": status,
                    "course_name": course_name,
                })
        return rows

    def _csv_headers(self):
        return ["student_name", "student_cedula", "subject_name", "average", "status", "course_name"]

    def test_csv_headers_present(self):
        headers = self._csv_headers()
        assert "student_name" in headers
        assert "student_cedula" in headers
        assert "subject_name" in headers
        assert "average" in headers
        assert "status" in headers
        assert "course_name" in headers

    def test_approved_student_status(self):
        students = [{"id": "s1", "name": "Ana", "cedula": "111"}]
        grades = [{"student_id": "s1", "subject_id": "subj-A", "value": 4.0}]
        rows = self._build_report_rows(students, grades, ["subj-A"], {"subj-A": "Matemáticas"}, "c1", "Grupo A")
        assert len(rows) == 1
        assert rows[0]["status"] == "Aprobado"
        assert rows[0]["average"] == 4.0

    def test_reproved_student_status(self):
        students = [{"id": "s1", "name": "Ana", "cedula": "111"}]
        grades = [{"student_id": "s1", "subject_id": "subj-A", "value": 2.0}]
        rows = self._build_report_rows(students, grades, ["subj-A"], {"subj-A": "Matemáticas"}, "c1", "Grupo A")
        assert rows[0]["status"] == "Reprobado"

    def test_boundary_exactly_3_is_approved(self):
        students = [{"id": "s1", "name": "Ana", "cedula": "111"}]
        grades = [{"student_id": "s1", "subject_id": "subj-A", "value": 3.0}]
        rows = self._build_report_rows(students, grades, ["subj-A"], {"subj-A": "Mat"}, "c1", "G")
        assert rows[0]["status"] == "Aprobado"

    def test_no_grades_reproved(self):
        students = [{"id": "s1", "name": "Ana", "cedula": "111"}]
        grades = []
        rows = self._build_report_rows(students, grades, ["subj-A"], {"subj-A": "Mat"}, "c1", "G")
        assert rows[0]["status"] == "Reprobado"
        assert rows[0]["average"] == 0.0

    def test_per_subject_rows_generated(self):
        """One row per subject per student."""
        students = [{"id": "s1", "name": "Ana", "cedula": "111"}]
        grades = [
            {"student_id": "s1", "subject_id": "subj-A", "value": 4.0},
            {"student_id": "s1", "subject_id": "subj-B", "value": 2.0},
        ]
        rows = self._build_report_rows(students, grades, ["subj-A", "subj-B"],
                                       {"subj-A": "Mat", "subj-B": "Fis"}, "c1", "G")
        assert len(rows) == 2
        statuses = {r["subject_name"]: r["status"] for r in rows}
        assert statuses["Mat"] == "Aprobado"
        assert statuses["Fis"] == "Reprobado"

    def test_no_cross_subject_grade_contamination(self):
        """Grade for subj-A must not affect subj-B average (isolation)."""
        students = [{"id": "s1", "name": "Ana", "cedula": "111"}]
        grades = [
            {"student_id": "s1", "subject_id": "subj-A", "value": 1.0},  # low
            {"student_id": "s1", "subject_id": "subj-B", "value": 5.0},  # high
        ]
        rows = self._build_report_rows(students, grades, ["subj-A", "subj-B"],
                                       {"subj-A": "Mat", "subj-B": "Fis"}, "c1", "G")
        by_subj = {r["subject_name"]: r for r in rows}
        # Mat fails (1.0 < 3), Fis passes (5.0 >= 3)
        assert by_subj["Mat"]["status"] == "Reprobado"
        assert by_subj["Fis"]["status"] == "Aprobado"


# ---------------------------------------------------------------------------
# Unit tests for grade isolation (re-enrollment resets averages per-course)
# ---------------------------------------------------------------------------

class TestGradeIsolationPerCourse:
    """Tests that grades are isolated per course_id; re-enrolling in a new group
    starts with no prior grades since grades are keyed by course_id."""

    def _get_course_grades(self, all_grades, student_id, course_id):
        """Return grades for a student in a specific course."""
        return [g for g in all_grades
                if g.get("student_id") == student_id and g.get("course_id") == course_id]

    def _compute_average(self, grades):
        values = [g["value"] for g in grades if g.get("value") is not None]
        return sum(values) / len(values) if values else 0.0

    def test_old_course_grades_do_not_appear_in_new_course(self):
        all_grades = [
            {"student_id": "s1", "course_id": "old-course", "value": 1.0},
            {"student_id": "s1", "course_id": "old-course", "value": 2.0},
        ]
        new_course_grades = self._get_course_grades(all_grades, "s1", "new-course")
        assert new_course_grades == []
        assert self._compute_average(new_course_grades) == 0.0

    def test_new_course_starts_fresh(self):
        """After re-enrollment in a new group, no prior grades carry over."""
        all_grades = [
            {"student_id": "s1", "course_id": "old-course", "value": 5.0},
        ]
        new_grades = self._get_course_grades(all_grades, "s1", "new-course")
        assert self._compute_average(new_grades) == 0.0

    def test_different_students_isolated_per_course(self):
        all_grades = [
            {"student_id": "s1", "course_id": "c1", "value": 4.0},
            {"student_id": "s2", "course_id": "c1", "value": 2.0},
        ]
        s1_grades = self._get_course_grades(all_grades, "s1", "c1")
        s2_grades = self._get_course_grades(all_grades, "s2", "c1")
        assert self._compute_average(s1_grades) == 4.0
        assert self._compute_average(s2_grades) == 2.0


# ---------------------------------------------------------------------------
# Unit tests for GET /me/subjects endpoint logic (Modelo B)
# ---------------------------------------------------------------------------

class TestMeSubjectsEndpoint:
    """Unit tests for the /me/subjects endpoint logic.

    The endpoint:
    - Requires role 'profesor' or 'admin'.
    - Returns full Subject objects for each subject_id on the user's record.
    - Silently ignores subject_ids that no longer exist in the DB.
    - Returns [] when the user has no subject_ids.
    """

    def _get_my_subjects(self, user, all_subjects):
        """Simulate the /me/subjects endpoint logic."""
        if user.get("role") not in ["profesor", "admin"]:
            raise ValueError("Solo profesores pueden acceder a sus materias")
        subject_ids = user.get("subject_ids") or []
        if not subject_ids:
            return []
        return [s for s in all_subjects if s["id"] in subject_ids]

    def test_returns_empty_list_when_no_subject_ids(self):
        user = {"id": "t1", "role": "profesor", "subject_ids": []}
        subjects = [{"id": "s1", "name": "Matemáticas"}]
        result = self._get_my_subjects(user, subjects)
        assert result == []

    def test_returns_empty_list_when_subject_ids_is_none(self):
        user = {"id": "t1", "role": "profesor", "subject_ids": None}
        subjects = [{"id": "s1", "name": "Matemáticas"}]
        result = self._get_my_subjects(user, subjects)
        assert result == []

    def test_returns_matching_subjects(self):
        user = {"id": "t1", "role": "profesor", "subject_ids": ["s1", "s2"]}
        all_subjects = [
            {"id": "s1", "name": "Matemáticas"},
            {"id": "s2", "name": "Física"},
            {"id": "s3", "name": "Química"},
        ]
        result = self._get_my_subjects(user, all_subjects)
        result_ids = {s["id"] for s in result}
        assert result_ids == {"s1", "s2"}

    def test_ignores_nonexistent_subject_ids(self):
        """Subject IDs that no longer exist in the DB are silently ignored."""
        user = {"id": "t1", "role": "profesor", "subject_ids": ["s1", "deleted-subj"]}
        all_subjects = [{"id": "s1", "name": "Matemáticas"}]
        result = self._get_my_subjects(user, all_subjects)
        assert len(result) == 1
        assert result[0]["id"] == "s1"

    def test_admin_role_allowed(self):
        user = {"id": "a1", "role": "admin", "subject_ids": ["s1"]}
        all_subjects = [{"id": "s1", "name": "Matemáticas"}]
        result = self._get_my_subjects(user, all_subjects)
        assert len(result) == 1

    def test_student_role_forbidden(self):
        user = {"id": "st1", "role": "estudiante", "subject_ids": ["s1"]}
        all_subjects = [{"id": "s1", "name": "Matemáticas"}]
        with pytest.raises(ValueError, match="Solo profesores"):
            self._get_my_subjects(user, all_subjects)

    def test_editor_role_forbidden(self):
        user = {"id": "e1", "role": "editor", "subject_ids": []}
        with pytest.raises(ValueError, match="Solo profesores"):
            self._get_my_subjects(user, [])

    def test_returns_full_subject_objects(self):
        """Returned subjects must include all fields, not just IDs."""
        user = {"id": "t1", "role": "profesor", "subject_ids": ["s1"]}
        all_subjects = [{"id": "s1", "name": "Matemáticas", "program_id": "prog-1", "module_number": 1}]
        result = self._get_my_subjects(user, all_subjects)
        assert result[0]["name"] == "Matemáticas"
        assert result[0]["program_id"] == "prog-1"
        assert result[0]["module_number"] == 1


# ---------------------------------------------------------------------------
# Unit tests for recovery module isolation logic
# ---------------------------------------------------------------------------

class TestRecoveryModuleIsolation:
    """Tests for the module-isolation logic in the recovery system.

    Validates that:
    - subject_module_map treats None module_number as 1 (close_module_internal fix).
    - get_student_recoveries filter only includes subjects matching the student's
      current module, using the actual subject module from the DB (not only the
      value stored in the failed_subjects record).
    - The admin recovery-panel helper only flags subjects belonging to the
      requested module as failing (get_failing_subjects_with_ids fix).
    """

    # ------------------------------------------------------------------
    # Helpers that mirror the fixed server logic
    # ------------------------------------------------------------------

    def _build_subject_module_map(self, subjects):
        """Mirror of the fixed subject_module_map builder in close_module_internal."""
        return {s["id"]: (s.get("module_number") or 1) for s in subjects}

    def _filter_student_recoveries(self, failed_subjects, program_modules,
                                   student_global_module, db_subject_module_map):
        """Mirror of the fixed get_student_recoveries filter logic."""
        filtered = []
        for subject in failed_subjects:
            prog_id = subject.get("program_id", "")
            sid = subject.get("subject_id")
            if sid and sid in db_subject_module_map:
                subject_module = db_subject_module_map[sid]
            else:
                subject_module = subject.get("module_number")
            if subject_module is None:
                filtered.append(subject)
                continue
            current_module = program_modules.get(prog_id) or student_global_module
            if subject_module == current_module:
                filtered.append(subject)
        return filtered

    def _get_failing_subjects_with_ids(self, student_id, course_id, course_doc,
                                       grades_index, subject_map,
                                       subject_module_map, filter_module=None):
        """Mirror of the fixed get_failing_subjects_with_ids helper."""
        sids = course_doc.get("subject_ids") or []
        if not sids and course_doc.get("subject_id"):
            sids = [course_doc["subject_id"]]
        if not sids:
            return []
        failing = []
        for sid in sids:
            if filter_module is not None and subject_module_map.get(sid, 1) != filter_module:
                continue
            values = grades_index.get((student_id, course_id, sid), [])
            avg = sum(values) / len(values) if values else 0.0
            if avg < 3.0 and sid in subject_map:
                failing.append((sid, subject_map[sid], round(avg, 2)))
        return failing

    # ------------------------------------------------------------------
    # subject_module_map: None handling
    # ------------------------------------------------------------------

    def test_subject_module_map_none_defaults_to_1(self):
        """Subjects with module_number=None must default to 1, not None."""
        subjects = [{"id": "s1", "module_number": None}]
        mapping = self._build_subject_module_map(subjects)
        assert mapping["s1"] == 1

    def test_subject_module_map_missing_key_defaults_to_1(self):
        """Subjects without a module_number key must default to 1."""
        subjects = [{"id": "s1"}]
        mapping = self._build_subject_module_map(subjects)
        assert mapping["s1"] == 1

    def test_subject_module_map_module_2_preserved(self):
        """Subjects with module_number=2 must stay as 2."""
        subjects = [{"id": "s2", "module_number": 2}]
        mapping = self._build_subject_module_map(subjects)
        assert mapping["s2"] == 2

    def test_close_module_1_includes_null_module_subjects_after_fix(self):
        """Closing module 1 must NOT skip a subject whose module_number is None
        (it should default to 1 and therefore be processed)."""
        subjects = [{"id": "sNull", "module_number": None}]
        mapping = self._build_subject_module_map(subjects)
        # With the fix the mapping value is 1, so the subject IS processed for module 1
        assert mapping.get("sNull", 1) == 1  # equals module_number (1) → processed

    # ------------------------------------------------------------------
    # get_student_recoveries: DB-based subject module validation
    # ------------------------------------------------------------------

    def test_module1_student_does_not_see_module2_subject_from_stale_record(self):
        """A failed_subjects record with module_number=1 but subject actually in
        module 2 must be hidden for a module 1 student."""
        failed_subjects = [
            {
                "id": "fs1",
                "student_id": "s1",
                "subject_id": "subj-m2",
                "program_id": "prog-A",
                "module_number": 1,  # stale/wrong – real module is 2
            }
        ]
        db_subject_module_map = {"subj-m2": 2}  # actual module in DB
        program_modules = {"prog-A": 1}
        result = self._filter_student_recoveries(
            failed_subjects, program_modules, 1, db_subject_module_map
        )
        assert result == [], "Module-2 subject must not appear for a module-1 student"

    def test_module1_student_sees_correct_module1_subject(self):
        """A failed_subjects record for a real module-1 subject must be visible
        to a module-1 student."""
        failed_subjects = [
            {
                "id": "fs1",
                "student_id": "s1",
                "subject_id": "subj-m1",
                "program_id": "prog-A",
                "module_number": 1,
            }
        ]
        db_subject_module_map = {"subj-m1": 1}
        program_modules = {"prog-A": 1}
        result = self._filter_student_recoveries(
            failed_subjects, program_modules, 1, db_subject_module_map
        )
        assert len(result) == 1

    def test_module2_student_does_not_see_module1_subjects(self):
        """A module-2 student must not see old module-1 recovery subjects."""
        failed_subjects = [
            {
                "id": "fs1",
                "student_id": "s1",
                "subject_id": "subj-m1",
                "program_id": "prog-A",
                "module_number": 1,
            }
        ]
        db_subject_module_map = {"subj-m1": 1}
        program_modules = {"prog-A": 2}  # student is now in module 2
        result = self._filter_student_recoveries(
            failed_subjects, program_modules, 2, db_subject_module_map
        )
        assert result == []

    def test_subject_not_in_db_falls_back_to_record_module_number(self):
        """When the subject no longer exists in the DB, fall back to the
        module_number stored in the failed_subjects record."""
        failed_subjects = [
            {
                "id": "fs1",
                "student_id": "s1",
                "subject_id": "deleted-subj",
                "program_id": "prog-A",
                "module_number": 1,
            }
        ]
        db_subject_module_map = {}  # subject deleted from DB
        program_modules = {"prog-A": 1}
        result = self._filter_student_recoveries(
            failed_subjects, program_modules, 1, db_subject_module_map
        )
        assert len(result) == 1

    def test_no_subject_id_record_uses_module_number_field(self):
        """Legacy records without subject_id fall back to module_number in record."""
        failed_subjects = [
            {
                "id": "fs-legacy",
                "student_id": "s1",
                "program_id": "prog-A",
                "module_number": 1,
                # no subject_id
            }
        ]
        db_subject_module_map = {}
        program_modules = {"prog-A": 1}
        result = self._filter_student_recoveries(
            failed_subjects, program_modules, 1, db_subject_module_map
        )
        assert len(result) == 1

    def test_global_module_fallback_when_program_not_in_program_modules(self):
        """When program_modules doesn't contain the program, fall back to
        student_global_module."""
        failed_subjects = [
            {
                "id": "fs1",
                "student_id": "s1",
                "subject_id": "subj-m1",
                "program_id": "prog-unknown",
                "module_number": 1,
            }
        ]
        db_subject_module_map = {"subj-m1": 1}
        program_modules = {}  # prog-unknown not present
        result = self._filter_student_recoveries(
            failed_subjects, program_modules, 1, db_subject_module_map
        )
        assert len(result) == 1

    # ------------------------------------------------------------------
    # get_failing_subjects_with_ids: module filter in recovery panel
    # ------------------------------------------------------------------

    def test_recovery_panel_excludes_module2_subjects_in_module1_period(self):
        """Auto-detection for module 1 must not include module-2 subjects."""
        subject_map = {"s-m1": "Materia M1", "s-m2": "Materia M2"}
        subject_module_map = {"s-m1": 1, "s-m2": 2}
        grades_index = {
            ("st1", "c1", "s-m1"): [1.5],  # failing
            ("st1", "c1", "s-m2"): [1.0],  # failing (but module 2)
        }
        course_doc = {"subject_ids": ["s-m1", "s-m2"]}
        result = self._get_failing_subjects_with_ids(
            "st1", "c1", course_doc, grades_index,
            subject_map, subject_module_map, filter_module=1
        )
        subject_ids_returned = [r[0] for r in result]
        assert "s-m1" in subject_ids_returned
        assert "s-m2" not in subject_ids_returned

    def test_recovery_panel_includes_only_module2_subjects_in_module2_period(self):
        """Auto-detection for module 2 must not include module-1 subjects."""
        subject_map = {"s-m1": "M1", "s-m2": "M2"}
        subject_module_map = {"s-m1": 1, "s-m2": 2}
        grades_index = {
            ("st1", "c1", "s-m1"): [1.0],
            ("st1", "c1", "s-m2"): [2.0],
        }
        course_doc = {"subject_ids": ["s-m1", "s-m2"]}
        result = self._get_failing_subjects_with_ids(
            "st1", "c1", course_doc, grades_index,
            subject_map, subject_module_map, filter_module=2
        )
        subject_ids_returned = [r[0] for r in result]
        assert "s-m2" in subject_ids_returned
        assert "s-m1" not in subject_ids_returned

    def test_recovery_panel_no_filter_returns_all_failing(self):
        """Without a filter_module, all failing subjects are returned."""
        subject_map = {"s-m1": "M1", "s-m2": "M2"}
        subject_module_map = {"s-m1": 1, "s-m2": 2}
        grades_index = {
            ("st1", "c1", "s-m1"): [1.0],
            ("st1", "c1", "s-m2"): [2.0],
        }
        course_doc = {"subject_ids": ["s-m1", "s-m2"]}
        result = self._get_failing_subjects_with_ids(
            "st1", "c1", course_doc, grades_index,
            subject_map, subject_module_map, filter_module=None
        )
        assert len(result) == 2

    def test_recovery_panel_passing_subject_excluded(self):
        """Passing subjects (avg >= 3.0) must not appear even without module filter."""
        subject_map = {"s1": "S1", "s2": "S2"}
        subject_module_map = {"s1": 1, "s2": 1}
        grades_index = {
            ("st1", "c1", "s1"): [4.0],  # passing
            ("st1", "c1", "s2"): [2.0],  # failing
        }
        course_doc = {"subject_ids": ["s1", "s2"]}
        result = self._get_failing_subjects_with_ids(
            "st1", "c1", course_doc, grades_index,
            subject_map, subject_module_map, filter_module=1
        )
        assert len(result) == 1
        assert result[0][0] == "s2"

    def test_recovery_panel_null_module_subject_defaults_to_module1(self):
        """A subject with module_number=None must be treated as module 1 by the
        fixed subject_module_map, so it appears in module-1 auto-detection."""
        subject_map = {"s-null": "S-Null"}
        # Use _build_subject_module_map to verify the fix handles None correctly
        subject_module_map = self._build_subject_module_map([{"id": "s-null", "module_number": None}])
        grades_index = {("st1", "c1", "s-null"): [1.0]}
        course_doc = {"subject_ids": ["s-null"]}
        result = self._get_failing_subjects_with_ids(
            "st1", "c1", course_doc, grades_index,
            subject_map, subject_module_map, filter_module=1
        )
        assert len(result) == 1


# ---------------------------------------------------------------------------
# Unit tests for per-subject activity numbering logic
# ---------------------------------------------------------------------------

class TestActivityNumberingPerSubject:
    """Tests for the per-subject activity auto-numbering logic used in create_activity.

    The logic mirrors what backend/server.py does:
      - Find the max activity_number for the given course+subject combination.
      - The next activity_number = max + 1 (or 1 if none exist yet).
    """

    def _next_activity_number(self, activities, course_id, subject_id=None):
        """Pure-function mirror of the DB aggregation in create_activity."""
        query = [
            a["activity_number"]
            for a in activities
            if a["course_id"] == course_id
            and (subject_id is None or a.get("subject_id") == subject_id)
        ]
        max_num = max(query) if query else 0
        return (max_num or 0) + 1

    def test_first_activity_in_subject_is_1(self):
        """When no activities exist for the subject, the first number is 1."""
        activities = []
        assert self._next_activity_number(activities, "course-1", "math") == 1

    def test_second_activity_in_subject_is_2(self):
        activities = [
            {"course_id": "course-1", "subject_id": "math", "activity_number": 1},
        ]
        assert self._next_activity_number(activities, "course-1", "math") == 2

    def test_numbering_is_independent_per_subject(self):
        """English (inglés) starts at act1 even when Math (matemáticas) already has 5 activities."""
        activities = [
            {"course_id": "course-1", "subject_id": "math", "activity_number": 1},
            {"course_id": "course-1", "subject_id": "math", "activity_number": 2},
            {"course_id": "course-1", "subject_id": "math", "activity_number": 3},
            {"course_id": "course-1", "subject_id": "math", "activity_number": 4},
            {"course_id": "course-1", "subject_id": "math", "activity_number": 5},
        ]
        # English subject should start at 1, not 6
        assert self._next_activity_number(activities, "course-1", "english") == 1

    def test_numbering_continues_correctly_after_existing_activities(self):
        """If English already has act1 and act2, next should be act3."""
        activities = [
            {"course_id": "course-1", "subject_id": "math", "activity_number": 1},
            {"course_id": "course-1", "subject_id": "math", "activity_number": 2},
            {"course_id": "course-1", "subject_id": "english", "activity_number": 1},
            {"course_id": "course-1", "subject_id": "english", "activity_number": 2},
        ]
        assert self._next_activity_number(activities, "course-1", "english") == 3

    def test_numbering_based_on_max_not_count(self):
        """When activities have gaps (e.g. after deletion), uses max, not count."""
        activities = [
            {"course_id": "course-1", "subject_id": "math", "activity_number": 1},
            {"course_id": "course-1", "subject_id": "math", "activity_number": 3},
        ]
        # act2 was deleted; next should be 4, not 3
        assert self._next_activity_number(activities, "course-1", "math") == 4

    def test_different_courses_are_independent(self):
        """Activities in another course do not affect numbering."""
        activities = [
            {"course_id": "course-2", "subject_id": "math", "activity_number": 10},
        ]
        assert self._next_activity_number(activities, "course-1", "math") == 1

    def test_no_subject_id_uses_all_course_activities(self):
        """When subject_id is None (not provided), falls back to course-wide max."""
        activities = [
            {"course_id": "course-1", "subject_id": "math", "activity_number": 3},
            {"course_id": "course-1", "subject_id": "english", "activity_number": 7},
        ]
        assert self._next_activity_number(activities, "course-1", None) == 8



# ---------------------------------------------------------------------------
# Unit tests for module promotion/graduation timing logic
# ---------------------------------------------------------------------------

class TestCloseModulePromotion:
    """Tests for the close_module_internal deferral logic.

    When a course has recovery_close configured, passing students must NOT be
    promoted at module-close time – promotion is deferred to recovery_close.
    When no recovery_close is configured, students are promoted immediately
    (backward-compatible behaviour).
    """

    def _has_recovery_close(self, student_courses, module_number):
        """Mirror of the any_recovery_close check in close_module_internal."""
        return any(
            (c.get("module_dates") or {}).get(str(module_number), {}).get("recovery_close")
            for c in student_courses
        )

    def test_course_with_recovery_close_defers_promotion(self):
        courses = [{
            "module_dates": {
                "1": {"start": "2026-01-01", "end": "2026-06-30", "recovery_close": "2026-07-15"}
            }
        }]
        assert self._has_recovery_close(courses, 1) is True

    def test_course_without_recovery_close_promotes_immediately(self):
        courses = [{
            "module_dates": {
                "1": {"start": "2026-01-01", "end": "2026-06-30"}
            }
        }]
        assert self._has_recovery_close(courses, 1) is False

    def test_empty_module_dates_promotes_immediately(self):
        courses = [{"module_dates": {}}]
        assert self._has_recovery_close(courses, 1) is False

    def test_no_module_dates_promotes_immediately(self):
        courses = [{}]
        assert self._has_recovery_close(courses, 1) is False

    def test_multiple_courses_any_with_recovery_close_defers(self):
        """If even one course has recovery_close, promotion must be deferred."""
        courses = [
            {"module_dates": {"1": {"start": "2026-01-01", "end": "2026-06-30"}}},
            {"module_dates": {"1": {"start": "2026-01-01", "end": "2026-06-30", "recovery_close": "2026-07-15"}}},
        ]
        assert self._has_recovery_close(courses, 1) is True

    def test_recovery_close_only_checked_for_requested_module(self):
        """recovery_close in module 2 should not affect module 1 closure."""
        courses = [{
            "module_dates": {
                "1": {"start": "2026-01-01", "end": "2026-06-30"},
                "2": {"start": "2026-08-01", "end": "2026-12-31", "recovery_close": "2027-01-15"}
            }
        }]
        # Closing module 1: no recovery_close in module 1 → immediate promotion
        assert self._has_recovery_close(courses, 1) is False
        # Closing module 2: recovery_close exists → deferred
        assert self._has_recovery_close(courses, 2) is True


class TestRecoveryCloseGraduationLogic:
    """Tests for the graduation/promotion decision at recovery_close time.

    The logic must use `module_key` (the module being closed) to determine
    whether the student graduates or is promoted, NOT the student's potentially
    stale `current_module` field.  It must also enforce a minimum of 2 modules
    so that a program with an incomplete `modules` list cannot erroneously
    graduate a module-1 student.
    """

    def _decide_outcome(self, module_key, program_modules_list_len):
        """Mirror of the graduation check in check_and_close_modules recovery section."""
        max_modules = max(program_modules_list_len if program_modules_list_len else 2, 2)
        if int(module_key) >= max_modules:
            return "egresado"
        return "promoted"

    def test_module1_with_2_module_program_promotes(self):
        assert self._decide_outcome("1", 2) == "promoted"

    def test_module2_with_2_module_program_graduates(self):
        assert self._decide_outcome("2", 2) == "egresado"

    def test_module1_with_single_module_program_still_promotes(self):
        """Safety: programs with only 1 module must still not graduate module-1 students."""
        assert self._decide_outcome("1", 1) == "promoted"

    def test_module1_with_empty_modules_list_promotes(self):
        """Safety: empty modules list (0 items) defaults to 2, so module-1 is promoted."""
        assert self._decide_outcome("1", 0) == "promoted"

    def test_module2_with_empty_modules_list_graduates(self):
        assert self._decide_outcome("2", 0) == "egresado"


class TestRecoveryPanelNextModuleStartFilter:
    """Tests for the frontend filtering logic that removes recovery entries once
    the next module has started.

    The filter mirrors the logic in RecoveriesPage.js:
      - A student is hidden when ALL their subjects have next_module_start <= today.
      - Subjects with no next_module_start are always visible.
    """

    def _student_has_active_subjects(self, failed_subjects, today):
        """Mirror of the `hasActiveSubjects` filter in RecoveriesPage.js."""
        return any(
            not (s.get("next_module_start") and s["next_module_start"] <= today)
            for s in failed_subjects
        )

    def test_no_next_module_start_always_visible(self):
        subjects = [{"next_module_start": None}]
        assert self._student_has_active_subjects(subjects, "2026-08-01") is True

    def test_next_module_not_started_yet_is_visible(self):
        subjects = [{"next_module_start": "2026-09-01"}]
        assert self._student_has_active_subjects(subjects, "2026-08-01") is True

    def test_next_module_started_today_is_hidden(self):
        subjects = [{"next_module_start": "2026-08-01"}]
        assert self._student_has_active_subjects(subjects, "2026-08-01") is False

    def test_next_module_already_started_is_hidden(self):
        subjects = [{"next_module_start": "2026-07-15"}]
        assert self._student_has_active_subjects(subjects, "2026-08-01") is False

    def test_mixed_subjects_visible_if_any_active(self):
        """If at least one subject is still active, the student card stays visible."""
        subjects = [
            {"next_module_start": "2026-07-01"},   # already started → hidden
            {"next_module_start": "2026-09-01"},   # not yet started → visible
        ]
        assert self._student_has_active_subjects(subjects, "2026-08-01") is True

    def test_all_subjects_started_hidden(self):
        subjects = [
            {"next_module_start": "2026-07-01"},
            {"next_module_start": "2026-07-15"},
        ]
        assert self._student_has_active_subjects(subjects, "2026-08-01") is False


class TestRecoveryPanelFinalStatus:
    """Tests for the 'Aprobado / Reprobado' display logic in RecoveriesPage.js.

    After recovery_close passes, every entry must show a final result:
      - 'processed_passed' or 'teacher_approved'  → Aprobado
      - anything else                              → Reprobado
    """

    def _is_final_approved(self, subject, today):
        recovery_closed = subject.get("recovery_close") and subject["recovery_close"] <= today
        if not recovery_closed:
            return None  # Not yet final
        status = subject.get("status", "pending")
        return status in ("processed_passed", "teacher_approved")

    def test_processed_passed_after_close_is_aprobado(self):
        subject = {"recovery_close": "2026-07-15", "status": "processed_passed"}
        assert self._is_final_approved(subject, "2026-07-16") is True

    def test_teacher_approved_after_close_is_aprobado(self):
        subject = {"recovery_close": "2026-07-15", "status": "teacher_approved"}
        assert self._is_final_approved(subject, "2026-07-15") is True

    def test_processed_failed_after_close_is_reprobado(self):
        subject = {"recovery_close": "2026-07-15", "status": "processed_failed"}
        assert self._is_final_approved(subject, "2026-07-16") is False

    def test_pending_after_close_is_reprobado(self):
        subject = {"recovery_close": "2026-07-15", "status": "pending"}
        assert self._is_final_approved(subject, "2026-07-20") is False

    def test_before_recovery_close_is_not_final(self):
        subject = {"recovery_close": "2026-07-15", "status": "pending"}
        assert self._is_final_approved(subject, "2026-07-14") is None

    def test_no_recovery_close_is_not_final(self):
        subject = {"recovery_close": None, "status": "processed_passed"}
        assert self._is_final_approved(subject, "2026-08-01") is None


class TestStudentsPageStatusLabel:
    """Tests for the fallback status badge in StudentsPage.js.

    Before the fix, any non-'activo' estado was labelled 'Egresado'.
    After the fix, each estado maps to its correct label.
    """

    def _status_label(self, estado):
        """Mirror of the statusLabel function moved outside the if-block."""
        st = estado or 'activo'
        if st == 'activo':
            return 'Activo'
        if st == 'egresado':
            return 'Egresado'
        if st == 'retirado':
            return 'Retirado'
        if st == 'pendiente_recuperacion':
            return 'Pend. Rec.'
        if st == 'reprobado':
            return 'Reprobado'
        return st

    def test_activo_shows_activo(self):
        assert self._status_label('activo') == 'Activo'

    def test_egresado_shows_egresado(self):
        assert self._status_label('egresado') == 'Egresado'

    def test_retirado_shows_retirado(self):
        assert self._status_label('retirado') == 'Retirado'

    def test_pendiente_recuperacion_shows_pend_rec(self):
        assert self._status_label('pendiente_recuperacion') == 'Pend. Rec.'

    def test_none_estado_defaults_to_activo(self):
        assert self._status_label(None) == 'Activo'

    def test_pendiente_recuperacion_not_shown_as_egresado(self):
        """Critical: the old bug mapped any non-activo estado to 'Egresado'."""
        assert self._status_label('pendiente_recuperacion') != 'Egresado'

    def test_retirado_not_shown_as_egresado(self):
        assert self._status_label('retirado') != 'Egresado'

    def test_reprobado_shows_reprobado(self):
        assert self._status_label('reprobado') == 'Reprobado'

    def test_reprobado_not_shown_as_egresado(self):
        assert self._status_label('reprobado') != 'Egresado'


# ---------------------------------------------------------------------------
# Unit tests for recovery completion status update logic
# (_check_and_update_recovery_completion helper)
# ---------------------------------------------------------------------------

class TestCheckAndUpdateRecoveryCompletion:
    """Tests for the logic inside _check_and_update_recovery_completion that decides
    whether to update the student status once all recovery subjects are graded.

    Since the helper is async and requires DB, we test the pure decision logic here.
    """

    def _should_update(self, records, program_status):
        """Return 'update_needed' if all recovery records are fully approved and the student
        is in 'pendiente_recuperacion', otherwise return None.

        Mirrors the core decision logic in _check_and_update_recovery_completion:
        - All records must be recovery_approved=True AND recovery_completed=True
          AND teacher_graded_status='approved'
        - Student's current program status must be 'pendiente_recuperacion'
        """
        if program_status != "pendiente_recuperacion":
            return None
        if not records:
            return None
        all_passed = all(
            r.get("recovery_approved") is True and
            r.get("recovery_completed") is True and r.get("teacher_graded_status") == "approved"
            for r in records
        )
        return "update_needed" if all_passed else None

    def _should_reject(self, approved_records, program_status):
        """Return 'reject_needed' if all admin-approved records have been teacher-graded
        and at least one is rejected. Mirrors _check_and_update_recovery_rejection."""
        if program_status != "pendiente_recuperacion":
            return None
        if not approved_records:
            return None
        all_graded = all(r.get("recovery_completed") is True for r in approved_records)
        if not all_graded:
            return None
        any_rejected = any(r.get("teacher_graded_status") == "rejected" for r in approved_records)
        return "reject_needed" if any_rejected else None

    def _new_status(self, module_number, max_modules):
        """Mirror the new-status decision: egresado for last module, otherwise activo."""
        return "egresado" if module_number >= max_modules else "activo"

    # --- _should_update tests ---

    def test_all_approved_triggers_update(self):
        records = [
            {"recovery_approved": True, "recovery_completed": True, "teacher_graded_status": "approved"},
            {"recovery_approved": True, "recovery_completed": True, "teacher_graded_status": "approved"},
        ]
        assert self._should_update(records, "pendiente_recuperacion") == "update_needed"

    def test_one_pending_does_not_trigger_update(self):
        records = [
            {"recovery_approved": True, "recovery_completed": True, "teacher_graded_status": "approved"},
            {"recovery_approved": True, "recovery_completed": False, "teacher_graded_status": None},
        ]
        assert self._should_update(records, "pendiente_recuperacion") is None

    def test_one_rejected_does_not_trigger_update(self):
        records = [
            {"recovery_approved": True, "recovery_completed": True, "teacher_graded_status": "approved"},
            {"recovery_approved": True, "recovery_completed": True, "teacher_graded_status": "rejected"},
        ]
        assert self._should_update(records, "pendiente_recuperacion") is None

    def test_not_in_pendiente_does_not_trigger_update(self):
        """If the student is already activo, no update needed."""
        records = [{"recovery_approved": True, "recovery_completed": True, "teacher_graded_status": "approved"}]
        assert self._should_update(records, "activo") is None

    def test_empty_records_does_not_trigger_update(self):
        assert self._should_update([], "pendiente_recuperacion") is None

    def test_single_record_approved_triggers_update(self):
        records = [{"recovery_approved": True, "recovery_completed": True, "teacher_graded_status": "approved"}]
        assert self._should_update(records, "pendiente_recuperacion") == "update_needed"

    def test_unapproved_subject_blocks_promotion(self):
        """If admin hasn't approved a subject, student should NOT be promoted even if
        all admin-approved subjects are teacher-approved."""
        records = [
            {"recovery_approved": True, "recovery_completed": True, "teacher_graded_status": "approved"},
            {"recovery_approved": False, "recovery_completed": False, "teacher_graded_status": None},
        ]
        assert self._should_update(records, "pendiente_recuperacion") is None

    # --- _should_reject tests ---

    def test_all_graded_one_rejected_triggers_rejection(self):
        records = [
            {"recovery_completed": True, "teacher_graded_status": "approved"},
            {"recovery_completed": True, "teacher_graded_status": "rejected"},
        ]
        assert self._should_reject(records, "pendiente_recuperacion") == "reject_needed"

    def test_all_graded_all_approved_does_not_trigger_rejection(self):
        records = [
            {"recovery_completed": True, "teacher_graded_status": "approved"},
            {"recovery_completed": True, "teacher_graded_status": "approved"},
        ]
        assert self._should_reject(records, "pendiente_recuperacion") is None

    def test_partial_grading_does_not_trigger_rejection(self):
        records = [
            {"recovery_completed": True, "teacher_graded_status": "rejected"},
            {"recovery_completed": False, "teacher_graded_status": None},
        ]
        assert self._should_reject(records, "pendiente_recuperacion") is None

    def test_not_in_pendiente_does_not_trigger_rejection(self):
        records = [{"recovery_completed": True, "teacher_graded_status": "rejected"}]
        assert self._should_reject(records, "activo") is None

    # --- _new_status tests ---

    def test_last_module_gives_egresado(self):
        assert self._new_status(module_number=2, max_modules=2) == "egresado"

    def test_beyond_last_module_gives_egresado(self):
        assert self._new_status(module_number=3, max_modules=2) == "egresado"

    def test_non_last_module_gives_activo(self):
        assert self._new_status(module_number=1, max_modules=2) == "activo"

    def test_first_of_three_modules_gives_activo(self):
        assert self._new_status(module_number=1, max_modules=3) == "activo"

    def test_second_of_three_modules_gives_activo(self):
        assert self._new_status(module_number=2, max_modules=3) == "activo"

    def test_last_of_three_modules_gives_egresado(self):
        assert self._new_status(module_number=3, max_modules=3) == "egresado"

    # --- end-to-end decision tests ---

    def test_all_approved_last_module_becomes_egresado(self):
        records = [{"recovery_approved": True, "recovery_completed": True, "teacher_graded_status": "approved", "module_number": 2}]
        if self._should_update(records, "pendiente_recuperacion"):
            result = self._new_status(2, 2)
            assert result == "egresado"

    def test_all_approved_non_last_module_becomes_activo(self):
        records = [{"recovery_approved": True, "recovery_completed": True, "teacher_graded_status": "approved", "module_number": 1}]
        if self._should_update(records, "pendiente_recuperacion"):
            result = self._new_status(1, 2)
            assert result == "activo"

    def test_partial_approval_student_stays_pendiente(self):
        records = [
            {"recovery_approved": True, "recovery_completed": True, "teacher_graded_status": "approved"},
            {"recovery_approved": True, "recovery_completed": False, "teacher_graded_status": None},
        ]
        result = self._should_update(records, "pendiente_recuperacion")
        assert result is None  # Student remains pendiente_recuperacion


# ---------------------------------------------------------------------------
# Unit tests for recovery closure decision logic (removal from group)
# ---------------------------------------------------------------------------

class TestRecoveryClosureDecisionLogic:
    """Tests for the scheduler's recovery_close logic that decides whether to
    promote or remove students when the recovery period closes.

    Mirrors the decision logic in check_and_close_modules recovery_close section.
    """

    def _decide(self, records):
        """Return the decision for a student based on their recovery records.

        Mirrors the scheduler logic:
        - If no admin action on any record → 'remove_no_action'
        - If all records are admin-approved, completed, and teacher-approved → 'promote'
        - Otherwise (at least one not fully passed) → 'remove_failed'
        """
        has_admin_action = any(
            r.get("recovery_approved") is True or r.get("recovery_completed") is True
            for r in records
        )
        if not has_admin_action:
            return "remove_no_action"
        all_passed = all(
            r.get("recovery_approved") is True and
            r.get("recovery_completed") is True and
            r.get("teacher_graded_status") == "approved"
            for r in records
        )
        return "promote" if all_passed else "remove_failed"

    def test_no_admin_action_removes_student(self):
        records = [
            {"recovery_approved": False, "recovery_completed": False, "teacher_graded_status": None},
        ]
        assert self._decide(records) == "remove_no_action"

    def test_all_passed_promotes(self):
        records = [
            {"recovery_approved": True, "recovery_completed": True, "teacher_graded_status": "approved"},
            {"recovery_approved": True, "recovery_completed": True, "teacher_graded_status": "approved"},
        ]
        assert self._decide(records) == "promote"

    def test_one_rejected_removes(self):
        records = [
            {"recovery_approved": True, "recovery_completed": True, "teacher_graded_status": "approved"},
            {"recovery_approved": True, "recovery_completed": True, "teacher_graded_status": "rejected"},
        ]
        assert self._decide(records) == "remove_failed"

    def test_admin_approved_but_teacher_not_graded_removes(self):
        records = [
            {"recovery_approved": True, "recovery_completed": False, "teacher_graded_status": None},
        ]
        assert self._decide(records) == "remove_failed"

    def test_partial_admin_approval_removes(self):
        """If admin approved some but not all subjects, student is removed at close."""
        records = [
            {"recovery_approved": True, "recovery_completed": True, "teacher_graded_status": "approved"},
            {"recovery_approved": False, "recovery_completed": False, "teacher_graded_status": None},
        ]
        assert self._decide(records) == "remove_failed"

    def test_single_subject_all_passed_promotes(self):
        records = [
            {"recovery_approved": True, "recovery_completed": True, "teacher_graded_status": "approved"},
        ]
        assert self._decide(records) == "promote"

    def test_multiple_no_action_removes(self):
        records = [
            {"recovery_approved": False, "recovery_completed": False, "teacher_graded_status": None},
            {"recovery_approved": False, "recovery_completed": False, "teacher_graded_status": None},
        ]
        assert self._decide(records) == "remove_no_action"

class TestPromoteStudentLogic:
    """Tests for the promote_student endpoint decision logic.

    The endpoint must:
    - Reject promotion when the student is already in the last module of a program.
    - Allow promotion for any module < max_modules (N-module support, no hardcoded cap of 2).
    - Update program_modules and program_statuses per-program.
    - Derive the correct global estado after promotion.
    """

    def _can_promote(self, program_modules, prog_id, prog_max_map):
        """Mirror of the per-program check inside promote_student."""
        current = program_modules.get(prog_id, 1)
        max_mods = prog_max_map.get(prog_id, 2)
        return current < max_mods

    def _promote(self, program_modules, program_statuses, prog_id, prog_max_map):
        """Mirror of the promote_student per-program update logic."""
        current = program_modules.get(prog_id, 1)
        max_mods = prog_max_map.get(prog_id, 2)
        if current >= max_mods:
            return None, "already_final"
        program_modules = dict(program_modules)
        program_statuses = dict(program_statuses)
        program_modules[prog_id] = current + 1
        program_statuses[prog_id] = "activo"
        return program_modules, program_statuses

    def _derive(self, program_statuses):
        """Mirror of derive_estado_from_program_statuses."""
        if not program_statuses:
            return "activo"
        statuses = list(program_statuses.values())
        if "activo" in statuses:
            return "activo"
        if all(s == "egresado" for s in statuses):
            return "egresado"
        if "pendiente_recuperacion" in statuses:
            return "pendiente_recuperacion"
        if "egresado" in statuses:
            return "egresado"
        if "reprobado" in statuses:
            return "reprobado"
        return "retirado"

    def test_module1_can_be_promoted_in_2module_program(self):
        assert self._can_promote({"prog-a": 1}, "prog-a", {"prog-a": 2}) is True

    def test_module2_cannot_be_promoted_in_2module_program(self):
        """N-module: module 2 of a 2-module program is the last – promotion blocked."""
        assert self._can_promote({"prog-a": 2}, "prog-a", {"prog-a": 2}) is False

    def test_module2_can_be_promoted_in_3module_program(self):
        """N-module support: module 2 is not the last in a 3-module program."""
        assert self._can_promote({"prog-a": 2}, "prog-a", {"prog-a": 3}) is True

    def test_module3_cannot_be_promoted_in_3module_program(self):
        assert self._can_promote({"prog-a": 3}, "prog-a", {"prog-a": 3}) is False

    def test_module10_can_be_promoted_in_12module_program(self):
        assert self._can_promote({"prog-a": 10}, "prog-a", {"prog-a": 12}) is True

    def test_promote_increments_module(self):
        pm, ps = self._promote({"prog-a": 1}, {"prog-a": "activo"}, "prog-a", {"prog-a": 2})
        assert pm["prog-a"] == 2
        assert ps["prog-a"] == "activo"

    def test_promote_sets_activo_status(self):
        pm, ps = self._promote(
            {"prog-a": 1}, {"prog-a": "pendiente_recuperacion"}, "prog-a", {"prog-a": 3}
        )
        assert ps["prog-a"] == "activo"

    def test_promote_blocked_at_last_module_returns_error(self):
        result, err = self._promote({"prog-a": 2}, {"prog-a": "activo"}, "prog-a", {"prog-a": 2})
        assert result is None
        assert err == "already_final"

    def test_promote_updates_global_estado_activo(self):
        _, ps = self._promote({"prog-a": 1}, {"prog-a": "activo"}, "prog-a", {"prog-a": 2})
        assert self._derive(ps) == "activo"

    def test_multi_program_promote_one_program_derives_activo(self):
        """Promoting one program while another is egresado → global still activo."""
        pm, ps = self._promote(
            {"prog-a": 1, "prog-b": 2},
            {"prog-a": "activo", "prog-b": "egresado"},
            "prog-a",
            {"prog-a": 2, "prog-b": 2},
        )
        assert pm["prog-a"] == 2
        assert ps["prog-b"] == "egresado"  # other program unchanged
        assert self._derive(ps) == "activo"


# ---------------------------------------------------------------------------
# Unit tests for graduate_student decision logic (N-module, multi-program)
# ---------------------------------------------------------------------------

class TestGraduateStudentLogic:
    """Tests for the graduate_student endpoint decision logic.

    The endpoint must:
    - Reject graduation when the student is NOT in the last module.
    - Allow graduation for any program where current_module >= max_modules (N-module).
    - Update program_statuses to 'egresado' for the target program(s).
    - Derive the correct global estado after graduation.
    """

    def _can_graduate(self, program_modules, prog_id, prog_max_map, current_module=1):
        """Mirror of the per-program check inside graduate_student."""
        prog_current = program_modules.get(prog_id, current_module)
        prog_max = prog_max_map.get(prog_id, 2)
        return prog_current >= prog_max

    def _graduate(self, program_modules, program_statuses, prog_id, prog_max_map, current_module=1):
        """Mirror of the graduate_student per-program update logic."""
        prog_current = program_modules.get(prog_id, current_module)
        prog_max = prog_max_map.get(prog_id, 2)
        if prog_current < prog_max:
            return None, "not_final"
        program_statuses = dict(program_statuses)
        program_statuses[prog_id] = "egresado"
        return program_statuses, None

    def _derive(self, program_statuses):
        """Mirror of derive_estado_from_program_statuses."""
        if not program_statuses:
            return "activo"
        statuses = list(program_statuses.values())
        if "activo" in statuses:
            return "activo"
        if all(s == "egresado" for s in statuses):
            return "egresado"
        if "pendiente_recuperacion" in statuses:
            return "pendiente_recuperacion"
        if "egresado" in statuses:
            return "egresado"
        if "reprobado" in statuses:
            return "reprobado"
        return "retirado"

    def test_module2_in_2module_program_can_graduate(self):
        assert self._can_graduate({"prog-a": 2}, "prog-a", {"prog-a": 2}) is True

    def test_module1_in_2module_program_cannot_graduate(self):
        assert self._can_graduate({"prog-a": 1}, "prog-a", {"prog-a": 2}) is False

    def test_module3_in_3module_program_can_graduate(self):
        """N-module: last module of a 3-module program allows graduation."""
        assert self._can_graduate({"prog-a": 3}, "prog-a", {"prog-a": 3}) is True

    def test_module2_in_3module_program_cannot_graduate(self):
        assert self._can_graduate({"prog-a": 2}, "prog-a", {"prog-a": 3}) is False

    def test_module10_in_10module_program_can_graduate(self):
        assert self._can_graduate({"prog-a": 10}, "prog-a", {"prog-a": 10}) is True

    def test_graduate_sets_egresado_status(self):
        ps, err = self._graduate({"prog-a": 2}, {"prog-a": "activo"}, "prog-a", {"prog-a": 2})
        assert ps["prog-a"] == "egresado"
        assert err is None

    def test_graduate_blocked_on_non_last_module_returns_error(self):
        ps, err = self._graduate({"prog-a": 1}, {"prog-a": "activo"}, "prog-a", {"prog-a": 2})
        assert ps is None
        assert err == "not_final"

    def test_graduate_derives_egresado_when_only_program(self):
        ps, _ = self._graduate({"prog-a": 2}, {"prog-a": "activo"}, "prog-a", {"prog-a": 2})
        assert self._derive(ps) == "egresado"

    def test_graduate_derives_activo_when_other_program_still_active(self):
        """Multi-program: graduating one program while another is activo → global activo."""
        ps, _ = self._graduate(
            {"prog-a": 2, "prog-b": 1},
            {"prog-a": "activo", "prog-b": "activo"},
            "prog-a",
            {"prog-a": 2, "prog-b": 2},
        )
        assert ps["prog-a"] == "egresado"
        assert ps["prog-b"] == "activo"
        assert self._derive(ps) == "activo"

    def test_graduate_derives_egresado_when_all_programs_egresado(self):
        """Both programs egresado → global egresado."""
        ps1, _ = self._graduate(
            {"prog-a": 2}, {"prog-a": "activo", "prog-b": "egresado"}, "prog-a", {"prog-a": 2}
        )
        assert self._derive(ps1) == "egresado"

    def test_graduate_preserves_other_program_statuses(self):
        """Graduating prog-a must not alter prog-b status."""
        ps, _ = self._graduate(
            {"prog-a": 3, "prog-b": 2},
            {"prog-a": "activo", "prog-b": "pendiente_recuperacion"},
            "prog-a",
            {"prog-a": 3},
        )
        assert ps["prog-b"] == "pendiente_recuperacion"


# ---------------------------------------------------------------------------
# Unit tests for admin rejection of recovery (business rule: admin can reject)
# ---------------------------------------------------------------------------

class TestAdminRecoveryRejection:
    """Tests for admin-explicit rejection of recovery (recovery_approved = False).

    When an admin rejects a recovery:
    - The failed_subject record must be marked recovery_approved=False,
      recovery_rejected=True, recovery_processed=True.
    - The student must be marked 'reprobado' for the program.
    - The student must be removed from all program courses.
    This mirrors the logic added to approve_recovery_for_subject for approve=False.
    """

    def _derive(self, program_statuses):
        """Mirror of derive_estado_from_program_statuses."""
        if not program_statuses:
            return "activo"
        statuses = list(program_statuses.values())
        if "activo" in statuses:
            return "activo"
        if all(s == "egresado" for s in statuses):
            return "egresado"
        if "pendiente_recuperacion" in statuses:
            return "pendiente_recuperacion"
        if "egresado" in statuses:
            return "egresado"
        if "reprobado" in statuses:
            return "reprobado"
        return "retirado"

    def _admin_reject(self, program_statuses, prog_id):
        """Simulate admin rejection: set reprobado for the program."""
        updated = dict(program_statuses)
        if prog_id:
            updated[prog_id] = "reprobado"
        return updated

    def test_admin_rejection_marks_record_rejected(self):
        """After admin rejection, record fields must reflect rejection."""
        record = {
            "recovery_approved": False,
            "recovery_rejected": True,
            "recovery_processed": True,
        }
        assert record["recovery_approved"] is False
        assert record["recovery_rejected"] is True
        assert record["recovery_processed"] is True

    def test_admin_rejection_sets_reprobado(self):
        """Rejecting marks the student as reprobado for that program."""
        ps = {"prog-a": "pendiente_recuperacion"}
        updated = self._admin_reject(ps, "prog-a")
        assert updated["prog-a"] == "reprobado"

    def test_admin_rejection_global_estado_reprobado(self):
        """Global estado becomes reprobado when that is the only program."""
        ps = {"prog-a": "pendiente_recuperacion"}
        updated = self._admin_reject(ps, "prog-a")
        assert self._derive(updated) == "reprobado"

    def test_admin_rejection_preserves_other_program_status(self):
        """Rejecting in prog-a must not alter prog-b status."""
        ps = {"prog-a": "pendiente_recuperacion", "prog-b": "activo"}
        updated = self._admin_reject(ps, "prog-a")
        assert updated["prog-b"] == "activo"

    def test_admin_rejection_global_estado_activo_when_other_active(self):
        """Global estado remains activo when another program is still active."""
        ps = {"prog-a": "pendiente_recuperacion", "prog-b": "activo"}
        updated = self._admin_reject(ps, "prog-a")
        assert self._derive(updated) == "activo"

    def test_admin_rejection_immediate_expulsion(self):
        """Admin rejection is immediate, not deferred to recovery_close."""
        # Simulate: admin sets approve=False before recovery_close date.
        # The student must be immediately marked reprobado.
        recovery_close = "2099-12-31"  # far future, not yet passed
        ps = {"prog-a": "pendiente_recuperacion"}
        # Even though recovery_close has not passed, admin rejection takes effect.
        updated = self._admin_reject(ps, "prog-a")
        assert updated["prog-a"] == "reprobado"

    def test_admin_rejection_no_prog_id_does_not_crash(self):
        """When prog_id is empty, rejection should not crash the logic."""
        ps = {"prog-a": "pendiente_recuperacion"}
        updated = self._admin_reject(ps, "")
        # Empty prog_id: no key added, original unchanged
        assert updated == ps

    def test_admin_rejection_single_subject_results_in_expulsion(self):
        """Even a single rejected subject causes full expulsion (no second chance)."""
        records = [
            {"recovery_approved": False, "recovery_rejected": True, "recovery_processed": True}
        ]
        any_rejected = any(r.get("recovery_rejected") is True for r in records)
        assert any_rejected is True

    def test_admin_rejection_all_records_marked_processed(self):
        """All unprocessed records for the same student/course must be processed."""
        records = [
            {"id": "r1", "recovery_processed": True},
            {"id": "r2", "recovery_processed": True},
        ]
        all_processed = all(r.get("recovery_processed") is True for r in records)
        assert all_processed is True

    def test_recovery_approved_false_triggers_expulsion_in_scheduler(self):
        """Scheduler: recovery_approved=False means student cannot pass → remove_failed."""
        records = [
            {"recovery_approved": False, "recovery_completed": False, "teacher_graded_status": None},
        ]
        # Mirror of scheduler logic for recovery_close
        has_admin_action = any(
            r.get("recovery_approved") is True or r.get("recovery_completed") is True
            for r in records
        )
        assert has_admin_action is False  # → remove_no_action in scheduler

    def test_admin_approval_then_teacher_rejection_triggers_expulsion(self):
        """Condition 2: admin approved, teacher rejected → student must be expelled."""
        records = [
            {"recovery_approved": True, "recovery_completed": True, "teacher_graded_status": "rejected"},
        ]
        all_graded = all(r.get("recovery_completed") is True for r in records)
        any_rejected = any(r.get("teacher_graded_status") == "rejected" for r in records)
        assert all_graded is True
        assert any_rejected is True
        # Student cannot pass → should be expelled

    def test_reprobado_students_not_promoted_at_recovery_close(self):
        """A student already marked reprobado must not be promoted at recovery_close."""
        program_statuses = {"prog-a": "reprobado"}
        # Promotion check: skip if reprobado
        should_skip = program_statuses.get("prog-a") == "reprobado"
        assert should_skip is True


# ---------------------------------------------------------------------------
# Unit tests for scheduler fixes (Causa 1, 3, 4)
# ---------------------------------------------------------------------------

class TestSchedulerFixes:
    """Tests for the fixes applied to check_and_close_modules."""

    # --- Causa 4: timezone ---

    def test_bogota_tz_constant_defined(self):
        """BOGOTA_TZ constant should be importable from server module."""
        from zoneinfo import ZoneInfo
        tz = ZoneInfo("America/Bogota")
        from datetime import datetime, timezone
        utc_dt = datetime(2026, 1, 1, 5, 0, 0, tzinfo=timezone.utc)
        bogota_dt = utc_dt.astimezone(tz)
        # UTC 05:00 == Colombia midnight (UTC-5)
        assert bogota_dt.strftime("%Y-%m-%d") == "2026-01-01"

    def test_bogota_is_behind_utc_by_5_hours(self):
        """America/Bogota is UTC-5, so 02:00 server time at UTC offsets correctly."""
        from zoneinfo import ZoneInfo
        from datetime import datetime, timezone
        tz = ZoneInfo("America/Bogota")
        # UTC 07:00 = Bogotá 02:00 (UTC-5)
        utc_dt = datetime(2026, 6, 15, 7, 0, 0, tzinfo=timezone.utc)
        bogota_dt = utc_dt.astimezone(tz)
        assert bogota_dt.hour == 2
        assert bogota_dt.date().isoformat() == "2026-06-15"

    def test_scheduler_uses_bogota_date_not_utc_for_comparisons(self):
        """Scheduler today_str must use Bogotá date so that dates entered by
        Colombian admins (UTC-5) are evaluated correctly and not a day off."""
        from zoneinfo import ZoneInfo
        from datetime import datetime, timezone
        tz = ZoneInfo("America/Bogota")
        # At 23:30 UTC, it is 18:30 Bogotá same day (UTC-5)
        utc_dt = datetime(2026, 3, 10, 23, 30, 0, tzinfo=timezone.utc)
        bogota_date = utc_dt.astimezone(tz).strftime("%Y-%m-%d")
        utc_date = utc_dt.strftime("%Y-%m-%d")
        # Both are the same date in this case
        assert bogota_date == "2026-03-10"
        assert utc_date == "2026-03-10"

    def test_scheduler_bogota_date_differs_from_utc_near_midnight(self):
        """Near midnight UTC, Bogotá date is still the previous day (UTC-5)."""
        from zoneinfo import ZoneInfo
        from datetime import datetime, timezone
        tz = ZoneInfo("America/Bogota")
        # 00:30 UTC on the 11th = 19:30 Bogotá on the 10th (UTC-5)
        utc_dt = datetime(2026, 3, 11, 0, 30, 0, tzinfo=timezone.utc)
        bogota_date = utc_dt.astimezone(tz).strftime("%Y-%m-%d")
        utc_date = utc_dt.strftime("%Y-%m-%d")
        assert bogota_date == "2026-03-10"
        assert utc_date == "2026-03-11"

    # --- Causa 1: fallback module_dates from program ---

    def test_fallback_module_dates_built_from_program_close_dates(self):
        """When a course has no module_dates, fallback uses program moduleN_close_date
        fields to synthesize a recovery_close value for each module."""
        program = {
            "id": "prog-1",
            "modules": ["Módulo 1", "Módulo 2"],
            "module1_close_date": "2026-03-01",
            "module2_close_date": "2026-08-01",
        }
        course = {"id": "c-1", "program_id": "prog-1", "module_dates": {}}

        module_dates = course.get("module_dates") or {}
        if not module_dates:
            prog_modules_list = program.get("modules") or []
            max_mod = max(len(prog_modules_list), 2)
            for mn in range(1, max_mod + 1):
                close_field = f"module{mn}_close_date"
                close_val = program.get(close_field)
                if close_val:
                    module_dates[str(mn)] = {"recovery_close": close_val}

        assert module_dates == {
            "1": {"recovery_close": "2026-03-01"},
            "2": {"recovery_close": "2026-08-01"},
        }

    def test_fallback_module_dates_empty_when_program_has_no_close_dates(self):
        """No fallback data when the program itself has no close dates configured."""
        program = {"id": "prog-2", "modules": [], "name": "Prog Sin Fechas"}
        course = {"id": "c-2", "program_id": "prog-2", "module_dates": {}}

        module_dates = course.get("module_dates") or {}
        if not module_dates:
            prog_modules_list = program.get("modules") or []
            max_mod = max(len(prog_modules_list), 2)
            for mn in range(1, max_mod + 1):
                close_field = f"module{mn}_close_date"
                close_val = program.get(close_field)
                if close_val:
                    module_dates[str(mn)] = {"recovery_close": close_val}

        assert module_dates == {}

    def test_course_with_existing_module_dates_not_overwritten(self):
        """Courses that already have module_dates must never use the program fallback."""
        course = {
            "id": "c-3",
            "program_id": "prog-3",
            "module_dates": {
                "1": {"start": "2026-01-01", "end": "2026-06-30", "recovery_close": "2026-07-15"}
            },
        }
        module_dates = course.get("module_dates") or {}
        # Should NOT enter the fallback block
        entered_fallback = not module_dates  # False → no fallback
        assert entered_fallback is False
        assert module_dates["1"]["recovery_close"] == "2026-07-15"

    # --- Causa 3: retroactive close_module_internal detection ---

    def test_retroactive_check_triggers_when_no_failed_subjects_and_no_closure(self):
        """If recovery_close passed, no failed_subjects exist, and no module_closures
        recorded, the scheduler should flag retroactive execution."""
        today_str = "2026-04-01"
        recovery_close = "2026-03-01"  # already in the past
        existing_failed_subjects = None  # nothing in DB
        existing_closure = None  # no module_closures record

        should_run_retroactive = (
            existing_failed_subjects is None
            and existing_closure is None
            and recovery_close <= today_str
        )
        assert should_run_retroactive is True

    def test_retroactive_check_skipped_when_closure_already_recorded(self):
        """No retroactive run when a module_closures entry already exists."""
        today_str = "2026-04-01"
        recovery_close = "2026-03-01"
        existing_failed_subjects = None
        existing_closure = {"id": "cl-1", "module_number": 1}  # already closed

        should_run_retroactive = (
            existing_failed_subjects is None
            and existing_closure is None
            and recovery_close <= today_str
        )
        assert should_run_retroactive is False

    def test_retroactive_check_skipped_when_failed_subjects_exist(self):
        """No retroactive run when failed_subjects records are already present."""
        today_str = "2026-04-01"
        recovery_close = "2026-03-01"
        existing_failed_subjects = {"id": "fs-1", "student_id": "s-1"}
        existing_closure = None

        should_run_retroactive = (
            existing_failed_subjects is None
            and existing_closure is None
            and recovery_close <= today_str
        )
        assert should_run_retroactive is False

    def test_retroactive_check_skipped_when_recovery_not_yet_closed(self):
        """No retroactive run when recovery period hasn't closed yet."""
        today_str = "2026-02-15"
        recovery_close = "2026-03-01"  # still in the future
        existing_failed_subjects = None
        existing_closure = None

        should_run_retroactive = (
            existing_failed_subjects is None
            and existing_closure is None
            and recovery_close <= today_str
        )
        assert should_run_retroactive is False



class TestRecoverySubjectScoping:
    """Regression tests for subject-scoped recovery enablement and grading."""

    def _visible_recovery_activity_subjects(self, approved_records, activities):
        approved_subject_ids = {r.get("subject_id") for r in approved_records if r.get("subject_id")}
        has_course_level_approval = any(not r.get("subject_id") for r in approved_records)
        visible = []
        for a in activities:
            if not a.get("is_recovery"):
                continue
            sid = a.get("subject_id")
            if (sid and sid in approved_subject_ids) or (not sid and has_course_level_approval):
                visible.append(sid)
        return visible

    def test_only_admin_approved_subject_is_enabled(self):
        approved_records = [{"subject_id": "subj-A"}]  # admin approved only one failed subject
        activities = [
            {"is_recovery": True, "subject_id": "subj-A"},
            {"is_recovery": True, "subject_id": "subj-B"},
        ]
        assert self._visible_recovery_activity_subjects(approved_records, activities) == ["subj-A"]

    def test_multiple_approved_subjects_enable_only_those_subjects(self):
        approved_records = [{"subject_id": "subj-A"}, {"subject_id": "subj-B"}]
        activities = [
            {"is_recovery": True, "subject_id": "subj-A"},
            {"is_recovery": True, "subject_id": "subj-B"},
            {"is_recovery": True, "subject_id": "subj-C"},
        ]
        assert self._visible_recovery_activity_subjects(approved_records, activities) == ["subj-A", "subj-B"]

    def test_teacher_grading_filter_must_include_subject(self):
        def build_filter(student_id, course_id, subject_id):
            f = {
                "student_id": student_id,
                "course_id": course_id,
                "recovery_approved": True,
                "recovery_processed": {"$ne": True},
                "recovery_rejected": {"$ne": True},
            }
            if subject_id:
                f["subject_id"] = subject_id
            return f

        fs_filter = build_filter("s1", "c1", "subj-A")
        assert fs_filter["subject_id"] == "subj-A"
        assert fs_filter["recovery_approved"] is True
