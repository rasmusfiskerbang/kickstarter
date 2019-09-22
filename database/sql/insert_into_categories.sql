insert into kickstarter.categories (category, sub_category)
select category, sub_category from kickstarter.staging
	group by category, sub_category
    order by category, sub_category