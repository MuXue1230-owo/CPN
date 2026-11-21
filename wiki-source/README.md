# CPN26 Wiki source and publisher

CPN currently has exactly one language standard edition: **CPN26**.

Wiki pages are generated from the 32 canonical chapter files under [spec/](../spec/) by `tools/build_wiki.py`, rather than maintaining a second copy of normative content.

From a checkout of the repository, with GitHub Wiki write access configured in your local Git credentials, run:

```bash
bash tools/publish_wiki.sh
```

The command clones `MuXue1230-owo/CPN.wiki.git`, generates Home, six topical indexes, 32 chapter pages, sidebar, and footer, then commits and pushes the change. It preserves other Wiki pages and does not force-push.

GitHub Wiki is a separate Git repository. A GitHub REST contents connector with access to `CPN` does not automatically have Wiki Git-push support.
