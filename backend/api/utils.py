import pandas as pd
import io

def process_dataset(file_obj, filename):
    """
    Dynamic Parser:
    1. Finds a 'Text' column for the Pie Chart.
    2. Finds ALL 'Numeric' columns for the Stat Boxes.
    """
    try:
        # --- 1. READ FILE ---
        df = None
        name = filename.lower()
        if name.endswith('.csv'): df = pd.read_csv(file_obj)
        elif name.endswith(('.xls', '.xlsx')): df = pd.read_excel(file_obj)
        elif name.endswith('.json'): df = pd.read_json(file_obj)
        else: return {"error": "Unsupported format"}

        response = {
            "total_count": int(len(df)),
            "metrics": [],         # List for Stat Boxes
            "chart_data": {}       # Data for Pie Chart
        }

        # --- 2. DYNAMIC STATS (Find ALL Numeric Columns) ---
        # Select columns that are numbers (float/int)
        numeric_cols = df.select_dtypes(include=['number']).columns
        
        for col in numeric_cols:
            # Skip ID columns or empty ones
            if 'id' in col.lower() or 'index' in col.lower():
                continue
                
            # Calculate Average
            avg_val = df[col].mean()
            
            # Clean up label (e.g., "avg_temp_c" -> "Temp C")
            label = col.replace('_', ' ').title()
            
            # Add to response list
            response['metrics'].append({
                "label": label,
                "value": f"{avg_val:.1f}"
            })

        # --- 3. DYNAMIC CHART (Find Best Text Column) ---
        # Look for a column that describes the 'Category' or 'Item'
        text_cols = df.select_dtypes(include=['object', 'string']).columns
        chart_col = None
        
        # Priority search for "Type", "Name", "Equipment"
        priority_keys = ['type', 'equipment', 'category', 'machine', 'name', 'status']
        
        for key in priority_keys:
            for col in text_cols:
                if key in col.lower():
                    chart_col = col
                    break
            if chart_col: break
        
        # Fallback: Use the first text column found, or "Generic"
        if not chart_col and len(text_cols) > 0:
            chart_col = text_cols[0]
            
        if chart_col:
            # Top 5 categories
            response['chart_data'] = df[chart_col].value_counts().head(5).to_dict()
        else:
            response['chart_data'] = {"Unknown": len(df)}

        return response

    except Exception as e:
        print(f"Error: {e}")
        return {"total_count": 0, "metrics": [], "chart_data": {}, "error": str(e)}