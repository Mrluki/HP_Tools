{{ objname | escape | underline}}

.. currentmodule:: {{ module }}

.. autoclass:: {{ objname }}

   {% block methods %}

   {% if methods %}
      .. rubric:: Functions

      .. autosummary::
         :toctree:
         {% for item in all_methods %}
            {%- if not item.startswith('_') or item in ['__call__'] %}
               {%- if not item == '__call__' %}
                  {{ name }}.{{ item }}
               {%- endif -%}
            {%- endif -%}
      {%- endfor %}
   {% endif %}
   {% endblock %}