def build_command(command, params):
    """
    builds a command message
    :param command: command code
    :param params: params of message
    :return: built command message
    """
    return str(command) + "@".join(params)


def send_guess(guess):
    """
    build a guess message
    :param guess: guess of fruit (0-8)
    :return: built guess message
    """
    return build_command('01', str(guess))


def unpack(data):
    """
    split message into opcode and params
    :param data: full message including opcode
    :return: message opcode and params
    """
    opcode = data[:2]
    params = data[2:].split('@')
    return opcode, params