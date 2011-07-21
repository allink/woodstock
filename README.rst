=========
Woodstock
=========

Installation
------------

**Notice**: This is a first draft of an installation guide. It's not finished
and complete.

1. Make sure you have a working django project setup.

2. Install woodstock with pip::
    
    pip install woodstock

3. Make sure that the FeinCMS and Pennyblack Apps are added to your installed apps in your `settings.py`::
    
    'woodstock',
    
4. Install dependencies (over `pip`):

    - pennyblack_
    - feincms_
    - icalendar
    
      
5. Add Woodstock Models to south migration modules in your `settings.py`::

    SOUTH_MIGRATION_MODULES = {
        'woodstock': 'project_name.migrations_woodstock',
    }
        
6. Run `schemamigrations` and `migrate`::
    
    ./manage.py schemamigration --initial woodstock
    ./manage.py migrate
    
.. _pennyblack: https://github.com/allink/pennyblack/
.. _feincms: https://raw.github.com/matthiask/feincms/

