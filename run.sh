#!/bin/bash
# run.sh - Celery service manager

set -euo pipefail

VENV_DIR="venv"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$SCRIPT_DIR/logs/celery.pid"
LOG_DIR="$SCRIPT_DIR/logs"

# Logging functions
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
}

log_error() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $*" >&2
}

# Check if process is running
is_running() {
    local pid=$1
    kill -0 "$pid" 2>/dev/null
}

# Remove PID from file
remove_pid_from_file() {
    local name=$1
    local pid_file=$2
    if [ -f "$pid_file" ]; then
        sed -i "/^${name}:/d" "$pid_file" 2>/dev/null || \
        grep -v "^${name}:" "$pid_file" > "${pid_file}.tmp" && mv "${pid_file}.tmp" "$pid_file" 2>/dev/null || true
    fi
}

# Activate virtual environment
activate_venv() {
    if [ -f "$VENV_DIR/bin/activate" ]; then
        source "$VENV_DIR/bin/activate"
    elif [ -f "$VENV_DIR/Scripts/activate" ]; then
        source "$VENV_DIR/Scripts/activate"
    else
        log_error "Virtual environment not found"
        exit 1
    fi
}

# Check Redis connection
check_redis() {
    if command -v redis-cli &> /dev/null; then
        if redis-cli ping &> /dev/null 2>&1; then
            log "✓ Redis is running"
            return 0
        else
            log_error "Redis is not responding"
            log_error "Please start Redis before running Celery"
            return 1
        fi
    else
        log "⚠ Warning: redis-cli not found, skipping Redis check"
        return 0
    fi
}

# Start a service
start_service() {
    local name=$1
    local cmd=$2
    local log_file="$LOG_DIR/${name}.log"

    if [ -f "$PID_FILE" ] && grep -q "^${name}:" "$PID_FILE" 2>/dev/null; then
        local old_pid=$(grep "^${name}:" "$PID_FILE" | cut -d: -f2)
        if is_running "$old_pid"; then
            log "$name is already running (PID: $old_pid)"
            return 0
        fi
    fi

    log "Starting $name..."
    eval "$cmd >> $log_file 2>&1 &"
    local pid=$!
    sleep 2
    
    if ! is_running "$pid"; then
        log_error "$name failed to start. Check $log_file"
        return 1
    fi
    
    echo "${name}:${pid}" >> "$PID_FILE"
    log "$name started (PID: $pid)"
}

# Stop a service
stop_service() {
    local name=$1
    if [ ! -f "$PID_FILE" ]; then
        return 0
    fi

    local pid=$(grep "^${name}:" "$PID_FILE" 2>/dev/null | cut -d: -f2)
    if [ -n "$pid" ] && is_running "$pid"; then
        log "Stopping $name (PID: $pid)..."
        kill "$pid" 2>/dev/null || true
        sleep 2
        
        if is_running "$pid"; then
            log "Force stopping $name..."
            kill -9 "$pid" 2>/dev/null || true
        fi
        
        remove_pid_from_file "$name" "$PID_FILE"
        log "$name stopped"
    fi
}

# Check service status
check_status() {
    log "Checking Celery service status..."
    echo ""
    
    local services=("worker" "beat" "flower")
    local all_running=true

    for service in "${services[@]}"; do
        if [ -f "$PID_FILE" ]; then
            local pid=$(grep "^${service}:" "$PID_FILE" 2>/dev/null | cut -d: -f2)
            if [ -n "$pid" ] && is_running "$pid"; then
                echo "  ✓ Celery $service: RUNNING (PID: $pid)"
            else
                echo "  ✗ Celery $service: STOPPED"
                all_running=false
            fi
        else
            echo "  ✗ Celery $service: STOPPED"
            all_running=false
        fi
    done

    echo ""
    if [ "$all_running" = true ]; then
        log "All Celery services are running"
        echo "  Flower UI: http://localhost:5555"
    else
        log "Some Celery services are not running"
    fi
}

