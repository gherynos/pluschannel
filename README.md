Plus Channel
============

Plus Channel is a simple application that generates an RSS feed containing the public posts of a Google+ account,
letting you display them in your blog or site.  

You can use this application to generate the RSS feed associated to your account and, in example, use it with
TwitterFeed to propagate your public Google+ posts to Twitter, Facebook and LinkedIn.
The generated feed contains the last five public posts of the selected account or page.  

[Live service website](https://ws.pluschannel.nharyes.net)

Setup
-----

This project requires Grunt CLI and Bower; to install them run:

```bash
$ npm install -g grunt-cli
$ npm install -g bower
```

then move to the project folder, and run:

```bash
$ npm install
$ bower install
$ grunt bower:install
```

### Virtualenv

Install Virtualenv:

```bash
$ pip install virtualenv
```

and create the environment for the project:

```bash
$ virtualenv venv
```

### Dependencies

Install the dependencies in the virtual environment:

```bash
$ source venv/bin/activate
$ pip install -r requirements.txt \
    -f http://www.blarg.net/~steveha/pyfeed-0.7.4.tar.gz \
    -f http://www.blarg.net/~steveha/xe-0.7.4.tar.gz
$ deactivate
```

### DataBase

Create the database:

```bash
$ sqlite3 db.sqlite
$ sqlite> .read schema.sql
$ sqlite> .quit
```

### API Key

An API Key for Google+ needs to be acquired for the project; please follow the
[instructions](https://developers.google.com/+/web/api/rest/oauth#acquiring-and-using-an-api-key) provided by Google.  
Once generated, set the property `api_key` in the `config.yaml` file.

Development server
----------------------

To start the local development server, run the following command:

```bash
$ grunt dev-server
```

from the project folder.

Deployment
----------

Before deploying any new version, run:

```bash
$ grunt
```

from the project folder.  
The files to deploy to the web server (WSGI) will be placed in the `deploy` folder.

Copyright and license
---------------------

Copyright (C) 2012-2016  Luca Zanconato (<luca.zanconato@nharyes.net>)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.