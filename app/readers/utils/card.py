NFC_CARD = 0x00
RFID_CARD = 0x01


class Card:
    def __init__(self, card_type, uid):
        self.card_type = card_type
        self.uid = uid

    def __repr__(self):
        return f'<Card {self.__class__.__name__.replace("Card", "")} uid={self.uid}>'

    def get_card_type(self):
        return self.card_type

    def get_uid(self):
        return self.uid
