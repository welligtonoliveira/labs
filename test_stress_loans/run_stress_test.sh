#!/bin/bash

# Configuration and defaults
DURATION="1m"
USERS="10"
SPAWN_RATE="2"
HOST="https://api.stg.noverde.com.br"
REPORT_NAME="report_$(date +%Y%m%d_%H%M%S).html"
MODE="docker" # default mode

# Help helper
show_help() {
  echo "Usage: ./run_stress_test.sh [options]"
  echo ""
  echo "Options:"
  echo "  -d, --duration <duration>  Duration of the test (e.g., 10m, 1h, 30s) (default: 1m)"
  echo "  -u, --users <count>        Number of concurrent users to spawn (default: 10)"
  echo "  -r, --rate <rate>          Spawn rate (users spawned per second) (default: 2)"
  echo "  -h, --host <url>           Target API base URL (default: https://api.stg.noverde.com.br)"
  echo "  -o, --output <filename>    Output filename for the HTML report (default: report_<timestamp>.html)"
  echo "  -l, --local                Run locally on the host instead of using Docker"
  echo "  --web                      Run in Web GUI mode (does not run headless, opens port 8089)"
  echo "  --help                     Show this help message"
  echo ""
  echo "Examples:"
  echo "  ./run_stress_test.sh -u 50 -r 5 -d 5m"
  echo "  ./run_stress_test.sh --web"
  echo "  ./run_stress_test.sh -l -u 100"
}

# Parse CLI arguments
WEB_MODE=false
while [[ $# -gt 0 ]]; do
  case "$1" in
    -d|--duration)
      DURATION="$2"
      shift 2
      ;;
    -u|--users)
      USERS="$2"
      shift 2
      ;;
    -r|--rate)
      SPAWN_RATE="$2"
      shift 2
      ;;
    -h|--host)
      HOST="$2"
      shift 2
      ;;
    -o|--output)
      REPORT_NAME="$2"
      shift 2
      ;;
    -l|--local)
      MODE="local"
      shift
      ;;
    --web)
      WEB_MODE=true
      shift
      ;;
    --help)
      show_help
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      show_help
      exit 1
      ;;
  esac
done

echo "=========================================================="
echo "          NOVERDE LOANS STRESS TEST RUNNER                "
echo "=========================================================="
echo "Target Host: $HOST"
echo "Execution Mode: $MODE"

if [ "$WEB_MODE" = true ]; then
  echo "Web GUI Mode: Enabled"
  echo "Locust Web UI will be available at http://localhost:8089"
  echo "Press Ctrl+C to terminate the test."
  echo "=========================================================="
  
  if [ "$MODE" = "docker" ]; then
    docker compose up
  else
    locust -f locustfile.py --host "$HOST"
  fi
else
  echo "Headless Mode: Enabled"
  echo "Concurrency: $USERS users"
  echo "Spawn Rate: $SPAWN_RATE users/sec"
  echo "Duration: $DURATION"
  echo "Output Report: $REPORT_NAME"
  echo "=========================================================="
  
  if [ "$MODE" = "docker" ]; then
    echo "Running stress test in Docker container..."
    docker compose run --rm locust \
      -f /mnt/locust/locustfile.py \
      --host "$HOST" \
      --headless \
      -u "$USERS" \
      -r "$SPAWN_RATE" \
      --run-time "$DURATION" \
      --html "/mnt/locust/$REPORT_NAME"
  else
    echo "Running stress test locally..."
    locust \
      -f locustfile.py \
      --host "$HOST" \
      --headless \
      -u "$USERS" \
      -r "$SPAWN_RATE" \
      --run-time "$DURATION" \
      --html "$REPORT_NAME"
  fi
  
  echo ""
  echo "=========================================================="
  echo "Test finished! Report saved successfully to:"
  echo "  $REPORT_NAME"
  echo "=========================================================="
fi
