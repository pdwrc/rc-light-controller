import config

def test_config():
    
    c = config.config
    assert len(c.lights) == 3
    assert c.lights[0].pin == 12

    c.save()
