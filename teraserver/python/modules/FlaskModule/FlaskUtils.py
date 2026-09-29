from opentera.db.models.TeraUser import UserPasswordInsecure
import secrets
import string


class FlaskUtils:

    @staticmethod
    def get_password_weaknesses_text(weaknesses: list, separator=',') -> str:
        from flask_babel import gettext
        text_list = []
        for weakness in weaknesses:
            if weakness == UserPasswordInsecure.PasswordWeaknesses.NO_SPECIAL:
                text_list.append(gettext('Password missing special character'))
            if weakness == UserPasswordInsecure.PasswordWeaknesses.NO_NUMERIC:
                text_list.append(gettext('Password missing numeric character'))
            if weakness == UserPasswordInsecure.PasswordWeaknesses.BAD_LENGTH:
                text_list.append(gettext('Password not long enough (10 characters)'))
            if weakness == UserPasswordInsecure.PasswordWeaknesses.NO_LOWER_CASE:
                text_list.append(gettext('Password missing lower case letter'))
            if weakness == UserPasswordInsecure.PasswordWeaknesses.NO_UPPER_CASE:
                text_list.append(gettext('Password missing upper case letter'))

        return separator.join(text for text in text_list)

    @staticmethod
    def generate_unique_code(length: int = 6) -> str:
        digits = string.digits
        return ''.join(secrets.choice(digits) for _ in range(length))
