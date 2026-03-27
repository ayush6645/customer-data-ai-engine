import pandas as pd
from typing import Any
from utils import QueryIntent

def apply_conditions(df: pd.DataFrame, intent: QueryIntent) -> pd.DataFrame:
    """Applies the parsed conditions to filter the dataframe."""
    filtered_df = df.copy()
    
    for cond in intent.conditions:
        col = cond.column
        op = cond.operator
        val = cond.value
        
        # Verify column exists
        if col not in filtered_df.columns:
            # Try to handle case-sensitivity or spaces
            matched_cols = [c for c in filtered_df.columns if c.lower() == col.lower()]
            if matched_cols:
                col = matched_cols[0]
            else:
                continue
            
        try:
            if op == '==':
                 if isinstance(val, str):
                     filtered_df = filtered_df[filtered_df[col].astype(str).str.lower() == val.lower()]
                 else:
                     filtered_df = filtered_df[filtered_df[col] == val]
            elif op == '!=':
                 filtered_df = filtered_df[filtered_df[col] != val]
            elif op in ['>', '<', '>=', '<=', 'near']:
                try:
                    if op == 'near':
                        raise ValueError("Force datetime parsing for near")
                    # Try numeric comparison
                    float_val = float(val)
                    numeric_col = pd.to_numeric(filtered_df[col], errors='coerce')
                    if op == '>': filtered_df = filtered_df[numeric_col > float_val]
                    elif op == '<': filtered_df = filtered_df[numeric_col < float_val]
                    elif op == '>=': filtered_df = filtered_df[numeric_col >= float_val]
                    elif op == '<=': filtered_df = filtered_df[numeric_col <= float_val]
                except ValueError:
                    # Try datetime comparison
                    dt_col = pd.to_datetime(filtered_df[col], errors='coerce', dayfirst=True)
                    dt_val = pd.to_datetime(val, dayfirst=True)
                    if op == '>': filtered_df = filtered_df[dt_col > dt_val]
                    elif op == '<': filtered_df = filtered_df[dt_col < dt_val]
                    elif op == '>=': filtered_df = filtered_df[dt_col >= dt_val]
                    elif op == '<=': filtered_df = filtered_df[dt_col <= dt_val]
                    elif op == 'near':
                        filtered_df = filtered_df[abs(dt_col - dt_val) <= pd.Timedelta(days=7)]
            elif op == 'contains':
                filtered_df = filtered_df[filtered_df[col].astype(str).str.contains(str(val), case=False, na=False)]
        except Exception as e:
            print(f"Warning: Failed to apply condition {col} {op} {val}. Error: {e}")
            
    return filtered_df

def execute_query(intent: QueryIntent, df: pd.DataFrame) -> tuple[Any, pd.DataFrame]:
    """Executes the intent against the dataframe and returns (result_text, filtered_dataframe)."""
    if df.empty:
        return "The dataset is empty.", pd.DataFrame()
        
    filtered_df = apply_conditions(df, intent)
    
    if filtered_df.empty:
        return "No entries found matching those criteria.", pd.DataFrame()

    itype = intent.intent_type.lower()
    
    if itype == 'filter_count':
        return f"Found {len(filtered_df)} matching records.", filtered_df
        
    elif itype in ['average', 'sum', 'min', 'max']:
        target = intent.target_column
        if not target or target not in filtered_df.columns:
            if 'Budget (INR)' in filtered_df.columns:
                target = 'Budget (INR)'
            else:
                return "Error: Target column for math operation not specified or found.", filtered_df
        
        numeric_series = pd.to_numeric(filtered_df[target], errors='coerce').dropna()
        if numeric_series.empty:
            return f"Cannot perform {itype} on {target} because it contains no numeric data.", filtered_df
            
        if itype == 'average':
            res = numeric_series.mean()
        elif itype == 'sum':
            res = numeric_series.sum()
        elif itype == 'min':
            res = numeric_series.min()
        elif itype == 'max':
            res = numeric_series.max()
            
        return f"The {itype} of {target} is {res:,.2f}", filtered_df

    elif itype == 'summary':
        summary_info = [f"Total entities matching criteria: {len(filtered_df)}"]
        if 'Location' in filtered_df.columns:
            summary_info.append("Locations: " + ", ".join(filtered_df['Location'].value_counts().head(4).index))
        if 'Property Type' in filtered_df.columns:
            summary_info.append("Property Types: " + ", ".join(filtered_df['Property Type'].value_counts().head(4).index))
        return "\n".join(summary_info), filtered_df
        
    else: # 'filter' or any other
        # Return full dataframe natively for the UI to display as a table
        return f"Found {len(filtered_df)} matched records for the table display.", filtered_df
