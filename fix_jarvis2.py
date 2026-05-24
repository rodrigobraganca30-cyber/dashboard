f = '/docker/whatsapp-agenda/backend/index.js'
content = open(f, 'r', encoding='utf-8').read()

# O marcador unico apos o log do Jarvis
marker = "log('info', 'Jarvis processou', {"
idx = content.find(marker)
if idx < 0:
    marker = 'log("info", "Jarvis processou", {'
    idx = content.find(marker)

if idx < 0:
    print("MARKER NOT FOUND")
    # Debug: mostrar linhas proximas de jarvisHandled
    for i, line in enumerate(content.split('\n')):
        if 'Jarvis processou' in line:
            print(f"Line {i+1}: {line.strip()}")
else:
    # Encontrar o final do bloco log(...});
    # Buscar a partir do marker, o primeiro ");" que fecha o log
    search_start = idx
    # Procurar "provider: resp.data.provider" e depois "})" e depois ";"
    provider_idx = content.find('provider: resp.data.provider', search_start)
    if provider_idx < 0:
        print("provider line not found")
    else:
        # Achar o "})" apos provider
        close_idx = content.find('});', provider_idx)
        if close_idx < 0:
            print("close not found")
        else:
            insert_point = close_idx + 3  # after ");"
            
            new_code = """

                  // Salvar resposta do Jarvis no historico de mensagens
                  if (resp.data.response) {
                    const jarvisText = resp.data.response;
                    await appendMsg(phone, {
                      from: 'me',
                      text: jarvisText,
                      ts: Date.now(),
                      instance: 'Jarvis_Auto',
                      auto: true
                    });
                    log('info', 'Jarvis resposta salva', { phone, text: jarvisText.slice(0, 60) });
                  }"""
            
            content = content[:insert_point] + new_code + content[insert_point:]
            open(f, 'w', encoding='utf-8').write(content)
            print("OK - Codigo inserido apos log do Jarvis")
