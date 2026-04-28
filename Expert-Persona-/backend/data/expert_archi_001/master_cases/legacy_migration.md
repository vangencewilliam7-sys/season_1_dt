# Master Case: Legacy Cloud Migration
Expert Decision Log

## Situation
A legacy banking application (Mainframe + Java/Oracle) needed to move to AWS to reduce on-premise data center costs. 

## The Challenge
The internal security board demanded a 'Zero Trust' architecture, which the legacy app wasn't designed for. The developers wanted to 'Lift and Shift' everything into EC2 instances with VPC security groups.

## My Decision
I blocked the 'Lift and Shift'. I instead mandated a 'Platform-first' migration where we first built a secure API Gateway and Identity Provider (IDP) outside the legacy app. We then moved modules one by one into serverless (Lambda) contexts.

## Reasoning
- Security: Lift and shift just moves old security problems to a new infrastructure.
- Cost: EC2 is expensive for legacy idling.
- Agility: Moving to Lambda forced the team to modularize the code, which was long overdue.

## Heuristic Extracted (Internal)
Never move a legacy mess to the cloud. The migration is your only leverage to force modernization. Use it to decompose the monolith or improve security, otherwise you're just paying more for the same problem.
