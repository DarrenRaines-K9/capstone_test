{% macro forward_fill(column) %}
    last_value({{ column }} ignore nulls) over (
        partition by geography
        order by observation_date
        rows between unbounded preceding and current row
    )
{% endmacro %}
