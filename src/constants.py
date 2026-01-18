"""Constants for Electric Data API"""

# Reading Types
READING_TYPE_VT = "32.0.4.1.1.2.12.0.0.0.0.1.0.0.0.3.72.0"  # VT Reading Type
READING_TYPE_MT = "32.0.4.1.1.2.12.0.0.0.0.2.0.0.0.3.72.0"  # MT Reading Type

# Reading Type Labels
READING_TYPE_LABELS = {
    READING_TYPE_VT: "VT",
    READING_TYPE_MT: "MT"
}

# API Endpoints
ELECTRIC_DATA_ENDPOINT = "/electric-data"
METER_READINGS_ENDPOINT = "/meter-readings"
