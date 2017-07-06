from app.readers.rfid.rfid_card import RFIDCard
from app.readers.utils import formats

# ID Type = U -> EM4200, 5551(Q5) / 5567 & read - only emulation. | UID | = 5 bytes
# Should work for EM42xx
ID_TYPE = 'U'


# NTNU uses this for the RFID 125 KHz chip in their cards (2016-2017->?)
class EM4200Card(RFIDCard):
    def __init__(self, uid):
        self.hex_uid = uid
        super().__init__(formats.convert(formats.WIEGAND_32, uid))
