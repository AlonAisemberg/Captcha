def build_command(command, params):
    """
    builds a command message
    :param command: command code
    :param params: params of message
    :return: built command message
    """
    return str(command) + "@".join(params)


def img_msg(img_data):
    """
    builds send img msg
    :param img_data: content of img
    :return: img message
    """
    return build_command('01', img_data)


def end_msg(end):
    """
    builds end status msg
    :param end: end status (pass/fail)
    :return: built end status msg
    """
    return build_command('02', end)


def unpack(data):
    """
    split message into opcode and params
    :param data: full message including opcode
    :return: message opcode and params
    """
    opcode = data[:2]
    params = data[2:].split('@')
    return opcode, params
