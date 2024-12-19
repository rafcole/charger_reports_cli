class ValidationUtils:
    @classmethod
    def is_usable_as_unsigned_int(cls, value, num_bits):
        if type(value) is str:
            if not value.isdigit():
                return False
            value = int(value)

        if type(value) is int:
            return 0 <= value <= 2**num_bits - 1

        return False

    @classmethod
    def is_usable_as_bool(cls, value):
        if type(value) is bool:
            return True

        if type(value) is str:
            return value in {"True", "true", "TRUE", "False", "false", "FALSE"}
        return False
