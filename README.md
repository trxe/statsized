# Statsized

A GRPC Server for live NHL stats

## Overview

While running, the server fetches the daily schedule every hour, 
and schedules the next provision job to begin running at the start of each game.
During the course of each game, the server `GET`s the latest game updates from the endpoint 
at an interval. Game updates come in 2 pieces of core data:

- Game Events (/playbyplay)
- Shifts (/shiftcharts)

The client runs a thin processing parser on this information, before making it available as a stream.
The gRPC service provides endpoints for the full game state (pbp and shifts) and streams for updates.

In the future, this project will be expanded to provide features such as 

- live player heatmaps
- streaming live advanced stats

## Roadmap

- Setup scheduler
- Finish all parsers
- Write tests for parsers
- Setup jobs
    - Game checking job
    - Per game event tracking
    - Per game shift tracking
- Setup server (grpc)

## Devlog

> Current status: scheduler and most mock methods have been setup and one basic endpoints. Some parser have been written

### 0.0.0 [WIP]

- Setup scheduler
- Setup GRPC server classes
- Setup (some) parsers