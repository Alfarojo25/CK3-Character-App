import json

json_path = r"c:\Users\edubl\OneDrive\Escritorio\CK3-Character-App\databases\Database_Default\character_data\characters.json"

# Leer JSON (con BOM)
with open(json_path, 'r', encoding='utf-8-sig') as f:
    data = json.load(f)

# Escribir con indentación correcta de 4 espacios y BOM
with open(json_path, 'w', encoding='utf-8-sig') as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

print("JSON reformateado correctamente con indentación de 4 espacios")
