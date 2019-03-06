#!/usr/bin/env python
import pika
import sys

#credentials = pika.PlainCredentials('admin', '123456')  
credentials = pika.PlainCredentials('admin', 'rbadmin')  
parameters = pika.ConnectionParameters('172.16.16.158',5672,'/',credentials    )  
#parameters = pika.ConnectionParameters('10.10.10.85',5672,'/',credentials    )  
connection = pika.BlockingConnection(parameters) 
channel = connection.channel()

channel.exchange_declare(exchange='amq.direct',
                         exchange_type='direct',durable=True)

result = channel.queue_declare()
queue_name = result.method.queue

severities = sys.argv[1:]
if not severities:
    print >> sys.stderr, "Usage: %s [info] [warning] [error]" % \
                         (sys.argv[0],)
    sys.exit(1)

for severity in severities:
    channel.queue_bind(exchange='amq.direct',
                       queue=queue_name,
                       routing_key=severity)

print ' [*] Waiting for logs. To exit press CTRL+C'

def callback(ch, method, properties, body):
    print "%r:%r" % (method.routing_key, body,)

channel.basic_consume(callback,
                      queue=queue_name,
                      no_ack=True)

channel.start_consuming()