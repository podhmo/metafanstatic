metafanstatic
========================================

1. create depenency config
2. download repository files via dependency config
3. create config for generating package via scannig downloaded repository
4. generating fanstatic packages


.. code:: bash

    $ metafanstatic search bootstrap-timepicker
    # 1. create depenency config
    $ metafanstatic dependency --recursive bootstrap-timepicker > config.json
    # 2. download repository files via dependency config
    $ metafanstatic download  --config config.json
    # 3. create config for generating package via scannig downloaded repository
    $ metafanstatic scan `ls | grep -v *.json` > generate.config.json
    # 4. generating fanstatic packages
    $ metafanstatic create generate.config.json .

after above instraction

.. code:: bash

    $ ls 
    autotype                        generate.config.json            meta.js.bootstrap-timepicker
    bootstrap-2.3.2                 jquery-2.0.3                    meta.js.jquery
    bootstrap-timepicker-0.2.6      meta.js.autotype
    config.json                     meta.js.bootstrap

after install package

.. code:: bash

    # for i in meta.*; do popd $i; python setup.py develop; popd; done
    $ metafanstatic list
    from js.autotype import jquery_autotype_js; jquery_autotype_js.need()
    from js.bootstrap import bootstrap_css; bootstrap_css.need()
    from js.bootstrap import bootstrap_js; bootstrap_js.need()
    from js.bootstrap_timepicker import bootstrap_timepicker_min_css; bootstrap_timepicker_min_css.need()
    from js.bootstrap_timepicker import bootstrap_timepicker_min_js; bootstrap_timepicker_min_js.need()
    from js.jquery import jquery_js; jquery_js.need()
