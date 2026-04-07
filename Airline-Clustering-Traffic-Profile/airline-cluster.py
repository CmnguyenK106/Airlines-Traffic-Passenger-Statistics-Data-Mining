"""
=============================================================
 Airline Clustering by Traffic Profile
 Dataset: Airlines Traffic Passenger Statistics (Kaggle)
=============================================================

ANALYSIS PLAN
--------------
Step 1 : Load & inspect the data
Step 2 : Feature engineering – build one row per airline
Step 3 : Exploratory analysis of airline-level features
Step 4 : Pre-processing (scaling)
Step 5 : Determine optimal k with Elbow + Silhouette score
Step 6 : Fit K-Means clustering
Step 7 : Profile each cluster
Step 8 : Visualise (PCA scatter, radar charts, heatmap, bar charts)
Step 9 : Export results + business interpretation
"""

# ─────────────────────────────────────────────────────────
# 0. IMPORTS
# ─────────────────────────────────────────────────────────
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns

from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score

import warnings
warnings.filterwarnings("ignore")

PALETTE = ["#2196F3", "#FF5722", "#4CAF50", "#9C27B0",
           "#FF9800", "#00BCD4", "#E91E63", "#795548"]

# ─────────────────────────────────────────────────────────
# STEP 1 – LOAD & INSPECT
# ─────────────────────────────────────────────────────────
print("=" * 60)
print("STEP 1 | Load & inspect data")
print("=" * 60)

# ► Update this path to wherever you saved the CSV from Kaggle
df = pd.read_csv("D:\\Data_mining\\assignment\\archive\\Air_Traffic_Passenger_Statistics.csv")

print(f"Shape      : {df.shape}")
print(f"Columns    : {df.columns.tolist()}")
print(f"\nSample rows:\n{df.head(3).to_string()}")

# Standardise column names (some Kaggle versions add extra spaces)
df.columns = df.columns.str.strip().str.replace(" ", "_")

print(f"\nMissing values:\n{df.isnull().sum()}")
print(f"\nUnique airlines : {df['Operating_Airline'].nunique()}")
print(f"Date range      : {df['Activity_Period'].min()} → {df['Activity_Period'].max()}")


# ─────────────────────────────────────────────────────────
# STEP 2 – FEATURE ENGINEERING
# Collapse many rows per airline into a single profile row.
# Features chosen to capture VOLUME, ROUTE MIX, FARE TYPE,
# GEOGRAPHIC REACH, and GROWTH TRAJECTORY.
# ─────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("STEP 2 | Feature engineering – airline-level profile")
print("=" * 60)

pax_col = "Adjusted_Passenger_Count"   # handles imputed missing counts

# ── 2a. Volume features ───────────────────────────────────
agg = (df.groupby("Operating_Airline")
         .agg(
             total_passengers      = (pax_col, "sum"),
             avg_monthly_passengers= (pax_col, "mean"),
             months_active         = (pax_col, "count"),
         )
         .reset_index())

# ── 2b. International vs Domestic mix ────────────────────
geo = (df.groupby(["Operating_Airline", "GEO_Summary"])[pax_col]
         .sum().unstack(fill_value=0).reset_index())
geo.columns.name = None
for col in ["Domestic", "International"]:
    if col not in geo.columns:
        geo[col] = 0
geo["intl_ratio"] = geo["International"] / (geo["Domestic"] + geo["International"] + 1e-9)

# ── 2c. Low-cost carrier share ────────────────────────────
if "Price_Category_Code" in df.columns:
    lcc_flag = df["Price_Category_Code"].str.lower().str.contains("low", na=False)
    lcc = (df.assign(is_low_cost=lcc_flag)
             .groupby("Operating_Airline")
             .agg(lcc_ratio=("is_low_cost", "mean"))
             .reset_index())
else:
    lcc = agg[["Operating_Airline"]].copy(); lcc["lcc_ratio"] = 0.0

# ── 2d. Terminal diversity ────────────────────────────────
if "Terminal" in df.columns:
    term_div = (df.groupby("Operating_Airline")["Terminal"]
                  .nunique().reset_index()
                  .rename(columns={"Terminal": "terminal_diversity"}))
else:
    term_div = agg[["Operating_Airline"]].copy(); term_div["terminal_diversity"] = 1

# ── 2e. Geographic region diversity ──────────────────────
if "GEO_Region" in df.columns:
    reg_div = (df.groupby("Operating_Airline")["GEO_Region"]
                 .nunique().reset_index()
                 .rename(columns={"GEO_Region": "region_diversity"}))
else:
    reg_div = agg[["Operating_Airline"]].copy(); reg_div["region_diversity"] = 1

