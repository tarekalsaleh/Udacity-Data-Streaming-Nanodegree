import producer_server
import socket

def run_kafka_server():
	# TODO get the json file path
    input_file = "./police-department-calls-for-service.json"

    # TODO fill in blanks
    producer = producer_server.ProducerServer(
        input_file=input_file,
        topic="com.sf.crime.police-event",
        bootstrap_servers="localhost:9092",
        client_id=socket.gethostname()
    )

    return producer


def feed():
    producer = run_kafka_server()
    producer.generate_data()


if __name__ == "__main__":
    feed()
