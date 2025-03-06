import sqlparse


def format_sql_like_example(sql):
    # Parse the SQL statement
    parsed = sqlparse.parse(sql)[0]

    # Format the SQL statement to match the style of the provided SQL file
    formatted_sql = sqlparse.format(sql, reindent=True, keyword_case='lower', identifier_case='lower',
                                    use_space_around_operators=True, comma_first=False, indent_width=4)

    # Custom formatting to match the style of the provided SQL file
    formatted_sql = formatted_sql.replace(",", ",\n\t")  # Add newline and tab after commas
    formatted_sql = formatted_sql.replace("from", "\nfrom")  # Add newline before FROM
    formatted_sql = formatted_sql.replace("group by", "\ngroup by")  # Add newline before GROUP BY
    formatted_sql = formatted_sql.replace("sum(", "sum(")  # Ensure no extra spaces around sum(

    # Manually adjust the CASE statement formatting
    # formatted_sql = formatted_sql.replace("case\n", "case\n\t\t")  # Add extra indentation for CASE
    # formatted_sql = formatted_sql.replace("when", "\t\twhen")  # Add extra indentation for WHEN
    # formatted_sql = formatted_sql.replace("then", "\tthen")  # Add extra indentation for THEN
    # formatted_sql = formatted_sql.replace("end", "\tend")  # Add extra indentation for END

    # Remove excessive newlines and spaces
    formatted_sql = "\n".join([line.rstrip() for line in formatted_sql.splitlines() if line.strip()])

    return formatted_sql


# SQL query to format
sql_query = "select a,b,c,sum(case when d>0 then d end), from ga group by a,b,c"

# Format the SQL query
formatted_query = format_sql_like_example(sql_query)

# Print the formatted SQL query
print(formatted_query)