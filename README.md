# Bitbucket repositories security check with [Trufflehog3](https://github.com/feeltheajf/truffleHog3)
[![License: GPL v3](https://img.shields.io/github/license/lucapisciotta/bitbucketSearch)](https://github.com/lucapisciotta/bitbucketSearch/blob/master/LICENSE.md)
[![GitHub: Release](https://img.shields.io/github/v/release/lucapisciotta/bitbucketSearch)](https://github.com/lucapisciotta/bitbucketSearch/releases/latest)


## Table of Contents

- [About](#about)
- [Prerequisites](#prerequisites)
- [Getting Started](#getting_started)
- [Usage](#usage)
- [To Do](#todo)
- [Thanks To](#thanksto)

## About <a name = "about"></a>

This script permits you to analyze all repositories in your Bitbucket account (If you have got the permissions) through `Trufflehog3` and find all occurrences based on the `secrets.yaml` file.

### Prerequisites <a name = "prerequisites"></a>

There are few requirements to run this:
- Python 3.6.0+
- Trufflehog3
- A git-credential-helper

The software has only been tested on OS X

Trufflehog3 is available as a pip module so, you can use this command to install it:

```
    pip install -U --use-feature=2020-resolver trufflehog3
```

## Getting Started <a name = "getting_started"></a>

To make all functions available, you must copy the dist file removing the `.dist` suffix.

```
cp secrets.yaml.dist secrets.yaml
cp credentials.json.dist credentials.json
```

After that, you can edit copied files, for `credential.json` you can fill it with your `OAuth consumers` credentials. <br/>
In `secrets.yaml` you find all secrets definition and, you can add yours. These secrets are used by the `re` Python module, be careful defining these.

The last step involves editing two variables in the `bitbucketSearch.py` file.

```
bitbucket_workspace = 'YOUR_WORKSPACE'
trufflehog_format = 'TRUFFLEHOG_FILE_FORMAT' # Valid format are {json, yaml and html}
```

## Usage <a name = "usage"></a>

Usage is simple, just run the following command:

```
python bitbucketSearch.py
```

## To Do <a name = "todo"></a>

- [ ] Add function to enable command line arguments


## Thanks To <a name = "thanksto"></a>

Thanks to [feeltheajf](https://github.com/feeltheajf) to have made [Trufflehog3](https://github.com/feeltheajf/truffleHog3)