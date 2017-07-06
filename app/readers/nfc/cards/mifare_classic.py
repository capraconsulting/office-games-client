from app.readers.nfc.nfc_card import NFCCard


class MifareClassicCard(NFCCard):
    def __init__(self, uid):
        # TODO: use another card format
        super().__init__(uid)
