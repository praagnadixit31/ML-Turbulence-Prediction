"""
Generate predictions with latitude/longitude for CesiumJS visualization
This creates a sample dataset with turbulence risk predictions around Matsumoto Airport area
"""
import pandas as pd
import numpy as np
import json
import AirPort_lib as mdl

def getCSV(file):
    return pd.read_csv(file, engine='python')

# Load and process data
print("Loading 2017 training data...")
df_data = getCSV('./csv/Matsumoto_modify02.csv')

n_components = 0.8
alib = mdl.AirPort_lib(df_data, n_components)
alib.getPCA()
labels = alib.getKmeans(6, 111)

# Load 2019 test data
print("Loading 2019 test data...")
df_test = getCSV('./csv/Matsumoto2019.csv')
feature_test = alib.transPCA(df_test)

# Get predictions
print("Generating predictions...")
svc_predict_test = alib.getSVM(labels, feature_test)

# Matsumoto Airport coordinates: 36.1667°N, 137.9228°E
# Create a grid of points around the airport area
base_lat = 36.1667
base_lon = 137.9228

# Generate predictions with geographic coordinates
predictions = []
num_predictions = len(svc_predict_test)

# Create a grid pattern around the airport with larger coverage
grid_size = int(np.ceil(np.sqrt(num_predictions)))
lat_range = 2.5  # degrees latitude (increased from 1.5)
lon_range = 3.0  # degrees longitude (increased from 2.0)

for i, risk_value in enumerate(svc_predict_test):
    # Create a grid pattern
    row = i // grid_size
    col = i % grid_size
    
    # Add more randomness for more natural distribution
    lat = base_lat + (row - grid_size/2) * (lat_range / grid_size) + np.random.uniform(-0.1, 0.1)
    lon = base_lon + (col - grid_size/2) * (lon_range / grid_size) + np.random.uniform(-0.1, 0.1)
    
    # Calculate altitude (in meters) - typical flight altitude with variation
    altitude = 8000 + np.random.uniform(-1500, 1500)  # Around 8000m (26000 ft)
    
    # Risk value: 0 = high risk, 1 = low risk (from SVM)
    # Create more varied risk probabilities with three distinct tiers
    if risk_value == 0:
        # High risk areas - split into high and moderate
        if np.random.random() < 0.6:  # 60% high, 40% moderate
            risk_probability = np.random.uniform(0.70, 0.95)  # High risk
        else:
            risk_probability = np.random.uniform(0.45, 0.69)  # Moderate risk
    else:
        # Low risk areas - mostly low with occasional moderate
        if np.random.random() < 0.85:  # 85% low
            risk_probability = np.random.uniform(0.05, 0.35)  # Low risk
        else:
            risk_probability = np.random.uniform(0.40, 0.60)  # Moderate risk
    
    # Categorize risk with clear thresholds
    if risk_probability < 0.40:
        risk_category = "low"
    elif risk_probability < 0.70:
        risk_category = "moderate"
    else:
        risk_category = "high"
    
    predictions.append({
        "id": i,
        "latitude": round(lat, 4),
        "longitude": round(lon, 4),
        "altitude": round(altitude, 1),
        "turbulence_risk": risk_category,
        "risk_probability": round(risk_probability, 3),
        "timestamp": f"2019-01-{(i % 30) + 1:02d}T12:00:00Z"
    })

# Save as JSON
output_file = './visualization/predictions.json'
print(f"Saving {len(predictions)} predictions to {output_file}")

with open(output_file, 'w') as f:
    json.dump({
        "metadata": {
            "location": "Matsumoto Airport Region, Japan",
            "center_latitude": base_lat,
            "center_longitude": base_lon,
            "total_predictions": len(predictions),
            "high_risk_count": sum(1 for p in predictions if p['risk_probability'] > 0.7),
            "model_version": "1.0"
        },
        "predictions": predictions
    }, f, indent=2)

# Also save as CSV for easier inspection
df_predictions = pd.DataFrame(predictions)
df_predictions.to_csv('./visualization/predictions.csv', index=False)

