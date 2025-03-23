/*	REGRESAMOS INFORMACION A ${table_name} */

insert into ${table_name}(
    ${colums})
select	${values}
from ${table_tmp} noholdlock