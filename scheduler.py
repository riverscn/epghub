from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
import time
from datetime import timezone
import os
import threading

CRON_TRIGGER = os.getenv("CRON_TRIGGER", "0 0 * * *")


def my_task():
    print("CRON task：", time.strftime("%Y-%m-%d %H:%M:%S"))
    os.system("poetry run python main.py")

class IndexServer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        PORT = os.getenv("PORT", "6688")
        os.system(f"gunicorn --workers {os.cpu_count()} --bind 0.0.0.0:{PORT} --access-logfile - api.app:app")

# 创建一个调度器
scheduler = BlockingScheduler()

# 使用CronTrigger来定义Cron表达式
cron_trigger = CronTrigger.from_crontab(CRON_TRIGGER, timezone.utc)

# 添加任务和触发器
scheduler.add_job(my_task, cron_trigger)

# 启动调度器
print("Start api server...")
threadIndex = IndexServer()
threadIndex.start()
time.sleep(3)
os.system("poetry run python main.py")
print(f"Start scheduler with cron trigger: {CRON_TRIGGER}", flush=True)
scheduler.start()