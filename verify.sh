#!/bin/bash
echo "=== 1. Python imports ==="
python -c "
from src.models.gcn_lstm_model import train_gcn_lstm
from src.real_data import train_rf_from_real_data, load_field_survey
from src.multi_agent_rl import train_independent_ppo_agents
from src.controller import SumoTrafficEnv
print('All imports OK')
"

echo "=== 2. Models exist ==="
for f in models/random_forest.pkl models/lstm_traffic.pt models/gcn_lstm_best.pt models/marl_joint.zip; do
  [ -f "$f" ] && echo "OK: $f" || echo "MISSING: $f"
done

echo "=== 3. Routes vehicle types ==="
python -c "
import xml.etree.ElementTree as ET
tree = ET.parse('simulation/routes.xml')
types = [v.attrib['id'] for v in tree.findall('.//vType')]
for t in ['emergency','bus','motorcycle']:
    print(f'  {t}:', 'OK' if t in types else 'MISSING')
"

echo "=== 4. Docker ==="
docker ps | grep mangalore && echo "Container running OK" || echo "Container not running"

echo "=== 5. API health ==="
curl -sf http://localhost:8000/health && echo "API OK" || echo "API not reachable"

echo "=== 6. Tests ==="
pytest tests/ -q --tb=no 2>&1 | tail -5
