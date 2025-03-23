if exists(select 1 from sysobjects where id = object_id('dbo.${sp_name}') and type = 'P') begin
	drop procedure dbo.${sp_name}
end