# ── 2f. Enplane ratio ─────────────────────────────────────
if "Activity_Type_Code" in df.columns:
    act = (df.groupby(["Operating_Airline", "Activity_Type_Code"])[pax_col]
             .sum().unstack(fill_value=0).reset_index())
    act.columns.name = None
    if "Enplaned" in act.columns and "Deplaned" in act.columns:
        act["enplane_ratio"] = act["Enplaned"] / (act["Enplaned"] + act["Deplaned"] + 1e-9)
        act = act[["Operating_Airline", "enplane_ratio"]]
    else:
        act = agg[["Operating_Airline"]].copy(); act["enplane_ratio"] = 0.5
else:
    act = agg[["Operating_Airline"]].copy(); act["enplane_ratio"] = 0.5

# ── 2g. Growth ratio (early-period avg vs late-period avg) ──
df["year"] = df["Activity_Period"].astype(str).str[:4].astype(int)
early_vol = (df[df["year"] <= df["year"].quantile(0.3)]
             .groupby("Operating_Airline")[pax_col].mean().rename("early_avg"))
late_vol  = (df[df["year"] >= df["year"].quantile(0.7)]
             .groupby("Operating_Airline")[pax_col].mean().rename("late_avg"))
growth = pd.concat([early_vol, late_vol], axis=1).fillna(0)
growth["growth_ratio"] = growth["late_avg"] / (growth["early_avg"] + 1e-9)
growth = growth[["growth_ratio"]].reset_index()

# ── Merge into one profile DataFrame ─────────────────────
profile = (agg
           .merge(geo[["Operating_Airline", "intl_ratio"]], on="Operating_Airline", how="left")
           .merge(lcc,      on="Operating_Airline", how="left")
           .merge(term_div, on="Operating_Airline", how="left")
           .merge(reg_div,  on="Operating_Airline", how="left")
           .merge(act,      on="Operating_Airline", how="left")
           .merge(growth,   on="Operating_Airline", how="left"))

profile.fillna(0, inplace=True)
profile.set_index("Operating_Airline", inplace=True)

print(f"Airline feature matrix: {profile.shape}")
print(profile.head())


# ─────────────────────────────────────────────────────────
# STEP 3 – EXPLORATORY ANALYSIS
# ─────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("STEP 3 | Exploratory analysis")
print("=" * 60)

plot_feats = [
    ("total_passengers",   "Total Passengers"),
    ("intl_ratio",         "International Ratio"),
    ("lcc_ratio",          "Low-Cost Ratio"),
    ("terminal_diversity", "Terminal Diversity"),
    ("region_diversity",   "Region Diversity"),
    ("growth_ratio",       "Growth Ratio"),
]

fig, axes = plt.subplots(2, 3, figsize=(16, 9))
fig.suptitle("Airline Feature Distributions", fontsize=14)
for ax, (feat, label) in zip(axes.flat, plot_feats):
    ax.hist(profile[feat], bins=20, color="#2196F3", edgecolor="white", alpha=0.85)
    ax.set_title(label, fontsize=11)
    ax.set_ylabel("# Airlines")
    ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout()
plt.savefig("01_feature_distributions.png", dpi=150, bbox_inches="tight")
plt.show()
print("Saved → 01_feature_distributions.png")

# Correlation heatmap
fig, ax = plt.subplots(figsize=(9, 7))
corr = profile[[f for f, _ in plot_feats]].corr()
sns.heatmap(corr, mask=np.triu(np.ones_like(corr, dtype=bool)),
            annot=True, fmt=".2f", cmap="RdBu_r", center=0,
            linewidths=0.5, ax=ax)
ax.set_title("Feature Correlation Matrix", fontsize=13)
plt.tight_layout()
plt.savefig("02_correlation_heatmap.png", dpi=150, bbox_inches="tight")
plt.show()
print("Saved → 02_correlation_heatmap.png")


# ─────────────────────────────────────────────────────────
# STEP 4 – PRE-PROCESSING (StandardScaler)
# ─────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("STEP 4 | Scaling features")
print("=" * 60)

features_for_clustering = [
    "total_passengers", "intl_ratio", "lcc_ratio",
    "terminal_diversity", "region_diversity",
    "enplane_ratio", "growth_ratio"
]

X = profile[features_for_clustering].values
X_scaled = StandardScaler().fit_transform(X)
print(f"Scaled matrix: {X_scaled.shape}  |  mean≈{X_scaled.mean():.3f}  std≈{X_scaled.std():.3f}")


# ─────────────────────────────────────────────────────────
# STEP 5 – OPTIMAL k  (Elbow + Silhouette)
# ─────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("STEP 5 | Elbow method & Silhouette score")
print("=" * 60)

k_range = range(2, min(10, len(profile)))
inertias, silhouettes = [], []

for k in k_range:
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = km.fit_predict(X_scaled)
    inertias.append(km.inertia_)
    sil = silhouette_score(X_scaled, labels)
    silhouettes.append(sil)
    print(f"  k={k}  inertia={km.inertia_:>10.1f}  silhouette={sil:.4f}")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
