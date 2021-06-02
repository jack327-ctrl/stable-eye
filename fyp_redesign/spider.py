import requests

headers = {
    'Connection': 'keep-alive',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
    'Accept': '*/*',
    'Origin': 'https://www.dandanzan.com',
    'Sec-Fetch-Site': 'cross-site',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Dest': 'empty',
    'Referer': 'https://www.dandanzan.com/',
    'Accept-Language': 'zh',
    'If-None-Match': '^\\^5c6e6826-159cc8^\\^',
    'If-Modified-Since': 'Thu, 21 Feb 2019 08:58:14 GMT',
}

response = requests.get('https://www.183757.com/20190221/b9XdREAH/b9XdREAH016.ts', headers=headers)
