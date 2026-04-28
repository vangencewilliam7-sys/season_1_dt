# Master Case: Scaling E-Commerce Traffic
Expert Decision Log

## Situation
A large e-commerce client faced 10x traffic spikes during 'Flash Sales'. The existing PHP/MySQL monolith was locking up due to database contention on the 'inventory' table.

## The Challenge
We had 3 weeks before the next sale. The team wanted to rewrite the entire system in Go and use a NoSQL database.

## My Decision
I rejected the rewrite. Instead, I introduced a 'Virtual Queue' using Redis and a side-car service for Inventory only. All other traffic stayed on the monolith. 

## Reasoning
- Risk: A 3-week rewrite of a core system is suicide.
- Strategy: Identify the bottleneck (inventory DB locks) and isolate ONLY that component using a 'Strangler pattern'.
- Result: The next sale handled 15x traffic with zero downtime.

## Heuristic Extracted (Internal)
When facing a high-pressure deadline, never replace a stable bottlenecked system with an unproven one. Isolate and scale the specific failure point instead.
