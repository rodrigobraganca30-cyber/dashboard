import yaml

# 1. whatsapp-agenda
with open('/docker/whatsapp-agenda/docker-compose.yml') as f:
    d = yaml.safe_load(f)
for svc, lim in [('backend',{'cpus':'1.0','memory':'256M'}), ('redis',{'cpus':'0.5','memory':'64M'}), ('evolution-api',{'cpus':'0.5','memory':'256M'})]:
    if svc in d.get('services',{}):
        d['services'][svc].setdefault('deploy',{}).setdefault('resources',{})['limits'] = lim
with open('/docker/whatsapp-agenda/docker-compose.yml','w') as f:
    yaml.dump(d, f, default_flow_style=False, sort_keys=False)
print('WA OK')

# 2. n8n
with open('/docker/n8n-15s7/docker-compose.yml') as f:
    d = yaml.safe_load(f)
if 'n8n' in d.get('services',{}):
    d['services']['n8n'].setdefault('deploy',{}).setdefault('resources',{})['limits'] = {'cpus':'1.5','memory':'512M'}
with open('/docker/n8n-15s7/docker-compose.yml','w') as f:
    yaml.dump(d, f, default_flow_style=False, sort_keys=False)
print('N8N OK')

# 3. traefik
with open('/docker/traefik/docker-compose.yml') as f:
    d = yaml.safe_load(f)
if 'traefik' in d.get('services',{}):
    d['services']['traefik'].setdefault('deploy',{}).setdefault('resources',{})['limits'] = {'cpus':'1.0','memory':'256M'}
    cmds = d['services']['traefik'].get('command',[])
    for i,c in enumerate(cmds):
        if '--log.level=' in str(c):
            cmds[i] = '--log.level=WARN'
with open('/docker/traefik/docker-compose.yml','w') as f:
    yaml.dump(d, f, default_flow_style=False, sort_keys=False)
print('TRAEFIK OK')

# 4. veicular-app
with open('/docker/veicular-app/docker-compose.yml') as f:
    d = yaml.safe_load(f)
for svc, lim in [('backend',{'cpus':'1.0','memory':'512M'}), ('frontend',{'cpus':'0.5','memory':'256M'}), ('worker',{'cpus':'0.5','memory':'256M'}), ('db',{'cpus':'0.5','memory':'256M'}), ('redis',{'cpus':'0.5','memory':'64M'})]:
    if svc in d.get('services',{}):
        d['services'][svc].setdefault('deploy',{}).setdefault('resources',{})['limits'] = lim
with open('/docker/veicular-app/docker-compose.yml','w') as f:
    yaml.dump(d, f, default_flow_style=False, sort_keys=False)
print('VEICULAR OK')

print('ALL LIMITS APPLIED')
