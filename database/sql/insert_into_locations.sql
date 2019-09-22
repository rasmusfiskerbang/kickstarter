insert into kickstarter.locations (country, city)
select country, city from kickstarter.staging
	group by country, city
    order by country, city