# Image downloader

This repository contains a simple command-line tool for downloading images from a site in an advanced way (allows filtering the target images but requires HTML knowledge). 
The idea is to filter the target images by: 

* Tag name (sometimes images can be represented by other tags besides <img>). Related option --image_tag
* Attribute (the solution can filter only the tags that have a specific attribute). Related option --required_attr
* Attribute regex (optional) (The attribute at the --required_attr option might be required to match a regex. If this argument is not specified, all tags that have the attribute will match, regardless of the attribute value). Related option --attr_regex
* Referer (optional) (Sometimes, images can be on a CDN that requires a specific Referer header. In such cases, use this argument). Related option --referer

For example, suppose that we want to download all images in <img> tags that contain the *loading* attribute (regardless of the value). We might use this tool like this:

```sh
python download_from_link --url=*url_to_be_scanned* --image_tag=img --required_attr=loading --dest_folder=result
```

Use *-h* for help.