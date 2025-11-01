# A brief thought process on my work

## Overview
The core aim of this project is to implement an Nginx reverse proxy with blue-green deployment support for the backend containers which is pulled from a provided image link.

## Key Decisions
- Used `nginx.conf.template` with dynamic upstreams (`app_blue`, `app_green`) for flexibility in deployments.
- Chose environment variables to manage ports dynamically.
- Added `fail_timeout` and `max_fails` for better fault tolerance.
- Used a backup server configuration for green deployment to minimize downtime during switches.



## Brief Thought Process
My approach was to design a lightweight and fault-tolerant reverse proxy setup for blue-green deployment. I began by:
1. Defining two backend servers (`app_blue` and `app_green`) to ensure zero downtime during updates.
2. I ensured configuration files were highly simple and readable, not complex.
3. I focused on dynamic port handling using environment variables.
4. I ensured timeout values and upstream failover rules were introduced to improve reliability.
5. After resolving an initial Nginx configuration error, I validated that both upstreams could handle requests effectively.


## Challenges
- Initially encountered proxy argument errors, which were fixed by adjusting the `proxy_set_header` directives.
- Ensured `.env` is now excluded from version control and new credentials are regenerated.
