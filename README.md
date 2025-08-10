# jfkerman-outline

Quick and dirty VPN key manager for [jfkerman.me](https://jfkerman.me). Written over 2 evenings. Use at your own risk!

[![Built with Cookiecutter Django](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg?logo=cookiecutter)](https://github.com/cookiecutter/cookiecutter-django/)

## Features
- Allows users to create Outline VPN keys for configured servers.
- Also supports Marzban VLESS keys.
- Very basic admin interface for managing servers and keys.
- Hacky integration with OIDC for user authentication.

## Known Issues
- The code stinks. Even vibecoding it would be an improvement, sigh...
- OIDC integration relies on hardcoded `jfkerman-sso` provider ID in templates.
- Direct user authentication is not implemented, users are expected to log in via OIDC. All wiring should be there, though.
- A lot of code duplication between Outline and Marzban views.
- VPN API calls block processing while waiting for a response, which is not ideal.
- Key storage is insecure, keys are stored in plaintext in the database. Not really a big issue since who cares, this is just to watch Youtube in Russia, but still.
- Small bugs here and there, I didn't test everything thoroughly. Again, this was thrown together over a couple evenings.
- Only keys added via user/admin interface are managed, there is no way to import existing keys from the server as they would not be linked to any user. As a consequence, deleting keys directly on the server (with Outline Manager / Marzban) will not remove them from the database (orphaned keys).

License: MIT

## Settings

Moved to [settings](http://cookiecutter-django.readthedocs.io/en/latest/settings.html).

## Deployment

The following details how to deploy this application. This is a pretty standard Django deployment, most guides should work.

---
**NOTE**

I never bothered to set up Docker. Please send me a PR if you figure it out.

---

### Bare metal

0. Clone the repository. Create venv, install requirements with `pip install -r requirements/production.txt`.
1. Configure the settings for your production server (see [settings](http://cookiecutter-django.readthedocs.io/en/latest/settings.html)).
2. Add your server's IP to `ALLOWED_HOSTS` in `config/settings/production.py`.
3. Set `DEBUG = False`.
4. Create a production database and user, and update the `DATABASE_URL` in `config/settings/production.py`.
5. Create necessary directories for media and static files, and update `MEDIA_ROOT` and `STATIC_ROOT` in `config/settings/production.py`.
6. Run `python manage.py collectstatic`.
7. Run `python manage.py migrate`.
8. For translations, run `python manage.py compilemessages`.
9. Create a superuser with `python manage.py createsuperuser`.
10. Install a web server (such as Nginx) and configure it to serve the application using WSGI/ASGI.
11. Create systemd service files for the application and the web server (I forgot to add example files, you are on your own ¯\\\_(ツ)\_/¯). Systemd should point to the `start.sh` file.
12. Create another systemd service for the scheduler, and point it at `schedule.sh`.
13. Pray & start your services.

## Adding servers

To add a server, log in to the admin interface and create a new `Outline Server` object. `Outline Server` object has the following fields:

| Field | Description |
| --- | --- |
| Name | A human-readable name for the server. |
| Slug | A unique identifier for the server. |
| Country | Country where the server is located; this field is used to display flags. See possible options in `jfkerman_outline/static/images/country` |
| Url | URL of the server for client connections. |
| Port | Port of the server for client connections. |
| API URL | URL of the server for API connections, you can find it in installation logs or in Outline Manager. |
| API Cert | SHA256 fingerprint of the server's API certificate (self-signed). |
| Keys per user | Number of keys a user can generate for this server. |
| Max data per key | Max monthly data limit for a single key in megabytes. |


Command to obtain API Cert SHA256 fingerprint:

```
openssl s_client -connect <API URL> < /dev/null 2>/dev/null | openssl x509 -fingerprint -noout -in /dev/stdin
```



