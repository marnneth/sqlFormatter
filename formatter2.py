import re


class SQLBeautifier:
    def beautify(self, sql: str) -> str:
        # Convert to lowercase and normalize whitespace
        sql = sql.lower().strip()
        sql = re.sub(r'\s+', ' ', sql)

        # Add spaces around operators
        sql = self._add_operator_spaces(sql)

        # Format different parts
        parts = []

        # Handle CREATE VIEW statement
        if sql.startswith('create'):
            create_match = re.match(r'create or replace view ([^;]+);', sql)
            if create_match:
                parts.append(f'create or replace view {create_match.group(1)};')
                sql = sql[create_match.end():].strip()

        # Handle WITH clause
        if sql.startswith('with'):
            with_parts = self._format_with_clause(sql)
            parts.extend(with_parts)

            # Extract the main SELECT after WITH
            main_select = re.search(r'select\s+(.+)$', sql)
            if main_select:
                select_parts = self._format_main_select(main_select.group())
                parts.extend(select_parts)
        else:
            parts.extend(self._format_main_select(sql))

        return '\n'.join(parts)

    def _add_operator_spaces(self, sql: str) -> str:
        """Add spaces around operators"""
        sql = re.sub(r'([<>!=]+)', r' \1 ', sql)
        return re.sub(r'\s+', ' ', sql)

    def _format_with_clause(self, sql: str) -> list:
        parts = ['with']
        # Extract CTE definitions
        cte_pattern = r'(\w+)\s*\((.*?)\)(?=\s*(?:,|select\s+))'
        ctes = re.finditer(cte_pattern, sql, re.DOTALL)

        for i, cte in enumerate(ctes):
            cte_name, cte_query = cte.groups()

            if i == 0:
                parts.append(f'{cte_name} (')
            else:
                parts.append(f'\t{cte_name} (')

            cte_lines = self._format_subquery(cte_query)
            parts.extend('\t' + line for line in cte_lines)
            parts[-1] = parts[-1] + '),'

        return parts

    def _format_subquery(self, sql: str) -> list:
        parts = []
        select_match = re.search(r'select\s+(.*?)\s+from', sql, re.DOTALL)
        from_match = re.search(r'from\s+(.*?)(?:\s+group by|$)', sql, re.DOTALL)
        group_by_match = re.search(r'group by\s+(.*?)$', sql, re.DOTALL)

        if select_match:
            # Format SELECT on a single line
            columns = select_match.group(1).split(',')
            formatted_columns = [col.strip() for col in columns if col.strip()]
            parts.append(f'select {", ".join(formatted_columns)}')

        if from_match:
            parts.append('from')
            parts.append(f'\t{from_match.group(1).strip()}')

        if group_by_match:
            # Format GROUP BY on a single line
            cols = group_by_match.group(1).split(',')
            formatted_cols = [col.strip() for col in cols if col.strip()]
            parts.append(f'group by {", ".join(formatted_cols)}')

        return parts

    def _format_window_function(self, window_expr: str) -> str:
        """Format window function with OVER clause on a single line"""
        window_expr = re.sub(r'\s+', ' ', window_expr)
        if not window_expr.endswith(','):
            window_expr += ','
        return window_expr

    def _format_main_select(self, sql: str) -> list:
        parts = []
        select_match = re.search(r'select\s+(.*?)\s+from', sql, re.DOTALL)
        from_match = re.search(r'from\s+(.*?)(?:\s+left join|$)', sql, re.DOTALL)
        join_match = re.search(r'left join\s+(.*?)(?:\s+on\s+)(.*?)$', sql, re.DOTALL)

        if select_match:
            # Format SELECT on a single line
            columns = select_match.group(1).split(',')
            formatted_columns = [col.strip() for col in columns if col.strip()]
            parts.append(f'select {", ".join(formatted_columns)}')

        if from_match:
            parts.append('from')
            parts.append(f'\t{from_match.group(1).strip()}')

        if join_match:
            # Format LEFT JOIN and ON on a single line
            parts.append(f'left join {join_match.group(1).strip()} on {join_match.group(2).strip()}')

        return parts


# Test the formatter
beautifier = SQLBeautifier()
test_sql = """create or replace view pp.view;with ag (select id,min(case when a > 0 then b end) as xx,min(case when a < 0 then b end) as yy,sum(case when a > 0 then a end) as zz from etp.c group by id), se as (select  id, sum(a) over (              partition by id order by b) as tada        from         etp.c) select      xx,yy,zz,tada, from ag a left join se on se.id = ag.id  """
print(beautifier.beautify(test_sql))