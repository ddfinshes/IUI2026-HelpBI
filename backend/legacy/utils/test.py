import http.client
import json




conn = http.client.HTTPSConnection("api.baicaigpt.cn")
payload = json.dumps({
   "model": "gpt-4o-mini",
   "messages":"prompt"
})
headers = {
   'Authorization': 'Bearer sk-UnAxAzyzsl06tpp9d9LCi44C7X4IyWg8QU9DQeWI8wKK6',
   'Content-Type': 'application/json'
}
conn.request("POST", "/v1/chat/completions", payload, headers)
res = conn.getresponse()
data = res.read()
print(data.decode("utf-8"))