Toolbox
+++++++
.. _label_sec_toolbox:


Typo
====

*Italic*
**bold**
``code``

.. caution ::
   text
   text

.. danger ::
   text 
   text

.. tip ::
   text

.. note ::
   text

Code sample
===========

some code::
    Here is the code

it::
    here is another block

Include a figure:
=================

.. image:: /images/GA_these.png

Create a tables
===============


A basic table:

.. .. table:: Title of the table
.. =============== ========== ========== ============
.. This is a table a12        a13        a14
.. =============== ========== ========== ============
.. Table           y          y          y
.. Table           y          y          y
.. Table           y          y          y
.. Table           y          y          y
.. =============== ========== ========== ============

.. .. table:: another table
.. +--------------+----------+----------+-----------+
.. | here         |          |          |           |
.. | here         |          |          |           |
.. +--------------+----------+----------+-----------+

.. list-table:: table built from a list
    :widths: 20 10 10 15
    :header-rows: 1

    * - a11
      - a12
      - a13
      - a14
    * - a21
      - a22
      - a23
      - a24

.. csv-table:: table built from a csv   
    :header: header_1, header_2, header_3
    :widths: 15 10 30

    a11, a12, a13
    a21, a22, a23


Create links:
=============

URL links
---------

this is a link:
https://www.google.com

`an url hidden in the text: <https://www.google.com>`

Internal links
--------------

The toolbox containing all the tips are given here: ..targetedlink..
:doc:`/sections/Toolbox_sphinx`
:doc:`with an hyper link </sections/Toolbox_sphinx>`
This is a link to whereever I want : :ref:`label_sec_toolbox`
