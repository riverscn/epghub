import requests

# 请求头
headers = {
	"User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Mobile Safari/537.36",
	"accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
	"accept-encoding": "gzip, deflate, br",
}

# 请求地址
API_ENDPOINT = 'https://m.weibo.cn/api/container/getIndex'

def search(keyword: str, page: int = 1) -> list:
	"""
	Search weibo by keyword.

	Args:
		keyword (str): The keyword to search.
		page (int): The page number to search.

	Returns:
		list: The search result.
	"""
	# 请求参数
	params = {
		"containerid": "100103type=1&q={}".format(keyword),
		"page_type": "searchall",
		"page": page
	}

	# 发送请求
	try:
		r = requests.get(API_ENDPOINT, headers=headers, params=params, timeout=5)
	except:
		return []

	# 解析json数据
	cards = r.json()["data"]["cards"]

	# 提取微博数据
	weibo_list = []
	for card in cards:
		if "mblog" in card["card_group"][0]:
			weibo_list.append(card["card_group"][0]['mblog'])

	return weibo_list