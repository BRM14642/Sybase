/*	RESPALDAMOS INFORMACION DE ${table_name} EN ${table_tmp}   */
insert into ${table_tmp}
    select ${original_columns}
        from ${table_name} noholdlock