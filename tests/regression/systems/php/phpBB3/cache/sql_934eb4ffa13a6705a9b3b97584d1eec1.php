<?php exit; ?>
1389638072
SELECT m.*, u.user_colour, g.group_colour, g.group_type FROM (phpbb3test_moderator_cache m) LEFT JOIN phpbb3test_users u ON (m.user_id = u.user_id) LEFT JOIN phpbb3test_groups g ON (m.group_id = g.group_id) WHERE m.display_on_index = 1
6
a:0:{}