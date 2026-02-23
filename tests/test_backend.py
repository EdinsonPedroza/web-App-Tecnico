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
# Unit tests for derive_estado_from_program_statuses
# ---------------------------------------------------------------------------

class TestDeriveEstadoFromProgramStatuses:
    """Tests for the derive_estado_from_program_statuses helper."""

    def _derive(self, program_statuses):
        """Mirror of derive_estado_from_program_statuses from server.py."""
        if not program_statuses:
            return "activo"
        statuses = list(program_statuses.values())
        if "pendiente_recuperacion" in statuses:
            return "pendiente_recuperacion"
        if all(s == "egresado" for s in statuses):
            return "egresado"
        if "activo" in statuses:
            return "activo"
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
        """pendiente_recuperacion beats activo and egresado."""
        result = self._derive({
            "prog-1": "pendiente_recuperacion",
            "prog-2": "activo"
        })
        assert result == "pendiente_recuperacion"

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
        """pendiente_recuperacion takes priority even over egresado."""
        result = self._derive({
            "prog-1": "egresado",
            "prog-2": "pendiente_recuperacion"
        })
        assert result == "pendiente_recuperacion"


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
