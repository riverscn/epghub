from jinja2 import Environment, FileSystemLoader
from epg import utils
from epg.generator import xmltv
from epg.generator import diyp
from epg.scraper import __xmltv
from lxml import etree
from datetime import datetime, timezone
from croniter import croniter
import os
import shutil

CF_PAGES = os.getenv('CF_PAGES')
CF_PAGES_URL = os.getenv('CF_PAGES_URL')
DEPLOY_HOOK = os.getenv('DEPLOY_HOOK')
CLOUDFLARE_API_TOKEN = os.getenv('CLOUDFLARE_API_TOKEN')
XMLTV_URL = os.getenv('XMLTV_URL','')
TZ = os.getenv('TZ')
if TZ == None:
    print("!!!Please set TZ environment variables to define timezone or it will use system timezone by default!!!")
CRON_TRIGGER = os.getenv('CRON_TRIGGER', '0 0 * * *')
next_cron_time = croniter(CRON_TRIGGER, datetime.now(timezone.utc)).get_next(
    datetime).replace(tzinfo=timezone.utc).astimezone()

dtd = etree.DTD(open('xmltv.dtd', 'r'))

now = datetime.now()
current_timezone = now.astimezone().tzinfo
timezone_name = current_timezone.tzname(now)
timezone_offset = now.astimezone().strftime('%z')
print("use timezone:", timezone_name, f"UTC{timezone_offset}", flush=True)

config_path = os.path.join(os.getcwd(), 'config', 'channels.yaml')
epg_path = os.path.join(os.getcwd(), 'web', 'epg.xml')
if not os.path.exists(os.path.join(os.getcwd(), 'web')):
    os.mkdir(os.path.join(os.getcwd(), 'web'))

channels = utils.load_config(config_path)

if XMLTV_URL == '':
    xml_channels = []
    print("!!!Please set XMLTV_URL environment variables to reuse XML!!!")
else:
    print("reuse XML:", XMLTV_URL, flush=True)
    xml_channels = __xmltv.get_channels(XMLTV_URL, dtd)
    # Reuse channels
    if xml_channels != []:
        xml_result = utils.copy_channels(channels, xml_channels)
        num_reuse_channels = xml_result[0]
        xml_dates = xml_result[1]
        min_xml_date = min(xml_dates)
        max_xml_date = max(xml_dates)
        print(
            f"number of reused channels: {num_reuse_channels}/{len(channels)} from {min_xml_date} to {max_xml_date}", flush=True)

print("refreshing...")

num_refresh_channels = 0
for channel in channels:
    if utils.update_channel_full(channel, num_refresh_channels):
        num_refresh_channels += 1

print(
    f"number of refreshed channels: {num_refresh_channels}/{len(channels)}", flush=True)

print("deploying...", flush=True)
print("file path:", epg_path, flush=True)
xmltv.write(epg_path, channels, "epghub")

xml = open(epg_path, 'rb')
root = etree.XML(xml.read())
valid = dtd.validate(root)
if not valid:
    print(dtd.error_log.filter_from_errors()[0])

diyp.write(os.path.join(os.getcwd(), 'web', 'diyp_files'), channels)

# Load the template
templateLoader = FileSystemLoader(
    searchpath=os.path.join(os.getcwd(), 'templates'))
env = Environment(loader=templateLoader)
template = env.get_template("index.html.jinja2")

title = "EPG"
channel_list = [channel.metadata["name"][0] for channel in channels]
first_channel = channel_list[0]
channel_list = channel_list[1:]
# Convert CRON_TRIGGER next cron time to datetime type
next_update_time = next_cron_time

# Render the template with the list
rendered_html = template.render(
    title=title, channel_list=channel_list, first_channel=first_channel, num_refresh_channels=num_refresh_channels, num_channels=len(channels), last_update_time=datetime.now().astimezone().isoformat(timespec='seconds'), next_update_time=next_update_time, update_trigger=CRON_TRIGGER, timezone_offset=timezone_offset)

open(os.path.join(os.getcwd(), 'web', 'index.html'), 'w').write(rendered_html)
shutil.copyfile(os.path.join(os.getcwd(), 'templates', '404.html'), os.path.join(os.getcwd(), 'web', '404.html'))
shutil.copyfile(os.path.join(os.getcwd(), 'templates', '404.json'), os.path.join(os.getcwd(), 'web', '404.json'))
shutil.copyfile(os.path.join(os.getcwd(), 'templates', 'robots.txt'), os.path.join(os.getcwd(), 'web', 'robots.txt'))

if CF_PAGES != None:
    if CLOUDFLARE_API_TOKEN == None:
        print("!!!Please set DEPLOY_HOOK environment variables to deploy automatically!!!")
    if DEPLOY_HOOK == None:
        print("!!!Please set CLOUDFLARE_API_TOKEN environment variables to deploy automatically!!!")
    if DEPLOY_HOOK != None and CLOUDFLARE_API_TOKEN != None:
        cmd = f'cd workers && npx --yes wrangler deploy --var DEPLOY_HOOK:{DEPLOY_HOOK} --triggers \"{CRON_TRIGGER}\"'
        # print(cmd)
        os.system(cmd)
