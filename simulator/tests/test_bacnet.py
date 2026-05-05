from bacpypes.apdu import ReadPropertyRequest
from bacpypes.pdu import Address

def test_bacnet_ai():
    req = ReadPropertyRequest(
        objectIdentifier=("analogInput", 1),
        propertyIdentifier="presentValue",
        destination=Address("127.0.0.1")
    )
    # send & verify response (simplified)
