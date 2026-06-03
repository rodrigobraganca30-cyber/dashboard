#!/usr/bin/env python3
"""Adiciona debug alert no waParseCSV para diagnosticar"""
ARQUIVO = '/docker/dashboard/html/index.html'

with open(ARQUIVO, 'r', encoding='utf-8') as f:
    content = f.read()

OLD = "    if(!list.length){console.log('Nenhum agendamento pendente encontrado neste CSV ('+allRows.length+' linhas lidas)');return}"
NEW = "    if(!list.length){alert('DEBUG: Planilha lida - '+allRows.length+' linhas, mas 0 clientes encontrados. Colunas detectadas: nome='+iNome+' tel='+iTel);return}\n    alert('DEBUG: '+list.length+' clientes carregados!');"

if OLD in content:
    content = content.replace(OLD, NEW, 1)
    with open(ARQUIVO, 'w', encoding='utf-8') as f:
        f.write(content)
    print('[OK] Debug adicionado')
else:
    print('[ERRO] Ancora nao encontrada')
