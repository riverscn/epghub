export async function onRequest(context) {
  const { searchParams, protocol, host, pathname } = new URL(context.request.url)
  const channel_name = decodeURIComponent(searchParams.get('ch'))
  const date_str = decodeURIComponent(searchParams.get('date'))
  const url = encodeURI(`${protocol}//${host}${pathname}_files/${channel_name}/${date_str}.json`)

  /**
   * gatherResponse awaits and returns a response body as a string.
   * Use await gatherResponse(..) in an async function to get the response body
   * @param {Response} response
   */
  async function gatherResponse(response) {
    const { headers } = response;
    const contentType = headers.get("content-type") || "";
    if (contentType.includes("application/json")) {
      return JSON.stringify(await response.json());
    }
    return response.text();
  }

  const init = {
    headers: {
      "content-type": "application/json;charset=UTF-8",
    },
  };

  const response = await fetch(url);
  var result = await gatherResponse(response);
  if (response.status != 200) {
    const resJson = {
      "channel_name": channel_name,
      "date": date_str,
      "epg_data": []
    }
    // Fill epg_data with the specified pattern
    for (let hour = 0; hour < 24; hour++) {
      const startHour = hour.toString().padStart(2, '0');
      // const endHour = (hour + 1).toString().padStart(2, '0');

      const epgItem = {
        "start": startHour + ":00",
        "end": startHour + ":59",
        "title": "精彩节目-暂未提供节目预告信息",
        "desc": ""
      };
      resJson.epg_data.push(epgItem);
    };
    result = JSON.stringify(resJson);
  };
  // 将 response status 和 statusText 添加到 init 对象
  // init.status = response.status;
  // init.statusText = response.statusText;
  // 不建议这么做，因为DIYP会丢弃404的响应内容
  return new Response(result, init);
}