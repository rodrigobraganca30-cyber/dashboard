/**
 * dynamic_loader.js — Fase 2: Carrega dados de JSONs e atualiza o dashboard
 * Fallback: se fetch falhar, dados inline ficam intactos
 * 
 * Carrega: os.json, filtros.json, kpis.json, frota.json
 */
(function () {
  'use strict';
  var _t = Date.now();
  var BASE = 'data/';

  // Status mapping: processar_dados.py salva sem acento
  var STATUS_MAP = {
    'Concluida': 'Conclu\u00edda',
    'Nao Concluida': 'N\u00e3o Conclu\u00edda',
    'Cancelada': 'Cancelada',
    'Suspensa': 'Suspensa',
    'Pendente': 'Pendente'
  };

  // ─── Helpers ───
  function fmt(n, dec) {
    return n.toLocaleString('pt-BR', { minimumFractionDigits: dec || 0, maximumFractionDigits: dec || 0 });
  }

  function $(sel) { return document.querySelector(sel); }
  function $$(sel) { return document.querySelectorAll(sel); }

  // ─── 1. OS + Filtros ───
  var osReady = false, filtrosReady = false;

  function onDataReady() {
    if (!osReady || !filtrosReady) return;

    // Remapear status
    window.rawOSData = window.rawOSData.map(function (d) {
      if (STATUS_MAP[d.status]) d.status = STATUS_MAP[d.status];
      return d;
    });

    // Limpar dropdowns cacheados
    $$('.filter-dropdown').forEach(function (d) { d.innerHTML = ''; });

    // Limpar legenda externa do donut (a que fica fora do donut-wrap)
    var dw = $('.donut-wrap');
    if (dw) {
      var next = dw.nextElementSibling;
      while (next && next.classList.contains('donut-legend')) {
        var toRemove = next;
        next = next.nextElementSibling;
        toRemove.remove();
      }
    }

    // Encapsular runFilter para corrigir subtitulos e limpar legenda duplicada
    var _origRunFilter = window.runFilter;
    window.runFilter = function () {
      _origRunFilter.apply(this, arguments);
      fixSubtitles();
      fixPeriodo();

      // Garantir que qualquer legenda fora do donut-wrap seja removida
      var dw = document.querySelector('.donut-wrap');
      if (dw) {
        document.querySelectorAll('.donut-legend').forEach(function (leg) {
          if (!dw.contains(leg)) {
            leg.remove();
          }
        });
      }
    };

    // Executar filtro com dados novos
    window.runFilter();
    console.log('[DynLoader] OS: ' + window.rawOSData.length + ' registros carregados');
  }

  function getKPIVal(el) {
    if (!el) return 0;
    var txt = el.textContent.trim().replace(/\./g, '');
    return parseInt(txt) || 0;
  }

  function fixSubtitles() {
    var total = getKPIVal($('.kpi-value.blue'));

    // Canceladas
    var vRed = $('.kpi-value.red');
    if (vRed && vRed.closest('#visao-geral, .page.active')) {
      // Garantir que e o card de visao geral, nao de outra aba
      var card = vRed.closest('.kpi-card');
      if (card) {
        var label = card.querySelector('.kpi-label');
        if (label && label.textContent.indexOf('Cancelad') >= 0) {
          var sub = card.querySelector('.kpi-sub');
          var val = getKPIVal(vRed);
          var pct = total > 0 ? (val / total * 100).toFixed(1) : '0.0';
          if (sub) sub.textContent = pct + '% do total';
        }
      }
    }

    // Nao Concluidas
    var vYellow = $('.kpi-value.yellow');
    if (vYellow) {
      var card = vYellow.closest('.kpi-card');
      if (card) {
        var label = card.querySelector('.kpi-label');
        if (label && label.textContent.indexOf('Conclu') >= 0) {
          var sub = card.querySelector('.kpi-sub');
          var val = getKPIVal(vYellow);
          var pct = total > 0 ? (val / total * 100).toFixed(1) : '0.0';
          if (sub) sub.textContent = pct + '% do total';
        }
      }
    }

    // Suspensas e Pendentes
    $$('.kpi-value.white').forEach(function (el) {
      var card = el.closest('.kpi-card');
      if (card) {
        var sub = card.querySelector('.kpi-sub');
        var val = getKPIVal(el);
        var pct = total > 0 ? (val / total * 100).toFixed(1) : '0.0';
        if (sub) sub.textContent = pct + '% do total';
      }
    });
  }

  function fixPeriodo() {
    // Pegar datas do filtro
    var dsEl = document.getElementById('date-start');
    var deEl = document.getElementById('date-end');
    var ds = dsEl ? dsEl.value : '';
    var de = deEl ? deEl.value : '';

    // Encontrar o sub do Total de OS (primeiro card da visao geral)
    var page = document.getElementById('visao-geral');
    if (!page) return;
    var firstCard = page.querySelector('.kpi-card');
    if (!firstCard) return;
    var sub = firstCard.querySelector('.kpi-sub');
    if (!sub) return;

    if (ds && de) {
      // Filtro ativo: mostrar periodo do filtro
      var dsParts = ds.split('-');
      var deParts = de.split('-');
      sub.textContent = dsParts[2] + '/' + dsParts[1] + ' a ' + deParts[2] + '/' + deParts[1];
    } else if (window.rawOSData && window.rawOSData.length > 0) {
      // Sem filtro: primeira e ultima data dos dados
      var dates = window.rawOSData.map(function (d) { return d.date; }).filter(function (d) { return d && d !== '--'; });
      if (dates.length > 0) sub.textContent = dates[0] + ' a ' + dates[dates.length - 1];
    }
  }

  // Fetch os.json
  fetch(BASE + 'os.json?t=' + _t)
    .then(function (r) { if (!r.ok) throw 'HTTP ' + r.status; return r.json(); })
    .then(function (data) {
      window.rawOSData = data;
      osReady = true;
      onDataReady();
    })
    .catch(function (e) { console.log('[DynLoader] os.json falhou:', e); osReady = true; onDataReady(); });

  // Fetch filtros.json
  fetch(BASE + 'filtros.json?t=' + _t)
    .then(function (r) { if (!r.ok) throw 'HTTP ' + r.status; return r.json(); })
    .then(function (data) {
      window.filterLists = data;
      filtrosReady = true;
      onDataReady();
    })
    .catch(function (e) { console.log('[DynLoader] filtros.json falhou:', e); filtrosReady = true; onDataReady(); });


  // ─── 2. Frota ───
  fetch(BASE + 'frota.json?t=' + _t)
    .then(function (r) { if (!r.ok) throw 'HTTP ' + r.status; return r.json(); })
    .then(function (f) {
      console.log('[DynLoader] frota.json: ' + f.veiculos.length + ' veiculos');

      // ── Veiculos ──
      var vDiv = document.getElementById('frota-veiculos');
      if (vDiv && f.veiculos.length) {
        var tbl = vDiv.querySelector('table');
        if (tbl && tbl.tBodies[0]) {
          var rows = '';
          f.veiculos.forEach(function (v) {
            var st = (v.status || '').toUpperCase();
            var badge;
            if (st.indexOf('ATIVIDADE') >= 0) badge = '<span class="badge green">Em Atividade</span>';
            else if (st.indexOf('OFICINA') >= 0) badge = '<span class="badge red">Oficina</span>';
            else if (st === 'PARADO' || st === 'DESMOBILIZADO') badge = '<span class="badge yellow">Parado</span>';
            else if (st.indexOf('DEVOLVIDO') >= 0) badge = '<span class="badge yellow">Devolvido</span>';
            else if (st.indexOf('ATESTADO') >= 0) badge = '<span class="badge yellow">Atestado</span>';
            else badge = '<span class="badge">' + v.status + '</span>';
            rows += '<tr><td style="font-weight:600;color:#e8eaf6">' + v.placa + '</td><td>' + v.tecnico + '</td><td>' + v.locadora + '</td><td>' + badge + '</td></tr>';
          });
          tbl.tBodies[0].innerHTML = rows;
        }
      }

      // ── Oficina + Revisao ──
      var mDiv = document.getElementById('frota-manut');
      if (mDiv) {
        var tables = mDiv.querySelectorAll('table');
        if (tables[0] && f.oficina && f.oficina.length) {
          f.oficina.sort(function (a, b) { return (b.dias || 0) - (a.dias || 0); });
          var rows = '';
          f.oficina.forEach(function (o) {
            var st = o.status.toUpperCase();
            var badge = st.indexOf('OFICINA') >= 0 ? '<span class="badge red">Na Oficina</span>' : '<span class="badge">' + o.status + '</span>';
            var d = o.dias || 0;
            var db = d > 30 ? '<span class="badge red">' + d + 'd</span>' : d > 14 ? '<span class="badge yellow">' + d + 'd</span>' : '<span class="badge green">' + d + 'd</span>';
            rows += '<tr><td style="font-weight:600;color:#e8eaf6">' + o.placa + '</td><td>' + o.motorista + '</td><td>' + o.entrada + '</td><td>' + o.previsao + '</td><td>' + o.cidade + '</td><td>' + badge + '</td><td>' + db + '</td></tr>';
          });
          if (tables[0].tBodies[0]) tables[0].tBodies[0].innerHTML = rows;
        }
        if (tables[1] && f.revisao && f.revisao.length) {
          var rows2 = '';
          f.revisao.forEach(function (r) {
            var badge = r.status.toUpperCase().indexOf('AGENDAR') >= 0 ? '<span class="badge yellow">Agendar</span>' : '<span class="badge red">Revis\u00e3o</span>';
            rows2 += '<tr><td style="font-weight:600;color:#e8eaf6">' + r.placa + '</td><td>' + r.tecnico + '</td><td>' + r.locadora + '</td><td>' + r.km + ' km</td><td>' + r.data + '</td><td>' + badge + '</td></tr>';
          });
          if (tables[1].tBodies[0]) tables[1].tBodies[0].innerHTML = rows2;
        }
      }

      // ── Combustivel KPIs ──
      var cDiv = document.getElementById('frota-comb');
      if (cDiv) {
        var k = f.kpis || {};
        var nTec = (f.combustivel || []).length;
        var totalGasto = k.combustivel_total || 0;
        var litros = k.litros_total || 0;
        var km = k.km_total || 0;
        var dia = new Date().getDate();
        var proj = dia > 0 ? (totalGasto / dia) * 30 : 0;

        var cards = cDiv.querySelectorAll('.kpi-card');
        if (cards[0]) { var v = cards[0].querySelector('.kpi-value'); if (v) v.textContent = 'R$ ' + fmt(totalGasto, 2); var s = cards[0].querySelector('.kpi-sub'); if (s) s.textContent = nTec + ' t\u00e9cnicos'; }
        if (cards[1]) { var v = cards[1].querySelector('.kpi-value'); if (v) v.textContent = 'R$ ' + fmt(proj, 2); var s = cards[1].querySelector('.kpi-sub'); if (s) s.textContent = 'proje\u00e7\u00e3o mensal (dia ' + dia + '/30)'; }
        if (cards[2]) { var v = cards[2].querySelector('.kpi-value'); if (v) v.textContent = fmt(litros) + 'L'; var s = cards[2].querySelector('.kpi-sub'); if (s) s.textContent = 'm\u00e9dia ' + (nTec > 0 ? Math.round(litros / nTec) : 0) + 'L/t\u00e9cnico'; }
        if (cards[3]) { var v = cards[3].querySelector('.kpi-value'); if (v) v.textContent = fmt(km); var s = cards[3].querySelector('.kpi-sub'); if (s) s.textContent = 'm\u00e9dia ' + (nTec > 0 ? Math.round(km / nTec) : 0) + ' km/t\u00e9cnico'; }

        // Tabela combustivel
        var tbl = cDiv.querySelector('table');
        if (tbl && tbl.tBodies[0] && f.combustivel.length) {
          var rows = '';
          f.combustivel.forEach(function (c, i) {
            var kmR = c.km_rodado || 0, kmE = c.km || 0;
            var pct = kmE > 0 ? Math.min(Math.round(kmR / kmE * 100), 100) : 0;
            var color = pct >= 80 ? '#22d3a0' : pct >= 50 ? '#fbbf24' : '#ff4d6d';
            var bar = '<div style="display:flex;align-items:center;gap:10px;"><div style="flex:1;background:rgba(255,255,255,0.06);border-radius:4px;height:10px;min-width:120px;"><div style="width:' + pct + '%;height:100%;background:' + color + ';border-radius:4px;"></div></div><span style="font-size:12px;color:' + color + ';font-weight:700;min-width:40px;text-align:right;">' + pct + '%</span></div>';
            rows += '<tr><td style="padding:10px 8px;text-align:center;">' + (i + 1) + '</td><td style="padding:10px 12px;">' + c.tecnico + '</td><td style="padding:10px 12px;color:#f472b6;font-weight:600;text-align:right;">R$ ' + fmt(c.gasto, 2) + '</td><td style="padding:10px 12px;text-align:right;">' + c.litros + '</td><td style="padding:10px 12px;text-align:right;color:#60a5fa;font-weight:600;">' + fmt(kmR) + '</td><td style="padding:10px 12px;text-align:right;color:#94a3b8;">' + fmt(kmE) + '</td><td style="padding:10px 12px;min-width:180px;">' + bar + '</td></tr>';
          });
          tbl.tBodies[0].innerHTML = rows;
        }
      }

      // ── Deslocamento ──
      var dDiv = document.getElementById('frota-desl');
      if (dDiv) {
        var tables = dDiv.querySelectorAll('table');
        if (tables[0] && f.deslocamento_tec && f.deslocamento_tec.length && tables[0].tBodies[0]) {
          var rows = '';
          f.deslocamento_tec.forEach(function (t, i) {
            rows += '<tr><td>' + (i + 1) + '</td><td>' + t.tecnico + '</td><td>' + t.viagens + '</td><td>' + fmt(t.km) + '</td><td>R$ ' + fmt(t.valor, 2) + '</td></tr>';
          });
          tables[0].tBodies[0].innerHTML = rows;
        }
        if (tables[1] && f.deslocamento_dest && f.deslocamento_dest.length && tables[1].tBodies[0]) {
          var rows2 = '';
          f.deslocamento_dest.forEach(function (d, i) {
            rows2 += '<tr><td>' + (i + 1) + '</td><td style="font-weight:600;color:#e8eaf6">' + d.destino + '</td><td>' + d.viagens + '</td><td>' + fmt(d.km) + '</td></tr>';
          });
          tables[1].tBodies[0].innerHTML = rows2;
        }
      }
    })
    .catch(function (e) { console.log('[DynLoader] frota.json falhou:', e); });


  // ─── 3. Indicador Giga (_GIGA2) ───
  fetch(BASE + 'giga2.json?t=' + _t)
    .then(function (r) { if (!r.ok) throw 'HTTP ' + r.status; return r.json(); })
    .then(function (data) {
      if (!data || Object.keys(data).length === 0) return;
      window._GIGA2 = data;

      // Atualizar tabs de mes (caso tenha meses novos)
      var MORD = ['DEZEMBRO', 'JANEIRO', 'FEVEREIRO', 'MARÇO', 'ABRIL', 'MAIO', 'JUNHO', 'JULHO', 'AGOSTO', 'SETEMBRO', 'OUTUBRO', 'NOVEMBRO'];
      var mdisp = MORD.filter(function (m) { return data[m]; });
      var mdef = mdisp.length > 0 ? mdisp[mdisp.length - 1] : '';

      // Recriar tabs de mes
      var page = document.getElementById('indicador-giga');
      if (page) {
        var tabsDiv = page.querySelector('.ig-month-tabs');
        if (tabsDiv) {
          tabsDiv.innerHTML = '';
          mdisp.forEach(function (m) {
            var tab = document.createElement('div');
            tab.className = 'ig-month-tab' + (m === mdef ? ' active' : '');
            tab.textContent = m.charAt(0) + m.slice(1).toLowerCase();
            tab.onclick = function () { igSetMes(this, m); };
            tabsDiv.appendChild(tab);
          });
        }
      }

      // Setar mes default e re-renderizar
      if (typeof window._igMes !== 'undefined') {
        window._igMes = mdef;
        window._igC = null;
        window._igDay = null;
        if (typeof igRenderSectors === 'function') igRenderSectors();
      }

      console.log('[DynLoader] giga2.json: ' + mdisp.join(', '));
    })
    .catch(function (e) { console.log('[DynLoader] giga2.json falhou:', e); });

})();
