import os
import polars as pl
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report

dataset_url = (
    "https://sacodeassessment.blob.core.windows.net/public/data_set.csv"
    if "dataset.csv" not in os.listdir()
    else "dataset.csv"
)

df_dataset = pl.read_csv(dataset_url)

print(
    df_dataset.select("bought_toon")
    .group_by(by="bought_toon")
    .agg(pl.col("bought_toon").count())
)
exit()
boolean_columns = []
for column, datatype in zip(df_dataset.columns, df_dataset.dtypes):
    print(datatype)
    if datatype == pl.Boolean:
        boolean_columns.append(column)

df_dataset = df_dataset.select(*boolean_columns)


features = df_dataset.drop("bought_toon")
target = df_dataset.select("bought_toon").to_series().to_numpy()

features = features.to_dummies()

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    features, target, test_size=0.3, random_state=42
)

rf_model = RandomForestClassifier(random_state=42, verbose=1)
rf_model.fit(X_train, y_train)

feature_importances = pl.DataFrame(
    {"Feature": features.columns, "Importance": rf_model.feature_importances_}
)
feature_importances = feature_importances.sort(by="Importance", descending=True)

print("Top Features:\n", feature_importances.head())

# Logistic Regression for interpretability
lr_model = LogisticRegression(max_iter=1000, random_state=42)
lr_model.fit(X_train, y_train)

lr_model.fit(X_train, y_train)
coefficients = pl.DataFrame(
    {"Feature": features.columns, "Coefficient": lr_model.coef_[0]}
).sort(by="Coefficient", descending=True)

print(
    "Coefficients:\n",
    coefficients,
)

# Evaluate model
y_pred = lr_model.predict(X_test)
print("Classification Report:\n", classification_report(y_test, y_pred))
