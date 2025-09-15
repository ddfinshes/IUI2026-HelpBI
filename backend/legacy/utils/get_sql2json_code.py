import sqlparse
import json
from typing import List, Dict, Any

class SQLToJSONConverter:
    def __init__(self):
        self.virtual_tables = set()

    def capitalize_keyword(self, keyword: str) -> str:
        """Capitalize the first letter and lowercase the rest."""
        return keyword.capitalize()

    def process_select_content(self, tokens: List[sqlparse.sql.Token], parent_tokens=None) -> List[Dict[str, Any]]:
        """Process SELECT clause content, handling columns, aliases, and subqueries."""
        content = []
        current = ""
        subquery_depth = 0

        for token in tokens:
            if token.ttype is sqlparse.tokens.Punctuation and token.value == '(':
                subquery_depth += 1
            elif token.ttype is sqlparse.tokens.Punctuation and token.value == ')':
                subquery_depth -= 1

            if subquery_depth > 0 or (token.value == '(' and subquery_depth == 1):
                current += token.value
                continue

            if token.ttype is sqlparse.tokens.Punctuation and token.value == ',' and subquery_depth == 0:
                content.append(self.parse_column(current.strip()))
                current = ""
            else:
                current += token.value

        if current.strip():
            content.append(self.parse_column(current.strip()))

        return content

    def parse_column(self, column_str: str) -> Dict[str, Any]:
        """Parse a single column expression into column_name and column_processing."""
        column_str = column_str.strip()
        result = {"column_name": "", "column_processing": ""}

        if " AS " in column_str.upper():
            parts = column_str.rsplit(" AS ", 1)
            result["column_name"] = parts[1].strip()
            result["column_processing"] = column_str.strip()
        elif column_str.upper().startswith("DISTINCT "):
            result["column_name"] = column_str.strip()
            result["column_processing"] = column_str.strip()
        elif "(" in column_str and "SELECT" in column_str.upper():
            # Handle subquery in SELECT
            subquery = sqlparse.parse(column_str)[0]
            result["column_name"] = column_str.strip()
            result["column_processing"] = column_str.strip()
            result["sub_select"] = True
            result["sub_scratched_content"] = self.process_sql(subquery)
        else:
            result["column_name"] = column_str.strip()
            result["column_processing"] = ""

        return result

    def process_from_content(self, tokens: List[sqlparse.sql.Token]) -> List[Dict[str, str]]:
        """Process FROM clause content."""
        table_name = " ".join(str(t) for t in tokens).strip()
        return [{"table_name": table_name, "is_virtual_table": "True" if table_name in self.virtual_tables else "False"}]

    def process_generic_content(self, tokens: List[sqlparse.sql.Token]) -> List[Dict[str, str]]:
        """Process WHERE, GROUP BY, HAVING, ORDER BY, JOIN content."""
        content = " ".join(str(t) for t in tokens).strip()
        return [{"content": content}]

    def process_sql(self, parsed: sqlparse.sql.Statement) -> List[Dict[str, Any]]:
        """Process a single SQL statement or CTE into sql_content structure."""
        sql_content = []
        current_keyword = None
        current_tokens = []

        for token in parsed.tokens:
            if token.is_keyword and token.value.upper() in {"SELECT", "FROM", "WHERE", "GROUP BY", "JOIN", "HAVING", "ORDER BY"}:
                if current_keyword and current_tokens:
                    sql_content.append(self.process_clause(current_keyword, current_tokens))
                current_keyword = token.value.upper()
                current_tokens = []
            elif token.is_group or token.ttype not in {sqlparse.tokens.Whitespace, sqlparse.tokens.Punctuation}:
                current_tokens.append(token)

        if current_keyword and current_tokens:
            sql_content.append(self.process_clause(current_keyword, current_tokens))

        return sql_content

    def process_clause(self, keyword: str, tokens: List[sqlparse.sql.Token]) -> Dict[str, Any]:
        """Process a single SQL clause based on its keyword."""
        keyword = "Group By" if keyword.upper() == "GROUP BY" else "Order By" if keyword.upper() == "ORDER BY" else self.capitalize_keyword(keyword)
        if keyword == "Select":
            scratched_content = self.process_select_content(tokens)
        elif keyword == "From":
            scratched_content = self.process_from_content(tokens)
        else:
            scratched_content = self.process_generic_content(tokens)
        return {"keywords": keyword, "scratched_content": scratched_content}

    def convert(self, sql: str) -> Dict[str, List[Dict[str, Any]]]:
        """Convert SQL string to the specified JSON format."""
        if not sql.strip():
            return {"content": []}

        parsed = sqlparse.parse(sql)[0]
        result = []

        # Handle CTEs
        if parsed.tokens and parsed.tokens[0].value.upper() == "WITH":
            cte_tokens = parsed.tokens[2] if len(parsed.tokens) > 2 else None
            main_query_start = None
            for i, token in enumerate(parsed.tokens[4:], start=4):
                if token.is_keyword and token.value.upper() == "SELECT":
                    main_query_start = i
                    break

            if cte_tokens and isinstance(cte_tokens, sqlparse.sql.TokenList):
                ctes = []
                current_cte = {"name": "", "tokens": []}
                depth = 0

                for token in cte_tokens.tokens:
                    if token.value == '(':
                        depth += 1
                    elif token.value == ')':
                        depth -= 1
                    elif token.value == ',' and depth == 0:
                        ctes.append(current_cte)
                        current_cte = {"name": "", "tokens": []}
                    elif depth == 0 and token.ttype is sqlparse.tokens.Name:
                        current_cte["name"] = token.value
                    elif depth > 0:
                        current_cte["tokens"].append(token)

                ctes.append(current_cte)

                for cte in ctes:
                    cte_sql = sqlparse.sql.Statement(cte["tokens"])
                    self.virtual_tables.add(cte["name"])
                    result.append({
                        "created_virtual_table": "True",
                        "virtual_table_name": cte["name"],
                        "sql_content": self.process_sql(cte_sql)
                    })

            # Main query
            main_query_tokens = parsed.tokens[main_query_start:] if main_query_start else []
            main_query = sqlparse.sql.Statement(main_query_tokens)
            result.insert(0, {
                "created_virtual_table": "False",
                "sql_content": self.process_sql(main_query)
            })
        else:
            # No CTEs, just main query
            result.append({
                "created_virtual_table": "False",
                "sql_content": self.process_sql(parsed)
            })

        return {"content": result}

