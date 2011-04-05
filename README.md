Woodstock - allink.eventmanager
===============================

Installation
------------

**Notice**: This is a first draft of an installation guide. It's not finished
and complete.

0. Make sure you have a working django project setup.

0. Create link for woodstock:

        ln -s /path/to/woodstock/woodstock/ woodstock

0. Make sure that the FeinCMS and Pennyblack Apps are added to your installed apps in your `settings.py`:

        'woodstock',
    
0. Install dependencies (over `pip`):

    * [pennyblack](https://github.com/allink/pennyblack/)
      
0. Add Woodstock Models to south migration modules in your `settings.py`:

        SOUTH_MIGRATION_MODULES = {
            'woodstock': 'project_name.migrations_woodstock',
        }
        
0. Run `schemamigrations` and `migrate`:

        ./manage.py schemamigration --initial woodstock
        ./manage.py migrate
    

Dependencies
------------

*   Python
    *   django
