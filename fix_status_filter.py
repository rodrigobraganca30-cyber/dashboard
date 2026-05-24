#!/usr/bin/env python3
"""Remove o filtro de status do waParseCSV no index.html"""
ARQUIVO = '/docker/dashboard/html/index.html'

with open(ARQUIVO, 'r', encoding='utf-8') as f:
    content = f.read()

# Remove o filtro que descarta linhas sem status ou com status diferente
OLD = """      var st=g(row,iSt).toLowerCase();
      /* Aceitar apenas: pendentes, agendados e concluidos (nao incluir "nao concluida") */
      if(!st) continue;
      var isConclu = st.indexOf('conclu')>=0 && st.indexOf('nao conclu')<0 && st.indexOf('não conclu')<0;
      if(st.indexOf('pendente')<0 && st.indexOf('agendado')<0 && st.indexOf('pending')<0 && st.indexOf('nao iniciado')<0 && !isConclu) continue;"""

NEW = """      var st=g(row,iSt).toLowerCase();
      /* Sem filtro de status — aceita qualquer planilha */
      var isConclu = st.indexOf('conclu')>=0 && st.indexOf('nao conclu')<0 && st.indexOf('não conclu')<0;"""

if OLD in content:
    content = content.replace(OLD, NEW, 1)
    with open(ARQUIVO, 'w', encoding='utf-8') as f:
        f.write(content)
    print('[OK] Filtro de status removido do waParseCSV')
else:
    print('[ERRO] Ancora nao encontrada')
    import re
    m = re.search(r'Aceitar apenas', content)
    if m:
        print('[DIAG]:', repr(content[m.start()-100:m.start()+300]))
