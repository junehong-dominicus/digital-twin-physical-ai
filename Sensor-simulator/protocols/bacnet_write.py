from bacpypes.apdu import WritePropertyRequest
from bacpypes.primitivedata import Real, Null
import logging

def handle_write_property(apdu, registry):
    obj_type, obj_inst = apdu.objectIdentifier
    
    # We now use AnalogValue for commandable sensors
    if obj_type not in ("analogValue", "analogInput"):
        return

    sensor = registry.by_bacnet_instance(obj_inst)
    if not sensor or not sensor.writable:
        return

    priority = apdu.priority
    if not priority:
        priority = 16 # Default priority

    # propertyValue.value is an 'Any' object, must cast_out to get actual primitive
    try:
        value = apdu.propertyValue.value.cast_out()
    except Exception as e:
        logging.error(f"Failed to cast_out property value: {e}")
        return

    if isinstance(value, Null):
        sensor.clear_priority(priority)
    elif isinstance(value, Real):
        sensor.set_priority(float(value.value), priority)
    elif isinstance(value, (float, int)):
        sensor.set_priority(float(value), priority)
