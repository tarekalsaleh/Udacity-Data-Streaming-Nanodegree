"""Defines trends calculations for stations"""
import logging

import faust


logger = logging.getLogger(__name__)


# Faust will ingest records from Kafka in this format
class Station(faust.Record):
    stop_id: int
    direction_id: str
    stop_name: str
    station_name: str
    station_descriptive_name: str
    station_id: int
    order: int
    red: bool
    blue: bool
    green: bool


# Faust will produce records to Kafka in this format
class TransformedStation(faust.Record):
    station_id: int
    station_name: str
    order: int
    line: str


# TODO: Define a Faust Stream that ingests data from the Kafka Connect stations topic and
#   places it into a new topic with only the necessary information.
app = faust.App("stations-stream", broker="kafka://localhost:9092", store="memory://")

# TODO: Define the input Kafka Topic. Hint: What topic did Kafka Connect output to?
topic = app.topic("com.udacity.connect.stations", value_type=Station)
# TODO: Define the output Kafka Topic
out_topic = app.topic("com.udacity.station.transformed", partitions=1, value_type=TransformedStation)
# TODO: Define a Faust Table
table = app.Table(
    "stations.table",
    default=int,
    partitions=1,
    changelog_topic=out_topic,
)


@app.agent(topic)
async def process(station_stream):
    async for event in station_stream:
        """Transform station data"""
        table["station_id"] = event.station_id
        table["station_name"] = event.station_name
        table["order"] = event.order

        if event.red:
            table["line"] = "red"
        elif event.blue:
            table["line"] = "blue"
        elif event.green:
            table["line"] = "green"


if __name__ == "__main__":
    app.main()
