{% load thumbnail %}
{% if version.project.image_file %}
![](http://changelog.linfiniti.com/{{ version.project.image_file|thumbnail_url:'medium-entry' }})
{% endif %}

Project: {{ version.project }}
Changelog for version: {{ version.name }}
Description: {{ version.description }}
{% if version.image_file %}
![](http://changelog.linfiniti.com/{{ version.image_file|thumbnail_url:'medium-entry' }})
{% endif %}

{% for row in version.categories %}
{{row.category.name }}
---------------------------------------------------------
{% for entry in row.entries %}
Feature: **{{ entry.title }}**
.........................................................
{{ entry.description }}
{% if entry.image_file %}
![](http://changelog.linfiniti.com/{{ entry.image_file|thumbnail_url:'large-entry' }})
{% endif %}
{% endfor %}{# entry loop #}
{% endfor %}{# row loop #}
