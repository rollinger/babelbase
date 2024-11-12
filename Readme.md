# Babelbase

[![PyPI version](https://badge.fury.io/py/your-package-name.svg)](https://badge.fury.io/py/your-package-name)
[![Build Status](https://travis-ci.org/yourusername/your-package-name.svg?branch=main)](https://travis-ci.org/yourusername/your-package-name)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A brief description of your Django package and its purpose.

---

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Usage](#usage)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)

---

## Features

- List of main features
- Key functionalities
- Benefits of using the package

## Installation

### Requirements

- Python 3.10+
- Django 4.2+

### Install via pip

```bash
pip install babelbase
```

### Install via github

Or install directly from GitHub:

```bash
pip install git+https://github.com/rollinger/babelbase.git
```

## Quick Start

Add 'babelbase' to your INSTALLED_APPS settings.
Run migrations to create the models.

## Configuration

## Usage

Provide usage examples here. You may want to include:

- Code snippets showing how to use the package.
- A brief explanation of key functionalities or components.
- Screenshots or links to a demo if applicable.

```python
from your_package_name import SomeFunction
# Code example here
SomeFunction()
```

## Testing

## Contributing

Contributions are welcome! Please follow these steps:

- Fork the repository.
- Create a new branch with a descriptive name.
- Make your changes and commit them.
- Open a pull request.
  See the CONTRIBUTING.md file for more details.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## Contact

For questions or support, please contact your-email@example.com.

### Explanation of Each Section

- **Package Name**: Introduces the package and includes status badges.
- **Table of Contents**: Provides easy navigation.
- **Features**: Lists the main highlights of the package.
- **Installation**: Includes dependencies and instructions for installation.
- **Quick Start**: Basic setup steps.
- **Configuration**: Additional setup steps for advanced configuration.
- **Usage**: Shows examples of how to use the package.
- **Testing**: Instructions for running tests.
- **Contributing**: Guidelines for contributing to the project.
- **License**: States the license for the project.
- **Contact**: How to reach out for support.

This layout will help users understand the purpose, setup, and usage of your Django package at a glance.

=== OLD

# Content

Adds database translations as a templatetag to the frontend and the backend.

## How to use in Frontend

First the view has to be loaded with the ContentMixin and a list of namespaces. Note that the global namespaces set in
settings.DB_TRANSLATION_DEFAULT_IDENTIFIER are always prepended to the view_identifier_list and available the the View's
template.

While db translations are loaded on demand anywhere, using the ContentMixin on a view will prefetch all translations
of a given namespace and make them available to the template. T

```python
from kinderwunschpraxis_stuttgart_villa_haag.content_i18n.views import ContentMixin

class StartNewsfeedView( ..., ContentMixin):
    template_name = "news/index.html"
    view_identifier_list = ["newsfeed"]
```

Then in the template you can use one of the templatetags "get_content" or "blockcontent_i18n".
Three parameter are required:

- view_id or namespace
- key_id or identifier
- placeholder: the placeholder text that should appear (optional, but strongly recommended)

- The templatetags are builtins in settings.TEMPLATES and need not to be loaded separately.

```html
<p class="mb-4">
  {% blockcontent_i18n "newsletter" 'subscription_tagline' %} Get expert
  insights and timely updates on Private Markets developments with the Privatize
  Newsletter. {% endblockcontent_i18n %}
</p>

--or--

<p class="mb-4">
  {% get_content "start_index" "solutions_offer_privatize_title" "What Privatize
  offers to you and your clients" %}
</p>
```

## How to use in Backend

Prepare DB Translation for the script you want to use it after the imports, defining the namespaces to prefetch:

```python
from kinderwunschpraxis_stuttgart_villa_haag.content_i18n.translate import db_gettext_lazy as _db
from kinderwunschpraxis_stuttgart_villa_haag.content_i18n.translate import DatabaseTranslationBuffer

translation_namespace = ["user_tracks", "investor_qualification"]
db_buffer = DatabaseTranslationBuffer(translation_namespace)

# Then use it anywhere:
_db(db_buffer, "investor_qualification", "arbitrary_text", {"name": "Phil"})
```

IMPORTANT: Lazy loading is LOST once it is evaluated, so performing any operation on the returned **proxy** object will
break the on-demand translation functionality. E.g.:

```python
_db(db_buffer, "investor_qualification", "arbitrary_text", {"name": "Phil"}) + "another text"
```

would evaluate that composite string and translation would be lost.

## How to use in Management Commands

### manage_content_i18n_translations

RUN: python manage.py manage_content_i18n_translations

This management command iterates through all templates and get_or_creates the translations from the
templates. It also finds duplicates and stale translations.

This way, it's easy to update the translation state of an instance.

### update_content_i18n_fixture

RUN: python manage.py update_content_i18n_fixture

This management command updates the content_i18n fixture with the current state of the database.

### load_content_i18n_fixture

RUN: python manage.py load_content_i18n_fixture

This management command loads the content_i18n fixture into the database. Useful to apply translations to
production server
