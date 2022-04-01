# Reader Library

Alternative Reader Store for the [Sony Reader](https://en.wikipedia.org/wiki/Sony_Reader).

This software creates a webserver to browse and download your ebooks from a specific folder. Only epub format is supported.

The web ui was tested and optimized for the PRS-T2 model.

## Usage

Edit the `docker-compose.yml` file and set the path to your ebooks directory.

To run the container run `docker-compose up`.

You also need to create a DNS override for the domain `readerstore.sony.com` and point it to your server.

You can then click on the reader store icon on your reader and download your ebooks from your server.