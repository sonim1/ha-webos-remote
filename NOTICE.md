# Third-party notices

LG webOS Remote for Home Assistant is independently implemented and MIT-licensed.
It does not include source from `michalowskil/lovelace-touchpad-card` (CC BY-NC-ND 4.0).

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

The project website displays the original Home Assistant logomark to identify
its target platform. The logo is a trademark and property of the Open Home
Foundation and is not covered by this project's MIT license. Its source and
upstream usage notice are documented in [website/assets/NOTICE.md](website/assets/NOTICE.md).
