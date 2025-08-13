MAX_ATTEMPTS = 5
REQUIRED_SUCCESSES = 3

class CaptchaSession:
    def __init__(self):
        '''

        '''
        self.success_count = 0
        self.attempt_count = 0
        self.current_correct_answer = -1

    def handle_answer(self, answer):
        '''

        :param answer:
        :return:
        '''
        self.attempt_count += 1

        if answer == self.current_correct_answer:
            self.success_count += 1

    def get_status(self):
        '''

        :return:
        '''
        status = "continue"

        if self.success_count == REQUIRED_SUCCESSES:
            status = "pass"

        elif self.attempt_count == MAX_ATTEMPTS or self.success_count + (MAX_ATTEMPTS - self.attempt_count) < REQUIRED_SUCCESSES:
            status = "fail"

        return status