from app.readers.utils.card import RFID_CARD, Card


class RFIDCard(Card):
    def __init__(self, uid):
        super().__init__(RFID_CARD, uid)

    def __repr__(self):
        return super().__repr__()
