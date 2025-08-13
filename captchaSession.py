MAX_ATTEMPTS = 5
REQUIRED_SUCCESSES = 3

class CaptchaSession:
    def __init__(self):
        """
        initialize a new captcha session
        """
        self.success_count = 0
        self.attempt_count = 0
        self.current_correct_answer = -1

    def handle_answer(self, answer):
        """
        handle a client's answer
        :param answer: guess of which fruit is rotten (0-8)
        """
        self.attempt_count += 1

        if answer == self.current_correct_answer:
            self.success_count += 1

    def get_status(self):
        """
        get the status of what to do with the client's captcha session
        continue - send more images
        pass - the client passed the captcha
        fail - the client failed the captcha
        :return: captcha session status
        """
        status = "continue"

        # check if the client reached the required amount of successes
        if self.success_count == REQUIRED_SUCCESSES:
            status = "pass"

        # check if the client is unable to reach the required amount of successes - if the client failed
        elif self.success_count + MAX_ATTEMPTS - self.attempt_count < REQUIRED_SUCCESSES:
            status = "fail"

        return status