# View logs
view_logs() {
    local service=$1
    local log_file="$LOG_DIR/${service}.log"

    if [ ! -f "$log_file" ]; then
        log_error "Log file not found: $log_file"
        log "Available logs:"
        ls -1 "$LOG_DIR"/*.log 2>/dev/null || echo "  No log files found"
        return 1
    fi

    if [ "${2:-}" = "tail" ] || [ "${2:-}" = "follow" ]; then
        log "Following $service logs (Ctrl+C to stop)..."
        tail -f "$log_file"
    else
        cat "$log_file"
    fi
}

# Stop all Celery processes
stop_all_celery() {
    log "Stopping all Celery processes..."

    # Try graceful shutdown first
    pkill -f "celery.*worker" 2>/dev/null && sleep 2 || true
    pkill -f "celery.*beat" 2>/dev/null && sleep 2 || true
    pkill -f "celery.*flower" 2>/dev/null && sleep 2 || true

    # Force kill if still running
    pkill -9 -f "celery.*worker" 2>/dev/null || true
    pkill -9 -f "celery.*beat" 2>/dev/null || true
    pkill -9 -f "celery.*flower" 2>/dev/null || true

    # Clean PID file
    [ -f "$PID_FILE" ] && rm -f "$PID_FILE" || true

    log "All Celery processes stopped"
}

# Main commands
case "${1:-}" in
    start)
        activate_venv
        if ! check_redis; then
            exit 1
        fi
        mkdir -p "$LOG_DIR"
        cd "$SCRIPT_DIR"

        log "Starting Celery services..."
        start_service "worker" "celery -A src.main worker --loglevel=info --pool=solo"
        sleep 2
        start_service "beat" "celery -A src.main beat --loglevel=info"
        sleep 2
        start_service "flower" "celery -A src.main flower --port=5555 --address=0.0.0.0"
        sleep 2
        echo ""
        check_status
        ;;

    stop)
        log "Stopping Celery services..."
        stop_service "flower"
        stop_service "beat"
        stop_service "worker"

        # Always do cleanup to ensure all processes are stopped
        log "Cleaning up any remaining processes..."
        pkill -9 -f "celery.*worker" 2>/dev/null || true
        pkill -9 -f "celery.*beat" 2>/dev/null || true
        pkill -9 -f "celery.*flower" 2>/dev/null || true

        [ -f "$PID_FILE" ] && rm -f "$PID_FILE" || true

        log "All Celery services stopped"
        ;;

    kill)
        stop_all_celery
        ;;

    restart)
        log "Restarting Celery services..."
        $0 stop
        sleep 3
        $0 start
        ;;

    status)
        check_status
        ;;

    logs)
        if [ -z "${2:-}" ]; then
            log_error "Usage: ./run.sh logs {worker|beat|flower} [tail|follow]"
            echo ""
            echo "Available logs:"
            ls -1 "$LOG_DIR"/*.log 2>/dev/null | xargs -n1 basename || echo "  No log files found"
            exit 1
        fi
        view_logs "$2" "${3:-}"
        ;;

    worker)
        activate_venv
        if ! check_redis; then
            exit 1
        fi
        mkdir -p "$LOG_DIR"
        cd "$SCRIPT_DIR"
        start_service "worker" "celery -A src.main worker --loglevel=info --pool=solo"
        ;;

    beat)
        activate_venv
        if ! check_redis; then
            exit 1
        fi
        mkdir -p "$LOG_DIR"
        cd "$SCRIPT_DIR"
        start_service "beat" "celery -A src.main beat --loglevel=info"
        ;;

    flower)
        activate_venv
        if ! check_redis; then
            exit 1
        fi
        mkdir -p "$LOG_DIR"
        cd "$SCRIPT_DIR"
        start_service "flower" "celery -A src.main flower --port=5555 --address=0.0.0.0"
        ;;

    *)
        echo "Usage: ./run.sh {start|stop|restart|status|logs|kill|worker|beat|flower}"
        echo ""
        echo "Commands:"
        echo "  start    - Start worker, beat, and flower"
        echo "  stop     - Stop all services"
        echo "  restart  - Restart all services"
        echo "  status   - Check service status"
        echo "  logs     - View logs: ./run.sh logs {worker|beat|flower} [tail|follow]"
        echo "  kill     - Force stop all Celery processes"
        echo "  worker   - Start worker only"
        echo "  beat     - Start beat only"
        echo "  flower   - Start flower only"
        exit 1
        ;;
esac