"""
SIMPLE ML SCRIPT - Creates predictions.json for frontend
"""

import pandas as pd
import numpy as np
import json

print("🚀 Starting Delhi Water Logging Predictions...")

# 1. Load data
print("\n📁 Loading data files...")
drainage = pd.read_csv('drainage.csv')
rainfall = pd.read_csv('rainfall.csv')
wards = pd.read_csv('wards.csv')

print(f"✅ Loaded: {len(drainage)} wards from drainage data")

# 2. Show what we have
print("\n📋 First ward data:")
print(drainage.iloc[0])

# 3. Calculate water logging risk (SIMPLE FORMULA)
print("\n🎯 Calculating risk scores...")
drainage['risk_score'] = (
    0.40 * (100 - drainage['drainage_capacity_score']) +  # Lower drainage = higher risk
    0.25 * drainage['drainage_system_age_years'] +         # Older = higher risk  
    0.20 * drainage['historical_flood_events'] * 15 +      # Past floods = higher risk
    0.15 * (100 - drainage['sewage_network_coverage_percent'])  # Less coverage = higher risk
)

# Cap at 100
drainage['risk_score'] = drainage['risk_score'].clip(0, 100)

# 4. Merge with ward coordinates
print("\n🗺️ Adding locations...")
data = pd.merge(drainage, wards[['ward_id', 'centroid_lat', 'centroid_lon']], 
                on='ward_id', how='left')

# 5. Create predictions for frontend
print("\n💾 Creating predictions.json...")
predictions = []

for _, row in data.iterrows():
    risk = row['risk_score']
    
    # Risk category
    if risk >= 70:
        level = "CRITICAL 🔴"
        color = "#FF0000"
    elif risk >= 50:
        level = "HIGH 🟠"
        color = "#FFA500"
    elif risk >= 30:
        level = "MEDIUM 🟡"
        color = "#FFFF00"
    else:
        level = "LOW 🟢"
        color = "#00FF00"
    
    # Create prediction object
    pred = {
        'ward_id': row['ward_id'],
        'risk_score': float(risk),
        'risk_level': level,
        'risk_color': color,
        'lat': float(row.get('centroid_lat', 28.6139)),  # Delhi center if missing
        'lon': float(row.get('centroid_lon', 77.2090)),
        'drainage_score': int(row.get('drainage_capacity_score', 0)),
        'drainage_age': int(row.get('drainage_system_age_years', 0))
    }
    predictions.append(pred)

# 6. Save to JSON
with open('predictions.json', 'w') as f:
    json.dump(predictions, f, indent=2)

# 7. Show results
high_risk = len([p for p in predictions if p['risk_score'] >= 50])
print(f"\n📊 RESULTS:")
print(f"   Total wards predicted: {len(predictions)}")
print(f"   High/Critical risk: {high_risk} wards")
print(f"   Average risk score: {np.mean([p['risk_score'] for p in predictions]):.1f}/100")

print("\n✅ SUCCESS! Created predictions.json")
print("📁 Share this file with your frontend team!")
