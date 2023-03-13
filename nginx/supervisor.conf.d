[program:quotes_api]
directory=/api
command=/api/docker-compose up --build
autostart=true
autorestart=true
stderr_logfile=/var/log/quotes_api/quotes_api.err.log
stdout_logfile=/var/log/quotes_api/quotes_api.out.log
