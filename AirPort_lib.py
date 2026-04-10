import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import os

from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import f1_score
from sklearn.metrics import classification_report
from sklearn.metrics import roc_curve, auc
from sklearn.model_selection import cross_val_score, GridSearchCV
import scipy # Library for testing homogeneity of variance (F-test)

# Set style for better-looking plots
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# Results directory for saving graphs
RESULTS_DIR = './results'

class AirPort_lib :
    def __init__(self, df_data, n_components):
        self.df_data = df_data # With teacher label (mod_turb)
        self.t_label = df_data['mod_turb']
        #print(self.t_label)
        self.df_data_rm = df_data.drop(columns='mod_turb')
        self.df_data_sc = self.getSC(self.df_data_rm) # Normalized after removing teacher data (use this)
        #print(self.df_data_sc.shape)
        self.n_components= n_components

    def saveCSV(self, df, fname):
        pdf = pd.DataFrame(df) # Convert dataframe to pandas
        pdf.to_csv(fname)

    def getSC(self, df):
        sc = StandardScaler()
        return sc.fit_transform(df)

    def getPCA(self):
        self.pca = PCA(n_components=self.n_components)
        self.pca.fit(self.df_data_sc)
        self.feature = self.pca.transform(self.df_data_sc) # feature is the transformed dataset value (Z)
        #print(feature.shape)
        #print(feature)
        self.components = self.pca.components_ # components is the transformation matrix (W)
        #print(self.components.shape)
        self.explained_variance = self.pca.explained_variance_ # eigenvalues
        #print(self.pca.explained_variance_) 
        self.explained_variance_ratio = self.pca.explained_variance_ratio_ # factor contribution ratio
        #print(self.explained_variance_ratio)
        self.saveCSV(self.feature, './csv/feature.csv')

    def transPCA(self, df_test): # Transform validation data using principal components
        # Normalize df
        df_test_sc = self.getSC(df_test)
        feature_test = self.pca.transform(df_test_sc) # feature is the transformed dataset value (Z)
        return feature_test

    def getKmeans(self, n_cltr, rdm_state):
        kmodel = KMeans(n_clusters= n_cltr, random_state= rdm_state)
        kmodel.fit(self.feature)
        self.kmodel = kmodel
        self.kmodel_labels = kmodel.labels_
        self.kmodel_cluster_centers = kmodel.cluster_centers_
        self.kmodel_inertia = kmodel.inertia_
        print(kmodel.labels_) # kmeans result labels
        #print(kmodel.labels_.shape)
        #print(kmodel.cluster_centers_) # Cluster center coordinates
        #print(kmodel.inertia_) # Sum of squared distances to nearest cluster center
        
        # Create enhanced scatter plot
        plt.figure(figsize=(12, 8))
        scatter = plt.scatter(self.feature[:,0], self.feature[:,1], c=kmodel.labels_, 
                             cmap='viridis', s=100, alpha=0.6, edgecolors='black', linewidth=0.5)
        plt.scatter(kmodel.cluster_centers_[:,0], kmodel.cluster_centers_[:,1],
                   s=500, marker='*', c='red', edgecolors='black', linewidth=2, 
                   label='Cluster Centers', zorder=5)
        
        # Add labels and formatting
        plt.xlabel('First Principal Component (PC1)\n← Lower Values | Higher Values →', 
                  fontsize=14, fontweight='bold')
        plt.ylabel('Second Principal Component (PC2)\n← Lower Values | Higher Values →', 
                  fontsize=14, fontweight='bold')
        plt.title(f'K-Means Clustering Results: {n_cltr} Weather Pattern Clusters\nPCA-Transformed Weather Data (2017 Training Set)\nEach point = 1 day, Colors = Weather clusters', 
                 fontsize=15, fontweight='bold', pad=20)
        cbar = plt.colorbar(scatter, label='Cluster Number')
        cbar.set_label('Cluster Number\n(0 = High Risk)', fontsize=12, fontweight='bold')
        plt.legend(loc='best', fontsize=12, framealpha=0.9, 
                  title='Red Stars = Cluster Centers', title_fontsize=11)
        plt.grid(True, alpha=0.3, linestyle='--')
        plt.tight_layout()
        plt.savefig(os.path.join(RESULTS_DIR, 'kmeans_clusters.png'), dpi=300, bbox_inches='tight')
        plt.show()
        return kmodel.labels_

    def getSVM(self, labels, feature_test):
        for i,val in enumerate(labels):
            if(val > 0):
                labels[i] = 1
        print(labels)
        #df_data['kmeans'] = labels
        #print(df_data['kmeans'])
        svc_model = SVC(gamma='auto')
        svc_model.fit(self.feature, labels)
        svc_predict = svc_model.predict(self.feature)
        print(svc_predict)

        ac_acore = accuracy_score(labels, svc_predict)
        print('Accuracy = %.2f' % (ac_acore))

        cm = confusion_matrix(labels, svc_predict)
        print(cm)
        tn, fp, fn, tp = cm.flatten()
        print('TP: True Positive = %.2f' % tp) # Actual class is positive and prediction is positive (correct)
        print('TN: True Negative = %.2f' % tn) # Actual class is negative and prediction is negative (correct)
        print('FP: False Positive = %.2f' % fp) # Actual class is negative but prediction is positive (incorrect)
        print('FN: False Negative = %.2f' % fn) # Actual class is positive but prediction is negative (incorrect)

        print('Accuracy = %.2f' % (ac_acore))
        print('Precision = %.2f' % (precision_score(labels, svc_predict)))
        print('Recall = %.2f' % recall_score(labels, svc_predict))
        print('F1 = %.2f' % f1_score(labels, svc_predict))
        print(classification_report(labels, svc_predict))

        index = np.where(svc_predict > 0)
        #plt.scatter(self.feature[:, 0], self.feature[:, 1])
        #plt.scatter(self.feature[index, 0], self.feature[index, 1], c='r', label='outlair')

        # Classification on validation data
        svc_predict_test = svc_model.predict(feature_test)
        print(svc_predict_test)
        return svc_predict_test
    
    def getSVM2(self, feature_test): # 20220125 SVM validation (without using risk cluster)
        # Check if there are at least 2 classes in the training labels
        unique_labels = np.unique(self.t_label)
        if len(unique_labels) < 2:
            print(f"Warning: Only {len(unique_labels)} unique class(es) found in training data: {unique_labels}")
            print("Cannot perform SVM classification with less than 2 classes. Skipping getSVM2.")
            return
        
        svc_model = SVC(gamma='auto')
        svc_model.fit(self.feature, self.t_label)
        svc_predict = svc_model.predict(self.feature)
        print(svc_predict)
        ac_acore = accuracy_score(self.t_label, svc_predict)
        print('Accuracy = %.2f' % (ac_acore))

        cm = confusion_matrix(self.t_label, svc_predict)
        print(cm)
        tn, fp, fn, tp = cm.flatten()
        print('TP: True Positive = %.2f' % tp) # Actual class is positive and prediction is positive (correct)
        print('TN: True Negative = %.2f' % tn) # Actual class is negative and prediction is negative (correct)
        print('FP: False Positive = %.2f' % fp) # Actual class is negative but prediction is positive (incorrect)
        print('FN: False Negative = %.2f' % fn) # Actual class is positive but prediction is negative (incorrect)

        print('Accuracy = %.2f' % (ac_acore))
        print('Precision = %.2f' % (precision_score(self.t_label, svc_predict)))
        print('Recall = %.2f' % recall_score(self.t_label, svc_predict))
        print('F1 = %.2f' % f1_score(self.t_label, svc_predict))
        print(classification_report(self.t_label, svc_predict))
        
        # Classification on validation data
        svc_predict_test = svc_model.predict(feature_test)
        print(svc_predict_test)
        sum = len(svc_predict_test)
        for i in svc_predict_test:
            sum -= i
        rate = sum / len(svc_predict_test) * 100
        print('Risk days = %.2f' % sum)
        print('Risk rate = %.2f' % rate)


    def getHistgram(self, df_data, labels):
        df_data['kmeans'] = labels # Add label
        self.saveCSV(df_data, './csv/df_data.csv')
        # Average values of each kmeans cluster
        print("Average value of cluster in actual data")
        print(df_data[df_data['kmeans']==0].mean(numeric_only=True))

        df_data0 = df_data[(df_data['kmeans'] == 0 )] # Extract only risk cluster
        
        # Feature name mappings for better readability
        feature_names = {
            'fx106_03_500spd': 'Wind Speed at 500mb (03 UTC)',
            'WA_700_12_hum': 'Wajima Humidity at 700mb (12 UTC)',
            'fx106_00_500spd': 'Wind Speed at 500mb (00 UTC)',
            'TA_500_12_hum': 'Tokyo Humidity at 500mb (12 UTC)',
            'vis1': 'Visibility Station 1',
            'vis2 ': 'Visibility Station 2',
            'vis3': 'Visibility Station 3',
            'fx502_00_trough': 'Trough Indicator (00 UTC)',
            'fx502_00_alt': 'Altitude Anomaly (00 UTC)',
            'dwp': 'Dew Point Temperature',
            'relh': 'Relative Humidity',
            'fx106_00_500shear': 'Wind Shear at 500mb (00 UTC)',
            'fx106_03_500shear': 'Wind Shear at 500mb (03 UTC)'
        }
        
        graph_list = ['fx106_03_500spd','WA_700_12_hum', 'fx106_00_500spd','TA_500_12_hum','vis1','vis2 ','vis3','fx502_00_trough','fx502_00_alt','dwp','relh','fx106_00_500shear','fx106_03_500shear']
        
        plot_num = 0
        for i in graph_list:
            plot_num += 1
            plt.figure(figsize=(10, 6))
            plt.hist(df_data[i], bins=30, density=True, label="All Days", 
                    color='skyblue', alpha=0.7, edgecolor='black', linewidth=1.2)
            plt.hist(df_data0[i], bins=30, density=True, label="Risk Cluster (Turbulence)", 
                    color='red', alpha=0.5, edgecolor='darkred', linewidth=1.2)
            
            # Get readable name or use original
            readable_name = feature_names.get(i, i)
            
            # Determine appropriate unit based on feature
            if 'spd' in i:
                unit = 'Wind Speed (m/s)'
            elif 'hum' in i or 'relh' in i:
                unit = 'Humidity (%)'
            elif 'vis' in i:
                unit = 'Visibility (km)'
            elif 'temp' in i or 'dwp' in i:
                unit = 'Temperature (°C)'
            elif 'shear' in i:
                unit = 'Wind Shear (1/s)'
            else:
                unit = 'Measurement Value'
            
            plt.xlabel(f'{unit}\n← Lower | Higher →', fontsize=13, fontweight='bold')
            plt.ylabel('Probability Density\n(Higher = More Common)', fontsize=13, fontweight='bold')
            plt.title(f'{readable_name}\n🔵 Blue = All Weather Days | 🔴 Red = Turbulence Risk Days', 
                     fontsize=13, fontweight='bold', pad=15)
            plt.legend(['All Days (Normal Weather)', 'Risk Cluster Days (Turbulence Conditions)'], 
                      loc="best", fontsize=11, framealpha=0.9, 
                      title='Weather Condition Types', title_fontsize=10)
            plt.grid(True, alpha=0.3, linestyle='--', axis='y')
            plt.tight_layout()
            if plot_num == 1:
                plt.savefig(os.path.join(RESULTS_DIR, 'feature_histograms.png'), dpi=300, bbox_inches='tight')
            plt.show()

    def getdf_data_sc(self):
        return self.df_data_sc
    
    def getTtest(self, df_data, labels):
        df_data['kmeans'] = labels # Add label
        df_data_risk = df_data[(df_data['kmeans'] == 0 )] # Extract only risk cluster
        df_data_others = df_data[(df_data['kmeans'] != 0 )] # Extract only non-risk clusters
        graph_list = ['fx106_03_500spd','WA_700_12_hum', 'MA_500_12_hum','fx106_03_500shear']
        # Perform test for homogeneity of variance
        for i in graph_list:
            print(i)
            stat, p = scipy.stats.bartlett(df_data_risk[i], df_data_others[i])
            print('Bartlett p_value = {0}'.format(p))
            if p >= 0.05:
                stat, p = scipy.stats.ttest_ind(df_data_risk[i], df_data_others[i])
                print('T Test p_value = {0}'.format(p))
            elif p < 0.05:
                stat, p = scipy.stats.ttest_ind(df_data_risk[i], df_data_others[i], equal_var=False)
                print('Welch p_value = {0}'.format(p))
    
    def plot_confusion_matrix_heatmap(self, cm, title='Confusion Matrix - SVM Classification'):
        """Enhanced confusion matrix visualization with heatmap"""
        plt.figure(figsize=(10, 8))
        
        # Create heatmap with annotations
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                    xticklabels=['Turbulence Risk\n(Predicted)', 'Safe Weather\n(Predicted)'], 
                    yticklabels=['Turbulence Risk\n(Actual)', 'Safe Weather\n(Actual)'],
                    cbar_kws={'label': 'Number of Days'},
                    linewidths=2, linecolor='black',
                    annot_kws={'size': 16, 'weight': 'bold'})
        
        plt.title(f'{title}\nTop-Left = Correct Risk Detection | Bottom-Right = Correct Safe Detection', 
                 fontsize=14, fontweight='bold', pad=20)
        plt.ylabel('Actual Weather Condition\n(Ground Truth)', fontsize=13, fontweight='bold')
        plt.xlabel('Model Prediction\n(What SVM Classified)', fontsize=13, fontweight='bold')
        
        # Add accuracy text
        accuracy = (cm[0,0] + cm[1,1]) / cm.sum()
        plt.text(1, -0.3, f'Overall Accuracy: {accuracy:.2%}', 
                ha='center', fontsize=13, fontweight='bold',
                transform=plt.gca().transAxes)
        
        plt.tight_layout()
        plt.savefig(os.path.join(RESULTS_DIR, 'confusion_matrix.png'), dpi=300, bbox_inches='tight')
        plt.show()
    
    def plot_pca_variance(self):
        """Visualize PCA variance explained by components"""
        cumsum = np.cumsum(self.explained_variance_ratio)
        n_components = len(self.explained_variance_ratio)
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        # Plot 1: Individual variance
        ax1.bar(range(1, n_components+1), self.explained_variance_ratio, 
               color='steelblue', alpha=0.8, edgecolor='black')
        ax1.set_xlabel('Principal Component Number\n(1st, 2nd, 3rd, etc.)', 
                      fontsize=13, fontweight='bold')
        ax1.set_ylabel('Variance Explained\n(0.0 = 0%, 1.0 = 100%)', 
                      fontsize=13, fontweight='bold')
        ax1.set_title('How Much Information Each Component Captures\nTaller Bar = More Important Component', 
                     fontsize=13, fontweight='bold')
        ax1.grid(True, alpha=0.3, linestyle='--', axis='y')
        
        # Plot 2: Cumulative variance
        ax2.plot(range(1, n_components+1), cumsum, 'bo-', linewidth=2, markersize=8)
        ax2.axhline(y=0.8, color='red', linestyle='--', linewidth=2, 
                   label='80% Goal (Sufficient Information)')
        ax2.fill_between(range(1, n_components+1), cumsum, alpha=0.3, color='blue')
        ax2.set_xlabel('Number of Components Used\n(More components → More information)', 
                      fontsize=13, fontweight='bold')
        ax2.set_ylabel('Total Information Retained\n(0.0 = 0%, 1.0 = 100%)', 
                      fontsize=13, fontweight='bold')
        ax2.set_title('Cumulative Information Capture\nHow much data we keep vs. how many components we use', 
                     fontsize=13, fontweight='bold')
        ax2.legend(fontsize=11, loc='lower right')
        ax2.grid(True, alpha=0.3, linestyle='--')
        ax2.set_ylim([0, 1.05])
        
        # Add annotation for 80% point
        idx_80 = np.argmax(cumsum >= 0.8) + 1
        ax2.annotate(f'{idx_80} components\n{cumsum[idx_80-1]:.1%} variance', 
                    xy=(idx_80, cumsum[idx_80-1]), 
                    xytext=(idx_80+2, cumsum[idx_80-1]-0.15),
                    arrowprops=dict(arrowstyle='->', color='red', lw=2),
                    fontsize=11, fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.7))
        
        plt.tight_layout()
        plt.savefig(os.path.join(RESULTS_DIR, 'pca_variance.png'), dpi=300, bbox_inches='tight')
        plt.show()
        
        print(f"\n📊 PCA Summary:")
        print(f"   Total components: {n_components}")
        print(f"   Components for 80% variance: {idx_80}")
        print(f"   Total variance captured: {cumsum[-1]:.2%}")
    
    def plot_feature_importance(self):
        """Show which weather variables contribute most to principal components"""
        n_show = min(5, len(self.pca.components_))  # Show top 5 PCs
        
        components_df = pd.DataFrame(
            self.pca.components_[:n_show],
            columns=self.df_data_rm.columns,
            index=[f'PC{i+1}' for i in range(n_show)]
        )
        
        # Plot heatmap
        plt.figure(figsize=(16, 8))
        sns.heatmap(components_df, cmap='coolwarm', center=0, 
                   linewidths=0.5, annot=False, 
                   cbar_kws={'label': 'Influence Strength\n(Red=Strong Positive, Blue=Strong Negative)'})
        plt.title('Which Weather Variables Influence Each Principal Component Most?\n🔴 Red = Strong Positive Impact | 🔵 Blue = Strong Negative Impact | ⚪ White = Little Impact', 
                 fontsize=14, fontweight='bold', pad=20)
        plt.xlabel('Weather Measurement Variables\n(Each column = One weather measurement)', 
                  fontsize=13, fontweight='bold')
        plt.ylabel('Principal Components (PCs)\n(Each row = One compressed dimension)', 
                  fontsize=13, fontweight='bold')
        plt.xticks(rotation=45, ha='right', fontsize=9)
        plt.tight_layout()
        plt.savefig(os.path.join(RESULTS_DIR, 'feature_importance.png'), dpi=300, bbox_inches='tight')
        plt.show()
        
        # Show top features for PC1 and PC2
        print("\n🔍 Top 5 Features for PC1:")
        pc1_features = pd.Series(self.pca.components_[0], 
                                index=self.df_data_rm.columns).abs().sort_values(ascending=False)
        for i, (feature, value) in enumerate(pc1_features.head(5).items(), 1):
            print(f"   {i}. {feature}: {value:.4f}")
        
        print("\n🔍 Top 5 Features for PC2:")
        pc2_features = pd.Series(self.pca.components_[1], 
                                index=self.df_data_rm.columns).abs().sort_values(ascending=False)
        for i, (feature, value) in enumerate(pc2_features.head(5).items(), 1):
            print(f"   {i}. {feature}: {value:.4f}")
    
    def cross_validate_model(self, labels, cv=5):
        """Perform cross-validation to assess model generalization"""
        print(f"\n🔄 Performing {cv}-Fold Cross-Validation...")
        
        # Convert labels to binary
        binary_labels = np.where(labels > 0, 1, 0)
        
        svc_model = SVC(gamma='auto')
        cv_scores = cross_val_score(svc_model, self.feature, binary_labels, cv=cv)
        
        plt.figure(figsize=(12, 7))
        bars = plt.bar(range(1, cv+1), cv_scores, color='steelblue', alpha=0.8, edgecolor='black', linewidth=2)
        plt.axhline(y=cv_scores.mean(), color='red', linestyle='--', linewidth=2,
                   label=f'Average Accuracy: {cv_scores.mean():.1%}')
        
        # Add value labels on bars
        for i, (bar, score) in enumerate(zip(bars, cv_scores)):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01, 
                    f'{score:.1%}', ha='center', va='bottom', fontsize=11, fontweight='bold')
        
        plt.xlabel('Test Fold Number\n(Each fold = Different portion of data used for testing)', 
                  fontsize=12, fontweight='bold')
        plt.ylabel('Prediction Accuracy\n(1.0 = 100% Correct, 0.0 = 0% Correct)', 
                  fontsize=12, fontweight='bold')
        plt.title(f'{cv}-Fold Cross-Validation: Testing Model Consistency\nEach bar = Model performance when that fold was used for testing\nHigher & More Consistent = Better Model', 
                 fontsize=13, fontweight='bold', pad=15)
        plt.legend(fontsize=12, loc='lower right')
        plt.ylim([0, 1.1])
        plt.grid(True, alpha=0.3, axis='y', linestyle='--')
        plt.tight_layout()
        plt.savefig(os.path.join(RESULTS_DIR, 'cross_validation.png'), dpi=300, bbox_inches='tight')
        plt.show()
        
        print(f"\n✅ Cross-Validation Results:")
        print(f"   Individual fold scores: {cv_scores}")
        print(f"   Mean accuracy: {cv_scores.mean():.4f}")
        print(f"   Standard deviation: {cv_scores.std():.4f}")
        print(f"   95% Confidence interval: {cv_scores.mean():.4f} ± {1.96*cv_scores.std():.4f}")
        
        return cv_scores
    
    def optimize_svm_parameters(self, labels):
        """Find optimal SVM hyperparameters using grid search"""
        print("\n🔧 Optimizing SVM Hyperparameters (this may take a moment)...")
        
        # Convert labels to binary
        binary_labels = np.where(labels > 0, 1, 0)
        
        param_grid = {
            'C': [0.1, 1, 10, 100],
            'gamma': ['scale', 'auto', 0.001, 0.01, 0.1],
            'kernel': ['rbf', 'poly', 'sigmoid']
        }
        
        grid = GridSearchCV(SVC(), param_grid, cv=5, scoring='accuracy', n_jobs=-1)
        grid.fit(self.feature, binary_labels)
        
        print(f"\n✨ Optimization Complete!")
        print(f"   Best parameters: {grid.best_params_}")
        print(f"   Best cross-validation score: {grid.best_score_:.4f}")
        print(f"   Current model score (default params): {grid.score(self.feature, binary_labels):.4f}")
        
        # Visualize top parameter combinations
        results_df = pd.DataFrame(grid.cv_results_)
        top_10 = results_df.nlargest(10, 'mean_test_score')[['params', 'mean_test_score', 'std_test_score']]
        
        plt.figure(figsize=(14, 9))
        y_pos = np.arange(len(top_10))
        bars = plt.barh(y_pos, top_10['mean_test_score'], 
                xerr=top_10['std_test_score'], color='teal', alpha=0.7, 
                edgecolor='black', linewidth=1.5, error_kw={'linewidth': 2, 'ecolor': 'black'})
        plt.yticks(y_pos, [str(p) for p in top_10['params']], fontsize=9)
        plt.xlabel('Average Accuracy Score\n(0.0 = 0% Correct | 1.0 = 100% Correct)\nError bars show variability', 
                  fontsize=12, fontweight='bold')
        plt.ylabel('Parameter Combinations\n(C=Penalty, gamma=Influence, kernel=Algorithm type)', 
                  fontsize=12, fontweight='bold')
        plt.title('Top 10 Best SVM Parameter Combinations Found\nLonger bars = Better performance | Shorter error bars = More consistent\n🔴 Red line = Best overall combination', 
                 fontsize=13, fontweight='bold', pad=15)
        plt.axvline(x=grid.best_score_, color='red', linestyle='--', linewidth=3,
                   label=f'Best Accuracy: {grid.best_score_:.1%}', zorder=10)
        plt.legend(fontsize=12, loc='lower right')
        plt.grid(True, alpha=0.3, axis='x', linestyle='--')
        plt.xlim([top_10['mean_test_score'].min() - 0.05, 1.05])
        plt.tight_layout()
        plt.savefig(os.path.join(RESULTS_DIR, 'hyperparameter_optimization.png'), dpi=300, bbox_inches='tight')
        plt.show()
        
        return grid.best_estimator_, grid.best_params_