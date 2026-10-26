# Installing Plone on separate servers

This page shows you how to set up Graffiti with the ZEO server and Solr on one host and the Plone instance on another.
The ZEO server has no authentication.
That is why it and Solr bind to `localhost` only, and the Plone instance reaches both exclusively through the SSH tunnel from section 4.
The Plone instance itself also listens on `127.0.0.1` only, the web server on the same host (Apache) is the only way in.

## 1. Prepare the installation (on both servers)

Clone the repository:

```shell
git clone git@code.interaktiv.de:interaktiv/graffiti.git
cd graffiti
```

Prepare the buildout:

```shell
./bootstrap.sh
```

Adjust the configuration in `_stage-settings.cfg` to your environment:

```
zeo-address = ZEO_URL:ZEO_PORT    # example: zeo.graffiti.stage.interaktiv.de:15000
domain = PLONE_URL                # example: graffiti.stage.interaktiv.de
```

## 2. Install ZEO (on the ZEO host only)

Run the buildout:

```shell
bin/buildout -c stage-zeo.cfg
```

Start ZEO:

```shell
bin/zeo fg
```

## 3. Install Plone (on the Plone host only)

Install the programs of the PDF check (`graffiti.pdfcheck`), without them its steps are skipped:

```shell
sudo apt install poppler-utils qpdf
```

Run the buildout:

```shell
bin/buildout -c stage-plone.cfg
```

Start the instance:

```shell
bin/instance fg
```

The instance listens on `127.0.0.1:15001` only, not on all network interfaces.
This is set by `http-address` in section `[instance]` of [buildout.d/plone.cfg](../../buildout.d/plone.cfg).
Under WSGI the buildout recipe ignores `ip-address`, and a port without a host in `http-address` means `0.0.0.0`.
Apache on the same host forwards the requests to the instance.
To reach the instance directly from your machine, use an SSH tunnel as in section 5.

## 4. Port forwarding between Plone and the ZEO and Solr host

The port forwarding is set up automatically and fail-safe with [autossh](https://linux.die.net/man/1/autossh) and [collective.recipe.supervisor](https://pypi.org/project/collective.recipe.supervisor/).
This makes sure the connection comes back on its own after a server restart or a network problem.
The implementation is in [buildout.d/plone.cfg](../../buildout.d/plone.cfg), sections `[zeo-tunnel]` and `[supervisor]`.

The SSH connection to the ZEO host is configured with `zeo-tunnel-address`:

```
zeo-tunnel-address = graffiti-zeo-stage@rapunzel.interaktiv.de
```

The SSH connection from the Plone client to the ZEO host must be key based (the SSH key has to be in `~/.ssh/authorized_keys` on the ZEO host), so that the connection can be established in the background without interaction.

Background: because the Plone clients and the ZEO server run on different servers, they cannot talk to each other through `localhost` out of the box.
Opening the ZEO port to the public would make that possible, but it is a security risk.
Instead, SSH forwards the port only to the host of the Plone instance.
From the point of view of both systems the communication then runs through `localhost`, so the address of the ZEO server is set accordingly on both hosts:

```
zeo-host = localhost
zeo-port = 15000
```

You can also set the port forwarding up by hand instead of with autossh.
The option `-L` forwards the ports through the SSH connection, `-fN` keeps the process in the background:

```shell
ssh graffiti-zeo-stage@rapunzel.interaktiv.de -fN -L 15000:localhost:15000 -L 2100:localhost:2100
```

- 15000 is the port of the ZEO server.
- 2100 is the port of Solr.

## 5. Set up Plone

A fresh buildout starts without a Plone site.
You create it yourself, for example with the id `site`.

The site is then reachable at an address like `https://graffiti.stage.interaktiv.de`.
The page where you create the site is not, because the web server only proxies the site itself.
On a local installation `http://localhost:8080` may work, on a server behind Apache it does not.

Forward the port of the Plone instance to your machine:

```shell
ssh USER@SERVER -L 15001:localhost:15001
```

The command assumes the default port 15001 of the Plone instance.
Then open `http://localhost:15001` to reach the Zope root, where you can create the Plone site.
In the future `collective.recipe.plonesite` could make this step unnecessary.

## 6. More programs next to Plone (optional)

supervisor on the Plone host also loads programs from files in the buildout folder: `etc/supervisor.d/*.conf`.
This is the `include` line in section `[supervisor]` of [buildout.d/plone.cfg](../../buildout.d/plone.cfg).
So a service next to Plone can run under the same supervisor without a change to the buildout.

Each file holds one `[program:<name>]` section in the normal supervisor format.
Use absolute paths in it, the file is read from the folder `etc/supervisor.d/`.

```shell
mkdir -p etc/supervisor.d
ln -s /path/to/my-service.conf etc/supervisor.d/my-service.conf
bin/supervisorctl reread
bin/supervisorctl update
```

To remove the program, delete the file and run `reread` and `update` again.
The folder is in `.gitignore`.
Without any file there supervisor runs as before, it only writes the warning `No file matches via include` to its log.
