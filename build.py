#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

import os
from conans import tools
from bincrafters import build_template_default


if __name__ == "__main__":

    builder = build_template_default.get_builder()
    builder.run()
