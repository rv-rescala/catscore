import emoji

class CatsEmoji:
    @classmethod
    def remove_emoji(cls, src_str):
        return ''.join(c for c in src_str if c not in emoji.UNICODE_EMOJI)
    