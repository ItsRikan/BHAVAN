# BHAVAN
### Building Hospitality Assistance through Virtual Agent Networks
![Thumbnail](/thumbnail.png)
## Project Overview - Agent BHAVAN

This project contains the core logic for Agent BHAVAN, a multi-agent system designed to manage hotels. The agent is built using Google Agent Development Kit (ADK) and follows a modular architecture.
![workflow 1](/agent_workflow_01.png)

## Problem Statement

Many hotels struggle with service gaps and operational inefficiencies that directly harm guest satisfaction and revenue. Guest support is often limited to frontline staff hours, leaving late-night or early-morning travelers without timely help and increasing frustration. Peak periods create long queues and slow check-ins/check-outs when manual processing is the norm, while inconsistent staff knowledge produces uneven information and service quality. Language barriers further shrink a hotel’s ability to serve international guests reliably.


## Solution Statement

BHAVAN functions as a constantly accessible hospitality concierge that revolutionizes the way hotels engage with guests and oversee their operations. In contrast to systems limited by staff schedules or manual procedures BHAVAN offers round-the-clock assistance via natural chat communication, allowing guests to instantly reserve spa services, book dining tables, request late check-outs, or ask for additional towels without queuing or contacting the front desk. The agent provides precise and multilingual replies, eradicating human mistakes.


## Architecture

BHAVAN is a modular, multi-agent hospitality system built on Google’s Agent Development Kit (ADK). A single root agent orchestrates a set of specialized sub-agents and function-tools so the system behaves as a composable ecosystem of focused capabilities (guest interactions, approvals, bookings, maintenance routing, upselling, analytics) rather than a monolith. This modularity improves testability, extensibility, and clarity of responsibility.

**1. Latency reduction & availability :**

To speed availability checks and room selection, BHAVAN uses a precomputed room map (JSON). Faster available room search, sink with database if any corruption occure.

**2. Limitations :**

- Local demo datastore only: Not connected to any real property management system; intended for development and testing.
- Mocked payments: Approvals and charges are simulated for demo purposes; do not represent real financial flows. 


## Essential Tools & Utilities

BHAVAN offers a targeted collection of utilities and agent-specific tools designed for room administration, confirmation handling and suggestions directed at guests. Every element fulfills a role, within the hospitality process.

**1) Room Map utilities**

A consolidated set of tools tasked with verifying room numbers setting up or refreshing the room map fetching available rooms and modifying room occupancy during check-in and check-out procedures. These features together uphold the hotel’s binary room availability map. Guarantee quick consistent room searches and alignment, with the demo datastore.

**2) attraction point search**

A dedicated agent (functions, as a tool) that fetches tourist spots or attractions. It assists BHAVAN in suggesting points of interest to visitors according to closeness and pertinence.

**3) booking**

Function-call utilities that modify room statuses in the datastore. These symbolize the operations supporting each booking and checkout processed by the system.

**4) confirmation**

Approval utilities that enforce a confirmation step before sensitive operations like booking or checkout are executed. These tools ensure explicit guest consent before finalizing any room-related action.

