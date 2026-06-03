#!/usr/bin/env python3
"""Substitui showWaSub por versão com try/catch e alert de debug"""
ARQUIVO = '/docker/dashboard/html/index.html'

with open(ARQUIVO, 'r', encoding='utf-8') as f:
    content = f.read()

OLD = """  function showWaSub(id,btn){
    document.querySelectorAll('.wa-sub').forEach(function(s){s.classList.remove('active')});
    document.querySelectorAll('.wa-tab').forEach(function(b){b.classList.remove('active')});
    document.getElementById(id).classList.add('active');
    if(btn)btn.classList.add('active');
  }"""

NEW = """  function showWaSub(id,btn){
    try {
      var subs = document.querySelectorAll('.wa-sub');
      var tabs = document.querySelectorAll('.wa-tab');
      var target = document.getElementById(id);
      if(!target){ alert('ERRO: elemento #'+id+' nao encontrado!'); return; }
      subs.forEach(function(s){s.classList.remove('active')});
      tabs.forEach(function(b){b.classList.remove('active')});
      target.classList.add('active');
      if(btn)btn.classList.add('active');
    } catch(err) {
      alert('ERRO em showWaSub('+id+'): ' + err.message);
    }
  }"""

if OLD in content:
    content = content.replace(OLD, NEW, 1)
    with open(ARQUIVO, 'w', encoding='utf-8') as f:
        f.write(content)
    print('[OK] showWaSub com debug aplicado')
else:
    # Tenta match mais flexível
    import re
    m = re.search(r'function showWaSub\(id,btn\)\{.*?\}', content, re.DOTALL)
    if m:
        print('[DIAG] showWaSub encontrado:')
        print(repr(content[m.start():m.end()]))
    else:
        print('[ERRO] showWaSub nao encontrado')
