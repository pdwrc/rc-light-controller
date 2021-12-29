import config

def test_config():
    
    c = config.Config.load()
    assert len(c.lights) == 3
    assert c.lights[0].pin == 12

    c.save()
