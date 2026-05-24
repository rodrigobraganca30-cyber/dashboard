var txt = 'Ola, {{1}}! Tudo bem?';
var vars = txt.match(/\{\{[0-9]+\}\}/g);
console.log('vars:', vars);
if (vars) {
  var example = { body_text: [vars.map((_, i) => 'exemplo' + (i + 1))] };
  console.log('example:', JSON.stringify(example));
} else {
  console.log('SEM MATCH - exemplo nao sera incluido');
}
