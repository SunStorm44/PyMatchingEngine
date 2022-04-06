# Matching Engine
Matching Engine Simulator with the below functionalities implemented:
- Limit Orders
- Market Orders
- Iceberg Orders
- Fill-or-Kill Orders
- Stop (Loss) Orders

Functionalities pending:
- Take-Profit Orders
- Functionalities related to client, such as position, trade and working orders quering etc.

## Design
Main inspiration came from Jelle Pelgrims blogpost where he creates a Matching Engine in Python with a basic Limit Order functionality:
* [MatchingEngine](https://jellepelgrims.com/posts/matching_engines) 

## Structure
* Engine stored under `engine/`
* Order, OrderBook, Client and Trade classes located under `engine/src/`
* Tests stored under `tests/`