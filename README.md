# Hugo pages
https://jkosik.github.io/

### Bootstrap
```
hugo new site .
git init
git submodule add git@github.com:fauzanmy/pehtheme-hugo.git themes/pehtheme

# Copy data from themes/pehtheme to the root and adjust your content as needed.
# !!! If changing also themes/pehtheme, make sure you deinit submodule first to preserve the changes !!!

# publish to /public. Folder can be anytime deleted and rendered again
hugo

hugo serve
```

