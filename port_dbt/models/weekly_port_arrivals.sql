with weekly as (
    select port_id, port_name,
           date_trunc('week', day) as week_start,
           sum(port_calls)         as actual_calls
    from {{ ref('stg_ports') }}
    group by 1, 2, 3
),
with_expected as (
    select *,
           avg(actual_calls) over (
               partition by port_id order by week_start
               rows between 4 preceding and 1 preceding
           ) as expected_calls
    from weekly
)
select *,
       case when expected_calls is null then 'no history'
            when actual_calls < 0.6 * expected_calls
              or actual_calls > 1.4 * expected_calls then 'unusual'
            else 'normal' end as flag
from with_expected
