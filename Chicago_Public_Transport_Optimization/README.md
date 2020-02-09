# Public Transit Status with Apache Kafka

## Overview
In this project, I constructed a streaming event pipeline, around Apache Kafka and its ecosystem, that allows us to simulate and display the status of train lines in real time using public data from the [Chicago Transit Authority](https://www.transitchicago.com/data/). 
The final outcome of the project is a dashboard that a user can monitor to watch trains move from station to station.

## Prerequisites

The following are required to complete this project:

* Docker
* Python 3.7
* Access to a computer with a minimum of 16gb+ RAM and a 4-core CPU to execute the simulation

## System Architecture
The following components comprise the event streaming pipeline:

### Stream Data Producers
1. Configure the train stations to emit some of the events that we need. The CTA has placed a sensor on each side of every train station that can be programmed to take an action whenever a train arrives at the station.
2. Our partners at the CTA have asked that we also send weather readings into Kafka from their weather hardware. Unfortunately, this hardware is old and we cannot use the Python Client Library due to hardware restrictions. Instead, we are going to use HTTP REST to send the data to Kafka from the hardware using Kafka's REST Proxy.
3. Extract station information from the PostgreSQL database into Kafka using the Kafka JDBC Source Connector.

### Stream Data Store
A Kafka cluster is used as a persistent store to hold the event data that is produced. In this project a single Kafka broker is used but when it comes to deploying Kafka to production at least 3 nodes should be considered to take advantage of the fault tolerance and resiliance of Kafka  


### Stream Processing applications (Consumers)
Two stream processing frameworks are utilized to process the ingested streams:
1. Faust
We will leverage Faust Stream Processing to transform the raw Stations table that we ingested from Kafka Connect. The raw format from the database has more data than we need, and the line color information is not conveniently configured. To remediate this, we're going to ingest data from our Kafka Connect topic, and transform the data.
2. KSQL
to aggregate turnstile data for each of our stations. When we produced turnstile data, we simply emitted an event, not a count. What would make this data more useful would be to summarize it by station so that downstream applications always have an up-to-date count.


## Directory Layout
The project consists of two main directories, `producers` and `consumers`:

```

├── consumers
│   ├── consumer.py 
│   ├── faust_stream.py 
│   ├── ksql.py 
│   ├── models
│   │   ├── lines.py
│   │   ├── line.py 
│   │   ├── station.py 
│   │   └── weather.py 
│   ├── requirements.txt
│   ├── server.py
│   ├── topic_check.py
│   └── templates
│       └── status.html
└── producers
    ├── connector.py 
    ├── models
    │   ├── line.py
    │   ├── producer.py 
    │   ├── schemas
    │   │   ├── arrival_key.json
    │   │   ├── arrival_value.json 
    │   │   ├── turnstile_key.json
    │   │   ├── turnstile_value.json 
    │   │   ├── weather_key.json
    │   │   └── weather_value.json 
    │   ├── station.py 
    │   ├── train.py
    │   ├── turnstile.py 
    │   ├── turnstile_hardware.py
    │   └── weather.py 
    ├── requirements.txt
    └── simulation.py
```

## Running and Testing

To run the simulation, you must first start up the Kafka ecosystem on their machine utilizing Docker Compose.

```%> docker-compose up```

Docker compose will take a 3-5 minutes to start, depending on your hardware. Please be patient and wait for the docker-compose logs to slow down or stop before beginning the simulation.

### Running the Simulation

There are two pieces to the simulation, the `producer` and `consumer`. 

However, when you are ready to verify the end-to-end system, it is critical that you open a terminal window for each piece and run them at the same time. **If you do not run both the producer and consumer at the same time you will not be able to successfully complete the project**.

#### To run the `producer`:

1. `cd producers`
2. `virtualenv venv`
3. `. venv/bin/activate`
4. `pip install -r requirements.txt`
5. `python simulation.py`

Once the simulation is running, you may hit `Ctrl+C` at any time to exit.

#### To run the Faust Stream Processing Application:
1. `cd consumers`
2. `virtualenv venv`
3. `. venv/bin/activate`
4. `pip install -r requirements.txt`
5. `faust -A faust_stream worker -l info`

#### To run the KSQL Creation Script:
1. `cd consumers`
2. `virtualenv venv`
3. `. venv/bin/activate`
4. `pip install -r requirements.txt`
5. `python ksql.py`

#### To run the `consumer`:

1. `cd consumers`
2. `virtualenv venv`
3. `. venv/bin/activate`
4. `pip install -r requirements.txt`
5. `python server.py`

Once the server is running, you may hit `Ctrl+C` at any time to exit.
