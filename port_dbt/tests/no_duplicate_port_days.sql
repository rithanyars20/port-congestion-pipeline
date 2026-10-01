select port_id, day, count(*)
from {{ ref('stg_ports') }}
group by 1, 2
having count(*) > 1
