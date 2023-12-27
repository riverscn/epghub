from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
import time
from datetime import timezone
import os

CRON_TRIGGER = os.getenv("CRON_TRIGGER", "0 0 * * *")


def my_task():
    print("CRON task：", time.strftime("%Y-%m-%d %H:%M:%S"))
    os.system("poetry run python main.py")


# 创建一个调度器
scheduler = BlockingScheduler()

# 使用CronTrigger来定义Cron表达式
cron_trigger = CronTrigger.from_crontab(CRON_TRIGGER, timezone.utc)

# 添加任务和触发器
scheduler.add_job(my_task, cron_trigger)

# 启动调度器
print("Start api server...")
PORT = os.getenv("PORT", "6688")
os.system("poetry run python main.py")
print(f"Start scheduler with cron trigger: {CRON_TRIGGER}", flush=True)
scheduler.start()