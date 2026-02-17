# Rate Limiting

## Overview

The Self-Growth API implements rate limiting at the API Gateway level to protect against abuse and ensure fair resource allocation across all users.

## Rate Limit Configuration

### Default Limits

- **Burst Limit**: 100 concurrent requests
- **Rate Limit**: 50 requests per second (steady state)

These limits apply globally across the entire API for all authenticated users.

### What Happens When Rate Limited

When you exceed the rate limit, the API returns:

**HTTP Status**: `429 Too Many Requests`

**Response Body**:

```json
{
  "message": "Too Many Requests"
}
```

### Retry Strategy

When you receive a 429 response:

1. **Exponential Backoff**: Wait before retrying
   - First retry: Wait 1 second
   - Second retry: Wait 2 seconds
   - Third retry: Wait 4 seconds
   - Max wait: 32 seconds

2. **Jitter**: Add random delay (0-1 second) to prevent thundering herd

3. **Circuit Breaker**: After 5 consecutive 429s, pause requests for 60 seconds

### Example Retry Logic (JavaScript)

```javascript
async function apiCallWithRetry(url, options, maxRetries = 3) {
  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      const response = await fetch(url, options);

      if (response.status === 429) {
        if (attempt === maxRetries) {
          throw new Error("Rate limit exceeded after max retries");
        }

        // Exponential backoff with jitter
        const backoffMs = Math.pow(2, attempt) * 1000 + Math.random() * 1000;
        console.log(`Rate limited. Retrying in ${backoffMs}ms...`);
        await new Promise((resolve) => setTimeout(resolve, backoffMs));
        continue;
      }

      return response;
    } catch (error) {
      if (attempt === maxRetries) throw error;
    }
  }
}
```

## Monitoring Rate Limits

### CloudWatch Metrics

The following metrics are available in CloudWatch:

1. **4XXError**: Includes 429 rate limit responses
   - Namespace: `AWS/ApiGateway`
   - Dimensions: `ApiId`, `Stage`

2. **Count**: Total number of API requests
   - Namespace: `AWS/ApiGateway`
   - Dimensions: `ApiId`, `Stage`

3. **Latency**: API response time
   - Namespace: `AWS/ApiGateway`
   - Dimensions: `ApiId`, `Stage`

### CloudWatch Alarms

Two alarms are configured:

1. **4xx Errors Alarm**: Triggers when 4xx errors exceed 50 in 5 minutes
2. **5xx Errors Alarm**: Triggers when 5xx errors exceed 10 in 5 minutes

### Access Logs

API Gateway access logs are stored in CloudWatch Logs:

**Log Group**: `/aws/apigateway/self-growth-{environment}`

**Log Format** (JSON):

```json
{
  "requestId": "abc123",
  "ip": "192.168.1.1",
  "requestTime": "2026-02-16T10:30:00Z",
  "httpMethod": "POST",
  "routeKey": "POST /todos",
  "status": 429,
  "protocol": "HTTP/1.1",
  "responseLength": 45,
  "errorMessage": "Too Many Requests",
  "errorType": "ThrottlingException"
}
```

## Best Practices

### For Mobile Apps

1. **Implement Retry Logic**: Always retry 429 responses with exponential backoff
2. **Cache Responses**: Cache GET requests locally to reduce API calls
3. **Batch Operations**: Group multiple operations when possible
4. **Background Sync**: Use background sync for non-urgent operations
5. **Request Deduplication**: Prevent duplicate requests from user actions

### For Backend Integration

1. **Connection Pooling**: Reuse HTTP connections
2. **Request Queuing**: Queue requests and process at controlled rate
3. **Circuit Breaker**: Stop sending requests after repeated failures
4. **Monitoring**: Track 429 responses and adjust client behavior

## Adjusting Rate Limits

Rate limits can be adjusted in Terraform:

**File**: `terraform/modules/api/self_growth_api/variables.tf`

```hcl
variable "throttling_burst_limit" {
  type    = number
  default = 100  # Adjust this value
}

variable "throttling_rate_limit" {
  type    = number
  default = 50   # Adjust this value
}
```

After changing values:

```bash
cd terraform
terraform plan
terraform apply
```

## Per-User Rate Limiting (Future)

The current implementation uses API Gateway throttling which applies globally. For per-user rate limiting:

**Option 1: API Gateway Usage Plans**

- Create usage plans with API keys
- Assign different limits per user tier
- Requires API key management

**Option 2: DynamoDB-Based Tracking**

- Track request counts per user in DynamoDB
- Implement sliding window algorithm
- More flexible but adds latency

**Option 3: Redis/ElastiCache**

- Use Redis for fast rate limit tracking
- Sliding window or token bucket algorithm
- Best performance but adds infrastructure cost

For MVP, global API Gateway throttling is sufficient.

## Troubleshooting

### High 429 Rate

**Symptoms**: Many 429 responses in logs

**Possible Causes**:

1. Legitimate traffic spike (success!)
2. Client not implementing retry logic
3. Client making too many requests
4. DDoS attack or abuse

**Solutions**:

1. Increase rate limits if legitimate traffic
2. Implement client-side retry logic
3. Add per-user tracking to identify abusers
4. Enable AWS WAF for DDoS protection

### False Positives

**Symptoms**: Legitimate users getting rate limited

**Possible Causes**:

1. Rate limits too low for expected traffic
2. Burst traffic from mobile app sync
3. Multiple users behind same IP (NAT)

**Solutions**:

1. Increase burst limit
2. Implement request queuing in mobile app
3. Consider per-user rate limiting

## Related Documentation

- [API Reference](./api-reference.md)
- [Architecture Overview](./architecture-overview.md)
- [Error Handling](./error-handling-transformation.md)
