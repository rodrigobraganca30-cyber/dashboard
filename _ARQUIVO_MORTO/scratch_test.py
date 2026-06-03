# Simulate what the f-string produces for the waFluxoCancelar line
# In whatsapp_agenda_gen.py, the function returns f"""...""" with {{ and }}

# The exact line from the source (line 1322):
# html += '<button onclick="waFluxoCancelar(\\'' + fl.id + '\\')" ...>';

# Inside f"..." string, \\ becomes \ and \\' becomes \'
# Let's test:
test = f"""        html += '<button onclick="waFluxoCancelar(\\'' + fl.id + '\\')" style="test">';"""
print("F-string output:")
print(test)
print()
print("repr:", repr(test))
print()

# What we WANT in the final HTML:
want = """        html += '<button onclick="waFluxoCancelar(\\'' + fl.id + '\\')" style="test">';"""
print("What we want:")
print(want)
print()

# Does the f-string produce the same?
print("Match:", test == want)
