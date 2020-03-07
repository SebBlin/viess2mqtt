def error_str(rc):
    """Convert a Paho error to a human readable string."""
    return '{}: {}'.format(rc, mqtt.error_string(rc))


def on_connect(unused_client, unused_userdata, unused_flags, rc):
    """Callback for when a device connects."""
    print('on_connect', mqtt.connack_string(rc))

    # After a successful connect, reset backoff time and stop backing off.
    global should_backoff
    global minimum_backoff_time
    should_backoff = False
    minimum_backoff_time = 1


def on_disconnect(unused_client, unused_userdata, rc):
    """Paho callback for when a device disconnects."""
    print('on_disconnect', error_str(rc))

    # Since a disconnect occurred, the next loop iteration will wait with
    # exponential backoff.
    global should_backoff
    should_backoff = True


def on_publish(unused_client, unused_userdata, unused_mid):
    """Paho callback when a message is sent to the broker."""
    print('on_publish')


def on_message(unused_client, unused_userdata, message):
    """Callback when the device receives a message on a subscription."""
    payload = str(message.payload.decode('utf-8'))
    print('Received message \'{}\' on topic \'{}\' with Qos {}'.format(
            payload, message.topic, str(message.qos)))


def get_client(
        project_id, cloud_region, registry_id, device_id, private_key_file,
        algorithm, ca_certs, mqtt_bridge_hostname, mqtt_bridge_port):
    """Create our MQTT client. The client_id is a unique string that identifies
    this device. For Google Cloud IoT Core, it must be in the format below."""
    client_id = 'projects/{}/locations/{}/registries/{}/devices/{}'.format(
            project_id, cloud_region, registry_id, device_id)
    print('Device client_id is \'{}\''.format(client_id))

    client = mqtt.Client(client_id=client_id)

    # With Google Cloud IoT Core, the username field is ignored, and the
    # password field is used to transmit a JWT to authorize the device.
    client.username_pw_set(
            username='unused',
            password=create_jwt(
                    project_id, private_key_file, algorithm))

    # Enable SSL/TLS support.
    client.tls_set(ca_certs=ca_certs, tls_version=ssl.PROTOCOL_TLSv1_2)

    # Register message callbacks. https://eclipse.org/paho/clients/python/docs/
    # describes additional callbacks that Paho supports. In this example, the
    # callbacks just print to standard out.
    client.on_connect = on_connect
    client.on_publish = on_publish
    client.on_disconnect = on_disconnect
    client.on_message = on_message

    # Connect to the Google MQTT bridge.
    client.connect(mqtt_bridge_hostname, mqtt_bridge_port)

    # This is the topic that the device will receive configuration updates on.
    mqtt_config_topic = '/devices/{}/config'.format(device_id)

    # Subscribe to the config topic.
    client.subscribe(mqtt_config_topic, qos=1)

    # The topic that the device will receive commands on.
    mqtt_command_topic = '/devices/{}/commands/#'.format(device_id)

    # Subscribe to the commands topic, QoS 1 enables message acknowledgement.
    print('Subscribing to {}'.format(mqtt_command_topic))
    client.subscribe(mqtt_command_topic, qos=0)

    return client


# global minimum_backoff_time
# global MAXIMUM_BACKOFF_TIME

# # Publish to the events or state topic based on the flag.
# sub_topic = 'events' if args.message_type == 'event' else 'state'

# mqtt_topic = '/devices/{}/{}'.format(args.device_id, sub_topic)

# jwt_iat = datetime.datetime.utcnow()
# jwt_exp_mins = args.jwt_expires_minutes
# client = get_client(
#     args.project_id, args.cloud_region, args.registry_id,
#     args.device_id, args.private_key_file, args.algorithm,
#     args.ca_certs, args.mqtt_bridge_hostname, args.mqtt_bridge_port)

# # Publish num_messages messages to the MQTT bridge once per second.
# for i in range(1, args.num_messages + 1):
#     # Process network events.
#     client.loop()

#     # Wait if backoff is required.
#     if should_backoff:
#         # If backoff time is too large, give up.
#         if minimum_backoff_time > MAXIMUM_BACKOFF_TIME:
#             print('Exceeded maximum backoff time. Giving up.')
#             break

#         # Otherwise, wait and connect again.
#         delay = minimum_backoff_time + random.randint(0, 1000) / 1000.0
#         print('Waiting for {} before reconnecting.'.format(delay))
#         time.sleep(delay)
#         minimum_backoff_time *= 2
#         client.connect(args.mqtt_bridge_hostname, args.mqtt_bridge_port)

#     payload = '{}/{}-payload-{}'.format(
#             args.registry_id, args.device_id, i)
#     print('Publishing message {}/{}: \'{}\''.format(
#             i, args.num_messages, payload))
#     seconds_since_issue = (datetime.datetime.utcnow() - jwt_iat).seconds
#     if seconds_since_issue > 60 * jwt_exp_mins:
#         print('Refreshing token after {}s'.format(seconds_since_issue))
#         jwt_iat = datetime.datetime.utcnow()
#         client.loop()
#         client.disconnect()
#         client = get_client(
#             args.project_id, args.cloud_region,
#             args.registry_id, args.device_id, args.private_key_file,
#             args.algorithm, args.ca_certs, args.mqtt_bridge_hostname,
#             args.mqtt_bridge_port)
#     # Publish "payload" to the MQTT topic. qos=1 means at least once
#     # delivery. Cloud IoT Core also supports qos=0 for at most once
#     # delivery.
#     client.publish(mqtt_topic, payload, qos=1)

#     # Send events every second. State should not be updated as often
#     for i in range(0, 60):
#         time.sleep(1)
#         client.loop()