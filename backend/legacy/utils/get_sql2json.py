# 处理sql代码为前端需要的格式
from .get_llm import llm
import json
def sql2json(user_input):
    prompt_system = "You are now an experienced programmer. You know a lot about sql code (especially postgresql code), json and python dictionary formats, front-end and back-end data interactions, and so."
    prompt_assistant = "Data Processor"
    prompt_user ="""
        ### Task Instructions
        You need to convert the user-provided SQL code into a specific JSON format to facilitate visualization operations on the frontend. The converted JSON should accurately reflect the structure of the SQL query, including keywords such as `SELECT`, `FROM`, `WHERE`, `GROUP BY`, `JOIN`, `HAVING`, `ORDER BY`, as well as Common Table Expressions (CTEs) defined using `WITH AS`. Below are the detailed processing rules and output requirements:
        #### Output Structure
        The output is a **list of JSON objects**:
        1. **Main Query JSON**: Always included, with `"created_virtual_table": "False"`, indicating that the main query itself does not create a virtual table.
        2. **CTE JSON**: For each CTE in the SQL, create a separate JSON object with `"created_virtual_table": "True"` and specify `"virtual_table_name": "<CTE name>"`.
        Each JSON object contains the following fields:
        - `"created_virtual_table"`: `"True"` indicates a CTE; `"False"` indicates the main query.
        - `"virtual_table_name"`: Appears only in CTEs, representing the CTE’s name.
        - `"sql_content"`: An array describing the structured content of this SQL section.

        #### Handling CTEs
        - If the SQL begins with `WITH`, it indicates the presence of CTEs. For each CTE (e.g., `WITH CTE1 AS (...)`), generate a JSON object.
        - The order of CTE definitions should be reflected in the output list: the main query JSON is placed first, followed by CTE JSON objects in their definition order.
        - When referencing other CTEs in the `FROM` or `JOIN` of the main query or a CTE, correctly set `"is_virtual_table": "True"`.

        #### `sql_content` Structure
        `"sql_content"` is an array where each element corresponds to a keyword and its content in the SQL:
        - `"keywords"`: The SQL keyword, with the first letter capitalized and the rest in lowercase (e.g., `"Select"`, `"From"`, `"Where"`, `"Group By"`, `"Join"`, `"Having"`, `"Order By"`). Note, "SELECT DISTINCT" keywords are still "Select".
        - `"scratched_content"`: An array storing the specific content corresponding to that keyword.

        ##### 1. `"Select"`
        - `"scratched_content"` is an array, with each element representing a selected column:
        - `"column_name"`: If there is an `AS`, use the alias after `AS`; otherwise, use the column name itself.
        - `"column_processing"`: If there is an `AS`, record the full expression before `AS`; if no `AS`, use an empty string `""`.
        - `"SELECT DISTINCT"` keywords are still "Select".
        - **Example**:
            - SQL: `SUM(amt_notax) AS sales_notax`
            - JSON: `{"column_name": "sales_notax", "column_processing": "SUM(amt_notax) AS sales_notax"}`
            - SQL: `country`
            - JSON: `{"column_name": "country", "column_processing": ""}`
            - SQL: `SELECT DISTINCT country`
            - JSON: `{"column_name": "country", "column_processing": "DISTINCT country"}`
        - When a `"SELECT"` clause contains a subquery (identified by parentheses enclosing a `"SELECT"` statement), add the following fields to the "scratched_content" object for that column:
            - "sub_select": Set to "True" to indicate the presence of a nested sub-SELECT; otherwise, omit this field or set to "False".
            - "sub_scratched_content": An array that describes the structure of the nested subquery, following the same "keywords" and "scratched_content" structure as the top-level "sql_content".
            - Structure of "sub_scratched_content"
                - "sub_scratched_content" mirrors the "sql_content" structure, containing objects with:
                - "keywords": The subquery’s keywords (e.g., "Select", "From", "Where", etc.).
                - "scratched_content": The processed content for each keyword within the subquery.
            - **Example**:
                - Subquery: ```sql (SELECT COUNT(DISTINCT member_code) FROM Sep2024FirstTimeCustomers) ```
                - JSON: ```json
                    [
                    {
                        "keywords": "Select",
                        "scratched_content": [
                        {"column_name": "COUNT(DISTINCT member_code)", "column_processing": "COUNT(DISTINCT member_code)"}
                        ]
                    },
                    {
                        "keywords": "From",
                        "scratched_content": [
                        {"table_name": "Sep2024FirstTimeCustomers", "is_virtual_table": "True"}
                        ]
                    }
                    ]
                ```
        ##### 2. `"From"`
        - `"scratched_content"` is an array, typically containing one object representing the queried table:
        - `"table_name"`: The table name or CTE name (including aliases, e.g., `Effi_Comparison c`).
        - `"is_virtual_table"`: `"True"` if the table is a CTE defined in the SQL; `"False"` if it is a real table.
        - **Example**:
            - SQL: `FROM dm_fact_sales_chatbi`
            - JSON: `{"table_name": "dm_fact_sales_chatbi", "is_virtual_table": "False"}`
            - SQL: `FROM Monthly_Growth`
            - JSON: `{"table_name": "Monthly_Growth", "is_virtual_table": "True"}`

        ##### 3. `"Join"`, `"Where"`, `"Group By"`, `"Having"`, `"Order By"`
        - `"scratched_content"` is an array, typically containing one object:
        - `"content"`: The full SQL operation content for that keyword, preserving multi-line formatting.
        - **Example**:
            - SQL: `WHERE date_code <= '2024-10-31' AND country = 'Mainland'`
            - JSON: `{"content": "date_code <= '2024-10-31' AND country = 'Mainland'"}`
            - SQL: `JOIN Effi_Comparison p ON c.month_id = p.month_id`
            - JSON: `{"content": "JOIN Effi_Comparison p ON c.month_id = p.month_id"}`

        #### Processing Workflow
        1. **Identify CTEs**:
        - Check if the SQL starts with `WITH`. If so, extract each CTE (e.g., `Store_effi AS (...)`).
        - Generate a JSON object for each CTE, setting `"created_virtual_table": "True"` and `"virtual_table_name"`.
        2. **Handle the Main Query**:
        - Extract the main query after `WITH` (e.g., `SELECT ... FROM ...`), and generate a JSON object with `"created_virtual_table": "False"`.
        3. **Parse SQL Content**:
        - For the main query and each CTE, parse their SQL structure, identify keywords, and populate `"sql_content"`.
        - For `SELECT`, extract column names and processing operations individually.
        - For `FROM`, determine the table name and check if it is a virtual table.
        - For other keywords, record the full operation content directly.
        4. **Organize Output**:
        - Place the main query JSON at the start of the list, followed by CTE JSON objects in their definition order.

        #### Notes
        - **Keyword Format**: Must be capitalized with the first letter and lowercase for the rest (e.g., `"Select"`, not `"select"`).
        - **Multi-line Strings**: For complex `"column_processing"` or `"content"` (e.g., `CASE` statements), preserve the formatting.
        - **Column Name Handling**: If there is no `AS`, `"column_processing"` is empty; if there is an `AS`, include the full expression.
        - **Virtual Table Check**: In `FROM` or `JOIN`, verify if the table name matches a CTE defined in the SQL.

        #### Example Validation
        The following are the correct processing results for the two examples you provided, used to validate the rules:

        ##### Example 1：SQL Without CTE
        **Input SQL**：
        ```sql
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
        ```

        **Output JSON**：
        ```json
        [
        {
            "created_virtual_table": "False",
            "sql_content": [
            {
                "keywords": "Select",
                "scratched_content": [
                {"column_name": "country", "column_processing": ""},
                {"column_name": "sales_notax", "column_processing": "SUM(amt_notax) AS sales_notax"},
                {"column_name": "sales_notax_LW", "column_processing": "SUM(lw_amt_notax) AS sales_notax_LW"},
                {
                    "column_name": "sales_notax_wow_per",
                    "column_processing": "
                    CASE
                    WHEN SUM(COALESCE(lw_amt_notax, 0)) = 0 THEN 0
                    ELSE SUM(amt_notax) / SUM(COALESCE(lw_amt_notax, 0)) - 1
                    END AS sales_notax_wow_per
                    "
                },
                {"column_name": "traffic", "column_processing": "SUM(traffic) AS traffic"},
                {"column_name": "traffic_LW", "column_processing": "SUM(lw_traffic) AS traffic_LW"},
                {
                    "column_name": "traffic_wow_per",
                    "column_processing": "
                    CASE
                    WHEN SUM(COALESCE(lw_traffic, 0)) = 0 THEN 0
                    ELSE SUM(traffic) / SUM(COALESCE(lw_traffic, 0)) - 1
                    END AS traffic_wow_per
                    "
                }
                ]
            },
            {
                "keywords": "From",
                "scratched_content": [
                {"table_name": "dm_fact_sales_chatbi", "is_virtual_table": "False"}
                ]
            },
            {
                "keywords": "Where",
                "scratched_content": [
                {"content": "date_code BETWEEN '2025-02-23' AND '2025-02-24'"}
                ]
            },
            {
                "keywords": "Group By",
                "scratched_content": [
                {"content": "country"}
                ]
            },
            {
                "keywords": "Having",
                "scratched_content": [
                {"content": "sales_notax_wow_per < 0"}
                ]
            },
            {
                "keywords": "Order By",
                "scratched_content": [
                {"content": "sales_notax_wow_per"}
                ]
            }
            ]
          }
          ]
        ```\n
        ### Example2: SQL With CTE
        **Input SQL*
        ```sql
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
        ```

        **Output Json*
        ```json
      [
      {
        "created_virtual_table": "False",
        "sql_content": [
          {
            "keywords": "Select",
            "scratched_content": [
              {
                "column_name": "Sep2024NewMembers",
                "column_processing": "(SELECT COUNT(DISTINCT member_code) FROM Sep2024FirstTimeCustomers) AS Sep2024NewMembers",
                "sub_select": "True",
                "sub_scratched_content": [
                  {
                    "keywords": "Select",
                    "scratched_content": [
                      {"column_name": "COUNT(DISTINCT member_code)", "column_processing": "COUNT(DISTINCT member_code)"}
                    ]
                  },
                  {
                    "keywords": "From",
                    "scratched_content": [
                      {"table_name": "Sep2024FirstTimeCustomers", "is_virtual_table": "True"}
                    ]
                  }
                ]
              }
            ]
          },
          {
            "keywords": "From",
            "scratched_content": []
          }
        ]
      },
      {
        "created_virtual_table": "True",
        "virtual_table_name": "Sep2024Transactions",
        "sql_content": [
          {
            "keywords": "Select",
            "scratched_content": [
              {"column_name": "*", "column_processing": ""}
            ]
          },
          {
            "keywords": "From",
            "scratched_content": [
              {"table_name": "dm_member_sales_chatbi", "is_virtual_table": "False"}
            ]
          },
          {
            "keywords": "Where",
            "scratched_content": [
              {"content": "transaction_date BETWEEN '2024-09-01' AND '2024-09-30'"}
            ]
          }
        ]
      },
      {
        "created_virtual_table": "True",
        "virtual_table_name": "Sep2024FirstTimeCustomers",
        "sql_content": [
          {
            "keywords": "Select",
            "scratched_content": [
              {"column_name": "member_code", "column_processing": "DISTINCT member_code"}
            ]
          },
          {
            "keywords": "From",
            "scratched_content": [
              {"table_name": "Sep2024Transactions", "is_virtual_table": "True"}
            ]
          },
          {
            "keywords": "Where",
            "scratched_content": [
              {
                "content": "member_code NOT IN (SELECT member_code FROM dm_member_sales_chatbi)",
                "sub_select": "True",
                "sub_scratched_content": [
                  {
                    "keywords": "Select",
                    "scratched_content": [
                      {"column_name": "member_code", "column_processing": ""}
                    ]
                  },
                  {
                    "keywords": "From",
                    "scratched_content": [
                      {"table_name": "dm_member_sales_chatbi", "is_virtual_table": "False"}
                    ]
                  }
                ]
              }
            ]
          }
        ]
      }
    ]
        ```
        ### Output Requirements for User Feedback
            - The final output must be a single valid JSON object wrapped in a json {content} block.
            - The JSON content must strictly follow the structure defined above (a list of JSON objects).
            - Only one json block is allowed in the response to ensure compatibility with Python extraction (e.g., using json.loads()).
            - If the user input is an empty string (""), return an empty list [] within the json block to indicate no SQL was provided for conversion.
            - Do not include additional text, explanations, or multiple json blocks outside the single json {content} structure.
    """
    prompt_user += "Current User Input SQL: \n"
    prompt_user += user_input

    prompt = [
        {"role": "system", "content": prompt_system},
        {"role": "assistant", "content": prompt_assistant},
        {"role": "user", "content": prompt_user}
    ]
    # response = llm(model_name="gpt", messages=prompt)

    response = str({
      "content": [
            {
                "created_virtual_table": "False",
                "sql_content": [
                    {
                        "keywords": "Select",
                        "scratched_content": [
                            {
                                "column_name": "Sep2024NewMembers",
                                "column_processing": "(SELECT COUNT(DISTINCT member_code) FROM Sep2024FirstTimeCustomers) AS Sep2024NewMembers",
                                "sub_select": "True",
                                "sub_scratched_content": [
                                    {
                                        "keywords": "Select",
                                        "scratched_content": [
                                            {"column_name": "COUNT(DISTINCT member_code)", "column_processing": "COUNT(DISTINCT member_code)"}
                                        ]
                                    },
                                    {
                                        "keywords": "From",
                                        "scratched_content": [
                                            {"table_name": "Sep2024FirstTimeCustomers", "is_virtual_table": "True"}
                                        ]
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        "keywords": "From",
                        "scratched_content": []
                    }
                ]
            },
            {
                "created_virtual_table": "True",
                "virtual_table_name": "Sep2024Transactions",
                "sql_content": [
                    {
                        "keywords": "Select",
                        "scratched_content": [
                            {"column_name": "*", "column_processing": ""}
                        ]
                    },
                    {
                        "keywords": "From",
                        "scratched_content": [
                            {"table_name": "dm_member_sales_chatbi", "is_virtual_table": "False"}
                        ]
                    },
                    {
                        "keywords": "Where",
                        "scratched_content": [
                            {"content": "transaction_date BETWEEN '2024-09-01' AND '2024-09-30'"}
                        ]
                    }
                ]
            },
            {
                "created_virtual_table": "True",
                "virtual_table_name": "Sep2024FirstTimeCustomers",
                "sql_content": [
                    {
                        "keywords": "Select",
                        "scratched_content": [
                            {"column_name": "member_code", "column_processing": "DISTINCT member_code"}
                        ]
                    },
                    {
                        "keywords": "From",
                        "scratched_content": [
                            {"table_name": "Sep2024Transactions", "is_virtual_table": "True"}
                        ]
                    },
                    {
                        "keywords": "Where",
                        "scratched_content": [
                            {
                                "content": "member_code NOT IN (SELECT member_code FROM dm_member_sales_chatbi)",
                                "sub_select": "True",
                                "sub_scratched_content": [
                                    {
                                        "keywords": "Select",
                                        "scratched_content": [
                                            {"column_name": "member_code", "column_processing": ""}
                                        ]
                                    },
                                    {
                                        "keywords": "From",
                                        "scratched_content": [
                                            {"table_name": "dm_member_sales_chatbi", "is_virtual_table": "False"}
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ]
    })
    
    # response = json.loads(response)
    print("======================SQL2JSON=====================", response)
    return response
input_sql = """
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
sql2json(input_sql)
