#!/usr/bin/env python3.8

# Copyright (C) 2021 Christoph Görn
#
# This file is part of rebuldah.
#
# rebuldah is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# rebuldah is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with rebuldah.  If not, see <http://www.gnu.org/licenses/>.
#


"""A very simple Webhook receiver (from quay)."""

import sys
import logging

import json

from tornado.web import Application, RequestHandler
from tornado.ioloop import IOLoop

from tornado_prometheus import PrometheusMixIn, MetricsHandler


__version__ = "0.1.0-dev"


access_log = logging.getLogger("tornado.access")
access_log.propagate = False
access_log.setLevel(logging.INFO)
stdout_handler = logging.StreamHandler(sys.stdout)
access_log.addHandler(stdout_handler)


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class QuayHandler(RequestHandler):
    """This class handles JSON encoded webhooks coming from quay.io."""

    def set_default_headers(self):
        """Set a default header (for responses)."""
        self.set_header("Content-Type", "application/json")

    async def prepare(self):
        """Parse the Tornado payload into a JSON object."""
        if self.request.headers.get("Content-Type", "").startswith("application/json"):
            self.json_args = json.loads(self.request.body)
        else:
            self.json_args = None

    async def post(self):
        """Handle the POST method coming in from quay.io."""
        logger.info("got a push event from quay")

        logger.debug(self.json_args)

        # TODO forward all valid requests to the Release Engineer!

        r = json.dumps({"status": "ok"})
        self.write(r)


class HealthHandler(RequestHandler):
    """A tiny health handler for OpenShift/Kubernetes."""

    def set_default_headers(self):
        """Set a default header (for responses)."""
        self.set_header("Content-Type", "application/json")

    # noqa: D102
    async def get(self):
        """Handle health requests from the cluster."""
        r = json.dumps({"status": "ok"})
        self.write(r)


class WebhookReceiver(PrometheusMixIn, Application):
    """The main application class."""

    pass


if __name__ == "__main__":
    logger.info("starting...")

    app = WebhookReceiver(
        [
            (r"/quay", QuayHandler),
            (r"/_healthz", HealthHandler),
            (r"/metrics", MetricsHandler),
        ],
        settings={"debug": True, "autoreload": True},
    )

    app.listen(8080)
    IOLoop.current().start()
