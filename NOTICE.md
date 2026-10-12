# Third-party notices

LG webOS Remote for Home Assistant card and bridge code in this package were written separately and are MIT-licensed.
They **do not include** the source code of `michalowskil/lovelace-touchpad-card`
(CC BY-NC-ND 4.0). The aim is feature compatibility using new implementation code. This is not a formal clean-room legal certification; review licensing before redistribution.

The Home Assistant app installs, but does not vendor:

- [`bscpylgtv`](https://github.com/chros73/bscpylgtv) (MIT), copyright
  2017 Dennis Karpienski, 2019 Josh Bendavid and contributors. Full license:
  https://github.com/chros73/bscpylgtv/blob/master/LICENSE.txt
- [`websockets`](https://github.com/python-websockets/websockets), BSD-3-Clause;
  licenses are maintained by the upstream package.
- [`sqlitedict`](https://github.com/RaRe-Technologies/sqlitedict), Apache-2.0,
  copyright 2011-present Radim Rehurek and contributors; installed transitively
  by bscpylgtv. The Bridge uses its own JSON pairing storage instead of this
  library's SQLite storage. Full license:
  https://github.com/RaRe-Technologies/sqlitedict/blob/master/LICENSE.md

You must preserve applicable notices when distributing bundled copies of any
upstream libraries. LG and webOS are trademarks of their respective owners;
LG webOS Remote for Home Assistant is not affiliated with LG or Home Assistant.
