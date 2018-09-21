from . import login

sample = "-----------------------------28671180837090
Content-Disposition: form-data; name="changed"

1530922069
-----------------------------28671180837090
Content-Disposition: form-data; name="title[0][value]"

a
-----------------------------28671180837090
Content-Disposition: form-data; name="form_build_id"

form-FYkJPlXJGTMXw7EmIB6DS-AsIHScqYmZacOKRUW9bOI
-----------------------------28671180837090
Content-Disposition: form-data; name="form_token"

vvWRoXZD6hv5XeVqNyXE3OvMhVXJpZz865WjsdauL7g
-----------------------------28671180837090
Content-Disposition: form-data; name="form_id"

node_sf_article_form
-----------------------------28671180837090
Content-Disposition: form-data; name="body[0][summary]"


-----------------------------28671180837090
Content-Disposition: form-data; name="body[0][value]"

<p>a</p>

-----------------------------28671180837090
Content-Disposition: form-data; name="body[0][format]"

basic_html
-----------------------------28671180837090
Content-Disposition: form-data; name="field_sf_primary_image[0][fids]"


-----------------------------28671180837090
Content-Disposition: form-data; name="field_sf_primary_image[0][display]"

1
-----------------------------28671180837090
Content-Disposition: form-data; name="field_sf_primary_image[0][focal_point]"

50,50
-----------------------------28671180837090
Content-Disposition: form-data; name="revision_log[0][value]"


-----------------------------28671180837090
Content-Disposition: form-data; name="field_sf_meta_tags[0][basic][title]"

[current-page:title] | [site:name]
-----------------------------28671180837090
Content-Disposition: form-data; name="field_sf_meta_tags[0][basic][description]"

[node:summary]
-----------------------------28671180837090
Content-Disposition: form-data; name="field_sf_meta_tags[0][basic][abstract]"


-----------------------------28671180837090
Content-Disposition: form-data; name="field_sf_meta_tags[0][basic][keywords]"


-----------------------------28671180837090
Content-Disposition: form-data; name="field_sf_meta_tags[0][advanced][geo_placename]"


-----------------------------28671180837090
Content-Disposition: form-data; name="field_sf_meta_tags[0][advanced][geo_position]"


-----------------------------28671180837090
Content-Disposition: form-data; name="field_sf_meta_tags[0][advanced][geo_region]"


-----------------------------28671180837090
Content-Disposition: form-data; name="field_sf_meta_tags[0][advanced][icbm]"


-----------------------------28671180837090
Content-Disposition: form-data; name="field_sf_meta_tags[0][advanced][canonical_url]"

[node:url]
-----------------------------28671180837090
Content-Disposition: form-data; name="field_sf_meta_tags[0][advanced][content_language]"


-----------------------------28671180837090
Content-Disposition: form-data; name="field_sf_meta_tags[0][advanced][shortlink]"


-----------------------------28671180837090
Content-Disposition: form-data; name="field_sf_meta_tags[0][advanced][news_keywords]"


-----------------------------28671180837090
Content-Disposition: form-data; name="field_sf_meta_tags[0][advanced][standout]"


-----------------------------28671180837090
Content-Disposition: form-data; name="field_sf_meta_tags[0][advanced][generator]"


-----------------------------28671180837090
Content-Disposition: form-data; name="field_sf_meta_tags[0][advanced][image_src]"


-----------------------------28671180837090
Content-Disposition: form-data; name="field_sf_meta_tags[0][advanced][original_source]"


-----------------------------28671180837090
Content-Disposition: form-data; name="field_sf_meta_tags[0][advanced][referrer]"


-----------------------------28671180837090
Content-Disposition: form-data; name="field_sf_meta_tags[0][advanced][rights]"


-----------------------------28671180837090
Content-Disposition: form-data; name="field_sf_meta_tags[0][advanced][set_cookie]"


-----------------------------28671180837090
Content-Disposition: form-data; name="simple_sitemap_index_content"

1
-----------------------------28671180837090
Content-Disposition: form-data; name="simple_sitemap_priority"

0.5
-----------------------------28671180837090
Content-Disposition: form-data; name="simple_sitemap_changefreq"


-----------------------------28671180837090
Content-Disposition: form-data; name="simple_sitemap_include_images"

0
-----------------------------28671180837090
Content-Disposition: form-data; name="path[0][pathauto]"

1
-----------------------------28671180837090
Content-Disposition: form-data; name="uid[0][target_id]"

klanmiko (3311)
-----------------------------28671180837090
Content-Disposition: form-data; name="created[0][value][date]"

2018-07-06
-----------------------------28671180837090
Content-Disposition: form-data; name="created[0][value][time]"

17:07:49
-----------------------------28671180837090
Content-Disposition: form-data; name="field_sf_person_reference[0][target_id]"


-----------------------------28671180837090
Content-Disposition: form-data; name="field_sf_person_reference[0][_weight]"

0
-----------------------------28671180837090
Content-Disposition: form-data; name="field_sf_related_photo_gallery[0][target_id]"


-----------------------------28671180837090
Content-Disposition: form-data; name="field_sf_related_photo_gallery[0][_weight]"

0
-----------------------------28671180837090
Content-Disposition: form-data; name="field_sf_article_type"

30
-----------------------------28671180837090
Content-Disposition: form-data; name="field_sf_article_category"

_none
-----------------------------28671180837090
Content-Disposition: form-data; name="field_sf_tags[target_id]"


-----------------------------28671180837090
Content-Disposition: form-data; name="field_sf_content_audit[0][audit_status]"

None
-----------------------------28671180837090
Content-Disposition: form-data; name="field_sf_content_audit[0][audit_action]"

Leave As-is
-----------------------------28671180837090
Content-Disposition: form-data; name="field_sf_content_audit[0][audit_notes]"


-----------------------------28671180837090
Content-Disposition: form-data; name="field_sf_content_audit[0][audit_review_by_date]"


-----------------------------28671180837090
Content-Disposition: form-data; name="field_sf_content_audit[0][audit_reviewer]"


-----------------------------28671180837090
Content-Disposition: form-data; name="status[value]"

1
-----------------------------28671180837090
Content-Disposition: form-data; name="op"

Save
-----------------------------28671180837090--"

def add_article(base_url)
    url = base_url + "/node/add/sf_article"

if __name__ is "__main__":
