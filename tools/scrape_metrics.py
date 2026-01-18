import time, urllib.request

time.sleep(2)
try:
    body = urllib.request.urlopen('http://127.0.0.1:9091/metrics', timeout=5).read().decode('utf-8')
    print(body)
except Exception as e:
    print('SCRAPE FAILED:', repr(e))
