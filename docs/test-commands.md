## Analyze Lamdba Manual Invoke command

```
aws lambda invoke \
  --function-name contract-guard-analyze-dev \
  --payload fileb://./test-event.json \
  response.json
```