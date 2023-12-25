# EPGHUB

Demo: [演示地址](https://demo.epghub.com/)

[EPG](https://zh.wikipedia.org/wiki/%E7%94%B5%E5%AD%90%E8%8A%82%E7%9B%AE%E6%8C%87%E5%8D%97) = **E**lectronic **P**rogramming **G**uide （电子节目表）

在当下，许多宽带运营商都提供了 [IPTV](https://zh.wikipedia.org/wiki/IPTV) 服务，可以通过家庭网络观看。但如果不使用运营商提供的机顶盒，而是使用自己的设备，例如在NAS、电视盒子、智能电视等设备上运行 IPTV 播放软件，除了取得播放源地址，还需要自己获取节目表。

但是节目表信息质量存在参差不齐，甚至需要综合多个来源，才能得到完整的信息。有的来源未必是标准的节目表格式。本项目就是为了解决这个问题。

本项目可从多个来源获取 EPG 节目表数据，分析整合后以多种格式提供 EPG 服务。提供了良好的可配置和可扩展性，部署也非常简单而灵活。

欢迎 [fork](https://github.com/riverscn/epghub/fork) 和提交 PR，一起完善本项目。

## 特色

- 采用 Python3 实现，区别于 iptv-org 的 Javascript。但想[转换刮削器](/epg/scraper/mytvsuper.py)是很容易的
- 通过 yaml 文件进行配置, 使用无数据库设计，递归复用上一次的生成的 xmltv 结果。区别于 supzhang 使用的 Django
- DIYP 接口采用静态页面实现，很容易 serve，低碳环保
- 添加刮削器是非常容易的，只需要增加刮削器 .py 文件，然后联动 yaml 里的配置即可
- 支持刮削器的 plugin，进行后期处理，弥补数据源的不足
- 支持部署到 Cloudflare Pages + Workers 或 docker 部署
- 自带更新调度器

## 输出格式

- XMLTV
- DIYP API

# 部署

## Docker

在本地部署，或者在服务器上部署，都可以使用 Docker。

1. [Fork](https://github.com/riverscn/epghub/fork) 本项目
2. `git clone` fork的项目并 `cd` 到项目目录
3. 将频道配置文件 [`/config/channels.yaml`](/config/channels.yaml) 拷贝到 `/docker/config` 目录再修改。也可以不用修改，一次运行会自动将默认的拷贝过去，以后再修改即可
4. （可选）修改 [`/docker-compose.yml`](/docker-compose.yml) 中的环境变量、服务端口、映射的目录等
   - 默认使用项目目录中的 ./docker 目录，可修改为自己需要的
   - 默认使用 6688 端口，可修改为其它空闲端口。但要注意必须同时修改文件中的所有端口号
5. `docker-compose up --build -d` 启动服务
6. 可通过部署机器的 `http://ip:port` 访问主页，获取节目信息和 xmltv 文件、DIYP 接口地址等

配置环境变量：

- `TZ`: 如果你在中国，设为 `Asia/Shanghai`
- `CRON_TRIGGER`: 可以参考这里的 [Cron 表达式](https://crontab.guru/)，例如 `0 0 * * *` 表示每天 UTC 时间 0 点执行（相当于北京时间 8 点，不受上面的时区设置影响）
- `XMLTV_URL`: 别动它

## Cloudflare Pages + Workers

1. [Fork](https://github.com/riverscn/epghub/fork) 本项目
2. 修改频道配置文件 [`/config/channels.yaml`](/config/channels.yaml)
3. 在 Cloudflare Pages 中创建项目，选择 Fork 的项目：
   - Build command = `poetry run python main.py`
   - Build output directory = `/web` 
4. Environment variables：
   - `TZ`: 如果你在中国，设为 `Asia/Shanghai`
5. 开始第一次部署，等待部署完成。访问部署的域名，成功的话就能看到主页了
6. 补充 Environment variables 以便自动更新
   - `CLOUDFLARE_API_TOKEN`: Cloudflare API Token，需要有[部署 Workers 的权限](https://developers.cloudflare.com/workers/wrangler/ci-cd/#1-authentication)
   - `DEPLOY_HOOK`: 刚刚部署的 Pages 的 [Deploy Hook](https://developers.cloudflare.com/pages/platform/deploy-hooks/)，可以在 Pages 的项目设置中找到
   - `CRON_TRIGGER`: 可以参考这里的 [Cron 表达式](https://crontab.guru/)，例如 `0 0 * * *` 表示每天 0 点执行（UTC 时间，比北京时间晚 8 小时）
   - `XMLTV_URL`: Pages 生成的 xmltv 文件的 URL，例如 `https://example.com/epg.xml`，改成对应的地址即可
7. 使用 curl -X POST `DEPLOY_HOOK 地址` [手动触发](https://developers.cloudflare.com/pages/platform/deploy-hooks/#using-your-deploy-hook)一次更新，检查是否成功
8. 可通过 Pages 的域名访问主页，获取节目信息和 xmltv 文件、DIYP 接口地址等

# 配置

## 频道配置

在 [`/config/channels.yaml`](/config/channels.yaml) 中：

```yaml
zhejiangtv:
  name:
    - 浙江卫视
  scraper:
    tvmao: ZJTV1
    cctv: zhejiang
  refresh: once
  recap: 7
  preview: 2
```

### 频道定义

`zhejiangtv` 是该频道的 id，它将会对应出现在输出的 [xmltv 格式](/xmltv.dtd)文件中。大部分支持 xmltv 格式的播放软件，会使用这个 id 来匹配频道列表 m3u8 文件中的频道 `tvg-id`。有些人喜欢用数字来作为频道 id，也是可以的，但就是没有英文容易辨认，容易混淆。

更多频道信息可参考 [`/reference`](/reference) 目录中的文件。

`name` 属性是该频道的显示名。需要注意的是，DIYP 使用显示名进行频道匹配。显示名支持多个，但 DIYP 接口只会使用第一个。

### EPG 数据源

[`/epg/scraper`](/epg/scraper) 目录中是 EPG 数据源的刮削程序。

可以指定多个 `scraper`，程序会依次尝试获取数据，直到成功或全部失败。在上面的例子中，`tvmao` 对应 [`/epg/scraper/tvmao.py`](/epg/scraper/tvmao.py) 这个刮削器。其后的参数 `ZJTV1` 是该频道在 `tvmao` 中的 id。对应的 id 通常可以在节目表的来源网站上获得，通常是 URL 中的路径或者参数。

增加自己的刮削器，只需要增加一个 .py 文件，定义好 `update()` 函数。然后在 [`/config/channels.yaml`](/config/channels.yaml) 中增加对应的配置即可。欢迎提交 PR。

### 刷新规则

`refresh` 属性是刷新频率。可以是 `once` 或 `today`。

- `once` 表示不刷新已经存在的节目，只是增补节目内容。这样的好处是更新很快，但如果来源的节目表发生了变动，不会得到更新
- `today` 表示在运行时刷新今天的内容，即使今天的节目表内容已经存在。这样的好处是可以得到最新的节目表，但是会增加刮削时间

### 回顾天数

`recap` 属性是回顾天数。即在今天之前的多少天的节目表内容会被保留。这样的好处是可以回看之前的节目表，但是会占用更多存储空间。

### 预览天数

`preview` 属性是预览天数。即在今天之后的多少天的节目表内容会被保留。这样的好处是可以预览之后的节目表，但是会占用更多存储空间和刮削时间。

### 插件

看一个例子

```yaml
cctv9:
  name:
    - CCTV9 纪录
  scraper:
    cctv: cctvjilu
  plugin: weibo_cctv9
  refresh: today
  recap: 7
  preview: 2
```

`plugin` 的属性是插件名。插件是对刮削器的后期处理。在上面的例子中，`weibo_cctv9` 对应 [`/epg/plugin/weibo_cctv9.py`](/epg/plugin/weibo_cctv9.py) 这个插件。插件的作用是对刮削器的结果进行处理，例如增加一些额外的信息。插件的定义也非常简单，只需要增加一个 .py 文件，定义好 `update()` 函数。然后在 [`/config/channels.yaml`](/config/channels.yaml) 中增加对应的配置即可。欢迎提交 PR。

CCTV9 的这个插件是用来从 CCTV9 官方微博话题 #每日央视纪录片精选# 中获取每日的纪录片信息，并且在已有的节目表中查找对应的节目，将纪录片的片名和节目信息对应起来，从而补全了 tv.cctv.com 节目表中缺失的片名信息。

例如来自 tv.cctv.com 的 CCTV9 节目表与该频道的官方微博对应：

    10:00	全景自然2023-317    ->  10:00   《隐秘王国》第2集
    10:58	寰宇视野2023-291    ->  11:00   《蓝色星球》第二季 第4集
    11:59	特别呈现2023-293    ->  12:00   《大敦煌》第3集

# 参考

本项目受 [supzhang/epg](https://github.com/supzhang/epg) 以及 [iptv-org/epg](https://github.com/iptv-org/epg) 项目启发。感谢！

本项目大量使用 ChatGPT 和 Github Copilot 协助生成的代码，事半功倍！包括本文，也是 Copilot 协助撰写的。

# 待改进

- [x] 用 apiflask 重写一个 server
- [ ] main.py 和 scheduler.py 写得比较潦草，将来可考虑合并为一个命令行程序，更优雅
- [ ] 支持命令行输出 scraper 的频道列表
- [ ] 部分代码还不够严谨清晰，需要重构
  - [ ] recap/preview/today 应该作为一个连续时间范围合并处理
  - [ ] 能够跨日期一次性获取的内容可以避免多次抓取
  - [ ] plugin 应该作为 post process 出现
- [ ] xmltv 多语言标记支持
