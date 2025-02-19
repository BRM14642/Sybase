/*	COMPARAMOS QUE ESTEN LA MISMA CANTIDAD DE REGISTROS EN AMBAS TABLAS */
select '${table_name}', count(1) from ${table_name} noholdlock union
select '${table_tmp}', count(1) from ${table_tmp} noholdlock