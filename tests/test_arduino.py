

def test_send_query_to_arduino(arduino_instance):
    """test to query the arduino
    """
    res = arduino_instance.query("Test")
    assert  isinstance(res, str)
