

def test_send_query_to_arduino(arduino_instance):
    """test to query the arduino
    """
    res = arduino_instance.query("Test")
    assert  isinstance(res, str)


def test_adc_arduino(arduino_adc_instance):
    """Test that Arduino ADC measurement returns correct values."""
    arduino_adc_instance.measure()
    assert isinstance(arduino_adc_instance.measurement, list)
    assert len(arduino_adc_instance.raw_vals)==arduino_adc_instance.number_of_sensors
    assert isinstance(arduino_adc_instance.measurement[0], (float, int))
