# Blue/Green Deployment Runbook

## Alert Types & Operator Actions

### 1. Failover Detected
**Alert**: Pool switched from blue → green (or vice versa)

**Meaning**: Primary container failed, backup is now serving traffic

**Actions**:
1. Check health of failed container: `docker compose logs app_blue`
2. Verify backup is healthy: `curl http://localhost:8080/version`
3. Restart failed container: `docker compose restart app_blue`
4. Monitor for recovery

### 2. High Error Rate
**Alert**: Error rate X% exceeds threshold Y%

**Meaning**: Too many 5xx errors from upstream servers

**Actions**:
1. Check upstream logs: `docker compose logs app_blue app_green`
2. Verify container health: `docker compose ps`
3. If containers are down, restart: `docker compose up -d`
4. Consider manual pool toggle if one pool is consistently failing

### 3. Monitor Started
**Alert**: Blue/Green deployment monitor is now active

**Meaning**: Alert system has started successfully

**Actions**: No action required - informational only

## Maintenance Mode

To suppress alerts during planned maintenance:
1. Stop alert watcher: `docker compose stop alert_watcher`
2. Perform maintenance
3. Restart watcher: `docker compose start alert_watcher`

## Emergency Procedures

### Complete Service Failure
```bash
docker compose down
docker compose up -d
```

### Manual Pool Toggle
```bash
# Edit .env file
ACTIVE_POOL=green  # or blue
docker compose restart nginx
```

### View Real-time Logs
```bash
# Nginx access logs
docker compose logs -f nginx

# Alert watcher logs  
docker compose logs -f alert_watcher

# Application logs
docker compose logs -f app_blue app_green
```