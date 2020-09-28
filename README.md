# nose-launchable
A nose plugin to interact with [Launbhable](https://www.launchableinc.com/) API. 

## Install

```
$ pip install nose-launchable
```

## Usage

```
$ nosetests --launchable
```
In addition to specifying the `--launchable` flag, you need to set the following environment variables in your environment. These values should be provided from Launchable.

|  Key  |  Description  |
| ---- | ---- |
|  LAUNCHABLE_TOKEN  |  A token to access Launchable API |

## Development
Pull requests are always appreciated. If you want to see whether your changes work as expected,  run the following command to install the plugin locally.

```bash
$ python setup.py develop
``` 
