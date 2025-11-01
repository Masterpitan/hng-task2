# Blue/Green Deployment with Observability & Slack Alerts

This project implements a blue/green deployment setup with Nginx load balancing, real-time log monitoring, and Slack alerting for operational visibility.

## Features

- **Blue/Green Deployment**: Zero-downtime deployments with automatic failover
- **Real-time Monitoring**: Python log watcher that tails Nginx access logs
- **Slack Alerts**: Detailed JSON-formatted notifications for:
  - Failover events (Blue→Green, Green→Blue)
  - High error rates exceeding thresholds
  - System startup notifications
- **Configurable Thresholds**: Environment-based configuration for error rates, window sizes, and cooldowns

## Setting up and starting

1. **Clone and Setup**:
   ```bash
   git clone <your-repo-url>
   cd hng-task2
   cp .env.example .env
   ```

2. **Configure Slack Webhook**:
   Edit `.env` and after configuring your slack, set your `SLACK_WEBHOOK_URL`

3. **Start Services**:
   ```bash
   docker compose up -d
   ```

4. **Test the Setup**:
   ```bash
   curl http://localhost:8080/version
   ```

5. **Run Chaos Tests**:
   ```bash
   python test_chaos.py
   ```

## Testing Failover & Alerts

### Test Failover Detection
```bash
# Stop blue container to trigger failover
docker compose stop app_blue

# Make requests to see green taking over
curl http://localhost:8080/version

# Restart blue to see failover back
docker compose start app_blue
```

### Test Error Rate Alerts
```bash
# Use the chaos testing script
python test_chaos.py

# Or manually:
# Stop both containers briefly to generate errors
docker compose stop app_blue app_green
for i in {1..10}; do curl http://localhost:8080/version; done
docker compose start app_blue app_green
```

## Viewing Logs

- **Nginx Access Logs**: `docker compose logs nginx`
- **Alert Watcher Logs**: `docker compose logs alert_watcher`
- **Application Logs**: `docker compose logs app_blue app_green`

## Slack Alert Examples

The system sends detailed JSON-formatted alerts:

### Failover Alert
```json
{
  "type": "Failover Detected",
  "timestamp": "2024-10-30T10:30:00",
  "message": "Pool switched from blue → green",
  "metadata": {
    "previous_pool": "blue",
    "current_pool": "green",
    "upstream_server": "172.18.0.3:3000",
    "response_time": "0.002"
  }
}
```

### Error Rate Alert
```json
{
  "type": "High Error Rate",
  "timestamp": "2024-10-30T10:35:00",
  "message": "Error rate 15.2% exceeds threshold 2%",
  "metadata": {
    "current_error_rate": "15.2%",
    "threshold": "2%",
    "window_size": 200,
    "total_errors": 30
  }
}
```

## Configuration

All settings are configured via environment variables in `.env`:

| Variable | Default | Description |
|----------|---------|-------------|
| `SLACK_WEBHOOK_URL` | - | Slack incoming webhook URL |
| `ERROR_RATE_THRESHOLD` | 2 | Error rate percentage threshold |
| `WINDOW_SIZE` | 200 | Number of requests to track for error rate |
| `ALERT_COOLDOWN_SEC` | 300 | Seconds between duplicate alerts |
| `ACTIVE_POOL` | blue | Initial active pool |

## Architecture

- **Nginx**: Reverse proxy with custom logging format
- **App Containers**: Blue and green instances of the application
- **Alert Watcher**: Python service that monitors logs and sends alerts
- **Shared Volume**: Nginx logs accessible to watcher service

## Troubleshooting

1. **No Slack alerts?**: Check `SLACK_WEBHOOK_URL` in `.env`
2. **Logs not appearing**: Ensure shared volume is mounted correctly
3. **Failover not working**: Check container health and nginx upstream configuration

## Files Structure

```
├── docker-compose.yml          # Service definitions
├── nginx.conf.template         # Nginx configuration with custom logging
├── watcher.py                  # Log monitoring and alerting service
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── runbook.md                 # Operational runbook
├── test_chaos.py              # Chaos testing script
└── README.md                  # This file
```

## Verification Steps

1. Start the services: `docker compose up -d`
2. Run chaos tests: `python test_chaos.py`
3. Check Slack channel for alerts
4. Verify nginx logs: `docker compose logs nginx | grep pool=`
