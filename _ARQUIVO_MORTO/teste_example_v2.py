import json, urllib.request

TOKEN = "EAALhAKnNtjYBRapdZCak0ACRIFZCLptZAVD7XIj6y4aAkcJrRorIh1FnAMhoQ6PVM6SAZBc7rGxfkptl2FgZBLU2JvHJ5Sz5Y4jhr5GBBslMN1ZAsLsIoNG8BhibHMuBLrL0k2arHWEMhx3ZBTK5ZAjUG0ku0lpVrhQIFFOdIpsb12xKfpoq9JZCUOYTmTmZAaWrq3ZBAZDZD"
WABA = "2148960206013081"

body_text = "Ola {{1}} teste verificacao example."

import re
vars_found = re.findall(r'\{\{[0-9]+\}\}', body_text)
example_vals = ['exemplo' + str(i+1) for i in range(len(vars_found))] if vars_found else ['exemplo1']

payload = {
    "name": "teste_example_v2",
    "category": "UTILITY",
    "language": "pt_BR",
    "components": [{
        "type": "BODY",
        "text": body_text,
        "example": {"body_text": [example_vals]}
    }]
}

print("Payload enviado:")
print(json.dumps(payload, indent=2, ensure_ascii=False))

url = f"https://graph.facebook.com/v19.0/{WABA}/message_templates"
data = json.dumps(payload).encode("utf-8")
req = urllib.request.Request(url, data=data, headers={
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
})
try:
    with urllib.request.urlopen(req) as r:
        resp = json.loads(r.read())
        print("\nResposta Meta:")
        print(json.dumps(resp, indent=2))
except urllib.error.HTTPError as e:
    print("\nERRO Meta:")
    print(json.dumps(json.loads(e.read()), indent=2))