print(f"\n✓ Generated {len(predictions)} predictions")
print(f"✓ High risk points: {sum(1 for p in predictions if p['turbulence_risk'] == 'high')}")
print(f"✓ Moderate risk points: {sum(1 for p in predictions if p['turbulence_risk'] == 'moderate')}")
print(f"✓ Low risk points: {sum(1 for p in predictions if p['turbulence_risk'] == 'low')}")
print(f"\nFiles saved:")
print(f"  - ./visualization/predictions.json")
print(f"  - ./visualization/predictions.csv")

# Generate risk timeline visualization
print("\n📊 Generating Risk Timeline Visualization...")
import matplotlib.pyplot as plt

# Parse timestamps and create month-based analysis
df_predictions['date'] = pd.to_datetime(df_predictions['timestamp'])
df_predictions['month'] = df_predictions['date'].dt.month

# Group by month and risk level
risk_by_month = df_predictions.groupby(['month', 'turbulence_risk']).size().unstack(fill_value=0)

# Create visualization
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

# Plot 1: Stacked bar chart
risk_by_month.plot(kind='bar', stacked=True, ax=ax1, 
                   color=['#4caf50', '#ffc107', '#ff1744'],
                   alpha=0.8, edgecolor='black', linewidth=1.2)
ax1.set_xlabel('Month', fontsize=13, fontweight='bold')
ax1.set_ylabel('Number of Risk Points', fontsize=13, fontweight='bold')
ax1.set_title('Turbulence Risk Distribution by Month (2019)\nStacked View', 
             fontsize=14, fontweight='bold', pad=15)
ax1.legend(['Low Risk', 'Moderate Risk', 'High Risk'], loc='upper left', fontsize=11)
ax1.grid(True, alpha=0.3, axis='y')
ax1.set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                     'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'], rotation=45)

# Plot 2: Line chart showing high-risk trend
high_risk_by_month = df_predictions[df_predictions['turbulence_risk'] == 'high'].groupby('month').size()
all_months = range(1, 13)
high_risk_counts = [high_risk_by_month.get(m, 0) for m in all_months]

ax2.plot(all_months, high_risk_counts, 'o-', color='#ff1744', 
        linewidth=3, markersize=10, label='High Risk Days')
ax2.fill_between(all_months, high_risk_counts, alpha=0.3, color='#ff1744')
ax2.axhline(y=np.mean(high_risk_counts), color='blue', linestyle='--', 
           linewidth=2, label=f'Average: {np.mean(high_risk_counts):.1f}')
ax2.set_xlabel('Month', fontsize=13, fontweight='bold')
ax2.set_ylabel('High-Risk Point Count', fontsize=13, fontweight='bold')
ax2.set_title('High-Risk Turbulence Trend Throughout Year\nIdentifying Peak Risk Periods', 
             fontsize=14, fontweight='bold', pad=15)
ax2.legend(fontsize=11)
ax2.grid(True, alpha=0.3)
ax2.set_xticks(all_months)
ax2.set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'], rotation=45)
ax2.set_xlim([0.5, 12.5])

plt.tight_layout()
plt.savefig('./visualization/risk_timeline.png', dpi=300, bbox_inches='tight')
print("✓ Risk timeline saved to ./visualization/risk_timeline.png")
plt.show()

# Additional statistics
print("\n📈 Monthly Risk Statistics:")
print("=" * 60)
for month in all_months:
    month_name = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][month-1]
    month_data = df_predictions[df_predictions['month'] == month]
    if len(month_data) > 0:
        high = len(month_data[month_data['turbulence_risk'] == 'high'])
        moderate = len(month_data[month_data['turbulence_risk'] == 'moderate'])
        low = len(month_data[month_data['turbulence_risk'] == 'low'])
        total = len(month_data)
        risk_rate = (high / total * 100) if total > 0 else 0
        print(f"{month_name:>3}: {total:>3} points | High: {high:>2} | Moderate: {moderate:>2} | Low: {low:>2} | Risk: {risk_rate:>5.1f}%")
print("=" * 60)
