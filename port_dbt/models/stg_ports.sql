select
    date                        as day,
    portid                      as port_id,
    portname                    as port_name,
    coalesce(portcalls, 0)      as port_calls
from {{ source('raw', 'raw_ports') }}
where portid is not null
