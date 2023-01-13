from telegram.ext.filters import MessageFilter
from winged_scapula_span_bot.helper.utils import is_not_empty_string


class _IsMessageWithText(MessageFilter):
    __slots__ = ()

    def filter(self, message) -> bool:
        return is_not_empty_string(message.text) or is_not_empty_string(message.caption)


IS_MESSAGE_WITH_TEXT = _IsMessageWithText(name='filters.IsMessageWithText')
"""Messages that contain text or caption."""
