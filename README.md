# Hugo pages
https://jkosik.github.io/

### Bootstrap
```
hugo new site .
git init
git submodule add git@github.com:fauzanmy/pehtheme-hugo.git themes/pehtheme

# Copy data from themes/pehtheme to the root and adjust your content as needed.
# !!! If changing also themes/pehtheme, make sure you deinit submodule, clean .gitmodules and .git/modules first to preserve the changes !!!
```

### New site
- `_extra` - custom data
- `assets/images` - blog images
-  `content/posts` - blog post

publish to /public. Folder can be anytime deleted and rendered again
```
hugo

hugo serve
```
