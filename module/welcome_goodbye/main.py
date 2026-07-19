from ...utils.message.msg import MessageTemplate


class WelcomeGoodbye:
    """进退群提醒模块。"""

    _msg_template: MessageTemplate

    def __init__(self, msg_template: MessageTemplate):
        self._msg_template = msg_template
