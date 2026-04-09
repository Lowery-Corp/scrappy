#!/usr/bin/env python
import pika

credentials = pika.PlainCredentials("scrappy", "xxxxxxxxxxxxxxxxx")
params = pika.ConnectionParameters(
    host="localhost",
    port=5672,
    credentials=credentials,
)

connection = pika.BlockingConnection(params)
channel = connection.channel()

channel.queue_declare(queue='hello', durable=True, arguments={'x-queue-type': 'quorum'})

channel.basic_publish(exchange='', routing_key='hello', body='Hello World!')
print(" [x] Sent 'Hello World!'")
connection.close()