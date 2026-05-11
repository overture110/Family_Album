#!/bin/bash

# Family Album 部署启动脚本

PROJECT_DIR="/home/webuser/Family_Album"
VENV_DIR="$PROJECT_DIR/venv"
PIDFILE="$PROJECT_DIR/gunicorn.pid"
LOGDIR="$PROJECT_DIR/logs"

activate_venv() {
    source "$VENV_DIR/bin/activate"
}

start() {
    echo "启动 Gunicorn..."
    if [ -f $PIDFILE ]; then
        echo "Gunicorn 已在运行"
    else
        activate_venv
        cd $PROJECT_DIR
        mkdir -p $LOGDIR
        gunicorn family_album.wsgi:application \
            --bind 127.0.0.1:8000 \
            --workers 3 \
            --timeout 120 \
            --access-logfile $LOGDIR/access.log \
            --error-logfile $LOGDIR/error.log \
            --daemon
        echo $! > $PIDFILE
        echo "Gunicorn 已启动，PID: $(cat $PIDFILE)"
    fi
}

stop() {
    echo "停止 Gunicorn..."
    if [ -f $PIDFILE ]; then
        kill -9 $(cat $PIDFILE)
        rm -f $PIDFILE
        echo "Gunicorn 已停止"
    else
        echo "Gunicorn 未运行"
    fi
}

restart() {
    stop
    sleep 2
    start
}

status() {
    if [ -f $PIDFILE ]; then
        PID=$(cat $PIDFILE)
        if ps -p $PID > /dev/null; then
            echo "Gunicorn 正在运行，PID: $PID"
        else
            echo "PID文件存在但进程已停止"
            rm -f $PIDFILE
        fi
    else
        echo "Gunicorn 未运行"
    fi
}

case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    status)
        status
        ;;
    *)
        echo "用法: $0 {start|stop|restart|status}"
        exit 1
esac

exit 0