ax1.plot(list(k_range), inertias, "o-", color="#2196F3", linewidth=2)
ax1.set_title("Elbow Curve")
ax1.set_xlabel("k"); ax1.set_ylabel("Inertia (WCSS)")
ax1.spines[["top", "right"]].set_visible(False)

ax2.plot(list(k_range), silhouettes, "s-", color="#FF5722", linewidth=2)
ax2.set_title("Silhouette Score")
ax2.set_xlabel("k"); ax2.set_ylabel("Score")
ax2.spines[["top", "right"]].set_visible(False)

plt.tight_layout()
plt.savefig("03_elbow_silhouette.png", dpi=150, bbox_inches="tight")
plt.show()
print("Saved → 03_elbow_silhouette.png")

best_k = list(k_range)[silhouettes.index(max(silhouettes))]
print(f"\n✔ Best k (highest silhouette) = {best_k}")


# ─────────────────────────────────────────────────────────
# STEP 6 – FIT FINAL K-MEANS
# ─────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print(f"STEP 6 | Fitting K-Means  k={best_k}")
print("=" * 60)

km_final = KMeans(n_clusters=best_k, random_state=42, n_init=20)
profile["Cluster"] = km_final.fit_predict(X_scaled)

sizes = profile["Cluster"].value_counts().sort_index()
print("Cluster sizes:\n", sizes.to_string())


# ─────────────────────────────────────────────────────────
# STEP 7 – CLUSTER PROFILING
# ─────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("STEP 7 | Cluster profiles")
print("=" * 60)

cluster_profile = profile.groupby("Cluster")[features_for_clustering].mean()
print(cluster_profile.round(3).to_string())

print("\nAirlines per cluster:")
for c in sorted(profile["Cluster"].unique()):
    airlines = sorted(profile[profile["Cluster"] == c].index.tolist())
    print(f"\n  Cluster {c}  ({len(airlines)} airlines):")
    for a in airlines:
        print(f"    • {a}")


# ─────────────────────────────────────────────────────────
# STEP 8a – PCA SCATTER PLOT
# ─────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("STEP 8a | PCA 2-D scatter")
print("=" * 60)

pca = PCA(n_components=2, random_state=42)
X_pca = pca.fit_transform(X_scaled)
profile["PC1"] = X_pca[:, 0]
profile["PC2"] = X_pca[:, 1]
ev = pca.explained_variance_ratio_ * 100
print(f"Variance explained: PC1={ev[0]:.1f}%  PC2={ev[1]:.1f}%")

fig, ax = plt.subplots(figsize=(12, 8))
for c in sorted(profile["Cluster"].unique()):
    m = profile["Cluster"] == c
    ax.scatter(profile.loc[m, "PC1"], profile.loc[m, "PC2"],
               s=120, color=PALETTE[c % len(PALETTE)],
               edgecolors="white", linewidths=0.8, alpha=0.9)
    for airline, row in profile[m].iterrows():
        ax.annotate(airline, (row["PC1"], row["PC2"]),
                    fontsize=7, ha="center", va="bottom",
                    xytext=(0, 5), textcoords="offset points", alpha=0.8)

handles = [mpatches.Patch(color=PALETTE[c % len(PALETTE)], label=f"Cluster {c}")
           for c in sorted(profile["Cluster"].unique())]
ax.legend(handles=handles, loc="best", framealpha=0.7)
ax.set_xlabel(f"PC1 ({ev[0]:.1f}% variance)")
ax.set_ylabel(f"PC2 ({ev[1]:.1f}% variance)")
ax.set_title("K-Means Airline Clusters – PCA Projection", fontsize=14)
ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout()
plt.savefig("04_pca_clusters.png", dpi=150, bbox_inches="tight")
plt.show()
print("Saved → 04_pca_clusters.png")


# ─────────────────────────────────────────────────────────
# STEP 8b – RADAR (SPIDER) CHARTS
# ─────────────────────────────────────────────────────────
print("\nSTEP 8b | Radar charts")

radar_data = cluster_profile.copy()
for col in radar_data.columns:
    cmin, cmax = radar_data[col].min(), radar_data[col].max()
    radar_data[col] = (radar_data[col] - cmin) / (cmax - cmin + 1e-9)

feature_labels = ["Total\nPax", "Intl\nRatio", "LCC\nRatio",
                  "Terminal\nDiv", "Region\nDiv", "Enplane\nRatio", "Growth\nRatio"]
n = len(feature_labels)
angles = np.linspace(0, 2 * np.pi, n, endpoint=False).tolist() + \
         np.linspace(0, 2 * np.pi, n, endpoint=False).tolist()[:1]

fig, axes = plt.subplots(1, best_k, figsize=(5 * best_k, 5),
                         subplot_kw=dict(polar=True))
