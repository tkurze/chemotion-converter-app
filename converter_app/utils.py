import base64
import hashlib
import re
import uuid


def human2bytes(string):
    """
    Bytes size converter
    :param string: input unit string for example 100kb
    """
    if not string:
        return 0

    m = re.match(r'([0-9.]+)\s*([A-Za-z]+)', string)
    number, unit = float(m.group(1)), m.group(2).strip().lower()

    if unit in ['kb', 'k']:
        number = number * 1000
    elif unit in ['mb', 'm']:
        number = number * 1000**2
    elif unit in ['gb', 'g']:
        number = number * 1000**3
    elif unit in ['tb', 't']:
        number = number * 1000**4
    elif unit in ['pb', 'p']:
        number = number * 1000**5
    elif unit == 'kib':
        number = number * 1024
    elif unit == 'mib':
        number = number * 1024**2
    elif unit == 'gib':
        number = number * 1024**3
    elif unit == 'tib':
        number = number * 1024**4
    elif unit == 'pib':
        number = number * 1024**5
    return number


def check_uuid(string):
    """
    :param string: uuid string
    :return: True if string is a uuid
    """
    try:
        return uuid.UUID(string, version=4)
    except ValueError:
        return False


def checkpw(password, hashed_password):
    """
    :param password: Password string
    :param hashed_password: hashed password in htaccess
    :return: True if password is correct
    """
    m = hashlib.sha1()
    m.update(password)
    return (b'{SHA}' + base64.b64encode(m.digest())) == hashed_password
