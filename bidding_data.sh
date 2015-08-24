#!/bin/bash
mdb-export "$1" BiddingData > "$1.csv"
mdb-export "$1" RoundData > "$1.sitting.csv"
python bidding_data.py "$1.csv" "$1.sitting.csv" "$2"
