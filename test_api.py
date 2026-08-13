import urllib.request
import json

try:
    with urllib.request.urlopen('http://127.0.0.1:5000/api/dashboard', timeout=30) as resp:
        data = json.loads(resp.read().decode())
        print(f"✅ Status: {data.get('status')}")
        print(f"✅ Total Vendido: {data.get('kpis', {}).get('total_vendido')}")
        print(f"✅ Horário de Pico: {data.get('kpis', {}).get('horario_pico')}")
        print(f"✅ Timestamp: {data.get('timestamp')}")
        if 'message' in data:
            print(f"⚠️  Mensagem: {data.get('message')}")
except Exception as e:
    print(f"❌ Erro: {type(e).__name__}: {str(e)}")
