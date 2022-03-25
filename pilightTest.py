from pilight import pilight
pilight_connection = pilight.Client()  # Connect to the pilight-daemon at localhost:5000
pilight_connection.send_code(data={"protocol": [ "kaku_switch" ],  #  https://manual.pilight.org/en/api
                                    "id": 100,
                                    "unit": 1,
                                    "off": 1
                                    })