import pandas as pd
import json

df = pd.read_csv(
    r"C:\Users\sanya\Desktop\CRWN102\overture\data\part-00000-a6ae7f2e-7464-4ae1-b770-e53ab6b017b5-c000.csv",
    on_bad_lines="skip"
)

print(df.head())
print(df.columns)

artifact = {
    "total_rows": len(df),
    "columns": list(df.columns),
    "missing_values": df.isna().sum().to_dict()
}

with open(
    r"C:\Users\sanya\Desktop\CRWN102\overture\artifact\data_artifact.json",
    "w"
) as f:
    json.dump(artifact, f, indent=2)

print("Artifact created.")