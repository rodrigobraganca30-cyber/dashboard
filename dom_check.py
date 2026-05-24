import re
html = open("/opt/painel_robo/src/menu_acoes_erro.html").read()
titles = re.findall(r'title="([^"]+)"', html)
for t in sorted(set(titles)):
    print(t)
print("---NAV CLASSES---")
navs = re.findall(r'class="global-navigation-item[^"]*"', html)
for n in navs:
    print(n)
print("---CONSOLE---")
for m in re.finditer(r'Console[^<]{0,50}', html):
    print(m.group())
