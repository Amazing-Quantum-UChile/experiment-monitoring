



def test_subsensor(subsensor_instance):
    subsensor_instance.set_vals(3.1415)
    subsensor_instance.measure()
    subsensor_instance.to_db()
    assert subsensor_instance.measurement==3.1415


def test_multisensor(multi_sensor_instance):
    multi_sensor_instance.measure()
    multi_sensor_instance.to_db()
    assert isinstance(multi_sensor_instance.subsensors[1].measurement, float)
