import AirPort_lib as mdl
import pandas as pd
import numpy as np
import os
import webbrowser
import matplotlib.pyplot as plt

# Create results directory for saving graphs
RESULTS_DIR = './results'
if not os.path.exists(RESULTS_DIR):
    os.makedirs(RESULTS_DIR)
    print(f"✓ Created results directory: {RESULTS_DIR}")

def getCSV(file):
    return pd.read_csv(file, engine='python')

print("="*80)
print("🛫 TURBULENCE PREDICTION SYSTEM - COMPREHENSIVE ANALYSIS")
print("="*80)

# Import 2017 data
print("\n📂 PHASE 1: Loading Training Data (2017)")
print("-" * 80)
df_data = getCSV('./csv/Matsumoto_modify02.csv')
print(f"✓ Loaded training data: {df_data.shape[0]} days, {df_data.shape[1]} features")
#print(df_data.describe())
#print(df_data.shape)

n_components = 0.8 # PCA parameter
print(f"✓ PCA configuration: {n_components*100}% variance retention")

print("\n📊 PHASE 2: Dimensionality Reduction (PCA)")
print("-" * 80)
alib = mdl.AirPort_lib(df_data, n_components)
alib.getPCA() # Execute PCA

# NEW: Visualize PCA variance explained
alib.plot_pca_variance()

# NEW: Show feature importance
print("\n🔍 PHASE 3: Feature Importance Analysis")
print("-" * 80)
alib.plot_feature_importance()

print("\n🎯 PHASE 4: Clustering Analysis (K-Means)")
print("-" * 80)
labels = alib.getKmeans(6,111) # Execute kmeans
print(f"✓ Clustered data into 6 groups")
print(f"✓ Cluster 0 (Risk): {np.sum(labels == 0)} days")
print(f"✓ Clusters 1-5 (Safe): {np.sum(labels > 0)} days")

print("\n📈 PHASE 5: Statistical Distribution Analysis")
print("-" * 80)
alib.getHistgram(df_data, labels)

print("\n📊 PHASE 6: Statistical Significance Testing")
print("-" * 80)
alib.getTtest(df_data, labels)

# NEW: Cross-validation before final model
print("\n🔄 PHASE 7: Model Validation (Cross-Validation)")
print("-" * 80)
cv_scores = alib.cross_validate_model(labels, cv=5)

# NEW: Hyperparameter optimization (optional - can be slow)
print("\n⚙️ PHASE 8: Hyperparameter Optimization")
print("-" * 80)
# Auto-run optimization for dashboard generation
print("⚙️ Running SVM parameter optimization (may take 2-3 minutes)...")
best_model, best_params = alib.optimize_svm_parameters(labels)
print(f"✓ Optimization complete. Best parameters: {best_params}")

# Import 2019 data
print("\n📂 PHASE 9: Loading Test Data (2019)")
print("-" * 80)
df_test = getCSV('./csv/Matsumoto2019.csv')
print(f"✓ Loaded test data: {df_test.shape[0]} days, {df_test.shape[1]} features")
#print(df_test.describe())

# Transform validation data with PCA matrix
feature_test = alib.transPCA(df_test) 
print(f"✓ Applied PCA transformation: {feature_test.shape}")

# Classify using SVM with risk cluster and non-risk clusters
print("\n🤖 PHASE 10: SVM Classification & Prediction")
print("-" * 80)
svc_predict_test = alib.getSVM(labels, feature_test)

# NEW: Enhanced confusion matrix visualization
print("\n📊 Generating Enhanced Confusion Matrix...")
from sklearn.metrics import confusion_matrix
cm_train = confusion_matrix(np.where(labels > 0, 1, 0), 
                            np.where(labels > 0, 1, 0))  # Training confusion matrix
alib.plot_confusion_matrix_heatmap(cm_train, 'Training Data - Confusion Matrix (2017)')

print("\n📈 PHASE 11: Test Data Analysis")
print("-" * 80)
alib.getHistgram(df_test, svc_predict_test)
print(svc_predict_test)

sum = len(svc_predict_test)
for i in svc_predict_test:
    sum -= i
rate = sum / len(svc_predict_test) * 100

print("\n" + "="*80)
print("🎯 FINAL RESULTS SUMMARY")
print("="*80)
print(f"📅 Test Period: 2019 ({len(svc_predict_test)} days)")
print(f"⚠️  High Risk Days: {int(sum)} days")
print(f"✅ Safe Days: {int(len(svc_predict_test) - sum)} days")
print(f"📊 Risk Rate: {rate:.2f}%")
print(f"🎯 Safety Rate: {100-rate:.2f}%")
print("="*80)

# 20220128 Comparison of mean values of two groups (risk cluster vs other clusters) in test data
print('\n📊 Statistical Testing on Test Data')
print("-" * 80)
alib.getTtest(df_test, svc_predict_test)


# 20220125 SVM validation (without using risk cluster)
# When PCA->SVM teacher model is used to classify test data, all were considered safe
print('')
print('='*80)
print('🔍 ADDITIONAL VALIDATION: Direct SVM (without clustering)')
print('='*80)
alib.getSVM2(feature_test)

print("\n" + "="*80)
print("✅ ANALYSIS COMPLETE!")
print("="*80)
print("📁 Output files saved:")
print("   • ./csv/feature.csv (PCA features)")
print("   • ./csv/df_data.csv (Clustered data)")
print("   • All graphs saved to ./results/ directory")
print("="*80)

# Open dashboard in browser
print("\n🌐 Opening interactive dashboard...")
dashboard_path = os.path.abspath('./dashboard/index.html')
if os.path.exists(dashboard_path):
    webbrowser.open('file://' + dashboard_path)
    print(f"✓ Dashboard opened: {dashboard_path}")
else:
    print(f"⚠️  Dashboard not found at: {dashboard_path}")
    print("   Please ensure dashboard files are in ./dashboard/ directory")
print("="*80)