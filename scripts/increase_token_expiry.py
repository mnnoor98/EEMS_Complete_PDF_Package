with open('backend/src/EEMS.Api/appsettings.json', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('"AccessTokenMinutes": 15', '"AccessTokenMinutes": 1440')

with open('backend/src/EEMS.Api/appsettings.json', 'w', encoding='utf-8') as f:
    f.write(text)

print('Updated AccessTokenMinutes to 1440 successfully!')

