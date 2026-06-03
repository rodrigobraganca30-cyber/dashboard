import json, urllib.request

TOKEN = "EAALhAKnNtjYBRapdZCak0ACRIFZCLptZAVD7XIj6y4aAkcJrRorIh1FnAMhoQ6PVM6SAZBc7rGxfkptl2FgZBLU2JvHJ5Sz5Y4jhr5GBBslMN1ZAsLsIoNG8BhibHMuBLrL0k2arHWEMhx3ZBTK5ZAjUG0ku0lpVrhQIFFOdIpsb12xKfpoq9JZCUOYTmTmZAaWrq3ZBAZDZD"
WABA = "2148960206013081"

payload = {
    "name": "recolhimento_aparelho",
    "category": "UTILITY",
    "language": "pt_BR",
    "components": [{
        "type": "BODY",
        "text": "Ola, {{1}}! Tudo bem?\n\nIdentificamos que o equipamento roteador ainda nao foi devolvido ao nosso tecnico.\n\nSolicitamos, por gentileza, que informe a melhor data para realizarmos a retirada do aparelho.\n\nAguardamos seu retorno.",
        "example": {
            "body_text": [["Jose Silva"]]
        }
    }]
}

url = f"https://graph.facebook.com/v19.0/{WABA}/message_templates"
data = json.dumps(payload).encode("utf-8")
req = urllib.request.Request(url, data=data, headers={
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
})
try:
    with urllib.request.urlopen(req) as r:
        print(json.dumps(json.loads(r.read()), indent=2))
except urllib.error.HTTPError as e:
    print("ERRO:", json.dumps(json.loads(e.read()), indent=2))
