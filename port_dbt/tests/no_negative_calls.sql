select * from {{ ref('stg_ports') }} where port_calls < 0
