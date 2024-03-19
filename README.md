# jfkerman-outline

Quick and dirty Outline VPN key manager for [jfkerman.me](https://jfkerman.me). Written over 2 evenings, so don't expect any quality code or documentation here.

[![Built with Cookiecutter Django](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg?logo=cookiecutter)](https://github.com/cookiecutter/cookiecutter-django/)

License: MIT

## Settings

Moved to [settings](http://cookiecutter-django.readthedocs.io/en/latest/settings.html).

## Deployment

The following details how to deploy this application.

---
**NOTE**

I am a dum dum who never learned to use Docker. Please send me a PR if you figure it out.

---

### Bare metal

0. Clone the repository.
1. Configure the settings for your production server (see [settings](http://cookiecutter-django.readthedocs.io/en/latest/settings.html)).
2. Add your server's IP to `ALLOWED_HOSTS` in `config/settings/production.py`.
3. Set `DEBUG = False`.
4. Create a production database and user, and update the `DATABASE_URL` in `config/settings/production.py`.
5. Create necessary directories for media and static files, and update `MEDIA_ROOT` and `STATIC_ROOT` in `config/settings/production.py`.
6. Run `python manage.py collectstatic`.
7. Run `python manage.py migrate`.
8. Create a superuser with `python manage.py createsuperuser`.
9. Install a web server (e.g. Nginx) and configure it to serve the application using WSGI/ASGI.
10. Create systemd service files for the application and the web server (I forgot to add example files, you are on your own ¯\\\_(ツ)\_/¯). Systemd should point to the `start.sh` file.
11. Create a cron job (or a systemd timer) to run `schedule.sh` every 5 minutes.
12. Start your services, it should hopefully work.

## Adding servers

To add a server, log in to the admin interface and create a new `Outline Server` object. The `Outline Server` object has the following fields:

| Field | Description |
| --- | --- |
| Name | A human-readable name for the server. |
| Slug | A unique identifier for the server. |
| Country | The country where the server is located; this field is used to display flags. See possible options in `jfkerman_outline/static/images/country` |
| Url | The URL of the server for client connections. |
| Port | The port of the server for client connections. |
| API URL | The URL of the server for API connections, you can find it in installation logs or in Outline Manager. |
| API Cert | SHA256 fingerprint of the server's API certificate (self-signed). |
| Keys per user | The number of keys a user can generate for this server. |
| Max data per key | Max monthly data limit for a single key. |


Command to obtain API Cert SHA256 fingerprint:

```
openssl s_client -connect <API URL> < /dev/null 2>/dev/null | openssl x509 -fingerprint -noout -in /dev/stdin
```



