/*	ELIMINAMOS ${table_name}	*/
truncate table ${table_name}

/*	ELIMINAMOS OBJETO DE ${table_name}	*/
if exists(select 1 from sysobjects where id=object_id('${table_name}') and type='U') begin
    drop table ${table_name}
end