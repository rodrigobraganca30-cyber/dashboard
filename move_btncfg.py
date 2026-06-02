import paramiko, os, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
pkey = paramiko.RSAKey.from_private_key_file(os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'))
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('187.77.240.87', username='root', pkey=pkey)

move_script = r'''
import re

html = open('/docker/dashboard/html/index.html', 'r', encoding='utf-8').read()

# 1. Extrair o bloco btn-cfg completo (do <!-- BOTÃO CONFIG EDITOR --> até <!-- FIM BOTÃO CONFIG EDITOR -->)
start_marker = '<!-- BOTÃO CONFIG EDITOR (injetado) -->'
end_marker = '<!-- FIM BOTÃO CONFIG EDITOR -->'

start_idx = html.index(start_marker)
end_idx = html.index(end_marker) + len(end_marker)

btn_block = html[start_idx:end_idx]
print(f'[1] Bloco extraído: {len(btn_block)} bytes')

# 2. Remover da posição atual
html = html[:start_idx] + html[end_idx:]
print(f'[2] Bloco removido da posição atual')

# 3. Encontrar o ponto de inserção DENTRO do wa-disparo
# Inserir logo após "Histórico de Campanhas" div fechando
# A estrutura é:
#   <div class="chart-card" id="wa-campaigns" ...>...</div>
#     </div>    ← fecha grid-2 coluna direita
#   </div>      ← fecha grid-2
# </div>        ← fecha wa-disparo
# Precisamos inserir ANTES do fechamento do wa-disparo

# Encontrar wa-disparo
wa_disparo_start = html.index('id="wa-disparo"')
# Encontrar wa-campaigns dentro do disparo
wa_campaigns = html.index('id="wa-campaigns"', wa_disparo_start)

# Encontrar <!-- SUB: Configuração -->
sub_config = html.index('<!-- SUB: Configura')

# O wa-disparo fecha com </div> antes de <!-- SUB: Configuração -->
# Vamos procurar os 3 </div> antes de <!-- SUB: Configuração -->
# O padrão é: </div>\n  </div>\n</div>\n\n<!-- SUB: Configuração -->
before_config = html[:sub_config].rstrip()

# Encontrar onde inserir: antes dos últimos 3 </div> que fecham wa-disparo
# Procurar de trás pra frente a partir de sub_config
search_area = html[wa_campaigns:sub_config]

# Encontrar o último </div> do wa-campaigns e depois os 3 </div> de fechamento
# Inserir DENTRO do wa-disparo, logo após o wa-campaigns card
# Vamos inserir antes da sequência final de </div> que fecha wa-disparo
# Encontrar "Nenhuma campanha ainda" e depois os </div> de fechamento

insert_anchor = 'Nenhuma campanha ainda'
anchor_pos = html.index(insert_anchor, wa_campaigns)
# Avançar até o </div> que fecha o wa-campaigns
close1 = html.index('</div>', anchor_pos) + len('</div>')  # fecha o texto
# Os próximos </div> fecham:
# 1. wa-campaigns card
# 2. coluna direita do grid-2  
# 3. grid-2
# Queremos inserir ANTES do 4º </div> que fecha wa-disparo

# Contar os </div> após wa-campaigns
pos = close1
for i in range(3):
    pos = html.index('</div>', pos) + len('</div>')

# pos agora está logo após o 3º </div> (que fecha grid-2)
# O próximo </div> fecha wa-disparo — inserir ANTES dele

# Verificar se há espaço/newlines
while pos < len(html) and html[pos] in '\r\n \t':
    pos += 1

# Inserir AQUI (antes do </div> que fecha wa-disparo)
html = html[:pos] + '\n' + btn_block + '\n' + html[pos:]
print(f'[3] Bloco inserido dentro do wa-disparo (posição {pos})')

# 4. Verificar
check_disparo = html.index('id="wa-disparo"')
check_config = html.index('<!-- SUB: Configura')
check_btncfg = html.index('btn-cfg-section')

inside = check_disparo < check_btncfg < check_config
print(f'[4] btn-cfg está dentro do wa-disparo? {inside}')
print(f'    wa-disparo: {check_disparo}')
print(f'    btn-cfg: {check_btncfg}')
print(f'    SUB Config: {check_config}')

# 5. Salvar
open('/docker/dashboard/html/index.html', 'w', encoding='utf-8').write(html)
print(f'[5] HTML salvo ({len(html)} bytes)')
'''

sftp = c.open_sftp()
with sftp.open('/tmp/move_btncfg.py', 'w') as f:
    f.write(move_script)
sftp.close()

print('Movendo seção para dentro da sub-aba Disparo...')
i, o, e = c.exec_command('python3 /tmp/move_btncfg.py')
time.sleep(5)
out = o.read().decode('utf-8', errors='replace').strip()
err = e.read().decode('utf-8', errors='replace').strip()
print(out)
if err:
    print(f'ERR: {err[:300]}')

c.close()
