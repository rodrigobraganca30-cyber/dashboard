import json, urllib.request

TOKEN = "EAALhAKnNtjYBRapdZCak0ACRIFZCLptZAVD7XIj6y4aAkcJrRorIh1FnAMhoQ6PVM6SAZBc7rGxfkptl2FgZBLU2JvHJ5Sz5Y4jhr5GBBslMN1ZAsLsIoNG8BhibHMuBLrL0k2arHWEMhx3ZBTK5ZAjUG0ku0lpVrhQIFFOdIpsb12xKfpoq9JZCUOYTmTmZAaWrq3ZBAZDZD"
WABA = "2148960206013081"

body_text = (
    "Ol\u00e1, {{1}}! Tudo bem?\n"
    "Sou da equipe t\u00e9cnica da Giga+.\n"
    "Gostari\u00edamos de agendar a retirada do equipamento instalado em seu endere\u00e7o, "
    "referente ao servi\u00e7o encerrado.\n"
    "Poderia nos informar sua disponibilidade para o t\u00e9cnico passar?\n"
    "Aguardamos seu retorno! \U0001f60a"
)

payload = {
    "name": "visita_retirada_equipamento",
    "category": "UTILITY",
    "language": "pt_BR",
    "components": [{
        "type": "BODY",
        "text": body_text,
        "example": {"body_text": [["Jose Silva"]]}
    }]
}

print("Enviando template...")
url = f"https://graph.facebook.com/v19.0/{WABA}/message_templates"
data = json.dumps(payload).encode("utf-8")
req = urllib.request.Request(url, data=data, headers={
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
})
try:
    with urllib.request.urlopen(req) as r:
        resp = json.loads(r.read())
        print("Resposta Meta:", json.dumps(resp, indent=2))
except urllib.error.HTTPError as e:
    print("ERRO:", json.dumps(json.loads(e.read()), indent=2))
