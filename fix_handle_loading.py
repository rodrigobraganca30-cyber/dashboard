#!/usr/bin/env python3
"""
Fix: adiciona loading visual e try/catch completo no waHandleFile
para que o usuário saiba que o arquivo foi recebido.
"""
ARQUIVO = '/docker/dashboard/html/index.html'

with open(ARQUIVO, 'r', encoding='utf-8') as f:
    content = f.read()

OLD = "  function waHandleFile(e){\n    var files=e.target.files;\n    if(!files||!files.length)return;\n    for(var i=0;i<files.length;i++){\n      (function(file){\n        var ext=file.name.split('.').pop().toLowerCase();\n        if(ext==='csv'){var r=new FileReader();r.onload=function(ev){waShowMappingModal(ev.target.result)};r.readAsText(file,'UTF-8')}\n        else{\n          if(!window.XLSX){\n            var sc=document.createElement('script');sc.src='https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js';\n            sc.onload=function(){var r=new FileReader();r.onload=function(ev){try{var wb=XLSX.read(new Uint8Array(ev.target.result),{type:'array'});waShowMappingModal(XLSX.utils.sheet_to_csv(wb.Sheets[wb.SheetNames[0]]))}catch(e2){alert('Erro ao ler Excel: '+e2.message)}};r.onerror=function(){alert('Erro ao ler o arquivo.')};r.readAsArrayBuffer(file)};\n            sc.onerror=function(){var s2=document.createElement('script');s2.src='https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js';s2.onload=sc.onload;s2.onerror=function(){alert('Erro ao carregar biblioteca Excel. Recarregue a pagina.')};document.head.appendChild(s2)};\n            document.head.appendChild(sc);\n          } else {\n            var r=new FileReader();r.onload=function(ev){var wb=XLSX.read(new Uint8Array(ev.target.result),{type:'array'});waShowMappingModal(XLSX.utils.sheet_to_csv(wb.Sheets[wb.SheetNames[0]]))};r.readAsArrayBuffer(file);\n          }\n        }\n      })(files[i]);\n    }\n    e.target.value='';\n  }"

NEW = """  function waHandleFile(e){
    var files=e.target.files;
    if(!files||!files.length)return;

    function showLoading(name) {
      var dz = document.getElementById('wa-drop-zone');
      if(dz) dz.innerHTML = '<div style="padding:20px;text-align:center;color:#25d366;font-size:14px">⏳ Lendo <b>'+name+'</b>...</div>';
    }
    function resetDropzone() {
      var dz = document.getElementById('wa-drop-zone');
      if(dz) dz.innerHTML = '<div style="font-size:32px;margin-bottom:12px">⬆️</div><p style="color:#e8eaf6;font-size:14px;margin-bottom:6px">Arraste ou clique para importar</p><p style="color:#25d366;font-size:12px">CSV ou Excel da agenda OFS</p>';
    }

    function processCSV(csvText, filename) {
      try {
        resetDropzone();
        waShowMappingModal(csvText, filename);
      } catch(err) {
        resetDropzone();
        alert('Erro ao processar planilha: ' + err.message);
      }
    }

    function loadXLSX(cb) {
      if(window.XLSX) return cb();
      var sc=document.createElement('script');
      sc.src='https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js';
      sc.onload=cb;
      sc.onerror=function(){
        var s2=document.createElement('script');
        s2.src='https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js';
        s2.onload=cb;
        s2.onerror=function(){
          resetDropzone();
          alert('Erro ao carregar biblioteca Excel. Verifique a internet e tente novamente.');
        };
        document.head.appendChild(s2);
      };
      document.head.appendChild(sc);
    }

    for(var i=0;i<files.length;i++){
      (function(file){
        var ext=file.name.split('.').pop().toLowerCase();
        showLoading(file.name);
        if(ext==='csv'||ext==='tsv'){
          var r=new FileReader();
          r.onload=function(ev){processCSV(ev.target.result, file.name)};
          r.onerror=function(){resetDropzone();alert('Erro ao ler arquivo CSV.')};
          r.readAsText(file,'UTF-8');
        } else {
          loadXLSX(function(){
            var r=new FileReader();
            r.onload=function(ev){
              try{
                var wb=XLSX.read(new Uint8Array(ev.target.result),{type:'array'});
                var csv=XLSX.utils.sheet_to_csv(wb.Sheets[wb.SheetNames[0]]);
                processCSV(csv, file.name);
              }catch(e2){resetDropzone();alert('Erro ao ler Excel: '+e2.message);}
            };
            r.onerror=function(){resetDropzone();alert('Erro ao ler o arquivo.')};
            r.readAsArrayBuffer(file);
          });
        }
      })(files[i]);
    }
    e.target.value='';
  }"""

if OLD in content:
    content = content.replace(OLD, NEW, 1)
    with open(ARQUIVO, 'w', encoding='utf-8') as f:
        f.write(content)
    print('[OK] waHandleFile atualizado com loading e error handling')
else:
    print('[ERRO] Ancora nao encontrada')
    import re
    m = re.search(r'function waHandleFile', content)
    if m:
        print('[DIAG]', repr(content[m.start():m.start()+200]))
