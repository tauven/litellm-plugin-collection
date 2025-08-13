# Automated Integration Test for RemoveNamePlugin

# 0. Ensure a clean environment by removing old containers and volumes
echo "Cleaning up previous run (if any)..."
docker-compose down --volumes
docker-compose rm -f -s -v

# 1. Start Docker Compose in detached mode
echo "Starting Docker services..."
docker-compose up -d --force-recreate
if ($LASTEXITCODE -ne 0) {
    echo "Failed to start Docker services. Aborting."
    exit 1
}

# Wait for the vllm-chat service to be ready
echo "Waiting for vLLM service to initialize..."
$max_wait = 300 # Maximum wait time in seconds (5 minutes)
$wait_interval = 10 # Check every 10 seconds
$waited_time = 0
$startup_complete = $false

while ($waited_time -lt $max_wait) {
    $logs = docker-compose logs vllm-chat
    if ($logs -match "Application startup complete") {
        echo "vLLM service started successfully."
        $startup_complete = $true
        break
    }
    Start-Sleep -Seconds $wait_interval
    $waited_time += $wait_interval
    echo "Still waiting for vLLM service... ($waited_time / $max_wait seconds)"
}

if (-not $startup_complete) {
    echo "Timed out waiting for vLLM service to start. Aborting."
    docker-compose down
    exit 1
}


# 2. Send a test request with a 'name' field
echo "Sending test request..."
$requestBody = @{
    model = "chat"
    messages = @(
        @{
            role = "user"
            content = "This is a test message."
            name = "test-user"
        }
    )
} | ConvertTo-Json

try {
    Invoke-RestMethod -Uri "http://localhost:4000/chat/completions" -Method Post -Body $requestBody -ContentType "application/json"
} catch {
    # It's okay if this fails, we just need the log output
    echo "Request sent. Continuing to log verification."
}

# Give time for logs to be written
Start-Sleep -Seconds 5

# 3. Verify the logs
$exitCode = 0
echo "Verifying litellm logs..."
$litellm_logs = docker-compose logs litellm

# Verification 1: Check for Pre-API call log
if ($litellm_logs -match "Pre-API Call for model: chat") {
    echo "TEST PASSED: Pre-API call hook was triggered."
} else {
    echo "TEST FAILED: Pre-API call hook was not triggered."
    $exitCode = 1
}

# Verification 2: Check if 'name' field is removed
if ($litellm_logs -match "name") {
    echo "TEST FAILED: 'name' field was found in the litellm logs."
    $exitCode = 1
} else {
    echo "TEST PASSED: 'name' field was not found in the litellm logs."
}

echo "Verifying vllm-chat logs..."
$vllm_logs = docker-compose logs vllm-chat
if ($vllm_logs -match "POST /v1/chat/completions") {
    echo "TEST PASSED: vLLM service received the POST request."
} else {
    echo "TEST FAILED: vLLM service did not receive the POST request."
    $exitCode = 1
}

# 4. Stop Docker Compose services
echo "Stopping Docker services..."
docker-compose down --volumes

exit $exitCode