def sql_to_json(sql: str) -> str:
    """Convert SQL to JSON string."""
    converter = SQLToJSONConverter()
    result = converter.convert(sql)
    return json.dumps(result, indent=2, ensure_ascii=False)

# Example usage
if __name__ == "__main__":
    # Example 1: SQL without CTE
    sql1 = """
    SELECT
        country,
        SUM(amt_notax) AS sales_notax,
        SUM(lw_amt_notax) AS sales_notax_LW,
        CASE
            WHEN SUM(COALESCE(lw_amt_notax, 0)) = 0 THEN 0
            ELSE SUM(amt_notax) / SUM(COALESCE(lw_amt_notax, 0)) - 1
        END AS sales_notax_wow_per,
        SUM(traffic) AS traffic,
        SUM(lw_traffic) AS traffic_LW,
        CASE
            WHEN SUM(COALESCE(lw_traffic, 0)) = 0 THEN 0
            ELSE SUM(traffic) / SUM(COALESCE(lw_traffic, 0)) - 1
        END AS traffic_wow_per
    FROM
        dm_fact_sales_chatbi
    WHERE
        date_code BETWEEN '2025-02-23' AND '2025-02-24'
    GROUP BY
        country
    HAVING
        sales_notax_wow_per < 0
    ORDER BY
        sales_notax_wow_per;
    """

    # Example 2: SQL with CTE
    sql2 = """
    WITH
        Sep2024Transactions AS (
            SELECT * FROM dm_member_sales_chatbi
            WHERE transaction_date BETWEEN '2024-09-01' AND '2024-09-30'
        ),
        Sep2024FirstTimeCustomers AS (
            SELECT DISTINCT member_code FROM Sep2024Transactions
            WHERE member_code NOT IN (SELECT member_code FROM dm_member_sales_chatbi)
        )
    SELECT
        (SELECT COUNT(DISTINCT member_code) FROM Sep2024FirstTimeCustomers) AS Sep2024NewMembers;
    """

    print("Example 1 Result:")
    print(sql_to_json(sql1))
    print("\nExample 2 Result:")
    print(sql_to_json(sql2))