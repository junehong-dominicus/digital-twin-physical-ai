from bacpypes.apdu import WritePropertyRequest
from bacpypes.primitivedata import Real

def handle_write_property(apdu, registry):
    obj_type, obj_inst = apdu.objectIdentifier
    if obj_type != "analogInput":
        return

    sensor = registry.by_bacnet_instance(obj_inst)
    if not sensor or not sensor.writable:
        return

    if isinstance(apdu.propertyValue.value, Real):
        sensor.set_override(float(apdu.propertyValue.value))