if best_k == 1:
    axes = [axes]

for c, ax in zip(sorted(radar_data.index), axes):
    vals = radar_data.loc[c].tolist() + radar_data.loc[c].tolist()[:1]
    color = PALETTE[c % len(PALETTE)]
    ax.plot(angles, vals, color=color, linewidth=2)
    ax.fill(angles, vals, color=color, alpha=0.25)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(feature_labels, fontsize=8)
    ax.set_yticks([0.25, 0.5, 0.75, 1.0])
    ax.set_yticklabels(["0.25", "0.5", "0.75", "1.0"], fontsize=6)
    ax.set_title(f"Cluster {c}  ({sizes[c]} airlines)",
                 fontsize=12, pad=15, color=color, fontweight="bold")

fig.suptitle("Cluster Traffic Profile (Normalised)", fontsize=13, y=1.02)
plt.tight_layout()
plt.savefig("05_radar_charts.png", dpi=150, bbox_inches="tight")
plt.show()
print("Saved → 05_radar_charts.png")


# ─────────────────────────────────────────────────────────
# STEP 8c – CLUSTER × FEATURE HEATMAP
# ─────────────────────────────────────────────────────────
print("STEP 8c | Cluster × feature heatmap")

fig, ax = plt.subplots(figsize=(11, 4))
sns.heatmap(cluster_profile.T,
            annot=True, fmt=".2f", cmap="YlOrRd",
            linewidths=0.5, ax=ax,
            xticklabels=[f"Cluster {c}" for c in cluster_profile.index],
            yticklabels=feature_labels)
ax.set_title("Cluster × Feature Heatmap (Mean Values)", fontsize=13)
plt.tight_layout()
plt.savefig("06_cluster_heatmap.png", dpi=150, bbox_inches="tight")
plt.show()
print("Saved → 06_cluster_heatmap.png")


# ─────────────────────────────────────────────────────────
# STEP 8d – TOP AIRLINES PER CLUSTER BAR CHART
# ─────────────────────────────────────────────────────────
print("STEP 8d | Top airlines per cluster")

fig, axes = plt.subplots(1, best_k, figsize=(6 * best_k, 5))
if best_k == 1:
    axes = [axes]

for c, ax in zip(sorted(profile["Cluster"].unique()), axes):
    top = (profile[profile["Cluster"] == c]
           .sort_values("total_passengers", ascending=False)
           .head(10))
    ax.barh(top.index[::-1], top["total_passengers"].values[::-1] / 1e6,
            color=PALETTE[c % len(PALETTE)], edgecolor="white", alpha=0.85)
    ax.set_title(f"Cluster {c} – Top Airlines", fontsize=11)
    ax.set_xlabel("Total Passengers (millions)")
    ax.spines[["top", "right"]].set_visible(False)

plt.tight_layout()
plt.savefig("07_top_airlines_per_cluster.png", dpi=150, bbox_inches="tight")
plt.show()
print("Saved → 07_top_airlines_per_cluster.png")


# ─────────────────────────────────────────────────────────
# STEP 9 – EXPORT + BUSINESS INTERPRETATION
# ─────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("STEP 9 | Export results")
print("=" * 60)

profile.drop(columns=["PC1", "PC2"]).reset_index().to_csv(
    "airline_clusters.csv", index=False)
cluster_profile.to_csv("cluster_profiles.csv")
print("Saved → airline_clusters.csv")
print("Saved → cluster_profiles.csv")

print("\n" + "=" * 60)
print("BUSINESS INTERPRETATION (auto-generated)")
print("=" * 60)

for c in sorted(cluster_profile.index):
    row = cluster_profile.loc[c]
    print(f"\n── Cluster {c} ──────────────────────────────")
    tags = []
    if row["total_passengers"] == cluster_profile["total_passengers"].max():
        tags.append("Dominant carrier (highest volume)")
    elif row["total_passengers"] == cluster_profile["total_passengers"].min():
        tags.append("Niche / small carrier (lowest volume)")
    if row["intl_ratio"] > 0.6:
        tags.append("Primarily international routes")
    elif row["intl_ratio"] < 0.3:
        tags.append("Primarily domestic routes")
    if row["lcc_ratio"] > 0.5:
        tags.append("Low-cost carrier focus")
    if row["growth_ratio"] > 1.5:
        tags.append("High growth trajectory")
    elif row["growth_ratio"] < 0.8:
        tags.append("Declining or stagnant traffic")
    if row["region_diversity"] > cluster_profile["region_diversity"].median():
        tags.append("Wide geographic reach")
    if not tags:
        tags.append("Mixed / mid-tier profile")
    for t in tags:
        print(f"  ✓ {t}")

print("\n" + "=" * 60)
print("Analysis complete!")
print("=" * 60)