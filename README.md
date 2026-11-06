# DailyChange root hosting

This repository publishes the **existing** DailyChange homepage at
https://coderzhh.github.io/ so Google can read the brand at the hostname root.
There is no gateway, language-selection screen, new design or additional click.

All website source remains in [CoderZHH/DailyChange-Web](https://github.com/CoderZHH/DailyChange-Web).
The publisher copies the already published homepage byte for byte and checks
that its scripts and images are available at the existing project URLs.
English, support, privacy and guides retain their existing addresses.

After deploying changes to the source website, refresh this homepage with:

```sh
gh workflow run pages.yml --repo CoderZHH/CoderZHH.github.io
```

The workflow also publishes the PNG favicon, root sitemap, crawl instructions
and existing public search-verification files. Google chooses when to refresh
the search-result favicon and site name; publication does not guarantee either.
