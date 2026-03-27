from pydantic import BaseModel, Field
from typing import List, Optional, Any

class Condition(BaseModel):
    column: str = Field(description="The exact column name to filter on. Example: 'Budget (INR)', 'Property Type', 'Location', 'Last Call Status'")
    operator: str = Field(description="The operator for filtering: '==', '!=', '>', '<', '>=', '<=', 'contains'")
    value: Any = Field(description="The value to filter by. Ensure correct typing (number for Budget, string for Location).")

class QueryIntent(BaseModel):
    intent_type: str = Field(description="Type of query: 'filter' (list rows), 'filter_count' (count rows), 'average', 'sum', 'min', 'max', 'summary'")
    conditions: List[Condition] = Field(default_factory=list, description="List of conditions to apply to the data. Keep empty if no filters are needed.")
    target_column: Optional[str] = Field(default=None, description="The column to perform the aggregation on. Should be a numerical column for math ops.")

COLUMNS_SCHEMA = """
Available Columns:
1. 'Name' (string) - Customer Name
2. 'Budget (INR)' (numerical) - Customer Budget. e.g. 9000000 for 90 Lakhs
3. 'Property Type' (string) - Category of property, e.g., '1BHK', '2BHK', '3BHK', '4BHK'
4. 'Location' (string) - Specific locations in Pune, e.g., 'Kharadi', 'Hinjewadi', 'Hadapsar', 'Wakad'
5. 'Contact' (string/number) - Phone number
6. 'Expected Possession' (string/date) - Date of possession, e.g., 'Jun 2026'
7. 'Last Call Status' (string) - E.g., 'Busy', 'Connected', 'Not Reachable', 'Ringing'
8. 'Last Call Connected Time' (string) - formatting 'DD-MM-YYYY HH:MM'
"""
