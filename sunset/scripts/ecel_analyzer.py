import pandas as pd
import sys

def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze_columns.py <filename.xlsx>")
        sys.exit(1)

    filename = sys.argv[1]
    sheet_name = 'Consciousness Enhanced Jobs'

    try:
        df = pd.read_excel(filename, sheet_name=sheet_name)
    except Exception as e:
        print(f"Error loading file or sheet: {e}")
        sys.exit(1)

    def analyze_column(col):
        non_null = col.dropna()
        if non_null.empty:
            return 'Empty'
        elif non_null.nunique() == 1:
            return f'All Same ({non_null.iloc[0]})'
        else:
            return 'Varied'

    results = df.apply(analyze_column)
    print("\nColumn Analysis Results:")
    print(results)

if __name__ == "__main__":
    main()
