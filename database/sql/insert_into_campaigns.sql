insert into kickstarter.campaigns (name, backers_count, states_id, 
	categories_id, creator, blurb, locations_id, created_at_id, launched_at_id,
    state_changed_at_id, deadline_id, pledged, goal, spotlight, staff_pick)
select 
	s.name, 
	s.backers_count,
    st.states_id,
    c.categories_id,
    s.creator,
    s.blurb,
    l.locations_id,
    d_created_at.dates_id created_at_id,
    d_launched_at.dates_id launched_at_id,
    d_state_changed_at.dates_id state_changed_at_id,
    d_deadline.dates_id deadline_id,
    s.pledged,
    s.goal,
    s.spotlight,
    s.staff_pick
from 
	kickstarter.staging s
inner join kickstarter.states st
	on st.state = s.state
inner join kickstarter.locations l
	on l.country = s.country and l.city = s.city
inner join kickstarter.categories c
	on c.category = s.category and c.sub_category = s.sub_category
inner join kickstarter.dates d_created_at
	on d_created_at.date_value = s.created_at
inner join kickstarter.dates d_launched_at
	on d_launched_at.date_value = s.launched_at
inner join kickstarter.dates d_state_changed_at
	on d_state_changed_at.date_value = s.state_changed_at
inner join kickstarter.dates d_deadline
	on d_deadline.date_value = s.deadline