.. py:currentmodule:: configurator

Changes
=======

1.3.0 (29 Jan 2020)
-------------------

- Add :meth:`Config.from_env` class method to help with extacting
  large numbers of environment variables into configuration.

1.2.0 (29 May 2019)
-------------------

- Enable the context manager returned by :meth:`Config.push` to return
  the state of a global config object to what it was before :meth:`~Config.push`
  was called.

1.1.0 (29 May 2019)
-------------------

- Add support for :meth:`pushing <Config.push>` and :meth:`popping <Config.pop>`
  config data onto a global :class:`Config`.

1.0.0 (4 Apr 2019)
------------------

- Support for optional configuration files in :meth:`Config.from_path`.

- Add :meth:`if_supplied` mapping operation.

- Fully documented.

0.5.0 (15 Mar 2019)
---------------------

- Initial release without docs.

