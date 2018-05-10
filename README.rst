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
also a longpoll endpoint to get updates after a full download has been performed. And it is possible to
download historic version of the entries. The details of the API is described in swagger.yaml from which
docs are generated here:

    https://facetree-dev.ardoe.net/v1/ui/#/default


Getting started
===============

* Clone the repo:

    .. code-block:: bash

        git clone git@github.com:facetree/facetree.git

* Choose which backend to use by copying the template and edit it:

    .. code-block:: bash

        cp frontends/backend_name.js.example  frontends/backend_name.js

* Look at the examples in frontends/example/ by opening the files in a browser and looking in the console

* Create a directory under frontends for your frontend

