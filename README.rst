Facetree
========

The aim is to build a browsable family tree with names and photos of all the individuals. The tree will be
editable as a wiki and all the history of these edits will be saved. Each user of the system is one of the
individuals in the tree and the user profile indicates which one. The data use to represetn the tree is a
set of json records representing either Individuals or Families. Each record has an id-property identifying
it as well as a version. Each time a record is updated a new version is created and the old one is still
accessable. A Individual record can look like this:

.. code-block:: json

    {
      "author": "user@example.com",
      "birth": {
        "date": "1977-06-30",
        "eventType": "Birth",
        "from": 1977,
        "lat": "55.73781450000001",
        "long": "13.1771827"
      },
      "color": "röd",
      "gedId": "I0003",
      "id": "671d30b0-cafd-4ae4-a85a-8b419b4ab373",
      "imageIds": [],
      "location": [
        {
          "date": "1937-02-10",
          "eventType": "Birth",
          "from": 1937,
          "lat": "55.73781450000001",
          "long": "13.1771827"
        },
        {
          "date": "1950",
          "eventType": "Residence",
          "from": 2000,
          "lat": "55.7403757",
          "long": "13.1767375"
        }
      ],
      "name": "Otto Svensson",
      "sex": "M",
      "type": "Individual",
      "version": "1525925908655"
    }

and a Family entry connects a set of Individual entreies by refereing to their id-numbers. For example:

.. code-block:: json

    {
      "author": "user@example.com",
      "children": [
        "c4e4f73c-38b5-4ce2-96e5-23804522f309"
      ],
      "father": "ce7e30d2-20c3-4af2-a089-744a03e270d5",
      "gedId": "F0017",
      "id": "6f41f2a4-4fc2-41e8-8617-c9afd4d8af62",
      "marriages": [],
      "mother": "2a3ad938-9793-41d6-bc74-edecd36ff669",
      "type": "Family",
      "version": "1525925954698"
    }

Using the backend it is then possible to donwload these entries. Either one by one or all at once. There is
also a longpoll (??) endpoint to get updates after a full download has been performed. And it is possible to
download historic version of the entries. The details of the API is described in swagger.yaml from which
docs are generated here:

    https://facetree-dev.ardoe.net/v1/ui/#/default

There are two backends up and running. One development version at

    https://facetree-dev.ardoe.net/

where you can play around with the data as much as you like to test the functionality of your frontend. And one
production server at

    https://facetree.ardoe.net/

where we care about the data and are actively collecting images.


Getting started
===============

* Clone the repo:

    .. code-block:: bash

        git clone git@github.com:facetree/facetree.git

* Choose which backend to use by copying the template and edit it. The default should be fine in most cases:

    .. code-block:: bash

        cd facetree
        cp frontends/backend_name.js.example  frontends/backend_name.js

* Install a webserver, for example (or use the Python3 builtin http.server):

    .. code-block:: bash

        npm install -g serve

* Start the webserver and have it serve the frontends diretocy as it's root:

    .. code-block:: bash

        serve frontends/

  or

    .. code-block:: bash

        cd frontends/
        python3 -m http.server 5000

* In, frontends/examples/ copy login.html to tutorial.html and open it in your browser through the
  webserver: (http://localhost:5000/example/tutorial.html)

* Open the javascript consol and note that it was not granted access.

* Update tutorial.html with the credentials of your test user and verify using the javascript console that the login is
  successfull.

* Now we need to get the tree data. Look in database.html if the following instructions are unclear. Add the backend
  lib to the head section of tutorial.html:

    .. code-block:: html

        <script src="../facetree.js"></script>

* Start the database downloader after a successfull login. This will download all the records and then use the long
  poll. It needs two parameters, the auth_token from the login response and a callback (optional) that will be called when
  updates are made to the database. ??Where to put this code??

    .. code-block:: javascript

        start_database_updater(response.data.token, function (updated_records) {
            for (var id in database.individuals) {
                console.log(database.individuals[id].name);
            }
        });

* Create a branch for your frontend:

    .. code-block:: bash

        git checkout -b my-cool-frontend

* Decide what feature of the app you want to focus on and add your names to it on the wiki on github. If none of
  the suggestions there suits you, feel free to add points.

* Create a directory under frontends for your frontend and stat building it.

    .. code-block:: bash

        mkdir frontends/my-cool-frontend
        git add frontends/my-cool-frontend
        git commit -a -m "Nice fix"
        git push

* If you want, copy example/basic-vue.html to your directory and use it as a staring point for your frontend.

* Add a link to your frontend in frontends/index.html

* When you need to share your changes with the rest of the group, merge your branch to the develop branch (default)
  and push the chnages. That will also
  make your frontend availible at https://facetree-dev.ardoe.net/ after a minute or so,

    .. code-block:: bash

        git checkout develop
        git merge my-cool-frontend
        git push
        git checkout my-cool-frontend

* When you have something to show the world, merge your branch to the master branch. That will also
  make your frontend availible at https://facetree.ardoe.net/ after a minute or so

    .. code-block:: bash

        git checkout master
        git merge my-cool-frontend
        git push
        git checkout my-cool-frontend
