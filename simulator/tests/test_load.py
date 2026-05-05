def test_modbus_load():
    from tools.load_modbus import run
    rps = run()
    assert rps > 500
