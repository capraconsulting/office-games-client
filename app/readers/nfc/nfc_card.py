from app.readers.utils.card import NFC_CARD, Card


class NFCCard(Card):
    def __init__(self, uid):
        super().__init__(NFC_CARD, uid)

    def __repr__(self):
        return super().__repr__()
