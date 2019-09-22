insert into kickstarter.dates (date_value)
select distinct(created_at) from kickstarter.staging
union
select distinct(launched_at) from kickstarter.staging
union
select distinct(state_changed_at) from kickstarter.staging
union
select distinct(deadline) from kickstarter.staging
order by created_at