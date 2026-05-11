# Family Album Deploy Guide

## 服务器部署步骤

### 1. 服务器准备工作

```bash
# 连接服务器
ssh root@你的服务器IP

# 安装依赖 (CentOS/RHEL)
yum update -y
yum install python3 python3-pip nginx git -y

# 安装依赖 (Ubuntu/Debian)
apt update -y
apt install python3 python3-pip nginx git -y

# 创建项目用户
useradd -m -s /bin/bash webuser
passwd webuser
usermod -aG wheel webuser
```

### 2. 本地准备项目文件

在本地项目目录执行：

```bash
# 1. 安装所有依赖到 requirements.txt
pip3 freeze > requirements.txt

# 2. 收集静态文件
python manage.py collectstatic

# 3. 打包项目 (在项目父目录执行)
cd ..
tar -czvf family_album.tar.gz Family_Album/
```

### 3. 上传项目到服务器

```bash
# 方法1: 使用 scp
scp family_album.tar.gz webuser@你的服务器IP:/home/webuser/

# 方法2: 使用 rsync
rsync -avz -e ssh ./Family_Album/ webuser@你的服务器IP:/home/webuser/Family_Album/
```

### 4. 服务器配置

```bash
# 以 webuser 登录
ssh webuser@你的服务器IP

# 解压项目
cd /home/webuser
tar -xzvf family_album.tar.gz

# 安装Python依赖
cd Family_Album
pip3 install -r requirements.txt

# 创建虚拟环境 (推荐)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 设置权限
chmod -R 755 /home/webuser/Family_Album
chown -R webuser:webuser /home/webuser/Family_Album
```

### 5. 配置 Nginx

```bash
# 创建 Nginx 配置文件
sudo vi /etc/nginx/conf.d/family_album.conf
```

写入以下内容：

```nginx
server {
    listen 80;
    server_name 你的域名或IP;

    # Django项目路径
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # 静态文件
    location /static/ {
        alias /home/webuser/Family_Album/staticfiles/;
        expires 30d;
    }

    # 媒体文件 (用户上传的照片)
    location /media/ {
        alias /home/webuser/Family_Album/media/;
        expires 7d;
    }
}
```

```bash
# 测试Nginx配置
sudo nginx -t

# 重启Nginx
sudo systemctl restart nginx
sudo systemctl enable nginx
```

### 6. 配置 Gunicorn (WSGI服务器)

```bash
# 安装 gunicorn
pip3 install gunicorn

# 创建 gunicorn 启动脚本
vi /home/webuser/Family_Album/start_gunicorn.sh
```

写入内容：

```bash
#!/bin/bash
source /home/webuser/Family_Album/venv/bin/activate
cd /home/webuser/Family_Album
gunicorn family_album.wsgi:application \
    --bind 127.0.0.1:8000 \
    --workers 3 \
    --timeout 120 \
    --access-logfile /home/webuser/Family_Album/logs/access.log \
    --error-logfile /home/webuser/Family_Album/logs/error.log \
    --daemon

PIDFILE=/home/webuser/Family_Album/gunicorn.pid

case "$1" in
start)
    if [ -f $PIDFILE ]; then
        echo "Gunicorn is already running"
    else
        source /home/webuser/Family_Album/venv/bin/activate
        cd /home/webuser/Family_Album
        gunicorn family_album.wsgi:application \
            --bind 127.0.0.1:8000 \
            --workers 3 \
            --timeout 120 \
            --access-logfile /home/webuser/Family_Album/logs/access.log \
            --error-logfile /home/webuser/Family_Album/logs/error.log \
            --daemon
        echo "Gunicorn started"
    fi
    ;;
stop)
    if [ -f $PIDFILE ]; then
        kill -9 $(cat $PIDFILE)
        rm -f $PIDFILE
        echo "Gunicorn stopped"
    else
        echo "Gunicorn is not running"
    fi
    ;;
restart)
    $0 stop
    sleep 2
    $0 start
    ;;
*)
    echo "Usage: $0 {start|stop|restart}"
    exit 1
esac
```

```bash
# 设置执行权限
chmod +x /home/webuser/Family_Album/start_gunicorn.sh

# 创建日志目录
mkdir -p /home/webuser/Family_Album/logs

# 启动 Gunicorn
./start_gunicorn.sh start
```

### 7. 配置防火墙

```bash
# CentOS/RHEL
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload

# 或直接开放端口
sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --reload
```

### 8. 配置 HTTPS (SSL证书)

```bash
# 安装 certbot
yum install certbot python3-certbot-nginx -y  # CentOS
# 或 apt install certbot python3-certbot-nginx -y  # Ubuntu

# 获取SSL证书
sudo certbot --nginx -d 你的域名

# 自动续期
sudo certbot renew --dry-run
```

### 9. 小程序后端配置

小程序需要调用你的 API，确保：

1. **Django settings.py 配置 CORS**：
```python
INSTALLED_APPS += ['corsheaders']
MIDDLEWARE += ['corsheaders.middleware.CorsMiddleware']
CORS_ALLOW_ALL_ORIGINS = True  # 小程序域名
```

2. **微信小程序后台配置**：
   - 登录微信公众平台
   - 开发管理 → 开发设置 → 服务器域名
   - 添加 request 合法域名：`https://你的域名`
   - 添加 uploadFile 合法域名：`https://你的域名/media/`

3. **小程序代码中调用 API**：
```javascript
wx.request({
  url: 'https://你的域名/api/photos/',
  success: function(res) {
    console.log(res.data);
  }
})
```

---

## 快速命令汇总

```bash
# 服务器上一键部署命令
cd /home/webuser/Family_Album
source venv/bin/activate
pip install -r requirements.txt
mkdir -p logs
./start_gunicorn.sh restart
sudo systemctl restart nginx
```

---

## 常见问题排查

```bash
# 查看Gunicorn日志
cat /home/webuser/Family_Album/logs/error.log

# 查看Nginx日志
tail -f /var/log/nginx/error.log

# 重启服务
./start_gunicorn.sh restart
sudo systemctl restart nginx

# 检查端口占用
netstat -tlnp | grep 8000
```
