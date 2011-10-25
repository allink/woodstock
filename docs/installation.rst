Installation
============
This document describes the steps needed to set up woodstock in your own project.

You can also install woodstock using pip like so::

    $ pip install woodstock

Or you can grab your own copy of the woodstock source from github::

    $ git clone git://github.com/allink/woodstock.git


Make sure that woodstock and pennyblack are added to installed apps in
the `settings.py`::

    'woodstock',
    'pennyblack',


Configuration
=============


South Migrations
================

To use south migrations specify a south migration module in the settings::
    
    SOUTH_MIGRATION_MODULES = {
        'woodstock': 'project_name.migrations_woodstock',
    }
    
    