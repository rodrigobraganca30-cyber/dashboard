const fs = require('fs');
const filepath = '/docker/whatsapp-agenda/backend/index.js';
let content = fs.readFileSync(filepath, 'utf-8');

const old = `                  jarvisHandled = true;
                  log('info', 'Jarvis processou', {
                    phone,
                    clientId,
                    tools: resp.data.tools_used || [],
                    provider: resp.data.provider
                  });`;

const replacement = `                  jarvisHandled = true;
                  log('info', 'Jarvis processou', {
                    phone,
                    clientId,
                    tools: resp.data.tools_used || [],
                    provider: resp.data.provider
                  });

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
                  }`;

if (content.includes(old)) {
  content = content.replace(old, replacement);
  fs.writeFileSync(filepath, content);
  console.log('OK - Jarvis agora salva respostas no Redis');
} else {
  console.log('ERRO - bloco nao encontrado');
}
